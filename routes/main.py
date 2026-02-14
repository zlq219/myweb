from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from config.admin_menu import get_public_menu, get_user_menu, get_admin_menu  # 导入所有菜单函数

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页 - 未登录用户"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    # 获取公共菜单
    public_menu = get_public_menu()

    return render_template('index.html', public_menu=public_menu)


@main_bp.route('/home')
@login_required
def home():
    """用户主页 - 登录后显示"""
    from flask import current_app
    mongo = current_app.mongo

    # 获取最近公告
    recent_announcements = list(mongo.db.announcements.find(
        {'status': 'published'}
    ).sort('publish_time', -1).limit(5))

    # 处理公告数据
    for ann in recent_announcements:
        ann['_id'] = str(ann['_id'])
        ann['publish_time_str'] = ann['publish_time'].strftime('%Y-%m-%d %H:%M')
        if 'content' in ann and len(ann['content']) > 100:
            ann['summary'] = ann['content'][:100] + '...'
        else:
            ann['summary'] = ann.get('content', '')

    # 根据用户类型获取菜单
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        # 管理员看到的是管理员菜单
        menu = get_admin_menu(current_user)
        template = 'admin/dashboard.html'  # 管理员看到的是后台
    else:
        # 普通用户看到的是用户菜单
        menu = get_user_menu(current_user)
        template = 'home.html'

    return render_template(template,
                           recent_announcements=recent_announcements,
                           user_menu=menu)  # 传递菜单数据


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """控制台（保持兼容性）"""
    return redirect(url_for('main.home'))


@main_bp.route('/about')
def about():
    """关于页面"""
    # 获取公共菜单
    public_menu = get_public_menu()
    return render_template('about.html', public_menu=public_menu)


@main_bp.route('/admin-entry')
def admin_entry():
    """管理员专用入口页面"""
    public_menu = get_public_menu()
    return render_template('admin_entry.html', public_menu=public_menu)


# 错误处理函数
@main_bp.app_errorhandler(404)
def page_not_found(e):
    """404错误页面"""
    public_menu = get_public_menu()
    return render_template('404.html', public_menu=public_menu), 404


@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """500错误页面"""
    public_menu = get_public_menu()
    return render_template('500.html', public_menu=public_menu), 500