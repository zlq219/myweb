# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from bson import ObjectId
from datetime import datetime, timedelta
from flask import current_app
from config.admin_menu import get_admin_menu  # 只从config导入

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


def get_mongo():
    """安全地获取mongo实例"""
    return current_app.mongo


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    mongo = get_mongo()

    # 获取统计数据
    total_users = mongo.db.users.count_documents({})
    active_users = mongo.db.users.count_documents({'email_verified': True})
    unverified_users = mongo.db.users.count_documents({'email_verified': False})
    admin_users = mongo.db.users.count_documents({'is_admin': True})

    # 获取公告数量
    announcements_count = mongo.db.announcements.count_documents({})

    # 获取最后公告时间
    last_announcement = mongo.db.announcements.find_one(sort=[('created_at', -1)])
    last_announcement_time = last_announcement['created_at'].strftime('%Y-%m-%d %H:%M') if last_announcement else '暂无公告'

    # 获取管理员菜单（直接使用，不进行过滤）
    admin_menu = get_admin_menu(current_user)

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           active_users=active_users,
                           unverified_users=unverified_users,
                           admin_users=admin_users,
                           announcements_count=announcements_count,
                           last_announcement_time=last_announcement_time,
                           current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                           admin_menu=admin_menu)  # 传递菜单数据


@admin_bp.route('/users')
@login_required
@admin_required
def user_management():
    """用户管理页面"""
    mongo = get_mongo()

    # 获取管理员菜单
    admin_menu = get_admin_menu(current_user)

    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()
    filter_type = request.args.get('filter', 'all')

    # 构建查询条件
    query = {}

    # 搜索条件
    if search:
        query['$or'] = [
            {'username': {'$regex': search, '$options': 'i'}},
            {'email': {'$regex': search, '$options': 'i'}}
        ]

    # 筛选条件
    if filter_type == 'verified':
        query['email_verified'] = True
    elif filter_type == 'unverified':
        query['email_verified'] = False
    elif filter_type == 'admins':
        query['is_admin'] = True
    elif filter_type == 'active':
        query['is_active'] = True
    elif filter_type == 'inactive':
        query['is_active'] = False

    # 计算总数
    total_users = mongo.db.users.count_documents(query)

    # 分页查询
    skip = (page - 1) * per_page
    users_cursor = mongo.db.users.find(query).sort('created_at', -1).skip(skip).limit(per_page)

    # 处理用户数据
    users = []
    for user in users_cursor:
        # 转换ObjectId为字符串
        user['_id'] = str(user['_id'])

        # 格式化时间
        if isinstance(user.get('created_at'), datetime):
            user['created_at_str'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            user['created_at_str'] = 'N/A'

        if isinstance(user.get('updated_at'), datetime):
            user['updated_at_str'] = user['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            user['updated_at_str'] = 'N/A'

        users.append(user)

    # 统计信息
    stats = {
        'total': mongo.db.users.count_documents({}),
        'verified': mongo.db.users.count_documents({'email_verified': True}),
        'unverified': mongo.db.users.count_documents({'email_verified': False}),
        'admins': mongo.db.users.count_documents({'is_admin': True}),
        'active': mongo.db.users.count_documents({'is_active': True}),
        'inactive': mongo.db.users.count_documents({'is_active': False})
    }

    return render_template('users.html',
                           users=users,
                           page=page,
                           per_page=per_page,
                           total_users=total_users,
                           search=search,
                           filter_type=filter_type,
                           stats=stats,
                           admin_menu=admin_menu)  # 传递菜单数据


# ... 其他路由函数保持不变，但都需要添加 admin_menu=admin_menu
# 下面是其他路由函数的简化版本（需要添加admin_menu）

@admin_bp.route('/cleanup-now')
@login_required
@admin_required
def cleanup_unverified_users_page():
    """手动清理未验证用户页面"""
    mongo = get_mongo()
    admin_menu = get_admin_menu(current_user)  # 添加这行

    # 计算7天前的日期
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # 查询符合条件的用户
    query = {
        'email_verified': False,
        'created_at': {'$lt': seven_days_ago},
        'is_admin': False
    }

    # 获取要清理的用户列表
    users_to_cleanup = list(mongo.db.users.find(query))

    # 转换数据格式
    for user in users_to_cleanup:
        user['_id'] = str(user['_id'])
        user['created_at_str'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    return render_template('admin/cleanup.html',
                           users=users_to_cleanup,
                           count=len(users_to_cleanup),
                           admin_menu=admin_menu)  # 传递菜单数据


@admin_bp.route('/settings')
@login_required
@admin_required
def admin_settings():
    """管理员设置"""
    admin_menu = get_admin_menu(current_user)  # 添加这行
    return render_template('admin/settings.html', admin_menu=admin_menu)