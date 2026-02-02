# check_parts.py - 分段检查
print("分段检查 routes/auth.py")

# 读取文件
with open('routes/auth.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"文件总行数: {len(lines)}")

# 显示50-60行
print("\n📝 第50-60行内容:")
for i in range(49, min(60, len(lines))):
    line_num = i + 1
    line = lines[i].rstrip()

    # 检查常见问题
    issues = []
    if line.count("'") % 2 != 0: issues.append("引号不匹配")
    if line.count('"') % 2 != 0: issues.append("双引号不匹配")
    if line.endswith(('{', '[', '(')): issues.append("可能缺少闭合")

    prefix = ">>> " if line_num == 55 else "    "
    issue_str = f" ({', '.join(issues)})" if issues else ""
    print(f"{prefix}{line_num:3d}: {line}{issue_str}")

# 检查附近的字典定义
print("\n🔍 查找附近的字典定义:")
for i in range(max(0, 55 - 10), min(len(lines), 55 + 10)):
    if 'user_data = {' in lines[i]:
        print(f"在第{i + 1}行找到字典定义:")

        # 显示字典内容
        j = i
        brace_count = 0
        while j < len(lines):
            line = lines[j]
            brace_count += line.count('{')
            brace_count -= line.count('}')

            prefix = "    " if j + 1 != 55 else ">>> "
            print(f"{prefix}{j + 1:3d}: {line.rstrip()}")

            if brace_count <= 0 and j > i:
                break
            j += 1
