"""
菜单配置文件
非程序员可以通过修改这个文件来调整所有菜单项
支持一级菜单和两级菜单混合使用
"""

# ==================== 管理员菜单配置 ====================
ADMIN_MENU_ITEMS = [
    # 一级菜单
    {
        'title': '控制台y',
        'endpoint': 'admin.dashboard',
        'icon': 'fas fa-tachometer-alt',
        'type': 'single',  # 一级菜单
        'permission': 'admin',
        'order': 1
    },
    # 一级菜单
    {
        'title': '用户管理y',
        'endpoint': 'user.user_list',
        'icon': 'fas fa-users',
        'type': 'single',
        'permission': 'admin',
        'order': 2
    },
    # 一级菜单
    {
        'title': '公告管理y',
        'endpoint': 'announcements.admin_dashboard',
        'icon': 'fas fa-bullhorn',
        'type': 'single',
        'permission': 'admin',
        'order': 3
    },
    # 两级菜单（有子菜单）
    {
        'title': '系统设置y',
        'icon': 'fas fa-cog',
        'type': 'parent',  # 父菜单
        'permission': 'admin',
        'order': 4,
        'children': [
            {
                'title': '基本设置y',
                'endpoint': '#',
                'icon': 'fas fa-sliders-h',
                'type': 'child'
            },
            {
                'title': '邮件设置y',
                'endpoint': '#',
                'icon': 'fas fa-envelope',
                'type': 'child'
            },
            {
                'title': '安全设置y',
                'endpoint': '#',
                'icon': 'fas fa-shield-alt',
                'type': 'child'
            }
        ]
    },
    # 另一级菜单
    {
        'title': '日志查看y',
        'endpoint': '#',
        'icon': 'fas fa-history',
        'type': 'single',
        'permission': 'admin',
        'order': 5
    },
]

# ==================== 普通用户菜单配置 ====================
USER_MENU = [
    # 一级菜单
    {
        'title': '个人中心g',
        'endpoint': 'user.profile',
        'icon': 'fas fa-user',
        'type': 'single',
        'permission': 'user',
        'order': 1
    },
    # 两级菜单
    {
        'title': '消息中心g',
        'icon': 'fas fa-bell',
        'type': 'parent',
        'permission': 'user',
        'order': 2,
        'children': [
            {
                'title': '系统消息g',
                'endpoint': '#',
                'icon': 'fas fa-info-circle',
                'type': 'child'
            },
            {
                'title': '私信g',
                'endpoint': '#',
                'icon': 'fas fa-envelope',
                'type': 'child'
            },
            {
                'title': '通知设置g',
                'endpoint': '#',
                'icon': 'fas fa-cog',
                'type': 'child'
            }
        ]
    },
    # 一级菜单
    {
        'title': '我的收藏g',
        'endpoint': '#',
        'icon': 'fas fa-star',
        'type': 'single',
        'permission': 'user',
        'order': 3
    },
    # 两级菜单
    {
        'title': '账户设置g',
        'icon': 'fas fa-cog',
        'type': 'parent',
        'permission': 'user',
        'order': 4,
        'children': [
            {
                'title': '个人资料g',
                'endpoint': 'user.profile',
                'icon': 'fas fa-id-card',
                'type': 'child'
            },
            {
                'title': '修改密码g',
                'endpoint': '#',
                'icon': 'fas fa-key',
                'type': 'child'
            },
            {
                'title': '隐私设置g',
                'endpoint': '#',
                'icon': 'fas fa-lock',
                'type': 'child'
            }
        ]
    },
]

# ==================== 公共菜单配置 ====================
PUBLIC_MENU = [
    # 一级菜单
    {
        'title': '首页w',
        'endpoint': 'main.home',
        'icon': 'fas fa-home',
        'type': 'single',
        'permission': 'public',
        'order': 1
    },
    # 一级菜单
    {
        'title': '公告w',
        'endpoint': 'announcements.announcement_list',
        'icon': 'fas fa-bullhorn',
        'type': 'single',
        'permission': 'public',
        'order': 2
    },
    # 两级菜单
    {
        'title': '关于我们w',
        'icon': 'fas fa-info-circle',
        'type': 'parent',
        'permission': 'public',
        'order': 3,
        'children': [
            {
                'title': '公司介绍w',
                'endpoint': '#',
                'icon': 'fas fa-building',
                'type': 'child'
            },
            {
                'title': '团队文化w',
                'endpoint': '#',
                'icon': 'fas fa-users',
                'type': 'child'
            },
            {
                'title': '加入我们w',
                'endpoint': '#',
                'icon': 'fas fa-handshake',
                'type': 'child'
            }
        ]
    },
    # 两级菜单
    {
        'title': '联系我们w',
        'icon': 'fas fa-envelope',
        'type': 'parent',
        'permission': 'public',
        'order': 4,
        'children': [
            {
                'title': '在线留言w',
                'endpoint': '#',
                'icon': 'fas fa-comment',
                'type': 'child'
            },
            {
                'title': '联系方式w',
                'endpoint': '#',
                'icon': 'fas fa-phone',
                'type': 'child'
            },
            {
                'title': '地图导航w',
                'endpoint': '#',
                'icon': 'fas fa-map-marker-alt',
                'type': 'child'
            }
        ]
    },
]


# ==================== 菜单获取函数 ====================
def get_admin_menu(current_user=None):
    """获取管理员菜单"""
    return ADMIN_MENU_ITEMS


def get_user_menu(current_user=None):
    """获取普通用户菜单"""
    return USER_MENU


def get_public_menu():
    """获取公共菜单"""
    return PUBLIC_MENU