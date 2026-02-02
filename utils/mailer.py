import os
from flask_mail import Mail, Message
from flask import current_app, url_for
from threading import Thread

# 创建邮件扩展实例
mail = Mail()


def send_async_email(app, msg):
    """异步发送邮件"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"✅ 邮件发送成功: {msg.recipients}")
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")


def send_email(to, subject, template, **kwargs):
    """发送邮件"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            html=template,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # 异步发送邮件
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


def send_verification_email(user):
    """发送邮箱验证邮件"""
    from itsdangerous import URLSafeTimedSerializer

    # 生成验证令牌
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='email-verification')

    # 生成验证链接
    verification_url = url_for('auth.verify_email', token=token, _external=True)

    # 邮件内容
    subject = "请验证您的邮箱 - MyWeb"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>邮箱验证</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; background-color: #f8f9fa; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; 
                      color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>MyWeb 邮箱验证</h1>
            </div>
            <div class="content">
                <p>亲爱的 <strong>{user.username}</strong>，</p>
                <p>感谢您注册 MyWeb！请点击下面的按钮验证您的邮箱地址：</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">验证邮箱</a>
                </p>
                <p>如果按钮无法点击，请复制以下链接到浏览器中打开：</p>
                <p><code>{verification_url}</code></p>
                <p>此验证链接将在1小时后失效。</p>
                <p>如果您没有注册 MyWeb，请忽略此邮件。</p>
            </div>
            <div class="footer">
                <p>© 2024 MyWeb. 此邮件由系统自动发送，请勿回复。</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


def send_password_reset_email(user):
    """发送密码重置邮件（为后续功能预留）"""
    from itsdangerous import URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='password-reset')

    reset_url = url_for('auth.reset_password', token=token, _external=True)

    subject = "重置您的密码 - MyWeb"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        <h2>密码重置请求</h2>
        <p>您请求重置 MyWeb 账户的密码。</p>
        <p>请点击以下链接重置密码：</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
        <p>此链接将在1小时后失效。</p>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)