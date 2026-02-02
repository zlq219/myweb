# deep_check.py - 深入检查导入问题
import sys
import traceback

print("🔍 深度检查导入问题")
print("=" * 60)

try:
    # 尝试导入 auth_bp
    print("尝试导入 routes.auth...")
    from routes.auth import auth_bp

    print("✅ 导入成功!")

except SyntaxError as e:
    print(f"❌ 语法错误详情:")
    print(f"   错误: {e}")
    print(f"   位置: 行{e.lineno}, 列{e.offset}")

    # 获取更多上下文
    import linecache

    line = linecache.getline('routes/auth.py', e.lineno)
    print(f"   错误行: {line.strip()}")

    # 显示前后几行
    print(f"\n📝 错误上下文:")
    for i in range(max(1, e.lineno - 3), min(e.lineno + 3, len(linecache.getlines('routes/auth.py')))):
        prefix = ">>> " if i == e.lineno else "    "
        print(f"{prefix}{i:3d}: {linecache.getline('routes/auth.py', i).rstrip()}")

except Exception as e:
    print(f"❌ 其他错误: {type(e).__name__}: {e}")
    traceback.print_exc()

print("=" * 60)

# 检查文件编码问题
print("\n🔍 检查文件编码和特殊字符")
with open('routes/auth.py', 'rb') as f:
    content = f.read()

# 检查是否有不可见字符
print(f"文件大小: {len(content)} 字节")
print(f"是否包含BOM: {content.startswith(b'\\xef\\xbb\\xbf')}")

# 检查第55行附近的字节
lines = content.split(b'\n')
if len(lines) >= 55:
    line_55 = lines[54]  # Python是0-based索引
    print(f"\n第55行原始字节: {line_55}")
    print(f"长度: {len(line_55)}")

    # 显示不可见字符
    for i, byte in enumerate(line_55):
        if byte < 32 or byte > 126:
            print(f"  位置 {i}: 不可见字符 0x{byte:02x}")