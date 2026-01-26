from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_login import LoginManager
from config import Config
import os

# 创建应用实例
app = Flask(__name__)
app.config.from_object(Config)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化MongoDB
mongo = PyMongo(app)
app.mongo = mongo  # 将mongo附加到app实例上

# 初始化Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'info'

# 用户加载器 - 在扩展初始化后定义
from models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(mongo, user_id)


# 注册蓝图 - 在扩展初始化后导入
from routes.auth import auth_bp
from routes.user import user_bp
from routes.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(main_bp)

# 注册错误处理器
from routes.main import page_not_found, internal_server_error

app.errorhandler(404)(page_not_found)
app.errorhandler(500)(internal_server_error)


# 主页路由
@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    # 测试数据库连接
    try:
        mongo.db.command('ping')
        print("✅ MongoDB 连接成功!")
    except Exception as e:
        print(f"❌ MongoDB 连接失败: {e}")
        print("请确保 MongoDB 服务正在运行")

    app.run(debug=True, host='0.0.0.0', port=5000)