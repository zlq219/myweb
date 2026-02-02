# routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import mongo
from models.user import User
import hashlib

user_bp = Blueprint('user', __name__)


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

    # 更新密码
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
    mongo.db.users.update_one(
        {'_id': current_user.id},
        {'$set': {'password': hashed_password}}
    )

    flash('密码修改成功！', 'success')
    return redirect(url_for('user.profile'))


# 在 routes/user.py 中添加
@user_bp.route('/users')
@login_required
def user_list():
    """普通用户的用户列表（如果有需要的话）"""
    # 这里可以显示一些公开的用户信息
    # 或者只显示朋友列表等

    # 如果是普通用户，可能不需要这个功能
    # 用户管理应该是管理员的功能

    # 临时实现：重定向到个人中心
    return redirect(url_for('user.profile'))