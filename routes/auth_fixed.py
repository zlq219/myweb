# routes/auth_fixed.py - 临时修复版
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from utils.mailer import send_verification_email
from datetime import datetime

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

        # 创建用户（但未激活） - 修复版
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'is_active': False,
            'is_admin': False,
            'email_verified': False,
            'created_at': datetime.utcnow()  # 添加时间戳
        }

        user = User.create(get_mongo(), user_data)

        # 发送验证邮件
        if send_verification_email(user):
            flash('注册成功！请检查您的邮箱完成验证。', 'success')
        else:
            flash('注册成功，但验证邮件发送失败。请联系管理员。', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('register.html')

# 其他函数保持不变...