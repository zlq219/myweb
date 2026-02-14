from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from utils.mailer import send_verification_email
from datetime import datetime
from werkzeug.security import generate_password_hash
#from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)


def get_mongo():
    return current_app.mongo


def get_user_model():
    from models.user import User
    return User


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 基本验证
        if not username or not email or not password:
            flash('请填写所有必填项', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('register.html')

        # 检查用户名和邮箱是否已存在
        User = get_user_model()
        if User.get_by_username(get_mongo(), username):
            flash('用户名已存在', 'danger')
            return render_template('register.html')

        if User.get_by_email(get_mongo(), email):
            flash('邮箱已被注册', 'danger')
            return render_template('register.html')

        # 创建用户（但未激活）
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),  # 这里改为 password_hash
            'is_active': False,
            'is_admin': False,
            'email_verified': False,
            'created_at': datetime.utcnow()
        }

        user = User.create(get_mongo(), user_data)

        # 发送验证邮件
        if send_verification_email(user):
            flash('注册成功！请检查您的邮箱完成验证。', 'success')
        else:
            flash('注册成功，但验证邮件发送失败。请联系管理员。', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    User = get_user_model()

    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-verification', max_age=3600)

        user = User.get_by_email(get_mongo(), email)
        if not user:
            flash('验证链接无效或已过期。', 'danger')
            return redirect(url_for('main.index'))

        update_data = {
            'email_verified': True,
            'is_active': True,
            'email_verification_token': '',
            'email_verification_sent_at': None
        }
        User.update(get_mongo(), user.id, update_data)

        flash('邮箱验证成功！您现在可以登录了。', 'success')
        return redirect(url_for('auth.login'))

    except SignatureExpired:
        flash('验证链接已过期，请重新请求验证邮件。', 'danger')
        return redirect(url_for('auth.resend_verification'))
    except BadSignature:
        flash('验证链接无效。', 'danger')
        return redirect(url_for('main.index'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('请输入邮箱地址。', 'danger')
            return render_template('resend_verification.html')

        User = get_user_model()
        user = User.get_by_email(get_mongo(), email)

        if not user:
            flash('该邮箱未注册。', 'danger')
            return render_template('resend_verification.html')

        if user.email_verified:
            flash('该邮箱已验证，请直接登录。', 'info')
            return redirect(url_for('auth.login'))

        if send_verification_email(user):
            flash('验证邮件已重新发送，请检查您的邮箱。', 'success')
        else:
            flash('邮件发送失败，请稍后重试。', 'danger')

        return redirect(url_for('auth.login'))

    return render_template('resend_verification.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        User = get_user_model()

        # 先尝试按用户名查找
        user = User.get_by_username(get_mongo(), identifier)

        # 如果按用户名没找到，再尝试按邮箱查找
        if not user:
            user = User.get_by_email(get_mongo(), identifier.lower())

        if user and user.check_password(password):
            # 检查邮箱验证
            if hasattr(user, 'email_verified') and not user.email_verified:
                flash('请先验证您的邮箱才能登录', 'warning')
                return render_template('auth/login.html')

            # 检查用户状态
            if hasattr(user, 'is_active') and not user.is_active:
                flash('账户已被禁用', 'error')
                return render_template('auth/login.html')

            login_user(user, remember=request.form.get('remember_me') == 'on')

            # 移除 update_last_login 调用，因为User类中没有这个方法

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.home')

            flash('登录成功！', 'success')
            return redirect(next_page)
        else:
            flash('用户名/邮箱或密码错误', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员专属登录 - 普通用户无法登录"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        User = get_user_model()
        user = User.get_by_email(get_mongo(), email)

        if user and user.check_password(password):
            # 🔥 关键修改：必须是管理员才能登录
            if not user.is_admin:
                flash('此页面仅限管理员访问', 'danger')
                return render_template('auth/admin_login.html')

            # 检查邮箱验证
            if not user.email_verified:
                flash('管理员账户也必须验证邮箱', 'warning')
                return render_template('verify_prompt.html', email=email)

            login_user(user, remember=True)
            flash('管理员登录成功！', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('邮箱或密码错误', 'danger')

    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """退出登录"""
    from flask import Response

    logout_user()
    flash('您已成功退出登录。', 'success')

    response = redirect(url_for('auth.login'))
    response.delete_cookie('flask_session')
    response.delete_cookie('session')
    response.delete_cookie('remember_token')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'

    return response