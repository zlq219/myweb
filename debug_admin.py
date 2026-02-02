#!/usr/bin/env python
"""
诊断管理员访问问题
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, mongo

print("🔍 诊断脚本 - 管理员访问问题")
print("=" * 60)

# 1. 检查User模型
try:
    from models.user import User

    print("✅ User模型导入成功")

    # 检查方法是否存在
    methods = ['get_by_id', 'get_by_email', 'get_by_username']
    for method in methods:
        if hasattr(User, method):
            print(f"✅ User.{method} 方法存在")
        else:
            print(f"❌ User.{method} 方法缺失")
except Exception as e:
    print(f"❌ User模型导入失败: {e}")

# 2. 检查管理员用户
print("\n👑 管理员用户检查:")
admins = list(mongo.db.users.find({'is_admin': True}))
print(f"找到 {len(admins)} 个管理员")

for admin in admins:
    print(f"\n用户: {admin.get('email')}")
    print(f"  is_admin: {admin.get('is_admin')}")
    print(f"  email_verified: {admin.get('email_verified')}")
    print(f"  is_active: {admin.get('is_active')}")

# 3. 检查路由
print("\n🌐 路由检查:")
for rule in app.url_map.iter_rules():
    if 'admin' in rule.rule:
        print(f"  - {rule.rule} -> {rule.endpoint}")

print("\n💡 建议:")
if len(admins) == 0:
    print("1. 需要先设置一个管理员用户")
    print("2. 运行: python make_admin.py")
else:
    print("1. 已有管理员用户，可以尝试登录")
    print("2. 访问: http://localhost:5000/admin/dashboard")

print("\n" + "=" * 60)
