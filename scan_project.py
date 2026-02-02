# scan_project.py - 项目结构扫描工具
import os
import json
from datetime import datetime
from pathlib import Path


def get_file_info(filepath):
    """获取文件详细信息"""
    stat = os.stat(filepath)
    return {
        'name': os.path.basename(filepath),
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'is_dir': os.path.isdir(filepath)
    }


def scan_directory(path, level=0, max_depth=5):
    """递归扫描目录结构"""
    if level > max_depth:
        return None

    result = {
        'path': path,
        'name': os.path.basename(path) if os.path.basename(path) else path,
        'type': 'directory',
        'level': level,
        'children': [],
        'file_count': 0,
        'dir_count': 0,
        'total_size': 0
    }

    try:
        items = os.listdir(path)
    except PermissionError:
        result['error'] = 'Permission denied'
        return result
    except Exception as e:
        result['error'] = str(e)
        return result

    for item in sorted(items):
        # 跳过隐藏文件和特定目录
        if item.startswith('.') or item in ['__pycache__', 'venv', '.git']:
            continue

        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            # 递归扫描子目录
            subdir = scan_directory(item_path, level + 1, max_depth)
            if subdir:
                result['children'].append(subdir)
                result['dir_count'] += 1
                result['total_size'] += subdir['total_size']
        else:
            # 文件信息
            file_info = get_file_info(item_path)
            file_info['type'] = 'file'
            file_info['level'] = level + 1
            file_info['extension'] = os.path.splitext(item)[1].lower()
            result['children'].append(file_info)
            result['file_count'] += 1
            result['total_size'] += file_info['size']

    return result


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def print_tree(data, indent='', is_last=True, show_size=True):
    """打印目录树"""
    if data['type'] == 'file':
        prefix = '└── ' if is_last else '├── '
        size_info = f" ({format_size(data['size'])})" if show_size else ''
        print(f"{indent}{prefix}{data['name']}{size_info}")
        return

    # 目录
    prefix = '└── ' if is_last else '├── '
    count_info = f" [{data['file_count']}文件, {data['dir_count']}目录]"
    size_info = f" ({format_size(data['total_size'])})" if show_size else ''
    print(f"{indent}{prefix}{data['name']}/{count_info}{size_info}")

    # 子项
    new_indent = indent + ('    ' if is_last else '│   ')
    children = data['children']

    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        print_tree(child, new_indent, is_last_child, show_size)


def generate_markdown_report(data, output_file='PROJECT_STRUCTURE.md'):
    """生成Markdown格式的项目结构报告"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 项目结构文档\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"项目路径: {data['path']}\n\n")

        f.write("## 📁 目录结构总览\n")
        f.write(f"- 总文件数: {data['file_count']}\n")
        f.write(f"- 总目录数: {data['dir_count']}\n")
        f.write(f"- 总大小: {format_size(data['total_size'])}\n\n")

        f.write("## 📋 详细目录结构\n```\n")

        def write_tree_to_md(data, indent='', is_last=True):
            if data['type'] == 'file':
                prefix = '└── ' if is_last else '├── '
                f.write(f"{indent}{prefix}{data['name']}\n")
                return

            prefix = '└── ' if is_last else '├── '
            f.write(f"{indent}{prefix}{data['name']}/\n")

            new_indent = indent + ('    ' if is_last else '│   ')
            children = data['children']

            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                write_tree_to_md(child, new_indent, is_last_child)

        write_tree_to_md(data)
        f.write("```\n\n")

        f.write("## 📊 文件类型统计\n")

        # 统计文件类型
        file_types = {}

        def count_file_types(data):
            if data['type'] == 'file':
                ext = data.get('extension', '无扩展名')
                file_types[ext] = file_types.get(ext, 0) + 1
            else:
                for child in data['children']:
                    count_file_types(child)

        count_file_types(data)

        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            if ext:
                f.write(f"- `{ext}`: {count} 个文件\n")
            else:
                f.write(f"- 无扩展名: {count} 个文件\n")

        f.write("\n## 🎯 关键文件说明\n")
        f.write("| 文件路径 | 用途说明 | 状态 |\n")
        f.write("|----------|----------|------|\n")

        # 关键文件说明
        key_files = {
            'app.py': 'Flask应用主入口',
            'config.py': '应用配置',
            'requirements.txt': 'Python依赖包',
            'models/user.py': '用户数据模型',
            'routes/auth.py': '认证相关路由',
            'routes/admin.py': '管理员功能路由',
            'templates/admin/dashboard.html': '管理员控制台',
            'make_admin.py': '管理员设置工具'
        }

        for file_path, description in key_files.items():
            f.write(f"| `{file_path}` | {description} | ✅ 存在 |\n")

        print(f"✅ Markdown报告已生成: {output_file}")


def main():
    """主函数"""
    project_path = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("📁 项目结构扫描工具")
    print("=" * 60)
    print(f"扫描路径: {project_path}")
    print()

    # 扫描项目结构
    print("🔄 正在扫描项目结构...")
    project_structure = scan_directory(project_path, max_depth=6)

    if 'error' in project_structure:
        print(f"❌ 扫描失败: {project_structure['error']}")
        return

    # 打印目录树
    print("\n🌳 目录结构:")
    print_tree(project_structure, show_size=True)

    print(f"\n📊 统计信息:")
    print(f"  文件总数: {project_structure['file_count']}")
    print(f"  目录总数: {project_structure['dir_count']}")
    print(f"  总大小: {format_size(project_structure['total_size'])}")

    # 生成Markdown报告
    generate_markdown_report(project_structure)

    # 生成JSON文件（便于程序读取）
    json_file = 'project_structure.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(project_structure, f, ensure_ascii=False, indent=2)
    print(f"📄 JSON数据已保存: {json_file}")

    print("\n" + "=" * 60)
    print("🎯 待办功能检查:")
    print("=" * 60)

    # 检查关键文件是否存在
    required_files = [
        ('app.py', 'Flask主程序'),
        ('config.py', '配置文件'),
        ('requirements.txt', '依赖文件'),
        ('models/user.py', '用户模型'),
        ('routes/auth.py', '认证路由'),
        ('routes/admin.py', '管理员路由'),
        ('templates/admin/dashboard.html', '管理页面')
    ]

    all_exist = True
    for filename, description in required_files:
        filepath = os.path.join(project_path, filename)
        if os.path.exists(filepath):
            print(f"✅ {filename:30s} - {description}")
        else:
            print(f"❌ {filename:30s} - {description} (缺失!)")
            all_exist = False

    if all_exist:
        print("\n✅ 所有关键文件都存在，项目结构完整")
    else:
        print("\n⚠️  部分关键文件缺失，请检查项目结构")

    print("\n" + "=" * 60)
    print("📋 功能完成度检查:")
    print("=" * 60)

    # 功能完成度检查
    features = [
        ("用户注册", "routes/auth.py 中的 register() 函数"),
        ("用户登录", "routes/auth.py 中的 login() 函数"),
        ("用户注销", "routes/auth.py 中的 logout() 函数 - 待测试"),
        ("邮箱验证", "routes/auth.py 中的 verify_email() 函数 - 待完善"),
        ("管理员权限", "routes/admin.py 中的 admin_required 装饰器"),
        ("用户删除", "routes/admin.py 中的 delete_user() 函数"),
        ("未验证用户清理", "routes/admin.py 中的 cleanup_unverified_users() 函数"),
        ("个人中心", "未实现 - 需要创建 user.py 路由"),
        ("修改个人信息", "未实现"),
        ("修改密码", "未实现"),
        ("邮箱验证流程", "未完成 - 需要测试邮件发送"),
        ("会话超时管理", "已实现 - 5分钟超时"),
        ("管理员控制台", "templates/admin/dashboard.html"),
        ("搜索用户功能", "routes/admin.py 中的 search_users() 函数")
    ]

    for feature, status in features:
        if "未" in status or "待" in status:
            print(f"🔶 {feature:20s} - {status}")
        else:
            print(f"✅ {feature:20s} - {status}")

    print("\n💡 建议下一步:")
    print("1. 测试注销功能")
    print("2. 完善邮箱验证流程")
    print("3. 创建个人中心页面")
    print("4. 实现修改密码功能")


if __name__ == '__main__':
    main()