from flask import Flask
from extensions import mongo, login_manager
from config import Config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 初始化扩展
    mongo.init_app(app)
    login_manager.init_app(app)

    # 配置LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'

    # 注册用户加载器
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(mongo, user_id)

    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(main_bp)

    # 注册错误处理器
    from .routes.main import not_found_error, internal_error
    app.errorhandler(404)(not_found_error)
    app.errorhandler(500)(internal_error)

    # 注册主页路由
    from .routes.main import index
    app.add_url_rule('/', 'index', index)

    return app