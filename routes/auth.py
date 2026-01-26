from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask import current_app

auth_bp = Blueprint('auth', __name__)


def get_mongo():
    """获取MongoDB连接"""
    return current_app.mongo


def get_user_model():
    """获取用户模型，避免循环导入"""
    from models.user import User
    return User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
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
            if not user.is_active:
                flash('账户已被禁用，请联系管理员', 'danger')
                return render_template('login.html')

            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('登录成功！', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('邮箱或密码错误', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 验证输入
        if not all([username, email, password, confirm_password]):
            flash('请填写所有字段', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('register.html')

        # 导入验证工具
        from utils.validators import validate_email, validate_password, validate_username

        if not validate_email(email):
            flash('邮箱格式不正确', 'danger')
            return render_template('register.html')

        if not validate_username(username):
            flash('用户名只能包含字母、数字和下划线，长度3-20位', 'danger')
            return render_template('register.html')

        if not validate_password(password):
            flash('密码必须包含大小写字母和数字，长度6-20位', 'danger')
            return render_template('register.html')

        User = get_user_model()

        # 检查用户是否存在
        if User.get_by_email(get_mongo(), email):
            flash('该邮箱已被注册', 'danger')
            return render_template('register.html')

        if User.get_by_username(get_mongo(), username):
            flash('该用户名已被使用', 'danger')
            return render_template('register.html')

        # 创建用户
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'is_active': True,
            'is_admin': False
        }

        user = User.create(get_mongo(), user_data)
        login_user(user)
        flash('注册成功！欢迎加入！', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('main.index'))