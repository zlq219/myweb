import pymongo
import sys

try:
    # 连接到 MongoDB
    client = pymongo.MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=5000)

    # 测试连接
    client.admin.command('ping')
    print("✅ MongoDB 连接成功！")

    # 列出所有数据库
    print("📊 数据库列表：")
    for db in client.list_databases():
        print(f"  - {db['name']}")

    # 检查我们的数据库是否存在
    db_name = "myweb"
    if db_name in client.list_database_names():
        print(f"✅ 数据库 '{db_name}' 已存在")
    else:
        print(f"📝 数据库 '{db_name}' 不存在，将在首次使用时自动创建")

    client.close()

except pymongo.errors.ConnectionFailure as e:
    print(f"❌ MongoDB 连接失败：{e}")
    print("\n🔧 请按以下步骤操作：")
    print("1. 检查 MongoDB 服务是否已启动")
    print("2. 打开服务管理器 (services.msc)")
    print("3. 找到 'MongoDB' 服务并启动它")
    print("4. 如果服务不存在，请重新安装 MongoDB")

except Exception as e:
    print(f"❌ 发生错误：{e}")