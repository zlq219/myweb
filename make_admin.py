#!/usr/bin/env python
"""
MyWeb 管理员设置工具 - 在PyCharm中运行
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import mongo
from datetime import datetime

print("=" * 60)
print("MyWeb - 管理员权限设置工具")
print("=" * 60)

# 1. 检查数据库连接
try:
    mongo.db.command('ping')
    print("✅ MongoDB连接正常")
except Exception as e:
    print(f"❌ MongoDB连接失败: {e}")
    sys.exit(1)

# 2. 获取所有用户
users = list(mongo.db.users.find().sort('created_at', -1))

if not users:
    print("❌ 数据库中没有用户")
    sys.exit(1)

# 3. 显示用户列表
print(f"\n📋 找到 {len(users)} 个用户:")
print("-" * 70)

for i, user in enumerate(users, 1):
    username = user.get('username', '未知')
    email = user.get('email', '未知')
    is_admin = "👑是" if user.get('is_admin') else "否"
    verified = "✓已验证" if user.get('email_verified') else "✗未验证"

    print(f"{i:2d}. {username:15} {email:25} 管理员:{is_admin:3} 邮箱:{verified}")

print("-" * 70)

# 4. 让用户选择
try:
    choice_input = input("\n请输入要设为管理员的用户编号 (直接回车选择第1个): ").strip()

    if choice_input == "":
        choice = 1
    else:
        choice = int(choice_input)

    if 1 <= choice <= len(users):
        user = users[choice - 1]
        user_email = user['email']
        username = user.get('username', '未知用户')

        print(f"\n📝 你选择的用户:")
        print(f"   用户名: {username}")
        print(f"   邮箱: {user_email}")
        print(f"   当前是管理员: {'是' if user.get('is_admin') else '否'}")
        print(f"   邮箱已验证: {'是' if user.get('email_verified') else '否'}")

        confirm = input(f"\n⚠️  确定要将 [{username}] 设为管理员吗？(y/N): ").strip().lower()

        if confirm == 'y' or confirm == 'yes':
            # 5. 更新用户为管理员
            result = mongo.db.users.update_one(
                {'email': user_email},
                {'$set': {
                    'is_admin': True,
                    'user_is_admin': True,
                    'email_verified': True,
                    'is_active': True,
                    'updated_at': datetime.utcnow()
                }}
            )

            if result.modified_count > 0:
                print(f"\n" + "=" * 50)
                print(f"✅ 成功！用户 [{username}] 现在是管理员了")
                print("=" * 50)
                print(f"\n🎯 下一步操作:")
                print(f"1. 确保Flask应用正在运行")
                print(f"2. 访问: http://localhost:5000/login")
                print(f"3. 使用邮箱 [{user_email}] 登录")
                print(f"4. 访问管理面板: http://localhost:5000/admin/dashboard")
                print(f"\n💡 提示: 如果管理页面打不开，请检查 app.py 中是否注册了 admin_bp")
            else:
                print(f"\n⚠️  用户 [{username}] 可能已经是管理员，或者更新失败")
        else:
            print("❌ 操作已取消")
    else:
        print(f"❌ 无效的选择编号，请输入 1-{len(users)} 之间的数字")

except ValueError:
    print("❌ 请输入有效的数字")
except KeyboardInterrupt:
    print("\n\n⏹️  操作被用户中断")
except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback

    traceback.print_exc()

input("\n按回车键退出...")