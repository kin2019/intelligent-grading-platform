/**
 * 学生底部导航通用函数
 * 基于homework-submit.html的底部导航制作
 * 包含：首页、拍照批改、错题本、学习计划、我的 五个按钮
 * 
 * @author ZYJC Team  
 * @version 1.0.0
 */

(function(global) {
    'use strict';
    
    /**
     * 学生底部导航配置
     */
    const STUDENT_NAV_CONFIG = {
        items: [
            {
                id: 'home',
                icon: '🏠',
                text: '首页',
                url: '/frontend/student-home.html',
                pages: ['student-home.html']
            },
            {
                id: 'camera',
                icon: '📷', 
                text: '拍照批改',
                url: '/frontend/homework-submit.html',
                pages: ['homework-submit.html', 'homework-result.html']
            },
            {
                id: 'errorbook',
                icon: '📚',
                text: '错题本',
                url: '/frontend/error-book.html',
                pages: ['error-book.html', 'error-book-test.html', 'error-detail.html']
            },
            {
                id: 'study',
                icon: '📋',
                text: '学习计划',
                url: '/frontend/study-plan.html',
                pages: ['study-plan.html', 'study-plan-create.html', 'subject-detail.html']
            },
            {
                id: 'profile',
                icon: '👤',
                text: '我的',
                url: '/frontend/profile.html',
                pages: ['profile.html', 'vip-center.html', 'homework-list.html']
            }
        ]
    };

    /**
     * 学生底部导航类
     */
    function StudentBottomNav() {
        this.currentNav = null;
        this.currentPageId = null;
    }

    /**
     * 初始化学生底部导航
     * @param {Object} options - 初始化选项
     * @param {string} options.currentPage - 当前页面ID (可选，自动检测)
     * @param {HTMLElement} options.container - 容器元素 (可选，默认body)
     * @param {boolean} options.debug - 调试模式 (可选)
     */
    StudentBottomNav.prototype.init = function(options) {
        options = options || {};
        
        const currentPage = options.currentPage || this._getCurrentPageId();
        const container = options.container || document.body;
        const isDebug = options.debug || false;
        
        // 防止重复初始化
        if (this.currentNav && this.currentPageId === currentPage) {
            if (isDebug) {
                console.log('学生底部导航已存在，跳过重复初始化');
            }
            return true;
        }
        
        // 记录当前状态
        this.currentPageId = currentPage;
        
        // 立即清理现有导航并隐藏所有可能的导航元素，防止闪烁
        this.destroy();
        this._clearOldNavigations();
        this._hideAllNavigations();
        
        // 为body添加导航标识类
        document.body.classList.add('has-student-nav');
        
        // 创建新导航
        this.currentNav = this._createNavigation(currentPage);
        
        if (this.currentNav) {
            // 先隐藏导航，等待DOM就绪
            this.currentNav.style.opacity = '0';
            this.currentNav.style.transform = 'translateX(-50%) translateY(100%)';
            
            container.appendChild(this.currentNav);
            
            // 使用双重requestAnimationFrame确保DOM完全就绪后再显示
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    if (this.currentNav) {
                        this.currentNav.style.opacity = '1';
                        this.currentNav.style.transform = 'translateX(-50%) translateY(0)';
                        
                        if (isDebug) {
                            console.log('学生底部导航初始化成功:', {
                                currentPage: currentPage,
                                itemsCount: STUDENT_NAV_CONFIG.items.length
                            });
                        }
                    }
                });
            });
            
            return true;
        }
        
        return false;
    };

    /**
     * 创建导航DOM结构
     * @private
     */
    StudentBottomNav.prototype._createNavigation = function(currentPage) {
        // 创建导航容器
        const nav = document.createElement('div');
        nav.className = 'student-bottom-nav';
        nav.setAttribute('data-component', 'student-bottom-nav');
        
        // 创建导航项
        STUDENT_NAV_CONFIG.items.forEach(item => {
            const navItem = this._createNavItem(item, currentPage);
            nav.appendChild(navItem);
        });
        
        return nav;
    };

    /**
     * 创建单个导航项
     * @private
     */
    StudentBottomNav.prototype._createNavItem = function(item, currentPage) {
        const isActive = item.id === currentPage;
        
        // 创建导航项容器
        const navItem = document.createElement('div');
        navItem.className = 'student-nav-item' + (isActive ? ' active' : '');
        navItem.setAttribute('data-nav-item', item.id);
        navItem.setAttribute('data-nav-url', item.url);
        
        // 创建图标
        const icon = document.createElement('div');
        icon.className = 'student-nav-icon';
        icon.textContent = item.icon;
        
        // 创建文字
        const text = document.createElement('div');
        text.className = 'student-nav-text';
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
    StudentBottomNav.prototype._handleNavClick = function(event, item) {
        event.preventDefault();
        
        // 防止重复点击当前页面
        if (item.id === this.currentPageId) {
            console.log('已在当前页面:', item.text);
            return;
        }
        
        // 触发导航前事件
        const beforeNavigateEvent = new CustomEvent('beforeStudentNavigate', {
            detail: {
                from: this.currentPageId,
                to: item.id,
                fromText: this._getItemText(this.currentPageId),
                toText: item.text,
                url: item.url
            }
        });
        
        document.dispatchEvent(beforeNavigateEvent);
        
        // 如果事件被取消，不进行导航
        if (beforeNavigateEvent.defaultPrevented) {
            return;
        }
        
        // 执行页面跳转
        try {
            window.location.href = item.url;
        } catch (error) {
            console.error('导航跳转失败:', error);
        }
        
        // 触发导航后事件
        setTimeout(() => {
            const afterNavigateEvent = new CustomEvent('afterStudentNavigate', {
                detail: {
                    to: item.id,
                    toText: item.text,
                    url: item.url
                }
            });
            document.dispatchEvent(afterNavigateEvent);
        }, 100);
    };

    /**
     * 根据当前页面URL自动检测页面ID
     * @private
     */
    StudentBottomNav.prototype._getCurrentPageId = function() {
        const currentPath = window.location.pathname;
        const currentFile = currentPath.split('/').pop();
        
        // 遍历配置寻找匹配的页面
        for (const item of STUDENT_NAV_CONFIG.items) {
            if (item.pages.includes(currentFile)) {
                return item.id;
            }
        }
        
        // 默认返回首页
        return 'home';
    };

    /**
     * 根据ID获取导航项文字
     * @private
     */
    StudentBottomNav.prototype._getItemText = function(itemId) {
        const item = STUDENT_NAV_CONFIG.items.find(item => item.id === itemId);
        return item ? item.text : '未知页面';
    };

    /**
     * 更新当前选中状态
     * @param {string} pageId - 页面ID
     */
    StudentBottomNav.prototype.setActivePage = function(pageId) {
        if (!this.currentNav) {
            return;
        }
        
        // 移除所有active状态
        const navItems = this.currentNav.querySelectorAll('.student-nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // 添加新的active状态
        const activeItem = this.currentNav.querySelector(`[data-nav-item="${pageId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
            this.currentPageId = pageId;
        }
    };

    /**
     * 清理旧版导航组件
     * @private
     */
    StudentBottomNav.prototype._clearOldNavigations = function() {
        // 清理可能存在的旧版导航
        const oldNavs = [
            '.global-bottom-nav',
            '.theme-bottom-nav', 
            '.bottom-nav:not(.student-bottom-nav)',
            '[data-nav-component="bottom-navigation"]'
        ];
        
        oldNavs.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (element && element.parentNode) {
                    element.parentNode.removeChild(element);
                }
            });
        });
    };

    /**
     * 立即隐藏所有可能存在的导航元素，防止闪烁
     * @private
     */
    StudentBottomNav.prototype._hideAllNavigations = function() {
        const allNavSelectors = [
            '.global-bottom-nav',
            '.theme-bottom-nav',
            '.bottom-nav:not(.student-bottom-nav)',
            '[data-nav-component="bottom-navigation"]:not(.student-bottom-nav)'
        ];
        
        allNavSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (element) {
                    element.style.display = 'none';
                    element.style.opacity = '0';
                    element.style.visibility = 'hidden';
                }
            });
        });
    };

    /**
     * 销毁导航
     */
    StudentBottomNav.prototype.destroy = function() {
        if (this.currentNav && this.currentNav.parentNode) {
            this.currentNav.parentNode.removeChild(this.currentNav);
        }
        
        // 移除body的导航标识类
        document.body.classList.remove('has-student-nav');
        
        this.currentNav = null;
        this.currentPageId = null;
    };

    /**
     * 刷新导航
     * @param {string} newPageId - 新的页面ID (可选)
     */
    StudentBottomNav.prototype.refresh = function(newPageId) {
        const pageId = newPageId || this._getCurrentPageId();
        this.destroy();
        this.init({ currentPage: pageId });
    };

    // 创建全局实例
    const studentBottomNav = new StudentBottomNav();

    // 暴露到全局
    global.StudentBottomNav = {
        /**
         * 初始化学生底部导航 (简化接口)
         * @param {Object|string} options - 初始化选项或页面ID
         */
        init: function(options) {
            if (typeof options === 'string') {
                options = { currentPage: options };
            }
            return studentBottomNav.init(options);
        },
        
        /**
         * 设置当前页面
         * @param {string} pageId - 页面ID
         */
        setActivePage: function(pageId) {
            return studentBottomNav.setActivePage(pageId);
        },
        
        /**
         * 刷新导航
         * @param {string} newPageId - 新的页面ID (可选)
         */
        refresh: function(newPageId) {
            return studentBottomNav.refresh(newPageId);
        },
        
        /**
         * 销毁导航
         */
        destroy: function() {
            return studentBottomNav.destroy();
        },
        
        /**
         * 获取当前页面ID
         */
        getCurrentPageId: function() {
            return studentBottomNav.currentPageId;
        },
        
        /**
         * 获取导航配置
         */
        getConfig: function() {
            return STUDENT_NAV_CONFIG;
        }
    };

    // 自动初始化 (可选)
    document.addEventListener('DOMContentLoaded', function() {
        // 检查是否需要自动初始化
        if (document.body.hasAttribute('data-auto-student-nav')) {
            StudentBottomNav.init();
        }
    });

})(window);