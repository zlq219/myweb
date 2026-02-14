from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/home')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """用户仪表盘"""
    return render_template('dashboard/index.html',
                           page_title='控制台')


@dashboard_bp.route('/admin/dashboard')
@login_required
def admin_index():
    """管理员仪表盘"""
    if not current_user.is_admin:
        return redirect(url_for('dashboard.index'))

    return render_template('dashboard/admin_index.html',
                           page_title='管理面板')