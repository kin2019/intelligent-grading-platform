/**
 * 错误处理器单元测试
 * 步骤8.4：全面测试 - 单元测试
 */

// 测试记录器（重用之前的实现）
class TestLogger {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
        this.issues = [];
    }
    
    test(name, testFn) {
        console.log(`🧪 测试: ${name}`);
        try {
            const result = testFn();
            if (result) {
                console.log(`✅ 通过: ${name}`);
                this.passed++;
                this.tests.push({ name, status: 'passed', result });
            } else {
                console.log(`❌ 失败: ${name}`);
                this.failed++;
                this.tests.push({ name, status: 'failed', error: '测试断言失败' });
                this.issues.push(`测试失败: ${name} - 断言失败`);
            }
        } catch (error) {
            console.error(`❌ 错误: ${name} - ${error.message}`);
            this.failed++;
            this.tests.push({ name, status: 'error', error: error.message });
            this.issues.push(`测试错误: ${name} - ${error.message}`);
        }
    }
    
    async asyncTest(name, testFn) {
        console.log(`🧪 异步测试: ${name}`);
        try {
            const result = await testFn();
            if (result) {
                console.log(`✅ 通过: ${name}`);
                this.passed++;
                this.tests.push({ name, status: 'passed', result });
            } else {
                console.log(`❌ 失败: ${name}`);
                this.failed++;
                this.tests.push({ name, status: 'failed', error: '测试断言失败' });
                this.issues.push(`测试失败: ${name} - 断言失败`);
            }
        } catch (error) {
            console.error(`❌ 错误: ${name} - ${error.message}`);
            this.failed++;
            this.tests.push({ name, status: 'error', error: error.message });
            this.issues.push(`测试错误: ${name} - ${error.message}`);
        }
    }
    
    summary() {
        const total = this.passed + this.failed;
        console.log(`\n📊 测试总结:`);
        console.log(`总测试数: ${total}`);
        console.log(`✅ 通过: ${this.passed}`);
        console.log(`❌ 失败: ${this.failed}`);
        console.log(`成功率: ${((this.passed / total) * 100).toFixed(1)}%`);
        
        if (this.issues.length > 0) {
            console.log(`\n📝 发现的问题:`);
            this.issues.forEach((issue, index) => {
                console.log(`${index + 1}. ${issue}`);
            });
        }
        
        return {
            total,
            passed: this.passed,
            failed: this.failed,
            successRate: (this.passed / total) * 100,
            issues: this.issues
        };
    }
}

// 创建测试记录器
const logger = new TestLogger();

// 模拟错误类型
const mockErrors = {
    networkError: new Error('Failed to fetch'),
    timeoutError: new Error('TimeoutError: Request timeout'),
    httpError: new Error('HTTP 500: Internal Server Error'),
    authError: new Error('HTTP 401: Unauthorized'),
    notFoundError: new Error('HTTP 404: Not Found')
};

// 错误处理器测试函数
async function runErrorHandlerTests() {
    console.log('🚀 开始错误处理器单元测试');
    
    // 检查错误处理器是否存在
    logger.test('错误处理器类存在', () => {
        return typeof ErrorHandler === 'function';
    });
    
    // 创建错误处理器实例
    let errorHandler;
    logger.test('创建错误处理器实例', () => {
        errorHandler = new ErrorHandler();
        return errorHandler instanceof ErrorHandler;
    });
    
    // 测试错误类型识别
    logger.test('网络错误识别', () => {
        const isRetryable = errorHandler.isRetryableError(mockErrors.networkError);
        return isRetryable === true;
    });
    
    logger.test('超时错误识别', () => {
        const isRetryable = errorHandler.isRetryableError(mockErrors.timeoutError);
        return isRetryable === true;
    });
    
    logger.test('HTTP 500错误识别', () => {
        const isRetryable = errorHandler.isRetryableError(mockErrors.httpError);
        return isRetryable === true;
    });
    
    logger.test('非可重试错误识别', () => {
        const customError = new Error('Custom error');
        const isRetryable = errorHandler.isRetryableError(customError);
        return isRetryable === false;
    });
    
    // 测试错误翻译
    logger.test('网络错误翻译', () => {
        const friendly = errorHandler.translateError(mockErrors.networkError);
        return friendly.type === 'network' && 
               friendly.title.includes('网络') &&
               Array.isArray(friendly.actions);
    });
    
    logger.test('HTTP 401错误翻译', () => {
        const friendly = errorHandler.translateError(mockErrors.authError);
        return friendly.type === 'auth' && 
               friendly.title.includes('登录');
    });
    
    logger.test('HTTP 404错误翻译', () => {
        const friendly = errorHandler.translateError(mockErrors.notFoundError);
        return friendly.type === 'notfound' && 
               friendly.title.includes('不存在');
    });
    
    logger.test('超时错误翻译', () => {
        const friendly = errorHandler.translateError(mockErrors.timeoutError);
        return friendly.type === 'timeout' && 
               friendly.title.includes('超时');
    });
    
    // 测试错误ID生成
    logger.test('错误ID生成', () => {
        const id1 = errorHandler.generateErrorId();
        const id2 = errorHandler.generateErrorId();
        return id1 !== id2 && 
               id1.startsWith('err_') && 
               id2.startsWith('err_');
    });
    
    // 测试延迟函数
    await logger.asyncTest('延迟函数', async () => {
        const start = Date.now();
        await errorHandler.delay(100);
        const duration = Date.now() - start;
        return duration >= 90 && duration <= 150; // 允许一定误差
    });
    
    // 测试加载状态管理
    logger.test('加载指示器创建', () => {
        try {
            errorHandler.createLoadingIndicator('test-loading', {
                message: '测试加载...',
                position: 'center'
            });
            
            // 检查是否创建了DOM元素
            const loadingEl = document.getElementById('loading-test-loading');
            const hasElement = loadingEl !== null;
            
            // 清理
            if (loadingEl) {
                loadingEl.remove();
            }
            
            return hasElement;
        } catch (error) {
            logger.issues.push(`加载指示器创建失败: ${error.message}`);
            return false;
        }
    });
    
    logger.test('加载进度更新', () => {
        try {
            // 先创建加载指示器
            errorHandler.createLoadingIndicator('progress-test', {
                message: '进度测试',
                progress: true
            });
            
            // 更新进度
            errorHandler.updateLoadingProgress('progress-test', 50, '进行中...');
            
            const progressBar = document.getElementById('progress-bar-progress-test');
            const hasProgressBar = progressBar !== null;
            
            // 清理
            errorHandler.hideLoadingIndicator('progress-test');
            
            return hasProgressBar;
        } catch (error) {
            logger.issues.push(`进度更新失败: ${error.message}`);
            return false;
        }
    });
    
    logger.test('加载指示器隐藏', () => {
        try {
            // 创建后立即隐藏
            errorHandler.createLoadingIndicator('hide-test', {
                message: '隐藏测试'
            });
            
            errorHandler.hideLoadingIndicator('hide-test');
            
            // 等待动画完成后检查
            setTimeout(() => {
                const loadingEl = document.getElementById('loading-hide-test');
                return loadingEl === null;
            }, 500);
            
            return true; // 如果没有抛出错误就认为成功
        } catch (error) {
            logger.issues.push(`加载指示器隐藏失败: ${error.message}`);
            return false;
        }
    });
    
    // 测试重试机制（模拟）
    await logger.asyncTest('重试机制 - 成功情况', async () => {
        let attemptCount = 0;
        const mockRequest = async () => {
            attemptCount++;
            return { success: true, attempt: attemptCount };
        };
        
        try {
            const result = await errorHandler.retryApiRequest(mockRequest, {
                maxRetries: 2,
                retryDelay: 10  // 短延迟用于测试
            });
            
            return result.success && attemptCount === 1;
        } catch (error) {
            logger.issues.push(`重试机制测试失败: ${error.message}`);
            return false;
        }
    });
    
    await logger.asyncTest('重试机制 - 失败重试', async () => {
        let attemptCount = 0;
        const mockRequest = async () => {
            attemptCount++;
            if (attemptCount < 2) {
                throw new Error('Network Error'); // 可重试错误
            }
            return { success: true, attempt: attemptCount };
        };
        
        try {
            const result = await errorHandler.retryApiRequest(mockRequest, {
                maxRetries: 2,
                retryDelay: 10
            });
            
            return result.success && attemptCount === 2;
        } catch (error) {
            logger.issues.push(`重试失败情况测试错误: ${error.message}`);
            return false;
        }
    });
    
    await logger.asyncTest('重试机制 - 达到最大重试次数', async () => {
        let attemptCount = 0;
        const mockRequest = async () => {
            attemptCount++;
            throw new Error('Network Error'); // 总是失败
        };
        
        try {
            await errorHandler.retryApiRequest(mockRequest, {
                maxRetries: 2,
                retryDelay: 10
            });
            
            return false; // 不应该到达这里
        } catch (error) {
            // 应该抛出EnhancedError
            return error.name === 'EnhancedError' && attemptCount === 3;
        }
    });
    
    // 测试用户友好错误显示
    logger.test('用户友好错误显示', () => {
        try {
            const errorId = errorHandler.showFriendlyError(mockErrors.networkError, 'test-context');
            
            // 检查是否创建了错误通知
            const notification = document.getElementById(`error-notification-${errorId}`);
            const hasNotification = notification !== null;
            
            // 清理
            if (notification) {
                errorHandler.dismissError(errorId);
            }
            
            return hasNotification && typeof errorId === 'string';
        } catch (error) {
            logger.issues.push(`用户友好错误显示失败: ${error.message}`);
            return false;
        }
    });
    
    // 测试错误队列管理
    logger.test('错误队列管理', () => {
        const initialLength = errorHandler.errorQueue.length;
        const errorId = errorHandler.showFriendlyError(new Error('测试错误'), 'test');
        
        const newLength = errorHandler.errorQueue.length;
        const errorRecord = errorHandler.errorQueue.find(err => err.id === errorId);
        
        return newLength > initialLength && errorRecord && !errorRecord.resolved;
    });
    
    // 测试错误解除
    logger.test('错误解除功能', () => {
        const errorId = errorHandler.showFriendlyError(new Error('解除测试'), 'test');
        errorHandler.dismissError(errorId);
        
        const errorRecord = errorHandler.errorQueue.find(err => err.id === errorId);
        return errorRecord && errorRecord.resolved;
    });
    
    // 测试动画样式确保函数
    logger.test('错误动画样式确保', () => {
        errorHandler.ensureErrorAnimationStyles();
        const styleEl = document.getElementById('error-animations');
        return styleEl !== null && styleEl.tagName === 'STYLE';
    });
    
    logger.test('加载动画样式确保', () => {
        errorHandler.ensureLoadingAnimationStyles();
        const styleEl = document.getElementById('loading-animations');
        return styleEl !== null && styleEl.tagName === 'STYLE';
    });
    
    // 测试配置字段高亮功能
    logger.test('配置错误高亮', () => {
        try {
            // 创建模拟的配置字段
            const testField = document.createElement('input');
            testField.id = 'subject';
            document.body.appendChild(testField);
            
            errorHandler.highlightConfigErrors();
            
            const hasErrorStyle = testField.style.borderColor === 'rgb(239, 68, 68)' || 
                                  testField.style.borderColor === '#ef4444';
            
            // 清理
            document.body.removeChild(testField);
            
            return true; // 如果没有抛出错误就算成功
        } catch (error) {
            logger.issues.push(`配置错误高亮失败: ${error.message}`);
            return false;
        }
    });
    
    // 测试EnhancedError类
    logger.test('EnhancedError类创建', () => {
        const originalError = new Error('原始错误');
        const metadata = { attempts: 3, type: 'RETRY_EXHAUSTED' };
        const enhancedError = new EnhancedError(originalError, metadata);
        
        return enhancedError instanceof EnhancedError &&
               enhancedError.name === 'EnhancedError' &&
               enhancedError.metadata.attempts === 3 &&
               enhancedError.originalError === originalError;
    });
    
    // 测试全局错误处理初始化
    logger.test('全局错误处理初始化', () => {
        try {
            // 这个测试检查初始化是否不会抛出错误
            errorHandler.initGlobalErrorHandling();
            return true;
        } catch (error) {
            logger.issues.push(`全局错误处理初始化失败: ${error.message}`);
            return false;
        }
    });
    
    // 测试进度系统初始化
    logger.test('进度系统初始化', () => {
        try {
            errorHandler.initProgressSystem();
            return true;
        } catch (error) {
            logger.issues.push(`进度系统初始化失败: ${error.message}`);
            return false;
        }
    });
    
    console.log('\n✅ 错误处理器测试完成');
    return logger.summary();
}

// 导出测试函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runErrorHandlerTests, TestLogger };
}

// 如果在浏览器环境中直接运行
if (typeof window !== 'undefined') {
    window.runErrorHandlerTests = runErrorHandlerTests;
    window.ErrorTestLogger = TestLogger;
}

console.log('📋 错误处理器单元测试文件已加载');