from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from utils.mailer import send_verification_email
from datetime import datetime  # 添加这一行！

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
            'password': password,
            'is_active': False,  # 初始状态为未激活
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

        # 不自动登录，需要先验证邮箱
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# 新增邮箱验证路由
@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    User = get_user_model()

    try:
        # 解码令牌
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-verification', max_age=3600)

        # 查找用户
        user = User.get_by_email(get_mongo(), email)
        if not user:
            flash('验证链接无效或已过期。', 'danger')
            return redirect(url_for('main.index'))

        # 更新用户验证状态
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


# 新增重新发送验证邮件路由
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

        # 重新发送验证邮件
        if send_verification_email(user):
            flash('验证邮件已重新发送，请检查您的邮箱。', 'success')
        else:
            flash('邮件发送失败，请稍后重试。', 'danger')

        return redirect(url_for('auth.login'))

    return render_template('resend_verification.html')


# 修改登录逻辑，检查邮箱是否验证
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # 如果已登录，根据用户权限跳转到不同页面
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = 'remember' in request.form

        if not email or not password:
            flash('请输入邮箱和密码', 'danger')
            return render_template('login.html')

        User = get_user_model()
        user = User.get_by_email(get_mongo(), email)

        if user and user.check_password(password):
            # 检查邮箱是否已验证
            if not user.email_verified:
                flash('请先验证您的邮箱。', 'warning')
                return render_template('verify_prompt.html', email=email)

            if not user.is_active:
                flash('账户已被禁用，请联系管理员', 'danger')
                return render_template('login.html')

            #login_user(user, remember=remember)
            # 找到这行（大约第121行）：
            login_user(user, remember=remember)

            # 确保它被修改为（如果没有，请现在修改）：
            login_user(user, remember=False)  # 强制不记住，即使表单有勾选

            next_page = request.args.get('next')
            flash('登录成功！', 'success')

            # ============ 新增的权限判断逻辑 ============
            if next_page:
                # 如果存在next参数（如访问受保护页面触发的跳转），优先跳转到next
                return redirect(next_page)
            elif user.is_admin:
                # 如果是管理员，跳转到管理后台
                return redirect(url_for('admin.dashboard'))
            else:
                # 普通用户跳转到用户面板
                return redirect(url_for('main.dashboard'))
            # ==========================================
        else:
            flash('邮箱或密码错误', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    from flask import Response

    logout_user()
    flash('您已成功退出登录。', 'success')

    # 创建重定向响应
    response = redirect(url_for('auth.login'))

    # 主动清除所有可能的会话Cookie
    response.delete_cookie('flask_session')
    response.delete_cookie('session')
    response.delete_cookie('remember_token')

    # 确保不会设置新的会话
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'

    return response