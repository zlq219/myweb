// 主JavaScript文件

// 显示加载状态
function showLoading(button) {
    button.classList.add('loading');
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>处理中...';
}

// 隐藏加载状态
function hideLoading(button, originalText) {
    button.classList.remove('loading');
    button.innerHTML = originalText;
}

// 表单验证
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// 密码强度检查
function checkPasswordStrength(password) {
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,20}$/;
    const mediumRegex = /^(?=.*[a-zA-Z])(?=.*\d).{6,20}$/;

    if (strongRegex.test(password)) {
        return 'strong';
    } else if (mediumRegex.test(password)) {
        return 'medium';
    } else {
        return 'weak';
    }
}

// 显示密码强度
function showPasswordStrength(inputId, displayId) {
    const password = document.getElementById(inputId);
    const display = document.getElementById(displayId);

    if (!password || !display) return;

    password.addEventListener('input', function() {
        const strength = checkPasswordStrength(this.value);
        const messages = {
            'strong': '密码强度：强',
            'medium': '密码强度：中',
            'weak': '密码强度：弱'
        };
        const classes = {
            'strong': 'text-success',
            'medium': 'text-warning',
            'weak': 'text-danger'
        };

        display.textContent = messages[strength] || '';
        display.className = classes[strength] || '';
    });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 表单验证
    const forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                alert('请填写所有必填字段');
            }
        });
    });

    // 自动隐藏警告消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 初始化密码强度显示
    showPasswordStrength('password', 'password-strength');
    showPasswordStrength('new_password', 'new-password-strength');

    // 头像预览
    const avatarInput = document.getElementById('avatar');
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('avatar-preview');
                    if (preview) {
                        preview.src = e.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});