# routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from config.admin_menu import get_user_menu  # 导入菜单函数

user_bp = Blueprint('user', __name__)


def get_mongo():
    """安全地获取mongo实例"""
    return current_app.mongo


def get_user_model():
    from models.user import User
    return User


@user_bp.route('/profile')
@login_required
def profile():
    """个人中心页面"""
    # 获取普通用户菜单
    user_menu = get_user_menu(current_user)

    return render_template('profile.html', user_menu=user_menu)


@user_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """更新个人信息"""
    username = request.form.get('username', '').strip()
    avatar = request.form.get('avatar', '').strip()
    bio = request.form.get('bio', '').strip()

    # 验证输入
    if not username:
        flash('用户名不能为空', 'danger')
        return redirect(url_for('user.profile'))

    # 验证用户名格式
    from utils.validators import validate_username
    if not validate_username(username):
        flash('用户名格式不正确（3-20个字符，只能包含字母、数字和下划线）', 'danger')
        return redirect(url_for('user.profile'))

    # 检查用户名是否已被其他人使用
    mongo = get_mongo()
    User = get_user_model()
    existing_user = User.get_by_username(mongo, username)
    if existing_user and existing_user.id != current_user.id:
        flash('该用户名已被使用，请选择其他用户名', 'danger')
        return redirect(url_for('user.profile'))

    # 构建更新数据
    update_data = {
        'username': username,
        'avatar': avatar if avatar else '',
        'bio': bio
    }

    # 更新数据库
    try:
        User.update(mongo, current_user.id, update_data)

        # 更新当前用户对象的属性
        current_user.username = username
        current_user.avatar = avatar if avatar else ''
        current_user.bio = bio

        flash('个人信息更新成功！', 'success')
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'danger')

    return redirect(url_for('user.profile'))


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
    User = get_user_model()

    # 生成新的密码哈希
    new_password_hash = generate_password_hash(new_password)

    # 更新数据库
    User.update(mongo, current_user.id, {'password_hash': new_password_hash})

    # 更新当前用户的password_hash（为了当前会话）
    current_user.password_hash = new_password_hash

    flash('密码修改成功！', 'success')
    return redirect(url_for('user.profile'))


@user_bp.route('/users')
@login_required
def user_list():
    """普通用户的用户列表（如果有需要的话）"""
    return redirect(url_for('user.profile'))