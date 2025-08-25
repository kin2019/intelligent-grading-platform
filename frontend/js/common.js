/**
 * ZYJC智能批改平台 - 通用工具函数
 * 统一管理常用功能，提高代码复用性
 */

class ZYJC {
    constructor() {
        this.API_BASE = 'http://localhost:8000/api/v1';
        this.token = localStorage.getItem('token');
        this.user = null;
        
        // 初始化
        this.initEventListeners();
    }
    
    // 通用API请求方法
    async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': this.token ? `Bearer ${this.token}` : ''
            }
        };
        
        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(`${this.API_BASE}${endpoint}`, config);
            
            if (response.status === 401) {
                this.handleAuthError();
                return null;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            this.showToast(`请求失败: ${error.message}`, 'error');
            return null;
        }
    }
    
    // GET请求
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    // POST请求
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // 文件上传
    async upload(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': this.token ? `Bearer ${this.token}` : ''
                // 不设置Content-Type，让浏览器自动设置multipart边界
            }
        });
    }
    
    // 认证相关
    async login(code, role) {
        const response = await this.post('/auth/wechat/login', { code, role });
        if (response && response.access_token) {
            this.token = response.access_token;
            localStorage.setItem('token', this.token);
            localStorage.setItem('user', JSON.stringify(response.user));
            localStorage.setItem('role', role);
            this.user = response.user;
            return response;
        }
        return null;
    }
    
    async getUserInfo() {
        if (!this.token) return null;
        const response = await this.get('/auth/me');
        if (response) {
            this.user = response;
            localStorage.setItem('user', JSON.stringify(response));
        }
        return response;
    }
    
    // 处理认证错误
    handleAuthError() {
        this.showToast('登录已过期，请重新登录', 'warning');
        this.logout();
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
    }
    
    // 登出
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('role');
    }
    
    // 通用Toast提示
    showToast(message, type = 'info', duration = 3000) {
        // 移除已存在的toast
        const existingToast = document.querySelector('.zyjc-toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = `zyjc-toast zyjc-toast-${type}`;
        
        const colors = {
            info: '#007AFF',
            success: '#4CAF50',
            warning: '#FF9500',
            error: '#FF3B30'
        };
        
        toast.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: ${colors[type] || colors.info};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            max-width: 80%;
            text-align: center;
            word-wrap: break-word;
        `;
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // 添加进入动画
        toast.style.opacity = '0';
        toast.style.transform = 'translate(-50%, -60%)';
        
        requestAnimationFrame(() => {
            toast.style.transition = 'all 0.3s ease';
            toast.style.opacity = '1';
            toast.style.transform = 'translate(-50%, -50%)';
        });
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.opacity = '0';
                toast.style.transform = 'translate(-50%, -40%)';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 300);
            }
        }, duration);
    }
    
    // 格式化日期
    formatDate(dateString, format = 'relative') {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        
        if (format === 'relative') {
            const minutes = Math.floor(diff / (1000 * 60));
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            
            if (minutes < 1) return '刚刚';
            if (minutes < 60) return `${minutes}分钟前`;
            if (hours < 24) return `${hours}小时前`;
            if (days === 1) return '昨天';
            if (days < 7) return `${days}天前`;
            return date.toLocaleDateString();
        } else if (format === 'short') {
            return date.toLocaleDateString();
        } else if (format === 'full') {
            return date.toLocaleString();
        }
        
        return dateString;
    }
    
    // 格式化数字
    formatNumber(num, decimals = 0) {
        if (typeof num !== 'number') return num;
        return num.toLocaleString('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }
    
    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // 节流函数
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // 文件大小格式化
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 图片压缩
    compressImage(file, maxWidth = 800, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
                canvas.width = img.width * ratio;
                canvas.height = img.height * ratio;
                
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob((blob) => {
                    resolve(new File([blob], file.name, {
                        type: file.type,
                        lastModified: Date.now()
                    }));
                }, file.type, quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }
    
    // 统一导航函数
    navigateTo(page, params = {}) {
        const role = localStorage.getItem('role') || 'student';
        const queryString = Object.keys(params).length > 0 
            ? '?' + new URLSearchParams(params).toString() 
            : '';
        
        switch (page) {
            case 'home':
                window.location.href = role === 'parent' ? 'parent-home.html' : 'student-home.html';
                break;
            case 'profile':
                window.location.href = 'profile.html' + queryString;
                break;
            case 'error-book':
                window.location.href = 'error-book.html' + queryString;
                break;
            case 'study-plan':
                window.location.href = 'study-plan.html' + queryString;
                break;
            case 'vip-center':
                window.location.href = 'vip-center.html' + queryString;
                break;
            case 'homework-submit':
                window.location.href = 'homework-submit.html' + queryString;
                break;
            case 'homework-result':
                window.location.href = 'homework-result.html' + queryString;
                break;
            case 'login':
                window.location.href = 'login.html' + queryString;
                break;
            default:
                console.warn('未知的导航目标:', page);
        }
    }
    
    // 初始化事件监听器
    initEventListeners() {
        // 全局错误处理
        window.addEventListener('error', (event) => {
            console.error('全局错误:', event.error);
        });
        
        // 网络状态监听
        window.addEventListener('online', () => {
            this.showToast('网络连接已恢复', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.showToast('网络连接已断开', 'warning');
        });
    }
    
    // 获取设备信息
    getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            screenWidth: screen.width,
            screenHeight: screen.height,
            windowWidth: window.innerWidth,
            windowHeight: window.innerHeight
        };
    }
    
    // 检查是否为移动设备
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    // 检查登录状态
    isLoggedIn() {
        return !!this.token && !!localStorage.getItem('user');
    }
    
    // 获取当前用户
    getCurrentUser() {
        if (!this.user && localStorage.getItem('user')) {
            try {
                this.user = JSON.parse(localStorage.getItem('user'));
            } catch (error) {
                console.error('解析用户信息失败:', error);
                this.logout();
            }
        }
        return this.user;
    }
    
    // 页面加载完成回调
    onPageLoad(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    }
}

// 创建全局实例
window.zyjc = new ZYJC();

// 导出常用方法到全局
window.showToast = (message, type, duration) => window.zyjc.showToast(message, type, duration);
window.formatDate = (date, format) => window.zyjc.formatDate(date, format);
window.navigateTo = (page, params) => window.zyjc.navigateTo(page, params);