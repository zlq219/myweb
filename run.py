#!/usr/bin/env python
"""
MyWeb 项目启动脚本
"""
import sys
import os
import subprocess


def check_mongodb():
    """检查MongoDB是否运行"""
    print("检查 MongoDB 连接...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("✅ MongoDB 连接正常")
        return True
    except Exception as e:
        print(f"❌ MongoDB 连接失败: {e}")
        return False


def start_mongodb():
    """尝试启动MongoDB"""
    print("尝试启动 MongoDB...")

    # 方法1: 尝试启动Windows服务
    try:
        subprocess.run(["net", "start", "MongoDB"], check=False, capture_output=True)
    except:
        pass

    # 方法2: 直接启动mongod进程
    mongod_paths = [
        r"D:\MongoDB\Server\8.2\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe"
    ]

    for path in mongod_paths:
        if os.path.exists(path):
            print(f"找到 MongoDB: {path}")
            try:
                subprocess.Popen([path, "--dbpath", "D:\\MongoDB\\Server\\8.2\\data"])
                print("✅ MongoDB 进程已启动")
                return True
            except Exception as e:
                print(f"启动失败: {e}")

    print("❌ 无法启动 MongoDB，请手动启动")
    return False


def main():
    print("=" * 50)
    print("MyWeb 项目启动器")
    print("=" * 50)

    # 检查MongoDB
    if not check_mongodb():
        if not start_mongodb():
            print("\n请手动启动 MongoDB:")
            print("1. 按 Win+R, 输入 services.msc")
            print("2. 找到 'MongoDB' 并启动")
            print("3. 或运行: net start MongoDB")
            input("\n按回车键继续...")

    # 等待MongoDB启动
    import time
    print("\n等待MongoDB启动...")
    time.sleep(2)

    # 再次检查MongoDB
    if not check_mongodb():
        print("❌ MongoDB 仍未启动，应用可能无法正常工作")

    # 导入并运行Flask应用
    print("\n" + "=" * 50)
    print("启动 Flask 应用...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止应用")
    print("=" * 50 + "\n")

    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n应用已停止")
    except Exception as e:
        print(f"\n启动失败: {e}")
        input("按回车键退出...")