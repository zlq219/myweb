import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 原有配置...
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/myweb'

    # Flask-Login配置...
    SESSION_PROTECTION = 'strong'

    # ============ 强制会话配置 ============
    # 核心：使会话仅在浏览器打开时有效
    SESSION_PERMANENT = False  # 不创建永久会话

    # 设置较短的活动生命周期（5分钟不活动就过期）
    PERMANENT_SESSION_LIFETIME = 300  # 5分钟，单位：秒

    # 会话Cookie设置 - 确保关闭浏览器即失效
    SESSION_COOKIE_NAME = 'flask_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 开发环境False，生产必须True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # 关键：使Cookie成为“会话Cookie”（不设过期时间，浏览器关闭即失效）
    SESSION_COOKIE_EXPIRES = None

    # Flask-Login 配置
    REMEMBER_COOKIE_DURATION = 300  # 5分钟，即使勾选“记住我”
    REMEMBER_COOKIE_NAME = 'remember_token'
    REMEMBER_COOKIE_SECURE = False
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True  # 每次请求刷新

    # 关键：禁用所有长期Cookie
    SESSION_REFRESH_EACH_REQUEST = True  # 每次请求刷新会话
    # ===================================
    # 上传文件配置...
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # 分页配置...
    USERS_PER_PAGE = 20

    # 新增邮箱配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # 邮箱验证配置
    EMAIL_VERIFICATION_EXPIRE = 3600  # 验证链接有效期（秒），1小时