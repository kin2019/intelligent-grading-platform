// 全局底部导航 - 简化版本
(function() {
    'use strict';
    
    // 获取当前页面名称
    function getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop();
        return filename.replace('.html', '');
    }
    
    // 创建底部导航HTML
    function createBottomNav() {
        const currentPage = getCurrentPage();
        
        // 登录页面不显示导航
        if (currentPage === 'login') {
            return;
        }
        
        const navHTML = `
            <div class="global-bottom-nav">
                <div class="global-nav-item ${isActive('student-home', currentPage) ? 'active' : ''}" onclick="navigateTo('/frontend/student-home.html')">
                    <div class="global-nav-icon">🏠</div>
                    <div class="global-nav-text">首页</div>
                </div>
                <div class="global-nav-item ${isActive('homework-submit', currentPage) ? 'active' : ''}" onclick="navigateTo('/frontend/homework-submit.html')">
                    <div class="global-nav-icon">📷</div>
                    <div class="global-nav-text">拍照批改</div>
                </div>
                <div class="global-nav-item ${isActive('error-book', currentPage) ? 'active' : ''}" onclick="navigateTo('/frontend/error-book.html')">
                    <div class="global-nav-icon">📚</div>
                    <div class="global-nav-text">错题本</div>
                </div>
                <div class="global-nav-item ${isActive('study-plan', currentPage) ? 'active' : ''}" onclick="navigateTo('/frontend/study-plan.html')">
                    <div class="global-nav-icon">📋</div>
                    <div class="global-nav-text">学习计划</div>
                </div>
                <div class="global-nav-item ${isActive('profile', currentPage) ? 'active' : ''}" onclick="navigateTo('/frontend/profile.html')">
                    <div class="global-nav-icon">👤</div>
                    <div class="global-nav-text">我的</div>
                </div>
            </div>
        `;
        
        // 移除现有导航
        const existingNav = document.querySelector('.global-bottom-nav');
        if (existingNav) {
            existingNav.remove();
        }
        
        const oldNav = document.querySelector('.bottom-nav');
        if (oldNav) {
            oldNav.remove();
        }
        
        // 添加新导航
        document.body.insertAdjacentHTML('beforeend', navHTML);
        
        // 调整页面底部间距
        adjustPagePadding();
    }
    
    // 判断导航项是否应该激活
    function isActive(navItem, currentPage) {
        if (currentPage === navItem) {
            return true;
        }
        
        // 页面映射关系
        const pageMapping = {
            'parent-home': 'profile',
            'homework-result': 'homework-submit',
            'homework-result-fixed': 'homework-submit',
            'subject-detail': 'study-plan',
            'study-plan-create': 'study-plan',
            'error-detail': 'error-book',
            'error-detail-fixed': 'error-book',
            'similar-practice': 'error-book',
            'learning-reports': 'profile',
            'learning-progress': 'profile',
            'error-analysis': 'error-book',
            'manage-children': 'profile',
            'child-detail': 'profile',
            'vip-center': 'profile',
            'homework-list': 'homework-submit'
        };
        
        return pageMapping[currentPage] === navItem;
    }
    
    // 页面跳转
    function navigateTo(url) {
        window.location.href = url;
    }
    
    // 调整页面底部间距
    function adjustPagePadding() {
        // 为页面内容添加底部间距
        const pageContent = document.querySelector('.page-content');
        if (pageContent) {
            pageContent.style.paddingBottom = '80px';
        }
        
        const container = document.querySelector('.container');
        if (container && !pageContent) {
            container.style.paddingBottom = '80px';
        }
        
        const themeContainer = document.querySelector('.theme-container');
        if (themeContainer) {
            themeContainer.style.paddingBottom = '80px';
        }
    }
    
    // 移除返回按钮
    function removeBackButtons() {
        const backButtons = document.querySelectorAll('.back-btn');
        backButtons.forEach(btn => {
            btn.style.display = 'none';
        });
    }
    
    // 初始化
    function init() {
        createBottomNav();
        removeBackButtons();
    }
    
    // 页面加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 暴露全局函数
    window.navigateTo = navigateTo;
    
})();