# check_email_verification.py
from app import mongo
from datetime import datetime

print("📧 邮箱验证功能诊断")
print("=" * 60)

# 检查用户验证状态
users = list(mongo.db.users.find({}, {'email': 1, 'email_verified': 1, 'is_active': 1}))
print(f"📊 用户总数: {len(users)}")

verified = [u for u in users if u.get('email_verified')]
unverified = [u for u in users if not u.get('email_verified')]

print(f"✅ 已验证用户: {len(verified)}")
print(f"❌ 未验证用户: {len(unverified)}")

if unverified:
    print("\n📋 未验证用户列表:")
    for i, user in enumerate(unverified, 1):
        print(f"  {i}. {user.get('email')} - 活跃: {user.get('is_active', '未知')}")

print("\n🔍 检查关键配置:")
try:
    from config import Config
    print(f"  MAIL_SERVER: {Config.MAIL_SERVER}")
    print(f"  MAIL_PORT: {Config.MAIL_PORT}")
    print(f"  MAIL_USE_TLS: {Config.MAIL_USE_TLS}")
    print(f"  EMAIL_VERIFICATION_EXPIRE: {Config.EMAIL_VERIFICATION_EXPIRE}秒")
except Exception as e:
    print(f"  配置检查失败: {e}")

print("=" * 60)