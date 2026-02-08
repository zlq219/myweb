from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_login import LoginManager
from utils.mailer import mail
from config import Config
import os
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def cleanup_unverified_users_on_startup():
    """应用启动时清理超过7天未验证的用户"""
    try:
        # 确保MongoDB已连接
        if not hasattr(app, 'mongo') or app.mongo is None:
            logger.warning("MongoDB连接未就绪，跳过启动清理")
            return 0

        mongo = app.mongo

        # 计算7天前的日期
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        logger.info(f"🔍 清理条件：未验证邮箱且创建时间早于 {seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')}")

        # 查询要删除的用户（未验证、非管理员、超过7天）
        query = {
            'email_verified': False,
            'created_at': {'$lt': seven_days_ago},
            'is_admin': False  # 保护管理员账户
        }

        # 先获取符合条件的用户数量
        count_to_delete = mongo.db.users.count_documents(query)

        if count_to_delete == 0:
            logger.info("ℹ️ 启动清理：没有需要清理的未验证用户")
            return 0

        logger.info(f"📊 找到 {count_to_delete} 个需要清理的用户")

        # 获取要删除的用户信息（用于日志）
        users_to_delete = list(mongo.db.users.find(
            query,
            {'email': 1, 'username': 1, 'created_at': 1}
        ).limit(10))  # 只取前10个用于日志

        # 执行删除
        result = mongo.db.users.delete_many(query)

        # 记录结果
        deleted_count = result.deleted_count

        if deleted_count > 0:
            logger.info(f"✅ 启动清理：成功删除了 {deleted_count} 个超过7天未验证的用户")

            # 记录被删除的用户（最多5个）
            if users_to_delete:
                deleted_emails = [user['email'] for user in users_to_delete[:5]]
                logger.info(f"🗑️ 清理的用户示例：{', '.join(deleted_emails)}")

            # 写入日志文件
            try:
                os.makedirs('logs', exist_ok=True)
                log_file = 'logs/startup_cleanup.log'
                with open(log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp}] 启动清理：删除了 {deleted_count} 个超过7天未验证的用户\n")
                    if users_to_delete:
                        f.write("清理的用户详情：\n")
                        for i, user in enumerate(users_to_delete[:5], 1):
                            user_time = user.get('created_at', datetime.utcnow())
                            if isinstance(user_time, datetime):
                                time_str = user_time.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                time_str = str(user_time)

                            f.write(f"  {i}. {user.get('email', '无邮箱')} "
                                    f"({user.get('username', '无用户名')}), "
                                    f"创建于: {time_str}\n")
                    f.write("-" * 50 + "\n")

                logger.info(f"📝 详细日志已保存到: {log_file}")
            except Exception as e:
                logger.warning(f"写入日志文件失败：{e}")
        else:
            logger.info("启动清理：没有用户被清理")

        return deleted_count

    except Exception as e:
        logger.error(f"❌ 启动清理失败：{str(e)}")

        # 记录错误日志
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/cleanup_errors.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] 启动清理失败：{str(e)}\n")
        except:
            pass

        return 0


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

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)

# 7. 注册错误处理器
from routes.main import page_not_found, internal_server_error

app.errorhandler(404)(page_not_found)
app.errorhandler(500)(internal_server_error)


# 8. 开发用的强制退出路由（可选）
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


# 9. 开发用的手动清理路由
@app.route('/dev/cleanup-now')
def cleanup_now_debug():
    """手动触发清理（开发环境）"""
    if not app.debug:
        return "此功能仅在调试模式下可用", 403

    deleted_count = cleanup_unverified_users_on_startup()
    return f"""
    <html>
        <head>
            <title>清理结果</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 30px; max-width: 800px; margin: 0 auto; }}
                h2 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
                .success {{ color: #4CAF50; font-weight: bold; }}
                .info {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                a {{ color: #2196F3; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h2>清理结果</h2>
            <div class="info">
                <p class="success">✅ 清理完成！</p>
                <p>删除了 <strong>{deleted_count}</strong> 个超过7天未验证的用户</p>
                <p>详细日志请查看控制台或 logs/startup_cleanup.log 文件</p>
            </div>
            <p><a href="/">返回首页</a> | <a href="/admin/dashboard">管理员后台</a></p>
        </body>
    </html>
    """


# 10. 应用启动信息
def print_startup_info():
    """打印应用启动信息"""
    logger.info("=" * 60)
    logger.info("🚀 MyWeb 应用启动")
    logger.info(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔗 访问地址: http://127.0.0.1:5000")
    logger.info(f"👑 管理员入口: http://127.0.0.1:5000/auth/admin/login")
    logger.info("=" * 60)


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

    # 启动应用
    logger.info("🌐 启动Flask应用服务器...")
    app.run(debug=True, host='0.0.0.0', port=5000)