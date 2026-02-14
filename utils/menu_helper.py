"""
菜单辅助函数
"""

from flask_login import current_user
from config.admin_menu import get_admin_menu as get_admin_menu_config


def get_admin_menu():
    """获取管理员菜单"""
    return get_admin_menu_config(current_user)


def filter_menu_by_permission(menu_items):
    """根据权限过滤菜单"""
    if not menu_items:
        return []

    filtered = []
    for item in menu_items:
        filtered.append(item)
        if 'children' in item:
            item['children'] = filter_menu_by_permission(item['children'])
    return filtered