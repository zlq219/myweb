from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager, current_user
from utils.mailer import mail
from config import Config
import os
import logging
from datetime import datetime, timedelta
from bson import ObjectId
from config.config import Config
from flask import send_from_directory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. 创建应用实例
app = Flask(__name__)
app.config.from_object(Config)

# 2. 初始化LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'info'

# 3. 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 4. 初始化扩展
mongo = PyMongo(app)
app.mongo = mongo
mail.init_app(app)


def get_dynamic_menu():
    """获取动态菜单数据"""
    try:
        if not hasattr(app, 'mongo'):
            return {'primary': [], 'secondary': {}}

        # 获取所有激活且显示在菜单中的功能
        functions = list(app.mongo.db.dynamic_functions.find({
            'is_active': True,
            'show_in_menu': True
        }).sort('menu_order', 1))

        # 组织菜单结构
        menu_structure = {
            'primary': [],  # 一级菜单
            'secondary': {}  # 二级菜单分组
        }

        for func in functions:
            func['_id'] = str(func['_id'])

            if func['menu_level'] == 1:  # 一级菜单
                # 检查权限
                if check_function_access(func, current_user):
                    menu_structure['primary'].append(func)
            elif func['menu_level'] == 2:  # 二级菜单
                parent_id = func.get('parent_id')
                if parent_id:
                    parent_id_str = str(parent_id) if isinstance(parent_id, ObjectId) else parent_id
                    if parent_id_str not in menu_structure['secondary']:
                        menu_structure['secondary'][parent_id_str] = []

                    # 检查权限
                    if check_function_access(func, current_user):
                        menu_structure['secondary'][parent_id_str].append(func)

        return menu_structure

    except Exception as e:
        logger.error(f"获取动态菜单失败: {e}")
        return {'primary': [], 'secondary': {}}


def check_function_access(function_config, user):
    """检查用户是否有权限访问功能"""
    if not function_config.get('is_active', True):
        return False

    access_level = function_config.get('access_level', 'verified')

    # 公开访问
    if access_level == 'public' or function_config.get('is_public', False):
        return True

    # 需要登录
    if not user or not user.is_authenticated:
        return False

    # 所有登录用户
    if access_level == 'all_users':
        return True

    # 需要验证邮箱
    if access_level == 'verified':
        return hasattr(user, 'email_verified') and user.email_verified

    # 仅管理员
    if access_level == 'admin':
        return hasattr(user, 'is_admin') and user.is_admin

    # 自定义角色/权限（后续扩展）
    if access_level == 'custom':
        required_roles = function_config.get('required_roles', [])
        required_perms = function_config.get('required_perms', [])

        if not required_roles and not required_perms:
            return True

        # 这里可以扩展角色和权限检查逻辑
        return True

    return False


@app.context_processor
def inject_global_variables():
    """向所有模板注入全局变量"""
    return {
        'current_year': datetime.now().year,
        'dynamic_menu': get_dynamic_menu(),
        'app_name': 'MyWeb'
    }


def cleanup_unverified_users_on_startup():
    """应用启动时清理超过7天未验证的用户"""
    try:
        if not hasattr(app, 'mongo') or app.mongo is None:
            logger.warning("MongoDB连接未就绪，跳过启动清理")
            return 0

        mongo = app.mongo

        # 计算7天前的日期
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # 查询要删除的用户（未验证、非管理员、超过7天）
        query = {
            'email_verified': False,
            'created_at': {'$lt': seven_days_ago},
            'is_admin': False
        }

        # 先获取符合条件的用户数量
        count_to_delete = mongo.db.users.count_documents(query)

        if count_to_delete == 0:
            logger.info("启动清理：没有需要清理的未验证用户")
            return 0

        # 执行删除
        result = mongo.db.users.delete_many(query)

        # 记录结果
        deleted_count = result.deleted_count

        if deleted_count > 0:
            logger.info(f"✅ 启动清理：成功删除了 {deleted_count} 个超过7天未验证的用户")

            # 写入日志文件
            try:
                os.makedirs('logs', exist_ok=True)
                with open('logs/startup_cleanup.log', 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp}] 启动清理：删除了 {deleted_count} 个超过7天未验证的用户\n")
            except Exception as e:
                logger.warning(f"写入日志文件失败：{e}")
        else:
            logger.info("启动清理：没有用户被清理")

        return deleted_count

    except Exception as e:
        logger.error(f"❌ 启动清理失败：{str(e)}")
        return 0


# 5. 用户加载器
from models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(mongo, user_id)


# 6. 注册蓝图
from routes.auth import auth_bp
from routes.user import user_bp
from routes.main import main_bp
from routes.admin import admin_bp
from routes.announcements import announcements_bp
from routes.dynamic import dynamic_bp  # 新增动态功能路由

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp)
app.register_blueprint(main_bp)
# 只保留这一个 admin_bp 注册，删除重复的
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(announcements_bp)  # 公告系统
app.register_blueprint(dynamic_bp)  # 动态功能路由

# 7. 注册错误处理器
from routes.main import page_not_found, internal_server_error

app.errorhandler(404)(page_not_found)
app.errorhandler(500)(internal_server_error)


# 8. 开发工具路由
@app.route('/dev/force-logout')
def force_logout():
    """强制退出登录（开发用）"""
    from flask import session
    from flask_login import logout_user

    logout_user()
    session.clear()

    response = redirect(url_for('auth.login'))
    response.set_cookie('session', '', expires=0)
    response.set_cookie('remember_token', '', expires=0)

    return response


@app.route('/dev/cleanup-now')
def cleanup_now_debug():
    """手动触发清理（开发用）"""
    if not app.debug:
        return "此功能仅在调试模式下可用", 403

    deleted_count = cleanup_unverified_users_on_startup()
    return f"""
    <html>
        <head>
            <title>清理结果</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 30px; }
                .success { color: green; }
            </style>
        </head>
        <body>
            <h2>清理结果</h2>
            <p class="success">✅ 清理完成！</p>
            <p>删除了 <strong>{deleted_count}</strong> 个超过7天未验证的用户</p>
            <p><a href="/">返回首页</a></p>
        </body>
    </html>
    """


# 9. 动态功能路由（通用路由处理器）
@app.route('/dynamic/<path:function_path>')
def dynamic_function_router(function_path):
    """动态功能路由处理器"""
    # 这里可以处理动态功能的通用路由
    # 目前先重定向到首页
    return redirect(url_for('main.index'))


# 10. 应用启动信息
def print_startup_info():
    """打印应用启动信息"""
    logger.info("=" * 60)
    logger.info("🚀 MyWeb 应用启动")
    logger.info(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔗 访问地址: http://127.0.0.1:5000")
    logger.info(f"👑 管理员入口: http://127.0.0.1:5000/admin/dashboard")
    logger.info("=" * 60)


# 11. 主函数
if __name__ == '__main__':
    # 测试数据库连接
    try:
        mongo.db.command('ping')
        logger.info("✅ MongoDB 连接成功!")
    except Exception as e:
        logger.error(f"❌ MongoDB 连接失败: {e}")
        logger.error("请确保 MongoDB 服务正在运行")
        exit(1)

    # 打印启动信息
    print_startup_info()

    # 应用启动时执行一次清理
    logger.info("🔧 正在执行应用启动清理...")
    deleted_count = cleanup_unverified_users_on_startup()

    if deleted_count > 0:
        logger.info(f"✅ 启动清理完成，清理了 {deleted_count} 个超过7天未验证的用户")
    else:
        logger.info("✅ 启动清理完成，没有需要清理的用户")

    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    # 检查动态功能系统
    try:
        # 检查是否有动态功能配置
        func_count = mongo.db.dynamic_functions.count_documents({'is_active': True})
        logger.info(f"📊 动态功能系统: 已加载 {func_count} 个激活功能")
    except Exception as e:
        logger.warning(f"⚠️ 动态功能系统初始化失败: {e}")
        logger.warning("可能需要运行数据库升级脚本: python database_upgrade.py")

    # 启动应用
    logger.info("🌐 启动Flask应用服务器...")
    app.run(debug=True, host='0.0.0.0', port=5000)

    # 7. 注册错误处理器
    from flask import render_template


    @app.errorhandler(404)
    def page_not_found(e):
        """404错误页面"""
        return render_template('404.html'), 404


    @app.errorhandler(500)
    def internal_server_error(e):
        """500错误页面"""
        return render_template('500.html'), 500


    @app.errorhandler(403)
    def forbidden(e):
        """403错误页面"""
        return "没有权限访问此页面", 403


    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('static', 'img/favicon.ico', mimetype='image/vnd.microsoft.icon')