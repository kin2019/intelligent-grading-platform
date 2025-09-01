/**
 * 底部导航配置文件
 * 支持学生和家长两种角色的导航配置
 */

const NAVIGATION_CONFIG = {
    // 学生端导航配置
    student: {
        cssPrefix: 'global',
        containerClass: 'global-bottom-nav',
        itemClass: 'global-nav-item',
        iconClass: 'global-nav-icon',
        textClass: 'global-nav-text',
        items: [
            {
                id: 'home',
                icon: '🏠',
                text: '首页',
                url: '/frontend/student-home.html',
                pages: ['student-home.html'] // 对应的页面文件名
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
    },

    // 家长端导航配置
    parent: {
        cssPrefix: 'theme',
        containerClass: 'theme-bottom-nav',
        itemClass: 'theme-nav-item',
        iconClass: 'theme-nav-icon',
        textClass: 'theme-nav-text',
        items: [
            {
                id: 'home',
                icon: '🏠',
                text: '首页',
                url: '/frontend/parent-home.html',
                pages: ['parent-home.html']
            },
            {
                id: 'report',
                icon: '📊',
                text: '学习报告',
                url: '/frontend/learning-reports.html',
                pages: ['learning-reports.html']
            },
            {
                id: 'error-analysis',
                icon: '🔍',
                text: '错题分析',
                url: '/frontend/error-analysis.html',
                pages: ['error-analysis.html']
            },
            {
                id: 'progress',
                icon: '📈',
                text: '学习进度',
                url: '/frontend/learning-progress.html',
                pages: ['learning-progress.html']
            },
            {
                id: 'manage',
                icon: '👶',
                text: '孩子管理',
                url: '/frontend/manage-children.html',
                pages: ['manage-children.html', 'parent-bind.html', 'child-detail.html']
            },
            {
                id: 'profile',
                icon: '👤',
                text: '我的',
                url: '/frontend/profile.html',
                pages: ['profile.html', 'homework-list.html']
            }
        ]
    }
};

/**
 * 根据当前页面URL获取页面ID
 * @param {string} url - 当前页面URL或路径
 * @returns {string} 页面ID
 */
function getCurrentPageId(url) {
    if (!url) {
        url = window.location.pathname;
    }
    
    // 提取文件名
    const fileName = url.split('/').pop() || 'student-home.html';
    
    // 遍历所有角色的导航配置，找到匹配的页面
    for (const role in NAVIGATION_CONFIG) {
        const config = NAVIGATION_CONFIG[role];
        for (const item of config.items) {
            if (item.pages.includes(fileName)) {
                return item.id;
            }
        }
    }
    
    // 默认返回首页
    return 'home';
}

/**
 * 获取当前用户角色
 * @returns {string} 'student' 或 'parent'
 */
function getCurrentUserRole() {
    // 与auth-utils.js保持一致，使用userRole键
    let role = localStorage.getItem('userRole');
    
    // 兼容性处理：如果没有找到 'userRole'，检查旧的 'role' 键
    if (!role) {
        role = localStorage.getItem('role');
        if (role) {
            console.log('检测到旧的role格式，正在迁移到新格式');
            // 迁移到新格式
            localStorage.setItem('userRole', role);
            localStorage.removeItem('role');
        }
    }
    
    // 如果仍然没有角色，尝试从token解析
    if (!role) {
        try {
            const token = localStorage.getItem('token');
            if (token) {
                const payload = JSON.parse(atob(token.split('.')[1]));
                const userId = payload.sub;
                
                // 根据用户ID判断角色：ID=1是学生，ID=2是家长
                if (userId === '2') {
                    role = 'parent';
                } else {
                    role = 'student';
                }
                
                // 更新localStorage
                localStorage.setItem('userRole', role);
                return role;
            }
        } catch (error) {
            console.warn('解析Token失败，使用默认学生角色:', error);
        }
    }
    
    // 如果还是没有角色，默认返回学生角色
    if (!role) {
        role = 'student';
        localStorage.setItem('userRole', role);
    }
    
    return role;
}

// 导出配置和工具函数
if (typeof module !== 'undefined' && module.exports) {
    // Node.js环境
    module.exports = {
        NAVIGATION_CONFIG,
        getCurrentPageId,
        getCurrentUserRole
    };
} else {
    // 浏览器环境 - 将函数和配置挂载到全局对象
    window.NAVIGATION_CONFIG = NAVIGATION_CONFIG;
    window.getCurrentPageId = getCurrentPageId;
    window.getCurrentUserRole = getCurrentUserRole;
}