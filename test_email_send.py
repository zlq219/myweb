# test_email_send.py
from app import app
from utils.mailer import send_test_email

print("📧 测试邮件发送功能")
print("=" * 60)

with app.app_context():
    test_email = input("请输入测试邮箱地址: ").strip()

    if not test_email:
        test_email = "test@example.com"  # 默认测试邮箱

    print(f"\n尝试发送测试邮件到: {test_email}")

    try:
        result = send_test_email(test_email)
        if result:
            print("✅ 测试邮件发送成功！")
            print("请检查邮箱收件箱（包括垃圾邮件）")
        else:
            print("❌ 测试邮件发送失败")
    except Exception as e:
        print(f"❌ 发送失败，错误信息: {e}")
        print("\n💡 常见问题排查:")
        print("1. 检查 config.py 中的邮箱配置")
        print("2. 确保使用了应用专用密码")
        print("3. 检查网络连接和SMTP端口")

print("=" * 60)