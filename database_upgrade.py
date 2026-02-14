#!/usr/bin/env python
"""
MyWeb 数据库升级脚本
用于添加动态功能系统和公告系统所需的集合和索引
"""

import sys
import os
from datetime import datetime
import pymongo

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def get_mongo_connection():
    """获取MongoDB连接"""
    from dotenv import load_dotenv
    load_dotenv()

    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/myweb')
    database = os.environ.get('MONGO_DB', 'myweb')

    client = pymongo.MongoClient(mongo_uri)
    db = client[database]
    return db


def create_collections_and_indexes():
    """创建新集合和索引"""
    db = get_mongo_connection()

    print("=" * 60)
    print("开始数据库升级...")
    print("=" * 60)

    # 1. 创建 dynamic_functions 集合（动态功能配置）
    if 'dynamic_functions' not in db.list_collection_names():
        print("🆕 创建 dynamic_functions 集合...")
        db.create_collection('dynamic_functions')
        print("✅ dynamic_functions 集合创建完成")

    # 创建索引
    print("📊 创建 dynamic_functions 集合索引...")
    db.dynamic_functions.create_index([('name', 1)], unique=True, name='name_unique')
    db.dynamic_functions.create_index([('menu_level', 1)], name='menu_level_idx')
    db.dynamic_functions.create_index([('is_active', 1)], name='is_active_idx')
    db.dynamic_functions.create_index([('show_in_menu', 1)], name='show_in_menu_idx')
    db.dynamic_functions.create_index([('menu_order', 1)], name='menu_order_idx')
    db.dynamic_functions.create_index([('created_at', -1)], name='created_at_idx')
    print("✅ dynamic_functions 索引创建完成")

    # 2. 创建 announcements 集合（公告系统）
    if 'announcements' not in db.list_collection_names():
        print("🆕 创建 announcements 集合...")
        db.create_collection('announcements')
        print("✅ announcements 集合创建完成")

    # 创建索引
    print("📊 创建 announcements 集合索引...")
    db.announcements.create_index([('status', 1)], name='status_idx')
    db.announcements.create_index([('is_pinned', -1), ('priority', -1), ('publish_time', -1)],
                                  name='display_order_idx')
    db.announcements.create_index([('category', 1)], name='category_idx')
    db.announcements.create_index([('author_id', 1)], name='author_idx')
    db.announcements.create_index([('created_at', -1)], name='ann_created_at_idx')

    # 创建文本搜索索引
    try:
        db.announcements.create_index([
            ('title', 'text'),
            ('content', 'text')
        ], name='text_search_idx')
        print("✅ 全文搜索索引创建完成")
    except Exception as e:
        print(f"⚠️  全文搜索索引创建失败（可能需要特殊配置）: {e}")

    print("✅ announcements 索引创建完成")

    # 3. 可选：创建 function_access_logs 集合（功能访问日志）
    if 'function_access_logs' not in db.list_collection_names():
        print("🆕 创建 function_access_logs 集合...")
        db.create_collection('function_access_logs')
        db.function_access_logs.create_index([('function_id', 1)], name='function_id_idx')
        db.function_access_logs.create_index([('user_id', 1)], name='user_id_idx')
        db.function_access_logs.create_index([('access_time', -1)], name='access_time_idx')
        print("✅ function_access_logs 集合创建完成")

    print("=" * 60)
    print("数据库升级完成！")
    print("=" * 60)

    return db


def add_default_dynamic_functions(db):
    """添加默认的动态功能配置"""
    print("\n🔄 添加默认动态功能配置...")

    default_functions = [
        {
            'name': 'home',
            'title': '首页',
            'description': '系统首页',
            'url_path': '/',
            'icon': 'fas fa-home',
            'menu_level': 1,
            'parent_id': None,
            'menu_order': 0,
            'show_in_menu': True,
            'is_external': False,
            'template_type': 'page',
            'content': '',
            'access_level': 'public',
            'required_roles': [],
            'required_perms': [],
            'is_public': True,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': 'system'
        },
        {
            'name': 'dashboard',
            'title': '控制台',
            'description': '用户控制台',
            'url_path': '/dashboard',
            'icon': 'fas fa-tachometer-alt',
            'menu_level': 1,
            'parent_id': None,
            'menu_order': 10,
            'show_in_menu': True,
            'is_external': False,
            'template_type': 'page',
            'content': '',
            'access_level': 'verified',
            'required_roles': [],
            'required_perms': [],
            'is_public': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': 'system'
        },
        {
            'name': 'profile',
            'title': '个人中心',
            'description': '个人资料管理',
            'url_path': '/profile',
            'icon': 'fas fa-user',
            'menu_level': 1,
            'parent_id': None,
            'menu_order': 20,
            'show_in_menu': True,
            'is_external': False,
            'template_type': 'page',
            'content': '',
            'access_level': 'verified',
            'required_roles': [],
            'required_perms': [],
            'is_public': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': 'system'
        },
        {
            'name': 'announcements',
            'title': '公告中心',
            'description': '系统公告发布和查看',
            'url_path': '/announcements',
            'icon': 'fas fa-bullhorn',
            'menu_level': 1,
            'parent_id': None,
            'menu_order': 30,
            'show_in_menu': True,
            'is_external': False,
            'template_type': 'list',
            'content': '',
            'access_level': 'verified',
            'required_roles': [],
            'required_perms': [],
            'is_public': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': 'system'
        }
    ]

    for func in default_functions:
        # 检查是否已存在
        existing = db.dynamic_functions.find_one({'name': func['name']})
        if not existing:
            db.dynamic_functions.insert_one(func)
            print(f"✅ 添加功能: {func['title']}")
        else:
            print(f"⚠️  功能已存在: {func['title']}")

    print("✅ 默认动态功能配置添加完成")


def add_sample_announcements(db):
    """添加示例公告数据"""
    print("\n📝 添加示例公告数据...")

    sample_announcements = [
        {
            'title': '欢迎使用MyWeb系统',
            'content': '<h3>欢迎！</h3><p>欢迎使用全新的MyWeb系统。这是一个基于Flask和MongoDB构建的现代Web平台。</p><p>系统特性：</p><ul><li>用户认证和授权</li><li>邮箱验证系统</li><li>管理员后台</li><li>动态功能扩展</li></ul>',
            'author_id': 'system',
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
            'author_id': 'system',
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
            'author_id': 'system',
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
    db.announcements.delete_many({'author_id': 'system'})

    # 插入新数据
    db.announcements.insert_many(sample_announcements)
    print(f"✅ 添加了 {len(sample_announcements)} 条示例公告")


def main():
    """主函数"""
    try:
        print("🚀 MyWeb 数据库升级工具")
        print("=" * 60)

        # 检查MongoDB连接
        db = get_mongo_connection()
        db.command('ping')
        print("✅ MongoDB 连接成功")

        # 创建集合和索引
        db = create_collections_and_indexes()

        # 添加默认动态功能
        add_default_dynamic_functions(db)

        # 添加示例公告
        add_sample_announcements(db)

        print("\n" + "=" * 60)
        print("🎉 数据库升级完成！")
        print("=" * 60)
        print("新功能已启用：")
        print("1. 动态功能系统（dynamic_functions）")
        print("2. 公告管理系统（announcements）")
        print("3. 访问日志系统（function_access_logs）")
        print("\n现在可以启动应用测试新功能了！")

    except Exception as e:
        print(f"❌ 数据库升级失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()