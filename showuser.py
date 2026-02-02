# check_delete.py - 保存到项目根目录并运行
from app import mongo
from bson import ObjectId

print("🔍 用户删除功能诊断")
print("=" * 60)

# 1. 显示所有用户及其状态
all_users = list(mongo.db.users.find({}, {'username': 1, 'email': 1, 'is_active': 1, '_is_active': 1, 'deleted_at': 1}))
print(f"📊 数据库中共有 {len(all_users)} 个用户")

print("\n📋 用户状态详情：")
for i, user in enumerate(all_users):
    status = "✅ 活跃" if user.get('is_active') else "❌ 非活跃"
    deleted = "🗑️ 已标记删除" if user.get('deleted_at') else "  未标记"
    print(f"  {i+1:2d}. {user.get('username', 'N/A'):15s} {user.get('email', 'N/A'):25s} {status} {deleted}")
    if user.get('deleted_at'):
        print(f"      删除时间: {user.get('deleted_at')}")

# 2. 统计不同状态的用户
active_count = sum(1 for u in all_users if u.get('is_active'))
inactive_count = len(all_users) - active_count
deleted_count = sum(1 for u in all_users if u.get('deleted_at'))

print(f"\n📈 状态统计:")
print(f"  • 活跃用户: {active_count} 个")
print(f"  • 非活跃用户: {inactive_count} 个")
print(f"  • 标记删除时间的用户: {deleted_count} 个")

# 3. 检查 make_admin.py 的查询条件
print(f"\n🔎 make_admin.py 可能查到的用户数:")
# 模拟 make_admin.py 的查询（通常不带筛选）
make_admin_users = list(mongo.db.users.find({}, {'username': 1, 'email': 1, 'is_active': 1}))
print(f"  不带筛选: {len(make_admin_users)} 个用户")

# 模拟管理页面的查询（可能带 is_active 筛选）
admin_page_users = list(mongo.db.users.find({'is_active': True}, {'username': 1, 'email': 1}))
print(f"  只查活跃用户: {len(admin_page_users)} 个用户")

print("=" * 60)
print("💡 可能的问题:")
if inactive_count > 0 and deleted_count == 0:
    print("  → 系统使用『软删除』(只改is_active，不物理删除)")
elif deleted_count > 0:
    print("  → 用户被标记删除时间但仍在数据库中")
elif active_count == len(all_users):
    print("  → 删除功能可能根本没执行")