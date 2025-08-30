/**
 * 错误处理和用户体验优化工具
 * 步骤8.3：错误处理和用户体验实现
 * - 生成失败重试机制
 * - 用户友好的错误提示
 * - 加载进度显示
 */

class ErrorHandler {
    constructor() {
        this.retryConfig = {
            maxRetries: 3,
            retryDelay: 2000, // 2秒
            exponentialBackoff: true,
            retryableErrors: [
                'Network Error',
                'TimeoutError',
                'HTTP 500',
                'HTTP 502',
                'HTTP 503',
                'HTTP 504'
            ]
        };

        this.loadingStates = new Map();
        this.errorQueue = [];
        this.notificationQueue = [];
        
        // 初始化全局错误处理
        this.initGlobalErrorHandling();
        this.initProgressSystem();
    }

    /**
     * 1. 生成失败重试机制实现
     */

    // 智能重试API请求
    async retryApiRequest(requestFn, options = {}) {
        const config = { ...this.retryConfig, ...options };
        let lastError = null;
        
        for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
            try {
                // 显示重试进度
                if (attempt > 0) {
                    this.showRetryProgress(attempt, config.maxRetries);
                }

                console.log(`🔄 API请求尝试 ${attempt + 1}/${config.maxRetries + 1}`);
                const result = await requestFn();
                
                // 请求成功，清除重试进度
                this.hideRetryProgress();
                return result;
                
            } catch (error) {
                lastError = error;
                console.error(`❌ API请求失败 (尝试 ${attempt + 1}):`, error);
                
                // 检查是否为可重试的错误
                if (!this.isRetryableError(error) || attempt >= config.maxRetries) {
                    this.hideRetryProgress();
                    break;
                }
                
                // 计算延迟时间
                const delay = config.exponentialBackoff 
                    ? config.retryDelay * Math.pow(2, attempt)
                    : config.retryDelay;
                
                console.log(`⏳ ${delay}ms 后重试...`);
                await this.delay(delay);
            }
        }
        
        // 所有重试都失败了
        this.hideRetryProgress();
        throw new EnhancedError(lastError, {
            attempts: config.maxRetries + 1,
            type: 'RETRY_EXHAUSTED',
            originalError: lastError
        });
    }

    // 练习生成重试包装器
    async retryExerciseGeneration(generationConfig) {
        return this.retryApiRequest(async () => {
            const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';
            const authToken = localStorage.getItem('authToken');
            
            const response = await fetch(`${API_BASE}/exercise/generate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(generationConfig)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP ${response.status}: ${errorData.message || response.statusText}`);
            }

            return await response.json();
        }, {
            maxRetries: 2, // 题目生成最多重试2次
            retryDelay: 3000 // 3秒延迟
        });
    }

    // 检查错误是否可重试
    isRetryableError(error) {
        const errorMessage = error.message || error.toString();
        return this.retryConfig.retryableErrors.some(retryableError => 
            errorMessage.includes(retryableError)
        );
    }

    // 显示重试进度
    showRetryProgress(attempt, maxAttempts) {
        this.hideRetryProgress(); // 先清除之前的
        
        const progressEl = document.createElement('div');
        progressEl.id = 'retry-progress';
        progressEl.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 20px rgba(251, 191, 36, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideDown 0.3s ease;
        `;

        progressEl.innerHTML = `
            <div class="retry-spinner" style="
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top: 2px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
            <span>重试中... (${attempt}/${maxAttempts})</span>
        `;

        document.body.appendChild(progressEl);

        // 添加动画样式
        if (!document.getElementById('retry-animations')) {
            const style = document.createElement('style');
            style.id = 'retry-animations';
            style.textContent = `
                @keyframes slideDown {
                    from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                    to { transform: translateX(-50%) translateY(0); opacity: 1; }
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // 隐藏重试进度
    hideRetryProgress() {
        const progressEl = document.getElementById('retry-progress');
        if (progressEl) {
            progressEl.remove();
        }
    }

    /**
     * 2. 用户友好的错误提示
     */

    // 显示用户友好的错误消息
    showFriendlyError(error, context = '') {
        const friendlyMessage = this.translateError(error, context);
        const errorId = this.generateErrorId();

        this.errorQueue.push({
            id: errorId,
            error,
            message: friendlyMessage,
            context,
            timestamp: new Date(),
            resolved: false
        });

        this.displayErrorNotification(friendlyMessage, error, errorId);
        
        // 记录错误到控制台（开发用）
        console.error('🚨 用户友好错误提示:', {
            errorId,
            originalError: error,
            friendlyMessage,
            context
        });

        return errorId;
    }

    // 将技术错误转换为用户友好的消息
    translateError(error, context = '') {
        const errorMessage = error.message || error.toString();
        const errorType = error.name || 'Error';

        // 网络相关错误
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Network Error')) {
            return {
                title: '网络连接问题',
                message: '请检查您的网络连接，然后重试',
                actions: ['重试', '检查网络'],
                type: 'network'
            };
        }

        // HTTP错误状态码
        if (errorMessage.includes('HTTP 500')) {
            return {
                title: '服务器暂时不可用',
                message: '服务器正在维护中，请稍后再试',
                actions: ['稍后重试', '联系客服'],
                type: 'server'
            };
        }

        if (errorMessage.includes('HTTP 401') || errorMessage.includes('Unauthorized')) {
            return {
                title: '登录已过期',
                message: '请重新登录后继续使用',
                actions: ['重新登录'],
                type: 'auth'
            };
        }

        if (errorMessage.includes('HTTP 403') || errorMessage.includes('Forbidden')) {
            return {
                title: '权限不足',
                message: '您没有执行此操作的权限',
                actions: ['联系管理员'],
                type: 'permission'
            };
        }

        if (errorMessage.includes('HTTP 404')) {
            return {
                title: '内容不存在',
                message: context ? `找不到${context}，可能已被删除` : '请求的内容不存在',
                actions: ['返回首页', '刷新页面'],
                type: 'notfound'
            };
        }

        if (errorMessage.includes('TimeoutError') || errorMessage.includes('timeout')) {
            return {
                title: '请求超时',
                message: '操作时间过长，请检查网络后重试',
                actions: ['重试', '检查网络'],
                type: 'timeout'
            };
        }

        // 练习生成相关错误
        if (context.includes('exercise') || context.includes('generation')) {
            if (errorMessage.includes('配置') || errorMessage.includes('config')) {
                return {
                    title: '配置参数错误',
                    message: '请检查题目配置参数是否完整',
                    actions: ['检查配置', '重新设置'],
                    type: 'config'
                };
            }

            return {
                title: '题目生成失败',
                message: '无法生成题目，请调整配置后重试',
                actions: ['调整配置', '重试', '联系客服'],
                type: 'generation'
            };
        }

        // 文件导出相关错误
        if (context.includes('export') || context.includes('download')) {
            return {
                title: '文件导出失败',
                message: '无法导出文件，请稍后重试',
                actions: ['重试导出', '选择其他格式'],
                type: 'export'
            };
        }

        // 默认错误消息
        return {
            title: '操作失败',
            message: '遇到了一些问题，请稍后重试',
            actions: ['重试', '刷新页面', '联系客服'],
            type: 'general'
        };
    }

    // 显示错误通知UI
    displayErrorNotification(friendlyMessage, originalError, errorId) {
        const notification = document.createElement('div');
        notification.id = `error-notification-${errorId}`;
        notification.className = 'error-notification';
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            border-left: 4px solid #ef4444;
            z-index: 10001;
            animation: slideInRight 0.3s ease;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        `;

        const typeColors = {
            network: '#3b82f6',
            server: '#ef4444', 
            auth: '#f59e0b',
            permission: '#8b5cf6',
            notfound: '#6b7280',
            timeout: '#10b981',
            config: '#f97316',
            generation: '#ec4899',
            export: '#14b8a6',
            general: '#6b7280'
        };

        const typeIcons = {
            network: '🌐',
            server: '⚠️',
            auth: '🔐',
            permission: '🚫',
            notfound: '❓',
            timeout: '⏱️',
            config: '⚙️',
            generation: '📝',
            export: '📁',
            general: '❗'
        };

        const borderColor = typeColors[friendlyMessage.type] || typeColors.general;
        notification.style.borderLeftColor = borderColor;

        notification.innerHTML = `
            <div style="padding: 16px;">
                <div style="display: flex; align-items: start; gap: 12px;">
                    <div style="font-size: 24px; flex-shrink: 0;">${typeIcons[friendlyMessage.type] || typeIcons.general}</div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-weight: 600; color: #111827; margin-bottom: 4px;">
                            ${friendlyMessage.title}
                        </div>
                        <div style="color: #6b7280; font-size: 14px; line-height: 1.4; margin-bottom: 12px;">
                            ${friendlyMessage.message}
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            ${friendlyMessage.actions.map((action, index) => `
                                <button onclick="handleErrorAction('${errorId}', '${action}', ${index})" 
                                        style="
                                            padding: 6px 12px;
                                            font-size: 12px;
                                            border: 1px solid ${borderColor};
                                            background: ${index === 0 ? borderColor : 'white'};
                                            color: ${index === 0 ? 'white' : borderColor};
                                            border-radius: 6px;
                                            cursor: pointer;
                                            transition: all 0.2s ease;
                                        "
                                        onmouseover="this.style.background='${borderColor}'; this.style.color='white';"
                                        onmouseout="this.style.background='${index === 0 ? borderColor : 'white'}'; this.style.color='${index === 0 ? 'white' : borderColor}';">
                                    ${action}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                    <button onclick="dismissError('${errorId}')" 
                            style="
                                background: none;
                                border: none;
                                color: #9ca3af;
                                cursor: pointer;
                                font-size: 18px;
                                line-height: 1;
                                padding: 0;
                                width: 24px;
                                height: 24px;
                            ">×</button>
                </div>
            </div>
        `;

        document.body.appendChild(notification);

        // 自动消失（除非用户正在交互）
        setTimeout(() => {
            if (document.getElementById(`error-notification-${errorId}`)) {
                this.dismissError(errorId);
            }
        }, 10000);

        // 添加动画样式
        this.ensureErrorAnimationStyles();
    }

    /**
     * 3. 加载进度显示
     */

    // 创建加载进度指示器
    createLoadingIndicator(id, options = {}) {
        const config = {
            message: '加载中...',
            position: 'center', // center, top, bottom
            backdrop: true,
            cancellable: false,
            progress: false, // 是否显示进度条
            ...options
        };

        this.loadingStates.set(id, {
            ...config,
            startTime: Date.now(),
            progress: 0
        });

        const loadingEl = document.createElement('div');
        loadingEl.id = `loading-${id}`;
        loadingEl.className = 'loading-indicator';

        // 根据位置设置样式
        const positionStyles = {
            center: `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 10002;
            `,
            top: `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10002;
            `,
            bottom: `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10002;
            `
        };

        loadingEl.style.cssText = `
            ${positionStyles[config.position]}
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            min-width: 200px;
            text-align: center;
            animation: fadeIn 0.3s ease;
        `;

        let innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px; justify-content: center;">
                <div class="loading-spinner" style="
                    width: 24px;
                    height: 24px;
                    border: 3px solid #e5e7eb;
                    border-top: 3px solid #3b82f6;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                "></div>
                <div style="font-weight: 500; color: #374151;">${config.message}</div>
            </div>
        `;

        if (config.progress) {
            innerHTML += `
                <div style="margin-top: 12px;">
                    <div style="
                        width: 100%;
                        height: 4px;
                        background: #e5e7eb;
                        border-radius: 2px;
                        overflow: hidden;
                    ">
                        <div id="progress-bar-${id}" style="
                            width: 0%;
                            height: 100%;
                            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    <div id="progress-text-${id}" style="
                        font-size: 12px;
                        color: #6b7280;
                        margin-top: 4px;
                    ">0%</div>
                </div>
            `;
        }

        if (config.cancellable) {
            innerHTML += `
                <button onclick="cancelLoading('${id}')" style="
                    margin-top: 12px;
                    padding: 6px 12px;
                    background: #f3f4f6;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 12px;
                    color: #374151;
                ">取消</button>
            `;
        }

        loadingEl.innerHTML = innerHTML;

        // 添加背景遮罩
        if (config.backdrop) {
            const backdrop = document.createElement('div');
            backdrop.id = `loading-backdrop-${id}`;
            backdrop.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.3);
                z-index: 10001;
                animation: fadeIn 0.3s ease;
            `;
            document.body.appendChild(backdrop);
        }

        document.body.appendChild(loadingEl);
        this.ensureLoadingAnimationStyles();

        console.log(`⏳ 加载指示器已显示: ${id}`);
    }

    // 更新加载进度
    updateLoadingProgress(id, progress, message) {
        const loadingState = this.loadingStates.get(id);
        if (!loadingState) return;

        loadingState.progress = progress;
        if (message) loadingState.message = message;

        const progressBar = document.getElementById(`progress-bar-${id}`);
        const progressText = document.getElementById(`progress-text-${id}`);
        const loadingEl = document.getElementById(`loading-${id}`);

        if (progressBar) {
            progressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
        }

        if (progressText) {
            progressText.textContent = `${Math.round(progress)}%`;
        }

        if (message && loadingEl) {
            const messageEl = loadingEl.querySelector('[style*="font-weight: 500"]');
            if (messageEl) {
                messageEl.textContent = message;
            }
        }

        console.log(`📊 加载进度更新 [${id}]: ${progress}% - ${message || ''}`);
    }

    // 隐藏加载指示器
    hideLoadingIndicator(id) {
        const loadingEl = document.getElementById(`loading-${id}`);
        const backdrop = document.getElementById(`loading-backdrop-${id}`);

        if (loadingEl) {
            loadingEl.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (loadingEl && loadingEl.parentNode) {
                    loadingEl.parentNode.removeChild(loadingEl);
                }
            }, 300);
        }

        if (backdrop) {
            backdrop.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (backdrop && backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
            }, 300);
        }

        const loadingState = this.loadingStates.get(id);
        if (loadingState) {
            const duration = Date.now() - loadingState.startTime;
            console.log(`✅ 加载完成 [${id}]: ${duration}ms`);
            this.loadingStates.delete(id);
        }
    }

    /**
     * 4. 全局错误处理和工具函数
     */

    // 初始化全局错误处理
    initGlobalErrorHandling() {
        // 捕获未处理的Promise错误
        window.addEventListener('unhandledrejection', (event) => {
            console.error('未处理的Promise错误:', event.reason);
            this.showFriendlyError(event.reason, 'system');
            event.preventDefault(); // 防止在控制台显示
        });

        // 捕获全局JavaScript错误
        window.addEventListener('error', (event) => {
            console.error('全局JavaScript错误:', event.error);
            this.showFriendlyError(event.error, 'system');
        });

        console.log('🛡️ 全局错误处理已初始化');
    }

    // 初始化进度系统
    initProgressSystem() {
        // 监听性能优化器的导出进度
        window.addEventListener('exportProgress', (e) => {
            const { taskId, progress, message } = e.detail;
            this.updateLoadingProgress(`export_${taskId}`, progress, message);
        });

        console.log('📊 进度系统已初始化');
    }

    // 工具函数
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    generateErrorId() {
        return 'err_' + Math.random().toString(36).substr(2, 9);
    }

    // 确保错误动画样式存在
    ensureErrorAnimationStyles() {
        if (!document.getElementById('error-animations')) {
            const style = document.createElement('style');
            style.id = 'error-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // 确保加载动画样式存在
    ensureLoadingAnimationStyles() {
        if (!document.getElementById('loading-animations')) {
            const style = document.createElement('style');
            style.id = 'loading-animations';
            style.textContent = `
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes fadeOut {
                    from { opacity: 1; }
                    to { opacity: 0; }
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // 解除错误通知
    dismissError(errorId) {
        const notification = document.getElementById(`error-notification-${errorId}`);
        if (notification) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }

        // 更新错误记录
        const errorRecord = this.errorQueue.find(err => err.id === errorId);
        if (errorRecord) {
            errorRecord.resolved = true;
        }
    }

    // 处理错误操作
    handleErrorAction(errorId, action, actionIndex) {
        console.log(`🔧 处理错误操作: ${action} (错误ID: ${errorId})`);

        // 先解除错误通知
        this.dismissError(errorId);

        // 根据操作类型执行相应动作
        switch (action) {
            case '重试':
                window.location.reload();
                break;
            case '刷新页面':
                window.location.reload();
                break;
            case '返回首页':
                window.location.href = '/frontend/parent-home.html';
                break;
            case '重新登录':
                localStorage.removeItem('authToken');
                window.location.href = '/frontend/login.html';
                break;
            case '检查网络':
                window.open('https://www.baidu.com', '_blank');
                break;
            case '联系客服':
                alert('客服电话：400-123-4567\n客服邮箱：support@example.com');
                break;
            case '检查配置':
                if (window.location.pathname.includes('exercise-config')) {
                    // 高亮配置错误的字段
                    this.highlightConfigErrors();
                }
                break;
            default:
                console.log(`未知操作: ${action}`);
        }
    }

    // 高亮配置错误的字段
    highlightConfigErrors() {
        const requiredFields = ['subject', 'grade', 'difficulty'];
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field && !field.value) {
                field.style.borderColor = '#ef4444';
                field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
                
                // 5秒后恢复正常
                setTimeout(() => {
                    field.style.borderColor = '';
                    field.style.boxShadow = '';
                }, 5000);
            }
        });
    }

    // 取消加载
    cancelLoading(id) {
        this.hideLoadingIndicator(id);
        // 这里可以添加取消相关请求的逻辑
        console.log(`❌ 用户取消加载: ${id}`);
    }
}

// 增强的错误类
class EnhancedError extends Error {
    constructor(originalError, metadata = {}) {
        super(originalError.message || originalError.toString());
        this.name = 'EnhancedError';
        this.originalError = originalError;
        this.metadata = metadata;
        this.timestamp = new Date();
    }
}

// 导出为全局可用
window.ErrorHandler = ErrorHandler;
window.EnhancedError = EnhancedError;

// 创建全局实例
window.errorHandler = new ErrorHandler();

// 全局错误处理函数
window.dismissError = (errorId) => window.errorHandler.dismissError(errorId);
window.handleErrorAction = (errorId, action, actionIndex) => 
    window.errorHandler.handleErrorAction(errorId, action, actionIndex);
window.cancelLoading = (id) => window.errorHandler.cancelLoading(id);

console.log('🛡️ 错误处理和用户体验工具加载完成');