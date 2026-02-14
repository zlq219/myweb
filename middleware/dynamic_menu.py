# middleware/dynamic_menu.py
from flask import current_app, g
from bson import ObjectId


def get_dynamic_menu(user):
    """获取动态菜单数据"""
    mongo = current_app.mongo
    menu_data = {
        'dynamic_functions': [],
        'primary_menu': [],
        'menu_groups': []
    }

    if not hasattr(user, 'is_authenticated') or not user.is_authenticated:
        return menu_data

    # 获取所有激活的菜单项
    query = {
        'is_active': True,
        'show_in_menu': True
    }

    # 根据用户权限筛选
    if not user.is_admin:
        query['access_level'] = {'$in': ['all', 'public', 'verified']}

    functions = list(mongo.db.dynamic_functions.find(query)
                     .sort('menu_order', 1))

    # 转换数据格式
    for func in functions:
        func['_id'] = str(func['_id'])

        # 检查权限
        if not check_function_access(func, user):
            continue

        menu_data['dynamic_functions'].append(func)

        # 按层级组织
        if func['menu_level'] == 1:
            menu_data['primary_menu'].append(func)
        elif func['menu_level'] == 2:
            # 查找父菜单
            for primary in menu_data['primary_menu']:
                if primary['_id'] == func.get('parent_id'):
                    if 'children' not in primary:
                        primary['children'] = []
                    primary['children'].append(func)
                    primary['has_children'] = True

    # 构建菜单组（有二级菜单的一级菜单）
    for item in menu_data['primary_menu']:
        if item.get('has_children'):
            menu_data['menu_groups'].append({
                'id': item['_id'],
                'title': item['title'],
                'icon': item.get('icon', ''),
                'items': item.get('children', [])
            })

    return menu_data


def check_function_access(func, user):
    """检查用户是否有权限访问功能"""
    access_level = func.get('access_level', 'auth')

    if access_level == 'public':
        return True

    if not user.is_authenticated:
        return False

    if access_level == 'all':
        return True

    if access_level == 'verified' and user.email_verified:
        return True

    if access_level == 'admin' and user.is_admin:
        return True

    if access_level == 'custom':
        # 检查自定义权限
        return check_custom_permission(func, user)

    return False


# 上下文处理器
@app.context_processor
def inject_dynamic_menu():
    """向所有模板注入动态菜单数据"""
    if current_user.is_authenticated:
        menu_data = get_dynamic_menu(current_user)
        return menu_data
    return {}