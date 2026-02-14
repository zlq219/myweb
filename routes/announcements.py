from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from bson import ObjectId
from config import get_admin_menu
from functools import wraps
from utils.menu_helper import get_admin_menu, filter_menu_by_permission

announcements_bp = Blueprint('announcements', __name__)


def get_mongo():
    """获取MongoDB连接"""
    from flask import current_app
    return current_app.mongo


def admin_required(f):
    """管理员权限装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限访问此页面。', 'danger')
            return redirect(url_for('announcements.announcement_list'))
        return f(*args, **kwargs)

    return decorated_function


def convert_announcement_data(announcement):
    """转换公告数据格式"""
    announcement['_id'] = str(announcement['_id'])

    # 格式化发布时间 - 转换为本地时间
    if 'publish_time' in announcement and announcement['publish_time']:
        if isinstance(announcement['publish_time'], str):
            # 如果是字符串，先转换为datetime对象
            try:
                dt = datetime.fromisoformat(announcement['publish_time'].replace('Z', '+00:00'))
                announcement['publish_time'] = dt
            except:
                pass

        # 格式化显示时间
        announcement['publish_time_str'] = announcement['publish_time'].strftime('%Y-%m-%d %H:%M')
        announcement['publish_date'] = announcement['publish_time'].strftime('%Y-%m-%d')
        announcement['publish_time_only'] = announcement['publish_time'].strftime('%H:%M')
    elif 'created_at' in announcement and announcement['created_at']:
        # 如果没有发布时间，使用创建时间
        announcement['publish_time_str'] = announcement['created_at'].strftime('%Y-%m-%d %H:%M')

    # 生成内容摘要
    if 'content' in announcement:
        content = announcement['content']
        # 移除HTML标签（如果有）并生成纯文本摘要
        import re
        plain_text = re.sub(r'<[^>]+>', '', content)  # 简单移除HTML标签
        if len(plain_text) > 100:
            announcement['summary'] = plain_text[:100] + '...'
        else:
            announcement['summary'] = plain_text

    # 确保所有必要字段都存在
    announcement.setdefault('view_count', 0)
    announcement.setdefault('is_pinned', False)
    announcement.setdefault('status', 'draft')
    announcement.setdefault('category', '通知')

    return announcement


# ============ 普通用户功能 ============

@announcements_bp.route('/announcements')
@login_required
def announcement_list():
    """公告列表页面 - 所有登录用户都可以访问"""
    mongo = get_mongo()

    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 15  # 每页显示数量
    skip = (page - 1) * per_page

    # 构建查询条件：只显示已发布的公告
    query = {'status': 'published'}

    # 获取公告总数
    total = mongo.db.announcements.count_documents(query)

    # 获取公告列表，按置顶和时间排序
    announcements = list(mongo.db.announcements.find(query)
                         .sort([('is_pinned', -1), ('publish_time', -1)])
                         .skip(skip)
                         .limit(per_page))

    # 转换数据格式
    announcements = [convert_announcement_data(ann) for ann in announcements]

    # 计算总页数
    total_pages = (total + per_page - 1) // per_page

    return render_template('announcements/list.html',
                           announcements=announcements,
                           page=page,
                           total_pages=total_pages,
                           total=total)


@announcements_bp.route('/announcements/<announcement_id>')
@login_required
def announcement_detail(announcement_id):
    """公告详情页面"""
    mongo = get_mongo()

    try:
        # 验证ID格式
        if not ObjectId.is_valid(announcement_id):
            flash('无效的公告ID', 'warning')
            return redirect(url_for('announcements.announcement_list'))

        # 查找公告（必须是已发布的）
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

        # 转换数据格式
        announcement = convert_announcement_data(announcement)

        # 格式化完整时间
        if 'publish_time' in announcement and announcement['publish_time']:
            announcement['publish_time_str'] = announcement['publish_time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return render_template('announcements/detail.html',
                               announcement=announcement)

    except Exception as e:
        flash('获取公告详情时发生错误', 'danger')
        return redirect(url_for('announcements.announcement_list'))


# ============ 管理员功能 ============

@announcements_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('需要管理员权限', 'error')
        return redirect(url_for('announcements.announcement_list'))

    # 获取管理员菜单
    admin_menu = get_admin_menu()
    admin_menu = filter_menu_by_permission(admin_menu)

    mongo = current_app.mongo
    announcements = list(mongo.db.announcements.find().sort('created_at', -1))

    return render_template('announcements/admin_dashboard.html',
                           announcements=announcements,
                           admin_menu=admin_menu)  # 传递菜单数据


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

    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 20
    skip = (page - 1) * per_page

    # 获取公告总数
    total = mongo.db.announcements.count_documents(query)

    # 获取公告列表
    announcements = list(mongo.db.announcements.find(query)
                         .sort([('is_pinned', -1), ('publish_time', -1)])
                         .skip(skip)
                         .limit(per_page))

    # 转换数据格式
    announcements = [convert_announcement_data(ann) for ann in announcements]

    # 计算总页数
    total_pages = (total + per_page - 1) // per_page

    return render_template('announcements/admin_list.html',
                           announcements=announcements,
                           status=status,
                           page=page,
                           total_pages=total_pages,
                           total=total,
                           admin_menu=get_admin_menu())


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
        status = request.form.get('status', 'published')  # 添加状态选择

        # 验证数据
        errors = []
        if not title:
            errors.append('标题不能为空')
        elif len(title) > 200:
            errors.append('标题长度不能超过200个字符')

        if not content:
            errors.append('内容不能为空')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('announcements/create.html',
                                   admin_menu=get_admin_menu(),
                                   form_data=request.form)

        # 发布时间处理
        publish_time = datetime.utcnow()

        # 创建公告数据
        announcement = {
            'title': title,
            'content': content,
            'category': category,
            'priority': priority,
            'status': status,
            'author_id': str(current_user.id),
            'author_name': current_user.username,
            'publish_time': publish_time,
            'view_count': 0,
            'is_pinned': is_pinned,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # 保存到数据库
        mongo.db.announcements.insert_one(announcement)

        flash(f'公告{"发布" if status == "published" else "保存为草稿"}成功！', 'success')
        return redirect(url_for('announcements.admin_announcement_list'))

    # GET请求，显示创建表单
    return render_template('announcements/create.html',
                           admin_menu=get_admin_menu())


@announcements_bp.route('/admin/announcements/<announcement_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(announcement_id):
    """编辑公告"""
    mongo = get_mongo()

    try:
        # 验证ID格式
        if not ObjectId.is_valid(announcement_id):
            flash('无效的公告ID', 'danger')
            return redirect(url_for('announcements.admin_announcement_list'))

        announcement = mongo.db.announcements.find_one({'_id': ObjectId(announcement_id)})

        if not announcement:
            flash('公告不存在', 'danger')
            return redirect(url_for('announcements.admin_announcement_list'))

        if request.method == 'POST':
            # 获取表单数据
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', '通知')
            priority = int(request.form.get('priority', 1))
            is_pinned = request.form.get('is_pinned') == 'on'
            status = request.form.get('status', 'published')

            # 验证数据
            errors = []
            if not title:
                errors.append('标题不能为空')
            elif len(title) > 200:
                errors.append('标题长度不能超过200个字符')

            if not content:
                errors.append('内容不能为空')

            if errors:
                for error in errors:
                    flash(error, 'danger')
                announcement['_id'] = str(announcement['_id'])
                return render_template('announcements/edit.html',
                                       announcement=announcement,
                                       admin_menu=get_admin_menu(),
                                       form_data=request.form)

            # 更新公告
            update_data = {
                'title': title,
                'content': content,
                'category': category,
                'priority': priority,
                'is_pinned': is_pinned,
                'status': status,
                'updated_at': datetime.utcnow()
            }

            # 如果是草稿转为发布，设置发布时间
            if status == 'published' and announcement.get('status') == 'draft':
                update_data['publish_time'] = datetime.utcnow()

            mongo.db.announcements.update_one(
                {'_id': ObjectId(announcement_id)},
                {'$set': update_data}
            )

            flash('公告更新成功！', 'success')
            return redirect(url_for('announcements.admin_announcement_list'))

        # GET请求，显示编辑表单
        announcement['_id'] = str(announcement['_id'])
        return render_template('announcements/edit.html',
                               announcement=announcement,
                               admin_menu=get_admin_menu())

    except Exception as e:
        flash(f'编辑公告时发生错误: {str(e)}', 'danger')
        return redirect(url_for('announcements.admin_announcement_list'))


@announcements_bp.route('/admin/announcements/<announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    """删除公告"""
    mongo = get_mongo()

    try:
        # 验证ID格式
        if not ObjectId.is_valid(announcement_id):
            return jsonify({'success': False, 'message': '无效的公告ID'})

        result = mongo.db.announcements.delete_one({'_id': ObjectId(announcement_id)})

        if result.deleted_count > 0:
            return jsonify({'success': True, 'message': '公告删除成功'})
        else:
            return jsonify({'success': False, 'message': '公告不存在'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'删除公告时发生错误: {str(e)}'})


@announcements_bp.route('/admin/announcements/<announcement_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_announcement_status(announcement_id):
    """切换公告状态（发布/草稿）"""
    mongo = get_mongo()

    try:
        # 验证ID格式
        if not ObjectId.is_valid(announcement_id):
            return jsonify({'success': False, 'message': '无效的公告ID'})

        announcement = mongo.db.announcements.find_one({'_id': ObjectId(announcement_id)})

        if not announcement:
            return jsonify({'success': False, 'message': '公告不存在'})

        # 切换状态
        new_status = 'draft' if announcement.get('status') == 'published' else 'published'

        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow()
        }

        # 如果是草稿转为发布，设置发布时间
        if new_status == 'published' and not announcement.get('publish_time'):
            update_data['publish_time'] = datetime.utcnow()

        mongo.db.announcements.update_one(
            {'_id': ObjectId(announcement_id)},
            {'$set': update_data}
        )

        status_text = '已发布' if new_status == 'published' else '草稿'
        return jsonify({
            'success': True,
            'message': f'状态已切换为{status_text}',
            'new_status': new_status
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'切换状态时发生错误: {str(e)}'})


@announcements_bp.route('/admin/announcements/<announcement_id>/toggle_pin', methods=['POST'])
@login_required
@admin_required
def toggle_pin_announcement(announcement_id):
    """切换公告置顶状态"""
    mongo = get_mongo()

    try:
        # 验证ID格式
        if not ObjectId.is_valid(announcement_id):
            return jsonify({'success': False, 'message': '无效的公告ID'})

        announcement = mongo.db.announcements.find_one({'_id': ObjectId(announcement_id)})

        if not announcement:
            return jsonify({'success': False, 'message': '公告不存在'})

        # 切换置顶状态
        new_pinned = not announcement.get('is_pinned', False)

        mongo.db.announcements.update_one(
            {'_id': ObjectId(announcement_id)},
            {'$set': {
                'is_pinned': new_pinned,
                'updated_at': datetime.utcnow()
            }}
        )

        pin_text = '已置顶' if new_pinned else '已取消置顶'
        return jsonify({
            'success': True,
            'message': pin_text,
            'is_pinned': new_pinned
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'切换置顶状态时发生错误: {str(e)}'})