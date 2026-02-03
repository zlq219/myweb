from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_login import LoginManager
from utils.mailer import mail
from config import Config
import os

# 1. 首先创建应用实例
app = Flask(__name__)
app.config.from_object(Config)

# 2. 初始化LoginManager并绑定到app
login_manager = LoginManager()
login_manager.init_app(app)  # 关键：必须调用init_app
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'info'

# 3. 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 4. 初始化其他扩展
mongo = PyMongo(app)
app.mongo = mongo

# 初始化邮件扩展
mail.init_app(app)

# 5. 用户加载器（必须放在login_manager初始化之后）
from models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(mongo, user_id)


# 6. 注册蓝图
from routes.auth import auth_bp
from routes.user import user_bp
from routes.main import main_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')  # 确保有url_prefix
app.register_blueprint(user_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)

# 7. 注册错误处理器
from routes.main import page_not_found, internal_server_error

app.errorhandler(404)(page_not_found)
app.errorhandler(500)(internal_server_error)


# 8. 开发用的强制退出路由（可选，调试后删除）
@app.route('/dev/force-logout')
def force_logout():
    from flask import session, redirect, url_for
    from flask_login import logout_user

    logout_user()
    session.clear()

    response = redirect(url_for('auth.login'))
    response.set_cookie('session', '', expires=0)
    response.set_cookie('remember_token', '', expires=0)

    return response


if __name__ == '__main__':
    # 测试数据库连接
    try:
        mongo.db.command('ping')
        print("✅ MongoDB 连接成功!")
    except Exception as e:
        print(f"❌ MongoDB 连接失败: {e}")
        print("请确保 MongoDB 服务正在运行")

    app.run(debug=True, host='0.0.0.0', port=5000)