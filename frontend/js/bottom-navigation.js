/**
 * 底部导航统一组件
 * 支持学生和家长两种角色的导航渲染
 * 
 * @author ZYJC Team
 * @version 1.0.0
 */

(function(global) {
    'use strict';
    
    /**
     * 底部导航组件构造函数
     */
    function BottomNavigation() {
        this.currentNav = null;
        this.currentRole = null;
        this.currentPageId = null;
        this.isDebugMode = false;
    }

    /**
     * 渲染底部导航
     * @param {Object} options - 渲染选项
     * @param {string} options.role - 用户角色 ('student' | 'parent')
     * @param {string} options.currentPage - 当前页面ID (可选，自动检测)
     * @param {HTMLElement} options.container - 容器元素 (可选，默认body)
     * @param {boolean} options.debug - 调试模式 (可选)
     */
    BottomNavigation.prototype.render = function(options) {
        options = options || {};
        
        // 参数处理
        const role = options.role || getCurrentUserRole();
        const currentPage = options.currentPage || getCurrentPageId();
        const container = options.container || document.body;
        this.isDebugMode = options.debug || false;
        
        // 验证角色
        if (!role || !NAVIGATION_CONFIG[role]) {
            console.error('BottomNavigation: 无效的用户角色:', role);
            return false;
        }
        
        // 记录当前状态
        this.currentRole = role;
        this.currentPageId = currentPage;
        
        // 清理现有导航
        this.destroy();
        
        // 创建新导航
        this.currentNav = this._createNavigation(role, currentPage);
        
        // 添加到容器
        if (this.currentNav) {
            container.appendChild(this.currentNav);
            
            if (this.isDebugMode) {
                console.log('BottomNavigation: 导航渲染成功', {
                    role: role,
                    currentPage: currentPage,
                    items: NAVIGATION_CONFIG[role].items.length
                });
                document.body.classList.add('bottom-nav-debug');
            }
            
            return true;
        }
        
        return false;
    };

    /**
     * 创建导航DOM结构
     * @private
     */
    BottomNavigation.prototype._createNavigation = function(role, currentPage) {
        const config = NAVIGATION_CONFIG[role];
        
        // 创建导航容器
        const nav = document.createElement('div');
        nav.className = config.containerClass;
        nav.setAttribute('data-nav-component', 'bottom-navigation');
        nav.setAttribute('data-nav-role', role);
        
        // 创建导航项
        config.items.forEach(item => {
            const navItem = this._createNavItem(item, config, currentPage);
            nav.appendChild(navItem);
        });
        
        return nav;
    };

    /**
     * 创建单个导航项
     * @private
     */
    BottomNavigation.prototype._createNavItem = function(item, config, currentPage) {
        const isActive = item.id === currentPage;
        
        // 创建导航项容器
        const navItem = document.createElement('div');
        navItem.className = config.itemClass + (isActive ? ' active' : '');
        navItem.setAttribute('data-nav-item', item.id);
        navItem.setAttribute('data-nav-url', item.url);
        
        // 创建图标
        const icon = document.createElement('div');
        icon.className = config.iconClass;
        icon.textContent = item.icon;
        
        // 创建文字
        const text = document.createElement('div');
        text.className = config.textClass;
        text.textContent = item.text;
        
        // 组装导航项
        navItem.appendChild(icon);
        navItem.appendChild(text);
        
        // 添加点击事件
        navItem.addEventListener('click', (e) => {
            this._handleNavClick(e, item);
        });
        
        return navItem;
    };

    /**
     * 处理导航项点击事件
     * @private
     */
    BottomNavigation.prototype._handleNavClick = function(event, item) {
        event.preventDefault();
        
        // 防止重复点击当前页面
        if (item.id === this.currentPageId) {
            if (this.isDebugMode) {
                console.log('BottomNavigation: 点击当前页面，忽略跳转');
            }
            return;
        }
        
        // 触发导航前事件
        const beforeNavigateEvent = new CustomEvent('beforeNavigate', {
            detail: {
                from: this.currentPageId,
                to: item.id,
                url: item.url,
                item: item
            },
            cancelable: true
        });
        
        document.dispatchEvent(beforeNavigateEvent);
        
        // 如果事件被阻止，则不进行跳转
        if (beforeNavigateEvent.defaultPrevented) {
            if (this.isDebugMode) {
                console.log('BottomNavigation: 导航被阻止');
            }
            return;
        }
        
        if (this.isDebugMode) {
            console.log('BottomNavigation: 导航到', item);
        }
        
        // 执行页面跳转
        this._navigateTo(item.url);
        
        // 触发导航后事件
        const afterNavigateEvent = new CustomEvent('afterNavigate', {
            detail: {
                from: this.currentPageId,
                to: item.id,
                url: item.url,
                item: item
            }
        });
        
        document.dispatchEvent(afterNavigateEvent);
    };

    /**
     * 执行页面跳转
     * @private
     */
    BottomNavigation.prototype._navigateTo = function(url) {
        try {
            window.location.href = url;
        } catch (error) {
            console.error('BottomNavigation: 页面跳转失败', error);
        }
    };

    /**
     * 更新当前激活的导航项
     */
    BottomNavigation.prototype.updateActive = function(pageId) {
        if (!this.currentNav) {
            console.warn('BottomNavigation: 导航未初始化');
            return;
        }
        
        const items = this.currentNav.querySelectorAll('[data-nav-item]');
        
        items.forEach(item => {
            const itemId = item.getAttribute('data-nav-item');
            if (itemId === pageId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        this.currentPageId = pageId;
    };

    /**
     * 销毁当前导航
     */
    BottomNavigation.prototype.destroy = function() {
        // 移除现有的导航元素
        const existingNavs = document.querySelectorAll('[data-nav-component="bottom-navigation"]');
        existingNavs.forEach(nav => {
            nav.remove();
        });
        
        // 清理旧版导航
        const oldNavs = document.querySelectorAll('.global-bottom-nav:not([data-nav-component]), .theme-bottom-nav:not([data-nav-component])');
        oldNavs.forEach(nav => {
            nav.remove();
        });
        
        // 重置状态
        this.currentNav = null;
        
        if (this.isDebugMode) {
            console.log('BottomNavigation: 旧导航已清理');
            document.body.classList.remove('bottom-nav-debug');
        }
    };

    /**
     * 重新渲染导航（角色变更时使用）
     */
    BottomNavigation.prototype.refresh = function(newRole) {
        const role = newRole || getCurrentUserRole();
        const currentPage = getCurrentPageId();
        
        if (this.isDebugMode) {
            console.log('BottomNavigation: 刷新导航', { 
                oldRole: this.currentRole, 
                newRole: role 
            });
        }
        
        this.render({
            role: role,
            currentPage: currentPage,
            debug: this.isDebugMode
        });
    };

    /**
     * 获取当前导航状态
     */
    BottomNavigation.prototype.getState = function() {
        return {
            role: this.currentRole,
            currentPage: this.currentPageId,
            isActive: !!this.currentNav,
            debug: this.isDebugMode
        };
    };

    /**
     * 设置调试模式
     */
    BottomNavigation.prototype.setDebugMode = function(enabled) {
        this.isDebugMode = !!enabled;
        
        if (enabled) {
            document.body.classList.add('bottom-nav-debug');
        } else {
            document.body.classList.remove('bottom-nav-debug');
        }
    };

    // 创建全局实例
    const bottomNavigation = new BottomNavigation();

    /**
     * 简化的全局API
     */
    const BottomNavigationAPI = {
        // 基础方法
        render: function(options) {
            return bottomNavigation.render(options);
        },
        
        destroy: function() {
            return bottomNavigation.destroy();
        },
        
        refresh: function(role) {
            return bottomNavigation.refresh(role);
        },
        
        updateActive: function(pageId) {
            return bottomNavigation.updateActive(pageId);
        },
        
        // 工具方法
        getState: function() {
            return bottomNavigation.getState();
        },
        
        setDebugMode: function(enabled) {
            return bottomNavigation.setDebugMode(enabled);
        },
        
        // 自动初始化方法
        init: function(options) {
            options = options || {};
            const role = options.role || getCurrentUserRole();
            const currentPage = options.currentPage || getCurrentPageId();
            
            return this.render({
                role: role,
                currentPage: currentPage,
                debug: options.debug || false
            });
        }
    };

    // 页面加载完成后自动初始化
    function autoInit() {
        // 检查是否已经有导航组件
        if (document.querySelector('[data-nav-component="bottom-navigation"]')) {
            return;
        }
        
        // 检查必要的依赖
        if (typeof NAVIGATION_CONFIG === 'undefined') {
            console.error('BottomNavigation: navigation-config.js 未加载');
            return;
        }
        
        if (typeof getCurrentUserRole !== 'function') {
            console.error('BottomNavigation: getCurrentUserRole 函数不可用');
            return;
        }
        
        // 自动初始化
        BottomNavigationAPI.init();
    }

    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoInit);
    } else {
        // 如果DOM已经加载完成，稍后执行
        setTimeout(autoInit, 100);
    }

    // 监听角色变更
    window.addEventListener('storage', function(e) {
        if (e.key === 'role' && e.newValue !== e.oldValue) {
            console.log('BottomNavigation: 检测到角色变更，刷新导航');
            BottomNavigationAPI.refresh(e.newValue);
        }
    });

    // 导出API
    if (typeof module !== 'undefined' && module.exports) {
        // Node.js环境
        module.exports = BottomNavigationAPI;
    } else {
        // 浏览器环境
        global.BottomNavigation = BottomNavigationAPI;
    }

})(typeof window !== 'undefined' ? window : this);