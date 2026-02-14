from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime

dynamic_bp = Blueprint('dynamic', __name__, url_prefix='/admin/dynamic')


def get_mongo():
    """获取MongoDB连接"""
    return current_app.mongo


def admin_required(f):
    """管理员权限装饰器"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限访问此页面。', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@dynamic_bp.route('/functions')
@login_required
@admin_required
def function_list():
    """动态功能列表"""
    mongo = get_mongo()

    # 获取所有功能
    functions = list(mongo.db.dynamic_functions.find().sort('menu_order', 1))

    # 转换ID
    for func in functions:
        func['_id'] = str(func['_id'])
        if 'parent_id' in func and func['parent_id']:
            func['parent_id'] = str(func['parent_id'])

    # 获取一级菜单作为父级选项
    parent_options = list(mongo.db.dynamic_functions.find(
        {'menu_level': 1},
        {'_id': 1, 'title': 1}
    ))
    for opt in parent_options:
        opt['_id'] = str(opt['_id'])

    return render_template('dynamic/function_list.html',
                           functions=functions,
                           parent_options=parent_options)


@dynamic_bp.route('/function/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_function():
    """添加新功能"""
    if request.method == 'POST':
        mongo = get_mongo()

        # 获取表单数据
        name = request.form.get('name', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        url_path = request.form.get('url_path', '').strip()
        icon = request.form.get('icon', 'fas fa-cube').strip()

        menu_level = int(request.form.get('menu_level', 1))
        parent_id = request.form.get('parent_id', '').strip()
        menu_order = int(request.form.get('menu_order', 999))
        show_in_menu = request.form.get('show_in_menu') == 'on'

        template_type = request.form.get('template_type', 'page')
        access_level = request.form.get('access_level', 'verified')

        # 验证数据
        if not name or not title or not url_path:
            flash('名称、标题和URL路径不能为空', 'danger')
            return redirect(url_for('dynamic.add_function'))

        # 检查名称是否唯一
        existing = mongo.db.dynamic_functions.find_one({'name': name})
        if existing:
            flash('功能名称已存在，请使用其他名称', 'danger')
            return redirect(url_for('dynamic.add_function'))

        # 准备数据
        function_data = {
            'name': name,
            'title': title,
            'description': description,
            'url_path': url_path,
            'icon': icon,

            'menu_level': menu_level,
            'menu_order': menu_order,
            'show_in_menu': show_in_menu,
            'is_external': False,

            'template_type': template_type,
            'content': '',

            'access_level': access_level,
            'required_roles': [],
            'required_perms': [],
            'is_public': False,

            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': current_user.email
        }

        # 处理父级ID
        if menu_level == 2 and parent_id:
            try:
                function_data['parent_id'] = ObjectId(parent_id)
            except:
                flash('父级菜单ID格式错误', 'danger')
                return redirect(url_for('dynamic.add_function'))

        # 保存到数据库
        mongo.db.dynamic_functions.insert_one(function_data)

        flash(f'功能"{title}"添加成功！', 'success')
        return redirect(url_for('dynamic.function_list'))

    return render_template('dynamic/add_function.html')


@dynamic_bp.route('/function/<function_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_function(function_id):
    """编辑功能"""
    mongo = get_mongo()

    try:
        function = mongo.db.dynamic_functions.find_one({'_id': ObjectId(function_id)})

        if not function:
            flash('功能不存在', 'danger')
            return redirect(url_for('dynamic.function_list'))

        if request.method == 'POST':
            # 获取表单数据
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            url_path = request.form.get('url_path', '').strip()
            icon = request.form.get('icon', 'fas fa-cube').strip()

            menu_level = int(request.form.get('menu_level', 1))
            parent_id = request.form.get('parent_id', '').strip()
            menu_order = int(request.form.get('menu_order', 999))
            show_in_menu = request.form.get('show_in_menu') == 'on'
            is_active = request.form.get('is_active') == 'on'

            template_type = request.form.get('template_type', 'page')
            access_level = request.form.get('access_level', 'verified')

            # 验证数据
            if not title or not url_path:
                flash('标题和URL路径不能为空', 'danger')
                return redirect(url_for('dynamic.edit_function', function_id=function_id))

            # 准备更新数据
            update_data = {
                'title': title,
                'description': description,
                'url_path': url_path,
                'icon': icon,

                'menu_level': menu_level,
                'menu_order': menu_order,
                'show_in_menu': show_in_menu,
                'is_active': is_active,

                'template_type': template_type,
                'access_level': access_level,

                'updated_at': datetime.utcnow(),
                'updated_by': current_user.email
            }

            # 处理父级ID
            if menu_level == 2 and parent_id:
                try:
                    update_data['parent_id'] = ObjectId(parent_id)
                except:
                    flash('父级菜单ID格式错误', 'danger')
                    return redirect(url_for('dynamic.edit_function', function_id=function_id))
            elif menu_level == 1:
                update_data['parent_id'] = None

            # 更新数据库
            mongo.db.dynamic_functions.update_one(
                {'_id': ObjectId(function_id)},
                {'$set': update_data}
            )

            flash('功能更新成功！', 'success')
            return redirect(url_for('dynamic.function_list'))

        # GET请求，显示编辑表单
        function['_id'] = str(function['_id'])
        if 'parent_id' in function and function['parent_id']:
            function['parent_id'] = str(function['parent_id'])

        # 获取父级选项
        parent_options = list(mongo.db.dynamic_functions.find(
            {'menu_level': 1},
            {'_id': 1, 'title': 1}
        ))
        for opt in parent_options:
            opt['_id'] = str(opt['_id'])

        return render_template('dynamic/edit_function.html',
                               function=function,
                               parent_options=parent_options)

    except:
        flash('功能ID格式错误', 'danger')
        return redirect(url_for('dynamic.function_list'))


@dynamic_bp.route('/function/<function_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_function(function_id):
    """删除功能"""
    mongo = get_mongo()

    try:
        result = mongo.db.dynamic_functions.delete_one({'_id': ObjectId(function_id)})

        if result.deleted_count > 0:
            return jsonify({'success': True, 'message': '功能删除成功'})
        else:
            return jsonify({'success': False, 'message': '功能不存在'})

    except:
        return jsonify({'success': False, 'message': '功能ID格式错误'})


@dynamic_bp.route('/function/<function_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_function(function_id):
    """切换功能状态（激活/禁用）"""
    mongo = get_mongo()

    try:
        # 获取当前状态
        function = mongo.db.dynamic_functions.find_one(
            {'_id': ObjectId(function_id)},
            {'is_active': 1, 'title': 1}
        )

        if not function:
            return jsonify({'success': False, 'message': '功能不存在'})

        # 切换状态
        new_status = not function.get('is_active', True)

        mongo.db.dynamic_functions.update_one(
            {'_id': ObjectId(function_id)},
            {'$set': {
                'is_active': new_status,
                'updated_at': datetime.utcnow(),
                'updated_by': current_user.email
            }}
        )

        status_text = '激活' if new_status else '禁用'
        return jsonify({
            'success': True,
            'message': f'功能"{function.get("title", "")}"已{status_text}',
            'is_active': new_status
        })

    except:
        return jsonify({'success': False, 'message': '操作失败'})