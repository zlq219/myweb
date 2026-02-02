# quick_fix_check.py - 快速检查语法错误
import ast
import sys

print("🔍 检查 routes/auth.py 语法错误")
print("=" * 60)

try:
    with open('routes/auth.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 尝试解析Python语法
    ast.parse(content)
    print("✅ routes/auth.py 语法正确")

except SyntaxError as e:
    print(f"❌ 发现语法错误:")
    print(f"   文件: {e.filename or 'routes/auth.py'}")
    print(f"   行号: {e.lineno}")
    print(f"   位置: {e.offset}")
    print(f"   错误: {e.msg}")

    # 显示错误行附近的内容
    lines = content.split('\n')
    start_line = max(0, e.lineno - 3)
    end_line = min(len(lines), e.lineno + 2)

    print(f"\n📝 错误附近的代码:")
    for i in range(start_line, end_line):
        line_num = i + 1
        prefix = ">>> " if line_num == e.lineno else "    "
        print(f"{prefix}{line_num:3d}: {lines[i]}")

    # 常见错误提示
    print("\n💡 常见问题:")
    print("1. 字典或列表缺少逗号")
    print("2. 括号不匹配")
    print("3. 字符串引号不匹配")
    print("4. 缩进错误")

except Exception as e:
    print(f"❌ 检查失败: {e}")

print("=" * 60)