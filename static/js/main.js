/**
 * MyWeb 主JavaScript文件
 * 版本: 2.0
 */
// 性能监控
console.time('MyWeb初始化');

// 在DOM加载完成后
document.addEventListener('DOMContentLoaded', function() {
    console.timeEnd('MyWeb初始化');

    // ... 其他初始化代码 ...
});

// 资源预加载
function preloadCriticalResources() {
    const resources = [
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
    ];

    resources.forEach(url => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = url;
        link.as = 'style';
        document.head.appendChild(link);
    });
}

// 页面完全加载后执行
window.addEventListener('load', function() {
    console.log('所有资源加载完成');

    // 移除加载状态
    if (document.querySelector('.loading')) {
        document.querySelector('.loading').style.display = 'none';
    }
});

// 页面可见性变化
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        console.log('页面恢复可见');
    }
});
// DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('MyWeb 系统初始化...');

    // 初始化所有组件
    initSidebar();
    initMenuHighlight();
    initMobileMenu();
    initTooltips();
    initAlerts();
    initForms();

    // 显示页面内容（防止FOUC）
    document.body.style.opacity = 1;
});

/**
 * 侧边栏功能
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const pageContainer = document.querySelector('.page-container');

    if (sidebarToggle && pageContainer) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            pageContainer.classList.toggle('sidebar-collapsed');

            // 切换图标
            const icon = this.querySelector('i');
            if (pageContainer.classList.contains('sidebar-collapsed')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-chevron-right');
            } else {
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-bars');
            }

            // 保存状态到localStorage
            const isCollapsed = pageContainer.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });

        // 恢复上次的状态
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            pageContainer.classList.add('sidebar-collapsed');
            const icon = sidebarToggle.querySelector('i');
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-chevron-right');
        }
    }

    // 子菜单点击事件
    const submenuTriggers = document.querySelectorAll('.nav-item.has-submenu > .nav-link');
    submenuTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            // 如果是外部链接或激活状态，不阻止默认行为
            if (this.classList.contains('external-link') || this.classList.contains('active')) {
                return;
            }

            e.preventDefault();
            e.stopPropagation();

            const parent = this.parentElement;
            const isOpen = parent.classList.contains('open');

            // 关闭其他打开的子菜单
            if (!isOpen) {
                document.querySelectorAll('.nav-item.has-submenu.open').forEach(item => {
                    if (item !== parent) {
                        item.classList.remove('open');
                    }
                });
            }

            // 切换当前子菜单
            parent.classList.toggle('open');

            // 如果侧边栏已折叠，点击后展开
            if (pageContainer && pageContainer.classList.contains('sidebar-collapsed')) {
                pageContainer.classList.remove('sidebar-collapsed');
                const icon = sidebarToggle.querySelector('i');
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-bars');
                localStorage.setItem('sidebarCollapsed', false);
            }
        });
    });

    // 点击页面内容区域关闭子菜单（移动端）
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const openMenus = document.querySelectorAll('.nav-item.has-submenu.open');
            openMenus.forEach(menu => {
                if (!menu.contains(e.target)) {
                    menu.classList.remove('open');
                }
            });
        }
    });
}

/**
 * 菜单高亮功能
 */
function initMenuHighlight() {
    const currentPath = window.location.pathname;

    // 清除所有active状态
    function clearActiveStates() {
        document.querySelectorAll('.nav-link.active, .submenu-item.active').forEach(item => {
            item.classList.remove('active');
        });
    }

    // 高亮当前菜单项
    function highlightCurrentMenu() {
        clearActiveStates();

        // 检查所有菜单项
        const allMenuItems = document.querySelectorAll('.nav-link:not(.external-link), .submenu-item:not(.external-link)');

        allMenuItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPath === href) {
                item.classList.add('active');

                // 展开父级菜单（如果是子菜单）
                const parentMenu = item.closest('.nav-item.has-submenu');
                if (parentMenu) {
                    parentMenu.classList.add('open');
                }
            }
        });

        // 如果没有精确匹配，尝试部分匹配
        if (!document.querySelector('.nav-link.active, .submenu-item.active')) {
            allMenuItems.forEach(item => {
                const href = item.getAttribute('href');
                if (href && href !== '/' && currentPath.startsWith(href)) {
                    item.classList.add('active');

                    const parentMenu = item.closest('.nav-item.has-submenu');
                    if (parentMenu) {
                        parentMenu.classList.add('open');
                    }
                }
            });
        }
    }

    highlightCurrentMenu();

    // 监听URL变化（对于单页应用或Ajax导航）
    if (typeof history.pushState === 'function') {
        const originalPushState = history.pushState;
        history.pushState = function() {
            originalPushState.apply(this, arguments);
            setTimeout(highlightCurrentMenu, 100);
        };

        window.addEventListener('popstate', function() {
            setTimeout(highlightCurrentMenu, 100);
        });
    }
}

/**
 * 移动端菜单功能
 */
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.querySelector('.sidebar');
    const pageContainer = document.querySelector('.page-container');

    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            sidebar.classList.toggle('sidebar-mobile-open');
            document.body.classList.toggle('menu-open');
        });

        // 点击页面内容区域关闭移动菜单
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && sidebar.classList.contains('sidebar-mobile-open')) {
                if (!sidebar.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                    sidebar.classList.remove('sidebar-mobile-open');
                    document.body.classList.remove('menu-open');
                }
            }
        });

        // ESC键关闭菜单
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('sidebar-mobile-open')) {
                sidebar.classList.remove('sidebar-mobile-open');
                document.body.classList.remove('menu-open');
            }
        });
    }

    // 窗口大小变化时调整
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 768) {
                if (sidebar) {
                    sidebar.classList.remove('sidebar-mobile-open');
                    document.body.classList.remove('menu-open');
                }
            }
        }, 250);
    });
}

/**
 * 工具提示初始化
 */
function initTooltips() {
    // 使用Bootstrap的tooltip
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover'
        });
    });
}

/**
 * 消息提示处理
 */
function initAlerts() {
    // 自动关闭的警告框
    const autoCloseAlerts = document.querySelectorAll('.alert[data-auto-close]');
    autoCloseAlerts.forEach(alert => {
        const delay = parseInt(alert.getAttribute('data-auto-close')) || 5000;
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, delay);
    });

    // 为所有警告框添加关闭按钮事件
    document.querySelectorAll('.alert').forEach(alert => {
        alert.addEventListener('closed.bs.alert', function() {
            console.log('警告框已关闭');
        });
    });
}

/**
 * 表单处理
 */
function initForms() {
    // 表单验证增强
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // 密码显示/隐藏切换
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.closest('.input-group').querySelector('input');
            const icon = this.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                this.setAttribute('aria-label', '隐藏密码');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                this.setAttribute('aria-label', '显示密码');
            }
        });
    });
}

/**
 * AJAX请求封装
 */
window.MyWeb = window.MyWeb || {};

MyWeb.ajax = {
    /**
     * 发送GET请求
     * @param {string} url
     * @param {Object} params
     * @param {Function} callback
     */
    get: function(url, params = {}, callback = null) {
        return this.request('GET', url, params, callback);
    },

    /**
     * 发送POST请求
     * @param {string} url
     * @param {Object} data
     * @param {Function} callback
     */
    post: function(url, data = {}, callback = null) {
        return this.request('POST', url, data, callback);
    },

    /**
     * 发送请求
     * @param {string} method
     * @param {string} url
     * @param {Object} data
     * @param {Function} callback
     */
    request: function(method, url, data = {}, callback = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };

        // 添加CSRF令牌（如果存在）
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            options.headers['X-CSRF-Token'] = csrfToken.getAttribute('content');
        }

        if (method === 'GET') {
            const params = new URLSearchParams(data).toString();
            url = params ? `${url}?${params}` : url;
        } else {
            options.body = JSON.stringify(data);
        }

        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (callback) callback(null, data);
                return data;
            })
            .catch(error => {
                console.error('请求失败:', error);
                if (callback) callback(error, null);
                throw error;
            });
    }
};

/**
 * 显示加载动画
 */
MyWeb.showLoading = function(element = null) {
    const loader = document.createElement('div');
    loader.className = 'loading-overlay';
    loader.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
        </div>
    `;

    if (element) {
        element.style.position = 'relative';
        element.appendChild(loader);
    } else {
        document.body.appendChild(loader);
    }

    return loader;
};

/**
 * 隐藏加载动画
 */
MyWeb.hideLoading = function(loader) {
    if (loader && loader.parentNode) {
        loader.parentNode.removeChild(loader);
    }
};

/**
 * 显示消息提示
 */
MyWeb.showMessage = function(message, type = 'success', duration = 3000) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type} alert-dismissible fade show message-toast`;
    messageDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;

    document.body.appendChild(messageDiv);

    if (duration > 0) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(messageDiv);
            bsAlert.close();
        }, duration);
    }

    return messageDiv;
};

/**
 * 确认对话框
 */
MyWeb.confirm = function(message, callback) {
    const modalHtml = `
        <div class="modal fade" id="confirmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">确认操作</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" id="confirmButton">确认</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    const modalDiv = document.createElement('div');
    modalDiv.innerHTML = modalHtml;
    document.body.appendChild(modalDiv);

    const modal = new bootstrap.Modal(modalDiv.querySelector('.modal'));
    modal.show();

    const confirmButton = modalDiv.querySelector('#confirmButton');
    confirmButton.addEventListener('click', function() {
        modal.hide();
        if (callback) callback(true);
    });

    modalDiv.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modalDiv);
    });
};

// 导出到全局
window.addEventListener('load', function() {
    console.log('MyWeb JavaScript 加载完成');
});