from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps

# 1. 首先定义蓝图
admin_bp = Blueprint('admin', __name__)

# 2. 管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'danger')
            return redirect(url_for('auth.login'))
        if not getattr(current_user, 'is_admin', False):
            flash('您没有管理员权限', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# 3. 现在可以定义路由了
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():  # 修改函数名：admin_dashboard → dashboard
    """管理员仪表板"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
@login_required
@admin_required
def user_management():
    """用户管理"""
    # 这里可以添加获取用户列表的逻辑
    return render_template('admin/users.html')

@admin_bp.route('/settings')
@login_required
@admin_required
def admin_settings():
    """管理员设置"""
    return render_template('admin/settings.html')

# 添加更多管理员路由...