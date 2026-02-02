#!/usr/bin/env python
"""
MyWeb 数据库管理工具
用于手动管理用户数据，便于测试
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import mongo
from models.user import User
from bson import ObjectId
from datetime import datetime, timedelta


def print_menu():
    print("\n" + "=" * 50)
    print("MyWeb 数据库管理工具")
    print("=" * 50)
    print("1. 列出所有用户")
    print("2. 搜索用户")
    print("3. 删除用户")
    print("4. 清理未验证邮箱的用户")
    print("5. 验证用户邮箱（测试用）")
    print("6. 创建测试用户")
    print("7. 显示统计信息")
    print("8. 退出")
    print("=" * 50)


def list_all_users():
    """列出所有用户"""
    try:
        users = list(mongo.db.users.find().sort('created_at', -1))

        if not users:
            print("暂无用户")
            return users

        print(f"\n总用户数: {len(users)}")
        print("-" * 100)
        print(f"{'序号':<4} {'ID':<24} {'用户名':<15} {'邮箱':<25} {'验证':<6} {'激活':<6} {'创建时间':<20}")
        print("-" * 100)

        for i, user in enumerate(users, 1):
            user_id = str(user['_id'])
            username = user.get('username', 'N/A')
            email = user.get('email', 'N/A')

            # 处理长字符串
            if len(username) > 14:
                username = username[:12] + ".."
            if len(email) > 24:
                email = email[:22] + ".."

            verified = '✓' if user.get('email_verified', False) else '✗'
            active = '✓' if user.get('is_active', False) else '✗'

            created = user.get('created_at')
            if isinstance(created, datetime):
                created_str = created.strftime('%Y-%m-%d %H:%M')
            else:
                created_str = str(created)[:19] if created else 'N/A'

            print(f"{i:<4} {user_id:<24} {username:<15} {email:<25} {verified:<6} {active:<6} {created_str:<20}")

        return users
    except Exception as e:
        print(f"❌ 列出用户时出错: {e}")
        return []


def search_user():
    """搜索用户"""
    keyword = input("\n请输入搜索关键词（用户名、邮箱或ID）: ").strip()
    if not keyword:
        print("搜索关键词不能为空")
        return

    query = {}
    if '@' in keyword:
        query['email'] = {'$regex': keyword, '$options': 'i'}
    elif ObjectId.is_valid(keyword):
        try:
            query['_id'] = ObjectId(keyword)
        except:
            print("无效的用户ID格式")
            return
    else:
        query['username'] = {'$regex': keyword, '$options': 'i'}

    users = list(mongo.db.users.find(query))

    if not users:
        print("未找到匹配的用户")
        return

    print(f"\n找到 {len(users)} 个用户:")
    for i, user in enumerate(users, 1):
        print(f"\n[{i}] ID: {user['_id']}")
        print(f"    用户名: {user.get('username', 'N/A')}")
        print(f"    邮箱: {user.get('email', 'N/A')}")
        print(f"    验证状态: {'已验证' if user.get('email_verified') else '未验证'}")
        print(f"    激活状态: {'已激活' if user.get('is_active') else '未激活'}")
        print(f"    创建时间: {user.get('created_at', 'N/A')}")

    return users


def delete_user():
    """删除用户"""
    users = search_user()
    if not users:
        return

    try:
        choice = int(input("\n请选择要删除的用户编号 (0取消): "))
        if choice == 0:
            return

        if 1 <= choice <= len(users):
            user = users[choice - 1]
            confirm = input(f"\n确定要删除用户 {user.get('username')} ({user.get('email')}) 吗？(y/N): ")

            if confirm.lower() == 'y':
                result = mongo.db.users.delete_one({'_id': user['_id']})
                if result.deleted_count > 0:
                    print("✅ 用户删除成功")
                else:
                    print("❌ 删除失败")
            else:
                print("取消删除")
        else:
            print("无效的选择")
    except ValueError:
        print("请输入有效的数字")


def cleanup_unverified_users():
    """清理未验证邮箱的用户"""
    try:
        days = int(input("\n请输入清理天数 (默认7): ") or "7")
        if days <= 0:
            print("天数必须大于0")
            return

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # 先查看将要删除的用户
        users_to_delete = list(mongo.db.users.find({
            'email_verified': False,
            'created_at': {'$lt': cutoff_date}
        }))

        if not users_to_delete:
            print(f"没有超过{days}天未验证的用户")
            return

        print(f"\n找到 {len(users_to_delete)} 个超过{days}天未验证的用户:")
        for user in users_to_delete:
            print(f"  - {user.get('username')} ({user.get('email')}) - {user.get('created_at')}")

        confirm = input(f"\n确定要删除这 {len(users_to_delete)} 个用户吗？(y/N): ")
        if confirm.lower() == 'y':
            result = mongo.db.users.delete_many({
                'email_verified': False,
                'created_at': {'$lt': cutoff_date}
            })
            print(f"✅ 清理完成，删除了 {result.deleted_count} 个用户")
        else:
            print("取消清理")

    except ValueError:
        print("请输入有效的数字")


def verify_user_email():
    """验证用户邮箱（测试用）"""
    users = search_user()
    if not users:
        return

    try:
        choice = int(input("\n请选择要验证的用户编号 (0取消): "))
        if choice == 0:
            return

        if 1 <= choice <= len(users):
            user = users[choice - 1]
            confirm = input(f"\n确定要验证用户 {user.get('username')} 的邮箱吗？(y/N): ")

            if confirm.lower() == 'y':
                result = mongo.db.users.update_one(
                    {'_id': user['_id']},
                    {'$set': {
                        'email_verified': True,
                        'is_active': True,
                        'email_verification_token': '',
                        'email_verification_sent_at': None,
                        'updated_at': datetime.utcnow()
                    }}
                )
                if result.modified_count > 0:
                    print("✅ 邮箱验证成功")
                else:
                    print("❌ 验证失败")
            else:
                print("取消验证")
        else:
            print("无效的选择")
    except ValueError:
        print("请输入有效的数字")


def create_test_user():
    """创建测试用户"""
    print("\n创建测试用户")
    print("-" * 30)

    username = input("用户名: ").strip()
    email = input("邮箱: ").strip().lower()
    password = input("密码: ").strip()
    is_admin = input("是否为管理员？(y/N): ").strip().lower() == 'y'

    if not all([username, email, password]):
        print("❌ 所有字段都必须填写")
        return

    # 检查用户是否已存在
    if mongo.db.users.find_one({'email': email}):
        print("❌ 邮箱已存在")
        return

    if mongo.db.users.find_one({'username': username}):
        print("❌ 用户名已存在")
        return

    user_data = {
        'username': username,
        'email': email,
        'password': password,
        'is_active': True,
        'is_admin': is_admin,
        'email_verified': True,  # 测试用户默认已验证
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    try:
        user = User.create(mongo, user_data)
        print(f"✅ 测试用户创建成功！")
        print(f"   ID: {user.id}")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print(f"   管理员: {'是' if is_admin else '否'}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")


def show_statistics():
    """显示统计信息"""
    total_users = mongo.db.users.count_documents({})
    active_users = mongo.db.users.count_documents({'is_active': True, 'email_verified': True})
    unverified_users = mongo.db.users.count_documents({'email_verified': False})
    admin_users = mongo.db.users.count_documents({'is_admin': True})

    # 最近7天注册的用户
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = mongo.db.users.count_documents({'created_at': {'$gt': seven_days_ago}})

    print("\n📊 用户统计信息")
    print("-" * 40)
    print(f"总用户数: {total_users}")
    print(f"活跃用户: {active_users}")
    print(f"未验证用户: {unverified_users}")
    print(f"管理员用户: {admin_users}")
    print(f"最近7天注册: {recent_users}")

    # 显示用户增长趋势（按天）
    if total_users > 0:
        print("\n📈 用户增长趋势:")
        for i in range(7, 0, -1):
            day = datetime.utcnow() - timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = mongo.db.users.count_documents({
                'created_at': {'$gte': day, '$lt': next_day}
            })
            print(f"  {day.strftime('%m-%d')}: {count} 人")


def main():
    """主函数"""
    # 测试数据库连接
    try:
        mongo.db.command('ping')
        print("✅ MongoDB 连接成功")
    except Exception as e:
        print(f"❌ MongoDB 连接失败: {e}")
        return

    while True:
        print_menu()

        try:
            choice = input("\n请选择操作 (1-8): ").strip()

            if choice == '1':
                list_all_users()
            elif choice == '2':
                search_user()
            elif choice == '3':
                delete_user()
            elif choice == '4':
                cleanup_unverified_users()
            elif choice == '5':
                verify_user_email()
            elif choice == '6':
                create_test_user()
            elif choice == '7':
                show_statistics()
            elif choice == '8':
                print("\n再见！")
                break
            else:
                print("❌ 无效的选择，请输入 1-8 之间的数字")

            input("\n按回车键继续...")

        except KeyboardInterrupt:
            print("\n\n程序被中断")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


if __name__ == '__main__':
    main()