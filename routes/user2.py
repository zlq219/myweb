# routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user import User
import hashlib

user_bp = Blueprint('user', __name__)


def get_mongo():
    """安全地获取mongo实例"""
    return current_app.mongo


@user_bp.route('/profile')
@login_required
def profile():
    """个人中心页面"""
    return render_template('profile.html')


@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    # 验证输入
    if not current_password or not new_password or not confirm_password:
        flash('请填写所有字段', 'danger')
        return redirect(url_for('user.profile'))

    if new_password != confirm_password:
        flash('两次输入的新密码不一致', 'danger')
        return redirect(url_for('user.profile'))

    if len(new_password) < 6:
        flash('新密码至少需要6位', 'danger')
        return redirect(url_for('user.profile'))

    # 验证当前密码
    if not current_user.check_password(current_password):
        flash('当前密码错误', 'danger')
        return redirect(url_for('user.profile'))

    # 使用User模型的update方法更新密码
    mongo = get_mongo()

    # 生成新的密码哈希
    from werkzeug.security import generate_password_hash
    new_password_hash = generate_password_hash(new_password)

    # 更新数据库
    User.update(mongo, current_user.id, {'password_hash': new_password_hash})

    # 更新当前用户的password_hash（为了当前会话）
    current_user.password_hash = new_password_hash

    flash('密码修改成功！', 'success')
    return redirect(url_for('user.profile'))