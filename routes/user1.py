from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)


def get_mongo():
    """获取MongoDB连接"""
    return current_app.mongo


def get_user_model():
    """获取用户模型，避免循环导入"""
    from models.user import User
    return User


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        bio = request.form.get('bio', '').strip()

        if not username:
            flash('用户名不能为空', 'danger')
            return redirect(url_for('user.profile'))

        User = get_user_model()

        # 检查用户名是否已被使用（除了当前用户）
        existing_user = User.get_by_username(get_mongo(), username)
        if existing_user and existing_user.id != current_user.id:
            flash('该用户名已被使用', 'danger')
            return redirect(url_for('user.profile'))

        update_data = {
            'username': username,
            'bio': bio
        }

        # 处理头像上传
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                update_data['avatar'] = f'/static/uploads/{filename}'

        User.update(get_mongo(), current_user.id, update_data)
        flash('个人资料已更新', 'success')
        return redirect(url_for('user.profile'))

    return render_template('profile.html')


@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not all([current_password, new_password, confirm_password]):
        flash('请填写所有密码字段', 'danger')
        return redirect(url_for('user.profile'))

    User = get_user_model()
    user = User.get_by_id(get_mongo(), current_user.id)

    if not user.check_password(current_password):
        flash('当前密码错误', 'danger')
        return redirect(url_for('user.profile'))

    if new_password != confirm_password:
        flash('新密码和确认密码不一致', 'danger')
        return redirect(url_for('user.profile'))

    from utils.validators import validate_password
    if not validate_password(new_password):
        flash('密码必须包含大小写字母和数字，长度6-20位', 'danger')
        return redirect(url_for('user.profile'))

    user.set_password(new_password)
    User.update(get_mongo(), current_user.id, {'password_hash': user.password_hash})
    flash('密码修改成功', 'success')
    return redirect(url_for('user.profile'))


@user_bp.route('/users')
@login_required
def user_list():
    User = get_user_model()

    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.dashboard'))

    page = request.args.get('page', 1, type=int)
    users = User.get_all(get_mongo(), page=page, per_page=current_app.config['USERS_PER_PAGE'])
    total = User.get_count(get_mongo())

    return render_template('users.html', users=users, page=page, total=total)


@user_bp.route('/user/<user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    User = get_user_model()

    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '没有权限'}), 403

    user = User.get_by_id(get_mongo(), user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    new_status = not user.is_active
    User.update(get_mongo(), user_id, {'is_active': new_status})

    return jsonify({
        'success': True,
        'message': '操作成功',
        'is_active': new_status
    })