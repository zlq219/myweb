# fix_dashboard_template.py
import os

print("🔧 修复 dashboard.html 模板")
print("=" * 60)

template_file = 'templates/dashboard.html'

if not os.path.exists(template_file):
    print(f"❌ 文件不存在: {template_file}")
    exit(1)

# 读取文件
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换
original_line = None
if 'url_for(\'user.user_list\')' in content:
    original_line = [line for line in content.split('\n') if 'user.user_list' in line][0]

    # 替换为管理后台链接
    new_content = content.replace(
        'url_for(\'user.user_list\')',
        'url_for(\'admin.dashboard\')'
    )

    # 或者直接注释掉
    # new_content = content.replace(original_line, f'<!-- {original_line} -->')

    # 保存修改
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 已修复: {template_file}")
    print(f"📝 原代码: {original_line}")
    print(f"🔄 已替换为指向 admin.dashboard")

elif 'url_for("user.user_list")' in content:
    # 处理双引号版本
    new_content = content.replace(
        'url_for("user.user_list")',
        'url_for("admin.dashboard")'
    )

    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 已修复双引号版本")

else:
    print("❓ 未找到 'user.user_list' 引用")
    print("💡 可能错误在其他位置")

# 检查文件内容
print("\n🔍 检查修复后的文件:")
with open(template_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if i + 1 == 31 or 'user_list' in line or 'admin.dashboard' in line:
            print(f"  行{i + 1}: {line.rstrip()}")

print("\n" + "=" * 60)
print("🎯 后续建议:")
print("1. 普通用户页面不应该有'用户管理'功能")
print("2. 用户管理应该是管理员专属功能")
print("3. 检查是否还有其他错误链接")