from flask import Blueprint, render_template, request, jsonify, flash, current_app
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ============ 辅助函数 ============
def get_mongo():
    return current_app.mongo


def get_user_model():
    from models.user import User
    return User


def convert_mongo_doc(doc):
    """将MongoDB文档转换为可JSON序列化的字典"""
    if not doc:
        return None

    result = {}
    for key, value in doc.items():
        # 转换ObjectId为字符串
        if isinstance(value, ObjectId):
            result[key] = str(value)
        # 转换datetime为ISO格式字符串
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        # 转换timedelta为秒数
        elif isinstance(value, timedelta):
            result[key] = value.total_seconds()
        # 处理嵌套字典
        elif isinstance(value, dict):
            result[key] = convert_mongo_doc(value)
        # 处理列表
        elif isinstance(value, list):
            result[key] = [
                convert_mongo_doc(item) if isinstance(item, dict) else
                (str(item) if isinstance(item, ObjectId) else
                 (item.isoformat() if isinstance(item, datetime) else item))
                for item in value
            ]
        # 其他类型直接保留
        else:
            result[key] = value
    return result


# ============ 权限装饰器 ============
def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限访问此页面。', 'danger')
            return jsonify({'success': False, 'message': '权限不足'}), 403
        return f(*args, **kwargs)

    return decorated_function


# ============ 路由定义 ============
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """管理员控制台"""
    mongo = get_mongo()

    # 获取统计信息
    total_users = mongo.db.users.count_documents({})
    active_users = mongo.db.users.count_documents({'is_active': True, 'email_verified': True})
    unverified_users = mongo.db.users.count_documents({'email_verified': False})
    admin_users = mongo.db.users.count_documents({'is_admin': True})

    # 获取最近注册的用户（转换MongoDB文档）
    recent_users_cursor = mongo.db.users.find().sort('created_at', -1).limit(10)
    recent_users = [convert_mongo_doc(user) for user in recent_users_cursor]

    # 获取未验证邮箱的用户（超过3天）
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    old_unverified_cursor = mongo.db.users.find({
        'email_verified': False,
        'created_at': {'$lt': three_days_ago}
    }).limit(20)
    old_unverified = [convert_mongo_doc(user) for user in old_unverified_cursor]

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           active_users=active_users,
                           unverified_users=unverified_users,
                           admin_users=admin_users,
                           recent_users=recent_users,
                           old_unverified=old_unverified)


@admin_bp.route('/users/delete', methods=['POST'])
@login_required
@admin_required
def delete_user():
    """删除用户（管理员操作）"""
    data = request.get_json()
    user_id = data.get('user_id')
    email = data.get('email')

    if not user_id and not email:
        return jsonify({'success': False, 'message': '需要提供用户ID或邮箱'}), 400

    mongo = get_mongo()

    # 构建查询条件
    query = {}
    if user_id:
        try:
            user_id_obj = ObjectId(user_id)
            query['_id'] = user_id_obj
        except:
            return jsonify({'success': False, 'message': '无效的用户ID'}), 400

        # 修复：正确比较用户ID，防止删除自己
        if hasattr(current_user, 'id'):
            # 获取当前用户的MongoDB _id
            current_user_doc = mongo.db.users.find_one({'email': current_user.email})
            if current_user_doc and current_user_doc['_id'] == user_id_obj:
                return jsonify({'success': False, 'message': '不能删除自己的账户'}), 400

    elif email:
        # 防止删除自己（通过邮箱）
        if email == current_user.email:
            return jsonify({'success': False, 'message': '不能删除自己的账户'}), 400
        query['email'] = email

    # 执行删除
    result = mongo.db.users.delete_one(query)

    if result.deleted_count > 0:
        # 记录删除日志
        print(f"管理员 {current_user.email} 删除了用户: {query}")
        return jsonify({'success': True, 'message': '用户删除成功'})
    else:
        return jsonify({'success': False, 'message': '用户不存在或删除失败'}), 404


@admin_bp.route('/users/cleanup-unverified', methods=['POST'])
@login_required
@admin_required
def cleanup_unverified_users():
    """清理超过指定天数未验证的用户"""
    data = request.get_json()
    days = data.get('days', 7)

    try:
        days = int(days)
        if days < 1:
            return jsonify({'success': False, 'message': '天数必须大于0'}), 400
    except:
        return jsonify({'success': False, 'message': '无效的天数'}), 400

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    mongo = get_mongo()
    result = mongo.db.users.delete_many({
        'email_verified': False,
        'created_at': {'$lt': cutoff_date}
    })

    return jsonify({
        'success': True,
        'message': f'清理了 {result.deleted_count} 个超过{days}天未验证的用户',
        'deleted_count': result.deleted_count
    })


@admin_bp.route('/users/search')
@login_required
@admin_required
def search_users():
    """搜索用户"""
    query_text = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    mongo = get_mongo()
    search_query = {}

    if query_text:
        # 支持按邮箱、用户名或ID搜索
        if '@' in query_text:
            search_query['email'] = {'$regex': query_text, '$options': 'i'}
        elif ObjectId.is_valid(query_text):
            try:
                search_query['_id'] = ObjectId(query_text)
            except:
                pass
        else:
            search_query['username'] = {'$regex': query_text, '$options': 'i'}

    total = mongo.db.users.count_documents(search_query)
    skip = (page - 1) * per_page

    # 获取用户数据并转换
    users_cursor = mongo.db.users.find(search_query).skip(skip).limit(per_page)
    users = []

    for user in users_cursor:
        # 使用转换函数处理MongoDB文档
        users.append(convert_mongo_doc(user))

    return jsonify({
        'success': True,
        'users': users,
        'total': total,
        'page': page,
        'total_pages': (total + per_page - 1) // per_page
    })


# ============ 测试路由（开发用，生产环境应删除）============
@admin_bp.route('/test/delete-manual/<user_email>')
@login_required
@admin_required
def test_delete_manual(user_email):
    """手动测试删除功能（仅用于调试）"""
    mongo = get_mongo()

    # 查找用户
    user = mongo.db.users.find_one({'email': user_email})
    if not user:
        return f"❌ 用户 {user_email} 不存在"

    # 防止删除自己
    if user_email == current_user.email:
        return "❌ 不能删除自己的账户"

    # 执行删除
    result = mongo.db.users.delete_one({'email': user_email})

    if result.deleted_count > 0:
        return f"✅ 用户 {user_email} 删除成功"
    else:
        return f"❌ 用户 {user_email} 删除失败"