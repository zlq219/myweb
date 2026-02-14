#!/usr/bin/env python
"""
公告系统数据库初始化脚本
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from datetime import datetime


def init_announcements_collection():
    """初始化announcements集合索引"""
    with app.app_context():
        mongo = app.mongo

        # 创建索引
        mongo.db.announcements.create_index([('status', 1)])
        mongo.db.announcements.create_index([('is_pinned', -1), ('priority', -1), ('publish_time', -1)])
        mongo.db.announcements.create_index([('category', 1)])
        mongo.db.announcements.create_index([('author_id', 1)])
        mongo.db.announcements.create_index([('created_at', -1)])

        # 创建全文搜索索引（可选）
        try:
            mongo.db.announcements.create_index([
                ('title', 'text'),
                ('content', 'text')
            ])
        except:
            print("注意：全文搜索索引可能需要特殊的MongoDB配置")

        print("✅ announcements集合索引创建完成")

        # 添加示例数据（开发环境）
        if app.debug:
            add_sample_announcements()
            print("✅ 示例公告数据已添加")


def add_sample_announcements():
    """添加示例公告"""
    mongo = app.mongo

    sample_announcements = [
        {
            'title': '欢迎使用MyWeb系统',
            'content': '<h3>欢迎！</h3><p>欢迎使用全新的MyWeb系统。这是一个基于Flask和MongoDB构建的现代Web平台。</p><p>系统特性：</p><ul><li>用户认证和授权</li><li>邮箱验证系统</li><li>管理员后台</li><li>动态功能扩展</li></ul>',
            'author_id': 'admin',
            'author_name': '系统管理员',
            'category': '通知',
            'priority': 1,
            'status': 'published',
            'publish_time': datetime.utcnow(),
            'view_count': 150,
            'is_pinned': True,
            'tags': ['欢迎', '系统介绍'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'title': '系统维护通知',
            'content': '<p>为了提升系统性能，我们将于<strong>本周末（2月8日）凌晨2:00-4:00</strong>进行系统维护。</p><p>维护期间系统将暂时无法访问，请提前做好安排。</p>',
            'author_id': 'admin',
            'author_name': '系统管理员',
            'category': '维护',
            'priority': 2,
            'status': 'published',
            'publish_time': datetime.utcnow(),
            'view_count': 89,
            'is_pinned': False,
            'tags': ['维护', '通知'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'title': '新增公告中心功能',
            'content': '<p>我们很高兴地宣布，公告中心功能现已上线！</p><p>管理员可以通过公告中心发布系统通知和更新，用户可以在此查看所有公告。</p>',
            'author_id': 'admin',
            'author_name': '系统管理员',
            'category': '更新',
            'priority': 1,
            'status': 'published',
            'publish_time': datetime.utcnow(),
            'view_count': 45,
            'is_pinned': True,
            'tags': ['新功能', '公告'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]

    # 清除现有示例数据（可选）
    mongo.db.announcements.delete_many({'author_id': 'admin'})

    # 插入新数据
    mongo.db.announcements.insert_many(sample_announcements)


if __name__ == '__main__':
    init_announcements_collection()