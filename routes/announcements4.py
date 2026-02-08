from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from bson import ObjectId

announcements_bp = Blueprint('announcements', __name__)


def get_mongo():
    from flask import current_app
    return current_app.mongo


# ============ 普通用户功能 ============

@announcements_bp.route('/announcements')
@login_required
def announcement_list():
    """公告列表页面 - 所有登录用户都可以访问"""
    mongo = get_mongo()

    # 只显示已发布的公告
    query = {'status': 'published'}

    # 获取公告列表
    announcements = list(mongo.db.announcements.find(query)
                         .sort([('is_pinned', -1), ('publish_time', -1)])
                         .limit(20))

    # 转换数据格式
    for ann in announcements:
        ann['_id'] = str(ann['_id'])
        ann['publish_time_str'] = ann['publish_time'].strftime('%Y-%m-%d %H:%M')
        # 简略内容
        if 'content' in ann and len(ann['content']) > 100:
            ann['summary'] = ann['content'][:100] + '...'
        else:
            ann['summary'] = ann.get('content', '')

    return render_template('announcements/list.html',
                           announcements=announcements)


@announcements_bp.route('/announcements/<announcement_id>')
@login_required
def announcement_detail(announcement_id):
    """公告详情页面"""
    mongo = get_mongo()

    try:
        announcement = mongo.db.announcements.find_one({
            '_id': ObjectId(announcement_id),
            'status': 'published'
        })

        if not announcement:
            flash('公告不存在或已被删除', 'warning')
            return redirect(url_for('announcements.announcement_list'))

        # 增加查看次数
        mongo.db.announcements.update_one(
            {'_id': ObjectId(announcement_id)},
            {'$inc': {'view_count': 1}}
        )

        # 转换格式
        announcement['_id'] = str(announcement['_id'])
        announcement['publish_time_str'] = announcement['publish_time'].strftime('%Y-%m-%d %H:%M:%S')

        return render_template('announcements/detail.html',
                               announcement=announcement)

    except:
        flash('公告ID格式错误', 'danger')
        return redirect(url_for('announcements.announcement_list'))


# ============ 管理员功能 ============

def admin_required(f):
    """管理员权限装饰器"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限访问此页面。', 'danger')
            return redirect(url_for('announcements.announcement_list'))
        return f(*args, **kwargs)

    return decorated_function


@announcements_bp.route('/admin/announcements')
@login_required
@admin_required
def admin_dashboard():
    """公告管理仪表盘"""
    mongo = get_mongo()

    # 获取统计数据
    stats = {
        'total': mongo.db.announcements.count_documents({}),
        'published': mongo.db.announcements.count_documents({'status': 'published'}),
        'draft': mongo.db.announcements.count_documents({'status': 'draft'})
    }

    # 获取最近公告
    recent_announcements = list(mongo.db.announcements.find()
                                .sort('created_at', -1)
                                .limit(5))

    for ann in recent_announcements:
        ann['_id'] = str(ann['_id'])
        if 'publish_time' in ann:
            ann['publish_time_str'] = ann['publish_time'].strftime('%Y-%m-%d %H:%M')

    return render_template('announcements/admin_dashboard.html',
                           stats=stats,
                           recent_announcements=recent_announcements)


@announcements_bp.route('/admin/announcements/list')
@login_required
@admin_required
def admin_announcement_list():
    """管理员公告列表"""
    mongo = get_mongo()

    # 状态筛选
    status = request.args.get('status', 'all')
    query = {}
    if status != 'all':
        query['status'] = status

    # 获取公告列表
    announcements = list(mongo.db.announcements.find(query)
                         .sort([('is_pinned', -1), ('publish_time', -1)]))

    for ann in announcements:
        ann['_id'] = str(ann['_id'])
        if 'publish_time' in ann:
            ann['publish_time_str'] = ann['publish_time'].strftime('%Y-%m-%d %H:%M')

    return render_template('announcements/admin_list.html',
                           announcements=announcements,
                           status=status)


@announcements_bp.route('/admin/announcements/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    """创建公告"""
    if request.method == 'POST':
        mongo = get_mongo()

        # 获取表单数据
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', '通知')
        priority = int(request.form.get('priority', 1))
        is_pinned = request.form.get('is_pinned') == 'on'

        # 验证数据
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return render_template('announcements/create.html')

        # 创建公告
        announcement = {
            'title': title,
            'content': content,
            'category': category,
            'priority': priority,
            'status': 'published',
            'author_id': current_user.id,
            'author_name': current_user.username,
            'publish_time': datetime.utcnow(),
            'view_count': 0,
            'is_pinned': is_pinned,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        mongo.db.announcements.insert_one(announcement)

        flash('公告发布成功!', 'success')
        return redirect(url_for('announcements.admin_announcement_list'))

    return render_template('announcements/create.html')


@announcements_bp.route('/admin/announcements/<announcement_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(announcement_id):
    """编辑公告"""
    mongo = get_mongo()

    try:
        announcement = mongo.db.announcements.find_one({'_id': ObjectId(announcement_id)})

        if not announcement:
            flash('公告不存在', 'danger')
            return redirect(url_for('announcements.admin_announcement_list'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', '通知')
            priority = int(request.form.get('priority', 1))
            is_pinned = request.form.get('is_pinned') == 'on'

            if not title or not content:
                flash('标题和内容不能为空', 'danger')
                return render_template('announcements/edit.html', announcement=announcement)

            mongo.db.announcements.update_one(
                {'_id': ObjectId(announcement_id)},
                {'$set': {
                    'title': title,
                    'content': content,
                    'category': category,
                    'priority': priority,
                    'is_pinned': is_pinned,
                    'updated_at': datetime.utcnow()
                }}
            )

            flash('公告更新成功!', 'success')
            return redirect(url_for('announcements.admin_announcement_list'))

        # GET请求，显示编辑表单
        announcement['_id'] = str(announcement['_id'])
        return render_template('announcements/edit.html', announcement=announcement)

    except:
        flash('公告ID格式错误', 'danger')
        return redirect(url_for('announcements.admin_announcement_list'))


@announcements_bp.route('/admin/announcements/<announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    """删除公告"""
    mongo = get_mongo()

    try:
        result = mongo.db.announcements.delete_one({'_id': ObjectId(announcement_id)})

        if result.deleted_count > 0:
            flash('公告删除成功!', 'success')
        else:
            flash('公告不存在', 'warning')

    except:
        flash('公告ID格式错误', 'danger')

    return redirect(url_for('announcements.admin_announcement_list'))