# 📁 MyWeb 项目结构文档

**生成时间**: 2026-02-08 20:35:00
**项目路径**: `E:\zlq\myweb`

## 📊 项目统计

- **总文件数**: 38 个
- **总目录数**: 10 个
- **总大小**: 3.2 MB
- **最后修改**: 2026-02-08 20:34:14

## 🌳 目录结构

```
└── myweb/ [38文件/10目录]
    ├── PROJECT_STRUCTURE.md
    ├── README.md
    ├── __init__.py
    ├── add_announcement_function.py
    ├── app.py
    ├── app3.py
    ├── auto_cleanup.py
    ├── check_email_verification.py
    ├── check_parts.py
    ├── config/ [3文件/0目录]
    │   ├── __init__.py
    │   ├── admin_menu.py
    │   └── config.py
    ├── config.py
    ├── create_test_user.py
    ├── database_upgrade.py
    ├── debug_admin.py
    ├── deep_check.py
    ├── dev_logs/ [1文件/0目录]
    │   └── 开发日志.md
    ├── extensions.py
    ├── fix_dashboard_template.py
    ├── flask_session/ [1文件/0目录]
    │   └── 2029240f6d1128be89ddc32729463129
    ├── generate_docs.py
    ├── init_announcements.py
    ├── logs/ [1文件/0目录]
    │   └── startup_cleanup.log
    ├── make_admin.py
    ├── manage.py
    ├── models/ [2文件/0目录]
    │   ├── __init__.py
    │   └── user.py
    ├── project_structure.json
    ├── quick_fix_check.py
    ├── requirements.txt
    ├── routes/ [16文件/0目录]
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── admin3.py
    │   ├── admin4.py
    │   ├── admin6.py
    │   ├── announcements.py
    │   ├── announcements4.py
    │   ├── auth.py
    │   ├── auth4.py
    │   ├── auth_backup.py
    │   ├── auth_fixed.py
    │   ├── dynamic.py
    │   ├── main.py
    │   ├── main4.py
    │   ├── user.py
    │   └── user2.py
    ├── run.bat
    ├── run.py
    ├── scan_project.py
    ├── schedule_cleanup.bat
    ├── showuser.py
    ├── start
    ├── static/ [0文件/3目录]
    │   ├── css/ [1文件/0目录]
    │   │   └── style.css
    │   ├── js/ [1文件/0目录]
    │   │   └── main.js
    │   └── uploads/ [1文件/0目录]
    │       └── 69773be5c69c1318a8839a8c_.png
    ├── templates/ [15文件/6目录]
    │   ├── 404.html
    │   ├── admin/ [7文件/0目录]
    │   │   ├── cleanup.html
    │   │   ├── dashboard.html
    │   │   ├── dashboard3.html
    │   │   ├── dashboard4.html
    │   │   ├── dashboard6.html
    │   │   ├── settings.html
    │   │   └── users.html
    │   ├── admin_entry.html
    │   ├── announcements/ [11文件/0目录]
    │   │   ├── admin_dashboard.html
    │   │   ├── admin_dashboard4.html
    │   │   ├── admin_list.html
    │   │   ├── admin_list4.html
    │   │   ├── create.html
    │   │   ├── create4.html
    │   │   ├── detail.html
    │   │   ├── edit.html
    │   │   ├── edit4.html
    │   │   ├── list.html
    │   │   └── list4.html
    │   ├── auth/ [3文件/0目录]
    │   │   ├── admin_login.html
    │   │   ├── admin_login4.html
    │   │   └── login.html
    │   ├── base.html
    │   ├── base2.html
    │   ├── dashboard.html
    │   ├── dynamic/ [2文件/0目录]
    │   │   ├── add_function.html
    │   │   └── function_list.html
    │   ├── home.html
    │   ├── index.html
    │   ├── index4.html
    │   ├── layouts/ [2文件/0目录]
    │   │   ├── admin_layout.html
    │   │   └── user_layout.html
    │   ├── login.html
    │   ├── partials/ [5文件/0目录]
    │   │   ├── footer.html
    │   │   ├── header.html
    │   │   ├── header1.html
    │   │   ├── header3.html
    │   │   └── messages.html
    │   ├── profile.html
    │   ├── profile2.html
    │   ├── register.html
    │   ├── resend_verification.html
    │   ├── users.html
    │   └── verify_prompt.html
    ├── test_auth_simple.py
    ├── test_db.py
    ├── test_email_send.py
    ├── uploads/ [0文件/0目录]
    ├── user.py
    ├── utils/ [5文件/0目录]
    │   ├── __init__.py
    │   ├── helpers.py
    │   ├── mailer.py
    │   ├── validators.py
    │   └── validators2.py
    ├── 总体设计.md
    ├── 操作手册.md
    ├── 重要文件.md
    ├── 需求说明书_基础盘录注册.md
    └── 需求说明书_新功能_公告系统.md
```

## 🎯 关键文件说明

| 文件 | 用途 | 状态 |
|------|------|------|
| `app.py` | Flask应用主入口 | ✅ 存在 (10.5 KB) |
| `config.py` | 应用配置（数据库、会话、邮箱） | ✅ 存在 (2.2 KB) |
| `requirements.txt` | Python依赖包列表 | ✅ 存在 (364.0 B) |
| `models/user.py` | 用户数据模型 | ✅ 存在 (4.3 KB) |
| `routes/auth.py` | 认证路由（登录/注册/注销/验证） | ✅ 存在 (8.2 KB) |
| `routes/admin.py` | 管理员功能路由 | ✅ 存在 (9.7 KB) |
| `routes/main.py` | 主页面路由 | ✅ 存在 (1.8 KB) |
| `templates/admin/dashboard.html` | 管理员控制台 | ✅ 存在 (1.2 KB) |
| `templates/auth/login.html` | 用户登录页面 | ✅ 存在 (7.3 KB) |
| `templates/auth/register.html` | 用户注册页面 | ❌ 缺失 |
| `make_admin.py` | 管理员设置工具（命令行） | ✅ 存在 (3.5 KB) |
| `static/css/style.css` | 主样式文件 | ✅ 存在 (1.7 KB) |
| `static/js/main.js` | 主JavaScript文件 | ✅ 存在 (3.4 KB) |
| `utils/mailer.py` | 邮件发送工具 | ✅ 存在 (4.1 KB) |

## 📈 文件类型统计

| 文件类型 | 数量 | 占比 |
|----------|------|------|
| `.py` | 52 | 46.0% |
| `.html` | 45 | 39.8% |
| `.md` | 8 | 7.1% |
| `.bat` | 2 | 1.8% |
| `.log` | 1 | 0.9% |
| `.json` | 1 | 0.9% |
| `.txt` | 1 | 0.9% |
| `.css` | 1 | 0.9% |
| `.js` | 1 | 0.9% |
| `.png` | 1 | 0.9% |

## 📝 最近修改的文件

| 文件 | 修改时间 | 大小 |
|------|----------|------|
| `开发日志.md` | 2026-02-08 20:34:14 | 23.3 KB |
| `需求说明书_基础盘录注册.md` | 2026-02-08 20:33:12 | 17.1 KB |
| `announcements.py` | 2026-02-08 20:25:59 | 12.4 KB |
| `profile.html` | 2026-02-08 20:22:21 | 4.4 KB |
| `user_layout.html` | 2026-02-08 20:21:34 | 2.6 KB |
| `admin.py` | 2026-02-08 20:17:32 | 9.7 KB |
| `config.py` | 2026-02-08 20:16:35 | 1.1 KB |
| `__init__.py` | 2026-02-08 20:16:02 | 178.0 B |
| `admin_menu.py` | 2026-02-08 20:15:34 | 866.0 B |
| `app.py` | 2026-02-08 20:11:58 | 10.5 KB |

---
*本文档由 `generate_docs.py` 自动生成，每次运行都会更新*
