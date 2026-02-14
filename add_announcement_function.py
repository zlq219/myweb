#!/usr/bin/env python
"""
通过动态功能系统添加公告中心菜单
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from datetime import datetime


def add_announcement_to_dynamic_functions():
    """向dynamic_functions集合添加公告中心配置"""
    with app.app_context():
        mongo = app.mongo

        # 检查是否已存在
        existing = mongo.db.dynamic_functions.find_one({'name': 'announcements'})

        if existing:
            print("公告中心功能已存在，跳过添加")
            return

        # 创建动态功能配置
        function_config = {
            'name': 'announcements',
            'title': '公告中心',
            'description': '系统公告发布和查看平台',
            'url_path': '/announcements',
            'icon': 'fas fa-bullhorn',

            # 菜单配置
            'menu_level': 1,
            'parent_id': None,
            'menu_order': 30,
            'show_in_menu': True,
            'is_external': False,

            # 页面配置
            'template_type': 'list',
            'content': '',  # 动态生成

            # 权限配置
            'access_level': 'verified',
            'required_roles': [],
            'required_perms': [],
            'is_public': False,

            # 状态管理
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': 'system'
        }

        # 插入数据库
        result = mongo.db.dynamic_functions.insert_one(function_config)

        print(f"✅ 公告中心功能已添加到动态菜单系统")
        print(f"功能ID: {result.inserted_id}")
        print(f"访问路径: {function_config['url_path']}")
        print(f"菜单位置: 一级菜单，排序 {function_config['menu_order']}")


if __name__ == '__main__':
    add_announcement_to_dynamic_functions()