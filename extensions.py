from flask_pymongo import PyMongo
from flask_login import LoginManager

# 创建全局变量
mongo = None
login_manager = None

def init_extensions(app):
    global mongo, login_manager
    mongo = PyMongo(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'
    return mongo, login_manager