# test_auth_simple.py - 简化测试
from flask import Blueprint

# 创建一个最简单的auth_bp
auth_bp_test = Blueprint('auth_test', __name__)

@auth_bp_test.route('/test')
def test():
    return "测试成功"

print("✅ 简化版auth创建成功")

# 然后修改app.py，临时使用这个：
# from test_auth_simple import auth_bp_test as auth_bp