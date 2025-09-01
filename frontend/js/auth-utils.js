/**
 * 用户身份认证工具类
 * 用于统一管理学生、家长、老师三种身份的token和权限
 */

// 测试token定义
const TEST_TOKENS = {
    student: 'test-token-123',  // 后端支持的学生测试token
    parent: 'test-token-parent',   // 后端支持的家长测试token
    teacher: 'test-token-123'   // 使用相同的测试token
};

// API基础路径
const API_BASES = {
    student: 'http://localhost:8000/api/v1/student',
    parent: 'http://localhost:8000/api/v1/parent', 
    teacher: 'http://localhost:8000/api/v1/teacher',
    common: 'http://localhost:8000/api/v1'
};

// 特殊API路径映射（将前端请求映射到正确的后端路径）
const API_PATH_MAPPINGS = {
    student: {
        'homework/list': '../homework/list',        // 映射到 /api/v1/homework/list
        'homework/submit': '../homework/submit',      // 映射到 /api/v1/homework/submit
        'homework/result': '../homework/result',      // 映射到 /api/v1/homework/result
        'auth/me': '../auth/me',                     // 映射到 /api/v1/auth/me
        'user/profile': '../user/profile',           // 映射到 /api/v1/user/profile
        'user/upload-avatar': '../user/upload-avatar', // 映射到 /api/v1/user/upload-avatar
        'user/set-default-avatar': '../user/set-default-avatar', // 映射到 /api/v1/user/set-default-avatar
        'error-book': 'error-book',                   // 保持 /api/v1/student/error-book
        'similar-practice': 'similar-practice',       // 保持 /api/v1/student/similar-practice 
        'dashboard': 'dashboard'                      // 保持 /api/v1/student/dashboard
    },
    parent: {
        'children': 'children',
        'dashboard': 'dashboard',
        'auth/me': '../auth/me',                     // 映射到 /api/v1/auth/me
        'user/profile': '../user/profile',           // 映射到 /api/v1/user/profile
        'user/upload-avatar': '../user/upload-avatar', // 映射到 /api/v1/user/upload-avatar
        'user/set-default-avatar': '../user/set-default-avatar', // 映射到 /api/v1/user/set-default-avatar
        'bind/': '../bind/'                           // 映射到 /api/v1/bind/
    },
    teacher: {
        'dashboard': 'dashboard',
        'auth/me': '../auth/me',                     // 映射到 /api/v1/auth/me
        'user/profile': '../user/profile',           // 映射到 /api/v1/user/profile
        'user/upload-avatar': '../user/upload-avatar', // 映射到 /api/v1/user/upload-avatar
        'user/set-default-avatar': '../user/set-default-avatar' // 映射到 /api/v1/user/set-default-avatar
    }
};

/**
 * 获取当前用户角色
 */
function getCurrentUserRole() {
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
    
    return role;
}

/**
 * 获取当前用户信息
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * 设置用户角色和对应token
 */
function setUserRole(role) {
    if (!['student', 'parent', 'teacher'].includes(role)) {
        console.error('无效的用户角色:', role);
        return false;
    }
    
    localStorage.setItem('userRole', role);
    localStorage.setItem('token', TEST_TOKENS[role]);
    console.log(`已设置用户角色为: ${role}`);
    return true;
}

/**
 * 获取当前用户的token
 */
function getCurrentToken() {
    const role = getCurrentUserRole();
    let token = localStorage.getItem('token');
    
    // 如果没有token或者token不匹配当前角色，使用测试token
    if (!token || (role && token !== TEST_TOKENS[role])) {
        if (role) {
            token = TEST_TOKENS[role];
            localStorage.setItem('token', token);
            console.log(`使用${role}测试token`);
        }
    }
    
    return token;
}

/**
 * 获取API基础路径
 */
function getAPIBase(endpoint = '') {
    const role = getCurrentUserRole();
    
    // 处理特殊路径映射
    if (role && endpoint && API_PATH_MAPPINGS[role]) {
        const mappedPath = API_PATH_MAPPINGS[role][endpoint];
        if (mappedPath) {
            endpoint = mappedPath;
        }
    }
    
    const base = role ? API_BASES[role] : API_BASES.common;
    return endpoint ? `${base}/${endpoint}` : base;
}

/**
 * 统一的API请求方法
 */
async function apiRequest(endpoint, options = {}) {
    const token = getCurrentToken();
    const url = getAPIBase(endpoint);
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        }
    };
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        console.log(`[API Request] ${finalOptions.method || 'GET'} ${url}`);
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API请求失败: ${url}`, error);
        throw error;
    }
}

/**
 * 检查页面权限
 */
function checkPagePermission(requiredRole) {
    const currentRole = getCurrentUserRole();
    
    if (!currentRole) {
        // 没有角色时，重定向到登录页
        console.log('未设置用户角色，重定向到登录页');
        window.location.href = '/frontend/login.html';
        return false;
    }
    
    if (requiredRole && currentRole !== requiredRole) {
        console.error(`页面权限不足: 需要${requiredRole}角色，当前为${currentRole}`);
        alert(`您没有访问此页面的权限。当前身份: ${getRoleDisplayName(currentRole)}`);
        // 重定向到对应角色的首页
        window.location.href = getRoleHomePage(currentRole);
        return false;
    }
    
    return true;
}

/**
 * 获取角色显示名称
 */
function getRoleDisplayName(role) {
    const names = {
        student: '学生',
        parent: '家长',
        teacher: '教师'
    };
    return names[role] || role;
}

/**
 * 获取角色首页路径
 */
function getRoleHomePage(role) {
    const pages = {
        student: '/frontend/student-home.html',
        parent: '/frontend/parent-home.html',
        teacher: '/frontend/teacher-home.html'
    };
    return pages[role] || '/frontend/login.html';
}

/**
 * 用户登出
 */
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    console.log('用户已登出');
    window.location.href = '/frontend/login.html';
}

/**
 * 页面初始化时自动检查权限
 */
function initPageAuth(requiredRole = null) {
    console.log('=== 页面权限检查 ===');
    console.log('当前页面:', window.location.pathname);
    console.log('需要角色:', requiredRole || '任何角色');
    console.log('当前角色:', getCurrentUserRole() || '未设置');
    
    return checkPagePermission(requiredRole);
}

// 导出所有方法供页面使用
window.AuthUtils = {
    getCurrentUserRole,
    getCurrentUser,
    setUserRole,
    getCurrentToken,
    getAPIBase,
    apiRequest,
    checkPagePermission,
    getRoleDisplayName,
    getRoleHomePage,
    logout,
    initPageAuth,
    TEST_TOKENS
};

console.log('认证工具类已加载');