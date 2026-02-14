"""
配置文件模块
"""

from .config import Config
from .admin_menu import get_admin_menu, ADMIN_MENU_ITEMS

__all__ = ['Config', 'get_admin_menu', 'ADMIN_MENU_ITEMS']