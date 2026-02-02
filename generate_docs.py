# generate_docs.py - 项目结构文档生成器
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


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def scan_directory(path, level=0, max_depth=6, exclude_patterns=None):
    """递归扫描目录结构"""
    if exclude_patterns is None:
        exclude_patterns = ['.git', '__pycache__', 'venv', '.vscode', '.idea', 'node_modules']

    # 检查是否应该跳过此目录
    dir_name = os.path.basename(path) if os.path.basename(path) else path
    if dir_name.startswith('.') or dir_name in exclude_patterns:
        return None

    if level > max_depth:
        return None

    result = {
        'path': path,
        'name': dir_name,
        'type': 'directory',
        'level': level,
        'children': [],
        'file_count': 0,
        'dir_count': 0,
        'total_size': 0,
        'last_modified': ''
    }

    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        result['error'] = '权限拒绝'
        return result
    except Exception as e:
        result['error'] = str(e)
        return result

    latest_mtime = 0

    for item in items:
        # 跳过隐藏文件和排除模式
        if item.startswith('.') or item in exclude_patterns:
            continue

        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            # 递归扫描子目录
            subdir = scan_directory(item_path, level + 1, max_depth, exclude_patterns)
            if subdir:
                result['children'].append(subdir)
                result['dir_count'] += 1
                result['total_size'] += subdir['total_size']
                latest_mtime = max(latest_mtime, os.path.getmtime(item_path))
        else:
            # 跳过特定文件类型
            if item.endswith(('.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe')):
                continue

            # 文件信息
            try:
                file_info = get_file_info(item_path)
                file_info['type'] = 'file'
                file_info['level'] = level + 1
                file_info['extension'] = os.path.splitext(item)[1].lower()

                result['children'].append(file_info)
                result['file_count'] += 1
                result['total_size'] += file_info['size']
                latest_mtime = max(latest_mtime, os.path.getmtime(item_path))
            except Exception as e:
                # 跳过无法访问的文件
                continue

    if latest_mtime > 0:
        result['last_modified'] = datetime.fromtimestamp(latest_mtime).strftime('%Y-%m-%d %H:%M:%S')

    return result


def generate_markdown_tree(data, output_file='PROJECT_STRUCTURE.md'):
    """生成Markdown格式的项目结构文档"""

    with open(output_file, 'w', encoding='utf-8') as f:
        # 标题和基本信息
        f.write(f"# 📁 MyWeb 项目结构文档\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**项目路径**: `{os.path.abspath(data['path'])}`\n\n")

        # 统计信息
        f.write("## 📊 项目统计\n\n")
        f.write(f"- **总文件数**: {data['file_count']:,} 个\n")
        f.write(f"- **总目录数**: {data['dir_count']:,} 个\n")
        f.write(f"- **总大小**: {format_size(data['total_size'])}\n")
        if data['last_modified']:
            f.write(f"- **最后修改**: {data['last_modified']}\n")
        f.write("\n")

        # 目录结构
        f.write("## 🌳 目录结构\n\n")
        f.write("```\n")

        def write_tree_to_md(data, indent='', is_last=True, max_depth=6):
            """递归写入目录树到Markdown"""
            if data['level'] > max_depth:
                return

            if data['type'] == 'file':
                prefix = '└── ' if is_last else '├── '
                f.write(f"{indent}{prefix}{data['name']}\n")
                return

            # 目录
            prefix = '└── ' if is_last else '├── '
            count_info = f" [{data['file_count']}文件/{data['dir_count']}目录]"
            f.write(f"{indent}{prefix}{data['name']}/{count_info}\n")

            # 处理子项
            new_indent = indent + ('    ' if is_last else '│   ')
            children = [c for c in data['children'] if c is not None]

            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                write_tree_to_md(child, new_indent, is_last_child, max_depth)

        write_tree_to_md(data)
        f.write("```\n\n")

        # 关键文件说明
        f.write("## 🎯 关键文件说明\n\n")
        f.write("| 文件 | 用途 | 状态 |\n")
        f.write("|------|------|------|\n")

        key_files = {
            'app.py': 'Flask应用主入口',
            'config.py': '应用配置（数据库、会话、邮箱）',
            'requirements.txt': 'Python依赖包列表',
            'models/user.py': '用户数据模型',
            'routes/auth.py': '认证路由（登录/注册/注销/验证）',
            'routes/admin.py': '管理员功能路由',
            'routes/main.py': '主页面路由',
            'templates/admin/dashboard.html': '管理员控制台',
            'templates/auth/login.html': '用户登录页面',
            'templates/auth/register.html': '用户注册页面',
            'make_admin.py': '管理员设置工具（命令行）',
            'static/css/style.css': '主样式文件',
            'static/js/main.js': '主JavaScript文件',
            'utils/mailer.py': '邮件发送工具'
        }

        project_root = os.path.abspath(data['path'])
        for file_path, description in key_files.items():
            full_path = os.path.join(project_root, file_path)
            if os.path.exists(full_path):
                status = "✅ 存在"
                # 获取文件大小
                try:
                    size = os.path.getsize(full_path)
                    status += f" ({format_size(size)})"
                except:
                    status += " (大小未知)"
            else:
                status = "❌ 缺失"

            f.write(f"| `{file_path}` | {description} | {status} |\n")

        f.write("\n")

        # 文件类型统计
        f.write("## 📈 文件类型统计\n\n")

        file_types = {}

        def count_file_types(data):
            if data['type'] == 'file':
                ext = data.get('extension', '无扩展名')
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
            else:
                for child in data['children']:
                    if child:
                        count_file_types(child)

        count_file_types(data)

        if file_types:
            f.write("| 文件类型 | 数量 | 占比 |\n")
            f.write("|----------|------|------|\n")

            total_files = sum(file_types.values())
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_files) * 100 if total_files > 0 else 0
                if ext == '':
                    ext_name = '无扩展名'
                else:
                    ext_name = ext
                f.write(f"| `{ext_name}` | {count} | {percentage:.1f}% |\n")
        else:
            f.write("暂无文件类型统计信息\n")

        f.write("\n")

        # 最近修改的文件
        f.write("## 📝 最近修改的文件\n\n")

        all_files = []

        def collect_files(data):
            if data['type'] == 'file':
                all_files.append({
                    'name': data['name'],
                    'path': data.get('relative_path', ''),
                    'modified': data.get('modified', ''),
                    'size': data['size']
                })
            else:
                for child in data['children']:
                    if child:
                        collect_files(child)

        # 先为文件添加相对路径信息
        def add_relative_paths(data, base_path=''):
            if data['type'] == 'file':
                data['relative_path'] = base_path
            else:
                current_path = f"{base_path}{data['name']}/" if base_path else f"{data['name']}/"
                for child in data['children']:
                    if child:
                        add_relative_paths(child, current_path)

        add_relative_paths(data)
        collect_files(data)

        # 按修改时间排序
        recent_files = sorted(
            all_files,
            key=lambda x: x.get('modified', ''),
            reverse=True
        )[:10]  # 只显示前10个

        if recent_files:
            f.write("| 文件 | 修改时间 | 大小 |\n")
            f.write("|------|----------|------|\n")
            for file_info in recent_files:
                file_name = file_info['name']
                file_path = file_info.get('relative_path', '')
                if file_path:
                    display_path = f"`{file_path}{file_name}`"
                else:
                    display_path = f"`{file_name}`"

                f.write(
                    f"| {display_path} | {file_info.get('modified', '未知')} | {format_size(file_info['size'])} |\n")
        else:
            f.write("暂无最近修改文件信息\n")

        f.write("\n---\n")
        f.write("*本文档由 `generate_docs.py` 自动生成，每次运行都会更新*\n")


def main():
    """主函数"""
    print("=" * 60)
    print("📁 MyWeb 项目结构文档生成器")
    print("=" * 60)

    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"项目根目录: {script_dir}")

    # 扫描项目结构
    print("\n🔄 正在扫描项目结构...")
    project_structure = scan_directory(script_dir, max_depth=6)

    if not project_structure:
        print("❌ 项目结构扫描失败")
        return

    if 'error' in project_structure:
        print(f"❌ 扫描错误: {project_structure['error']}")
        return

    # 生成Markdown文档
    output_file = os.path.join(script_dir, 'PROJECT_STRUCTURE.md')
    print(f"\n📄 正在生成文档: {output_file}")

    generate_markdown_tree(project_structure, output_file)

    # 打印摘要信息
    print(f"\n✅ 文档生成完成!")
    print(f"📊 项目统计:")
    print(f"  文件总数: {project_structure['file_count']:,}")
    print(f"  目录总数: {project_structure['dir_count']:,}")
    print(f"  总大小: {format_size(project_structure['total_size'])}")

    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"📄 文档大小: {format_size(file_size)}")

    print(f"\n💡 使用说明:")
    print(f"  - 文档位置: {output_file}")
    print(f"  - 更新方式: 重新运行本程序即可更新")
    print(f"  - 建议: 将文档提交到版本控制系统")


if __name__ == '__main__':
    main()