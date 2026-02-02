# create_test_user.py - 创建测试用户用于验证
from app import mongo
from datetime import datetime
import hashlib


def create_test_user():
    """创建一个测试用的未验证用户"""
    test_email = "test_unverified_" + datetime.now().strftime("%H%M%S") + "@test.com"

    user_data = {
        'username': f"test_{datetime.now().strftime('%H%M%S')}",
        'email': test_email,
        'password': hashlib.sha256("test123".encode()).hexdigest(),  # 简单哈希
        'is_active': False,
        'is_admin': False,
        'email_verified': False,
        'created_at': datetime.utcnow()
    }

    result = mongo.db.users.insert_one(user_data)

    if result.inserted_id:
        print(f"✅ 测试用户创建成功!")
        print(f"   邮箱: {test_email}")
        print(f"   密码: test123")
        print(f"   状态: 未验证，未激活")
        return test_email
    else:
        print("❌ 创建失败")
        return None


if __name__ == '__main__':
    email = create_test_user()
    if email:
        print(f"\n🎯 测试步骤:")
        print(f"1. 访问 http://localhost:5000/auth/login")
        print(f"2. 使用邮箱: {email}")
        print(f"3. 密码: test123")
        print(f"4. 应该看到'请先验证邮箱'的提示")