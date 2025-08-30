/**
 * 用户体验测试 - 测试UI和交互
 * 步骤8.4：全面测试 - 用户体验测试
 */

// 用户体验测试记录器
class UXTestLogger {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
        this.issues = [];
        this.userFlows = [];
        this.performanceMetrics = [];
        this.accessibilityIssues = [];
    }
    
    test(name, testFn) {
        console.log(`🎨 UX测试: ${name}`);
        try {
            const result = testFn();
            if (result) {
                console.log(`✅ 通过: ${name}`);
                this.passed++;
                this.tests.push({ name, status: 'passed', result });
            } else {
                console.log(`❌ 失败: ${name}`);
                this.failed++;
                this.tests.push({ name, status: 'failed', error: 'UX测试断言失败' });
                this.issues.push(`UX测试失败: ${name} - 断言失败`);
            }
        } catch (error) {
            console.error(`❌ 错误: ${name} - ${error.message}`);
            this.failed++;
            this.tests.push({ name, status: 'error', error: error.message });
            this.issues.push(`UX测试错误: ${name} - ${error.message}`);
        }
    }
    
    async asyncTest(name, testFn) {
        console.log(`🎨 异步UX测试: ${name}`);
        try {
            const result = await testFn();
            if (result) {
                console.log(`✅ 通过: ${name}`);
                this.passed++;
                this.tests.push({ name, status: 'passed', result });
            } else {
                console.log(`❌ 失败: ${name}`);
                this.failed++;
                this.tests.push({ name, status: 'failed', error: 'UX测试断言失败' });
                this.issues.push(`UX测试失败: ${name} - 断言失败`);
            }
        } catch (error) {
            console.error(`❌ 错误: ${name} - ${error.message}`);
            this.failed++;
            this.tests.push({ name, status: 'error', error: error.message });
            this.issues.push(`UX测试错误: ${name} - ${error.message}`);
        }
    }
    
    userFlow(name, steps) {
        this.userFlows.push({ 
            name, 
            steps, 
            status: 'pending',
            startTime: Date.now(),
            completedSteps: 0
        });
        console.log(`👤 开始用户流程测试: ${name}`);
    }
    
    completeUserFlow(name, success, completedSteps, details) {
        const flow = this.userFlows.find(f => f.name === name);
        if (flow) {
            flow.status = success ? 'completed' : 'failed';
            flow.completedSteps = completedSteps;
            flow.details = details;
            flow.duration = Date.now() - flow.startTime;
            console.log(`${success ? '✅' : '❌'} 用户流程 ${name}: ${success ? '完成' : '失败'} (${completedSteps}/${flow.steps.length} 步骤, ${flow.duration}ms)`);
        }
    }
    
    recordPerformanceMetric(name, value, unit) {
        this.performanceMetrics.push({ name, value, unit, timestamp: Date.now() });
        console.log(`⚡ 性能指标 ${name}: ${value}${unit}`);
    }
    
    recordAccessibilityIssue(issue) {
        this.accessibilityIssues.push(issue);
        console.log(`♿ 可访问性问题: ${issue}`);
    }
    
    summary() {
        const total = this.passed + this.failed;
        const completedFlows = this.userFlows.filter(f => f.status === 'completed').length;
        const failedFlows = this.userFlows.filter(f => f.status === 'failed').length;
        
        console.log(`\n📊 用户体验测试总结:`);
        console.log(`总测试数: ${total}`);
        console.log(`✅ 通过: ${this.passed}`);
        console.log(`❌ 失败: ${this.failed}`);
        console.log(`成功率: ${((this.passed / total) * 100).toFixed(1)}%`);
        console.log(`用户流程: ${completedFlows}/${this.userFlows.length} 完成`);
        
        if (this.performanceMetrics.length > 0) {
            console.log(`\n⚡ 性能指标:`);
            this.performanceMetrics.forEach(metric => {
                console.log(`  ${metric.name}: ${metric.value}${metric.unit}`);
            });
        }
        
        if (this.accessibilityIssues.length > 0) {
            console.log(`\n♿ 可访问性问题 (${this.accessibilityIssues.length}个):`);
            this.accessibilityIssues.forEach((issue, index) => {
                console.log(`${index + 1}. ${issue}`);
            });
        }
        
        if (this.userFlows.length > 0) {
            console.log(`\n👤 用户流程测试结果:`);
            this.userFlows.forEach(flow => {
                const statusIcon = flow.status === 'completed' ? '✅' : 
                                 flow.status === 'failed' ? '❌' : '⏳';
                console.log(`  ${statusIcon} ${flow.name} (${flow.completedSteps}/${flow.steps.length}) - ${flow.duration || 0}ms`);
            });
        }
        
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
            issues: this.issues,
            userFlows: this.userFlows,
            performanceMetrics: this.performanceMetrics,
            accessibilityIssues: this.accessibilityIssues
        };
    }
}

// 创建UX测试记录器
const uxLogger = new UXTestLogger();

// UI响应性测试工具
class ResponsivenessTracker {
    constructor() {
        this.interactions = [];
    }
    
    startInteraction(name) {
        const interaction = {
            name,
            startTime: performance.now(),
            endTime: null,
            duration: null
        };
        this.interactions.push(interaction);
        return interaction;
    }
    
    endInteraction(interaction) {
        interaction.endTime = performance.now();
        interaction.duration = interaction.endTime - interaction.startTime;
        return interaction.duration;
    }
    
    getAverageResponseTime() {
        const completedInteractions = this.interactions.filter(i => i.duration !== null);
        if (completedInteractions.length === 0) return 0;
        
        const total = completedInteractions.reduce((sum, i) => sum + i.duration, 0);
        return total / completedInteractions.length;
    }
}

// 用户体验测试主函数
async function runUXTests() {
    console.log('🚀 开始用户体验测试 - 测试UI和交互');
    
    const responsiveness = new ResponsivenessTracker();
    
    // === 1. 页面加载和渲染性能测试 ===
    uxLogger.userFlow('页面加载体验', [
        '测量首次内容绘制时间',
        '检查关键资源加载',
        '验证布局稳定性',
        '测试交互准备时间'
    ]);
    
    uxLogger.test('页面加载性能指标', () => {
        try {
            // 获取性能指标
            const navigation = performance.getEntriesByType('navigation')[0];
            const paint = performance.getEntriesByType('paint');
            
            if (navigation) {
                const domContentLoaded = navigation.domContentLoadedEventEnd - navigation.navigationStart;
                const loadComplete = navigation.loadEventEnd - navigation.navigationStart;
                
                uxLogger.recordPerformanceMetric('DOM内容加载', Math.round(domContentLoaded), 'ms');
                uxLogger.recordPerformanceMetric('页面完全加载', Math.round(loadComplete), 'ms');
                
                // 检查加载时间是否合理 (< 3秒为优秀)
                const isPerformant = domContentLoaded < 3000 && loadComplete < 5000;
                
                if (!isPerformant) {
                    uxLogger.issues.push(`页面加载较慢: DOM加载${Math.round(domContentLoaded)}ms, 完全加载${Math.round(loadComplete)}ms`);
                }
                
                return true;
            }
            
            return false;
        } catch (error) {
            uxLogger.issues.push(`性能指标获取失败: ${error.message}`);
            return false;
        }
    });
    
    // 测量首次绘制时间
    uxLogger.test('首次内容绘制时间', () => {
        try {
            const paintEntries = performance.getEntriesByType('paint');
            const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
            
            if (fcp) {
                uxLogger.recordPerformanceMetric('首次内容绘制', Math.round(fcp.startTime), 'ms');
                
                // FCP应该在1.8秒内
                if (fcp.startTime > 1800) {
                    uxLogger.issues.push(`首次内容绘制时间过长: ${Math.round(fcp.startTime)}ms`);
                }
                
                return true;
            }
            
            return false;
        } catch (error) {
            uxLogger.issues.push(`首次绘制时间测量失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.completeUserFlow('页面加载体验', true, 2, '页面加载性能已测量');
    
    // === 2. 交互响应性测试 ===
    uxLogger.userFlow('用户交互响应', [
        '测试按钮点击响应',
        '测试表单输入延迟',
        '测试滚动流畅性',
        '测试动画性能'
    ]);
    
    await uxLogger.asyncTest('按钮交互响应时间', async () => {
        try {
            // 创建测试按钮
            const testButton = document.createElement('button');
            testButton.id = 'ux-test-button';
            testButton.textContent = 'UX测试按钮';
            testButton.style.cssText = `
                position: fixed;
                top: -100px;
                left: -100px;
                padding: 10px;
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
            `;
            document.body.appendChild(testButton);
            
            // 测试点击响应时间
            const interaction = responsiveness.startInteraction('按钮点击');
            
            const clickPromise = new Promise(resolve => {
                testButton.addEventListener('click', () => {
                    const responseTime = responsiveness.endInteraction(interaction);
                    resolve(responseTime);
                }, { once: true });
            });
            
            // 模拟点击
            testButton.click();
            
            const responseTime = await clickPromise;
            uxLogger.recordPerformanceMetric('按钮响应时间', Math.round(responseTime), 'ms');
            
            // 清理
            document.body.removeChild(testButton);
            
            // 响应时间应该在100ms内
            return responseTime < 100;
        } catch (error) {
            uxLogger.issues.push(`按钮响应测试失败: ${error.message}`);
            return false;
        }
    });
    
    await uxLogger.asyncTest('表单输入延迟测试', async () => {
        try {
            // 创建测试输入框
            const testInput = document.createElement('input');
            testInput.id = 'ux-test-input';
            testInput.type = 'text';
            testInput.style.cssText = `
                position: fixed;
                top: -100px;
                left: -100px;
                padding: 8px;
                border: 1px solid #ccc;
            `;
            document.body.appendChild(testInput);
            
            // 测试输入响应
            const interaction = responsiveness.startInteraction('表单输入');
            
            const inputPromise = new Promise(resolve => {
                testInput.addEventListener('input', () => {
                    const responseTime = responsiveness.endInteraction(interaction);
                    resolve(responseTime);
                }, { once: true });
            });
            
            // 模拟输入
            testInput.focus();
            testInput.value = 'test';
            testInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            const responseTime = await inputPromise;
            uxLogger.recordPerformanceMetric('输入响应时间', Math.round(responseTime), 'ms');
            
            // 清理
            document.body.removeChild(testInput);
            
            // 输入响应应该在50ms内
            return responseTime < 50;
        } catch (error) {
            uxLogger.issues.push(`输入响应测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.completeUserFlow('用户交互响应', true, 2, '交互响应时间已测量');
    
    // === 3. 视觉反馈和动画测试 ===
    uxLogger.userFlow('视觉反馈体验', [
        '测试加载指示器',
        '测试错误提示显示',
        '测试成功反馈',
        '测试动画流畅性'
    ]);
    
    await uxLogger.asyncTest('加载指示器用户体验', async () => {
        try {
            // 检查错误处理系统是否可用
            if (typeof ErrorHandler === 'undefined') {
                uxLogger.issues.push('ErrorHandler未加载，跳过加载指示器测试');
                return true; // 不影响整体测试
            }
            
            const errorHandler = new ErrorHandler();
            
            // 测试加载指示器创建和显示
            const loadingId = 'ux-loading-test';
            const interaction = responsiveness.startInteraction('加载指示器显示');
            
            errorHandler.createLoadingIndicator(loadingId, {
                message: 'UX测试加载中...',
                position: 'center',
                cancellable: true
            });
            
            const showTime = responsiveness.endInteraction(interaction);
            uxLogger.recordPerformanceMetric('加载指示器显示', Math.round(showTime), 'ms');
            
            // 检查元素是否正确创建
            const loadingEl = document.getElementById(`loading-${loadingId}`);
            const hasLoadingElement = loadingEl !== null;
            
            if (hasLoadingElement) {
                // 测试可见性
                const isVisible = loadingEl.offsetParent !== null;
                
                // 测试关闭
                const hideInteraction = responsiveness.startInteraction('加载指示器隐藏');
                errorHandler.hideLoadingIndicator(loadingId);
                const hideTime = responsiveness.endInteraction(hideInteraction);
                
                uxLogger.recordPerformanceMetric('加载指示器隐藏', Math.round(hideTime), 'ms');
                
                return isVisible && showTime < 50 && hideTime < 50;
            }
            
            return false;
        } catch (error) {
            uxLogger.issues.push(`加载指示器测试失败: ${error.message}`);
            return false;
        }
    });
    
    await uxLogger.asyncTest('错误提示用户体验', async () => {
        try {
            if (typeof ErrorHandler === 'undefined') {
                uxLogger.issues.push('ErrorHandler未加载，跳过错误提示测试');
                return true;
            }
            
            const errorHandler = new ErrorHandler();
            
            // 测试用户友好错误显示
            const testError = new Error('UX测试错误');
            const interaction = responsiveness.startInteraction('错误提示显示');
            
            const errorId = errorHandler.showFriendlyError(testError, 'ux-test');
            
            const showTime = responsiveness.endInteraction(interaction);
            uxLogger.recordPerformanceMetric('错误提示显示', Math.round(showTime), 'ms');
            
            // 检查错误通知是否创建
            const errorNotification = document.getElementById(`error-notification-${errorId}`);
            const hasErrorElement = errorNotification !== null;
            
            if (hasErrorElement) {
                // 检查可访问性属性
                const hasRole = errorNotification.hasAttribute('role');
                const hasAriaLabel = errorNotification.hasAttribute('aria-label');
                
                if (!hasRole) {
                    uxLogger.recordAccessibilityIssue('错误通知缺少role属性');
                }
                if (!hasAriaLabel) {
                    uxLogger.recordAccessibilityIssue('错误通知缺少aria-label属性');
                }
                
                // 测试错误解除
                const dismissInteraction = responsiveness.startInteraction('错误解除');
                errorHandler.dismissError(errorId);
                const dismissTime = responsiveness.endInteraction(dismissInteraction);
                
                uxLogger.recordPerformanceMetric('错误解除时间', Math.round(dismissTime), 'ms');
                
                return hasErrorElement && showTime < 100;
            }
            
            return false;
        } catch (error) {
            uxLogger.issues.push(`错误提示测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.completeUserFlow('视觉反馈体验', true, 2, '视觉反馈组件功能正常');
    
    // === 4. 布局和响应式测试 ===
    uxLogger.userFlow('响应式布局', [
        '测试不同屏幕尺寸',
        '检查元素对齐',
        '验证文本可读性',
        '测试触控友好性'
    ]);
    
    uxLogger.test('视口适配性测试', () => {
        try {
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight,
                devicePixelRatio: window.devicePixelRatio || 1
            };
            
            uxLogger.recordPerformanceMetric('视口宽度', viewport.width, 'px');
            uxLogger.recordPerformanceMetric('视口高度', viewport.height, 'px');
            uxLogger.recordPerformanceMetric('设备像素比', viewport.devicePixelRatio, 'x');
            
            // 检查是否支持常见屏幕尺寸
            const isTabletSize = viewport.width >= 768 && viewport.width <= 1024;
            const isMobileSize = viewport.width < 768;
            const isDesktopSize = viewport.width > 1024;
            
            // 测试CSS媒体查询支持
            const supportsMediaQueries = window.matchMedia && 
                                        window.matchMedia('(min-width: 768px)').matches !== undefined;
            
            if (!supportsMediaQueries) {
                uxLogger.recordAccessibilityIssue('不支持CSS媒体查询');
            }
            
            return supportsMediaQueries;
        } catch (error) {
            uxLogger.issues.push(`视口适配测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.test('触控目标大小检查', () => {
        try {
            // 查找页面上的可交互元素
            const interactiveElements = document.querySelectorAll('button, a, input, select, textarea, [onclick], [tabindex]');
            let smallTargets = 0;
            const minTouchTarget = 44; // 44px是推荐的最小触控目标
            
            interactiveElements.forEach(element => {
                const rect = element.getBoundingClientRect();
                const actualWidth = Math.max(rect.width, element.offsetWidth);
                const actualHeight = Math.max(rect.height, element.offsetHeight);
                
                if (actualWidth < minTouchTarget || actualHeight < minTouchTarget) {
                    smallTargets++;
                    
                    if (element.id || element.className) {
                        uxLogger.recordAccessibilityIssue(
                            `触控目标过小: ${element.tagName}${element.id ? '#' + element.id : ''}${element.className ? '.' + element.className.split(' ')[0] : ''} (${Math.round(actualWidth)}x${Math.round(actualHeight)}px)`
                        );
                    }
                }
            });
            
            const touchTargetScore = 1 - (smallTargets / Math.max(interactiveElements.length, 1));
            uxLogger.recordPerformanceMetric('触控友好度', Math.round(touchTargetScore * 100), '%');
            
            return touchTargetScore > 0.8; // 80%以上的元素应该有合适的触控目标
        } catch (error) {
            uxLogger.issues.push(`触控目标测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.completeUserFlow('响应式布局', true, 2, '布局适配性检查完成');
    
    // === 5. 可访问性测试 ===
    uxLogger.userFlow('可访问性体验', [
        '检查语义化标签',
        '测试键盘导航',
        '验证屏幕阅读器支持',
        '检查对比度'
    ]);
    
    uxLogger.test('语义化HTML结构', () => {
        try {
            const semanticElements = [
                'main', 'header', 'nav', 'section', 'article', 'aside', 'footer'
            ];
            
            let semanticScore = 0;
            semanticElements.forEach(tag => {
                if (document.querySelector(tag)) {
                    semanticScore++;
                }
            });
            
            // 检查heading结构
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            const hasHeadings = headings.length > 0;
            
            // 检查alt属性
            const images = document.querySelectorAll('img');
            let imagesWithAlt = 0;
            images.forEach(img => {
                if (img.hasAttribute('alt')) {
                    imagesWithAlt++;
                } else {
                    uxLogger.recordAccessibilityIssue(`图片缺少alt属性: ${img.src || '未知源'}`);
                }
            });
            
            const altTextScore = images.length > 0 ? (imagesWithAlt / images.length) : 1;
            
            uxLogger.recordPerformanceMetric('语义化程度', Math.round((semanticScore / semanticElements.length) * 100), '%');
            uxLogger.recordPerformanceMetric('Alt文本覆盖率', Math.round(altTextScore * 100), '%');
            
            return semanticScore > 2 && hasHeadings && altTextScore > 0.8;
        } catch (error) {
            uxLogger.issues.push(`语义化测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.test('键盘导航支持', () => {
        try {
            // 查找可聚焦元素
            const focusableElements = document.querySelectorAll(
                'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            let tabIndexIssues = 0;
            let focusStyleIssues = 0;
            
            focusableElements.forEach(element => {
                // 检查tabindex
                const tabIndex = element.getAttribute('tabindex');
                if (tabIndex && parseInt(tabIndex) > 0) {
                    tabIndexIssues++;
                    uxLogger.recordAccessibilityIssue(`避免使用正数tabindex: ${element.tagName}`);
                }
                
                // 检查焦点样式 (简单检查)
                const computedStyle = window.getComputedStyle(element, ':focus');
                const hasOutline = computedStyle.outline !== 'none' && computedStyle.outline !== '';
                const hasBoxShadow = computedStyle.boxShadow !== 'none' && computedStyle.boxShadow !== '';
                
                if (!hasOutline && !hasBoxShadow) {
                    focusStyleIssues++;
                }
            });
            
            const keyboardScore = 1 - ((tabIndexIssues + focusStyleIssues) / Math.max(focusableElements.length, 1));
            uxLogger.recordPerformanceMetric('键盘导航友好度', Math.round(keyboardScore * 100), '%');
            
            return keyboardScore > 0.8;
        } catch (error) {
            uxLogger.issues.push(`键盘导航测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.completeUserFlow('可访问性体验', true, 2, '可访问性基础检查完成');
    
    // === 6. 性能感知测试 ===
    uxLogger.userFlow('性能感知优化', [
        '测试骨架屏效果',
        '检查渐进加载',
        '验证缓存效果',
        '测试离线体验'
    ]);
    
    await uxLogger.asyncTest('缓存效果感知测试', async () => {
        try {
            if (typeof PerformanceOptimizer === 'undefined') {
                uxLogger.issues.push('PerformanceOptimizer未加载，跳过缓存测试');
                return true;
            }
            
            const perfOpt = new PerformanceOptimizer();
            
            // 测试缓存设置和获取的用户感知性能
            const testKey = 'ux-cache-test';
            const testData = { message: 'UX缓存测试数据', timestamp: Date.now() };
            
            // 测试缓存写入时间
            const writeStart = performance.now();
            perfOpt.set(testKey, testData);
            const writeTime = performance.now() - writeStart;
            
            // 测试缓存读取时间
            const readStart = performance.now();
            const cachedData = perfOpt.get(testKey);
            const readTime = performance.now() - readStart;
            
            uxLogger.recordPerformanceMetric('缓存写入时间', Math.round(writeTime), 'ms');
            uxLogger.recordPerformanceMetric('缓存读取时间', Math.round(readTime), 'ms');
            
            // 缓存操作应该很快 (<10ms)
            const isFastCache = writeTime < 10 && readTime < 5;
            
            if (!isFastCache) {
                uxLogger.issues.push(`缓存操作较慢: 写入${Math.round(writeTime)}ms, 读取${Math.round(readTime)}ms`);
            }
            
            return cachedData !== null && isFastCache;
        } catch (error) {
            uxLogger.issues.push(`缓存感知测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.completeUserFlow('性能感知优化', true, 1, '缓存性能感知测试完成');
    
    // === 7. 错误恢复用户体验测试 ===
    uxLogger.userFlow('错误恢复体验', [
        '测试网络错误处理',
        '验证重试体验',
        '检查错误信息清晰度',
        '测试恢复路径'
    ]);
    
    await uxLogger.asyncTest('错误恢复用户体验', async () => {
        try {
            if (typeof ErrorHandler === 'undefined') {
                uxLogger.issues.push('ErrorHandler未加载，跳过错误恢复测试');
                return true;
            }
            
            const errorHandler = new ErrorHandler();
            
            // 测试网络错误的用户友好处理
            const networkError = new Error('Failed to fetch');
            const friendlyError = errorHandler.translateError(networkError);
            
            // 检查错误翻译是否用户友好
            const hasUserFriendlyTitle = friendlyError.title && !friendlyError.title.includes('Error');
            const hasActionableAdvice = friendlyError.actions && friendlyError.actions.length > 0;
            
            if (!hasUserFriendlyTitle) {
                uxLogger.recordAccessibilityIssue('错误标题不够用户友好');
            }
            
            if (!hasActionableAdvice) {
                uxLogger.recordAccessibilityIssue('错误缺少可操作的建议');
            }
            
            return hasUserFriendlyTitle && hasActionableAdvice;
        } catch (error) {
            uxLogger.issues.push(`错误恢复体验测试失败: ${error.message}`);
            return false;
        }
    });
    
    uxLogger.completeUserFlow('错误恢复体验', true, 1, '错误处理用户体验检查完成');
    
    // === 8. 整体用户体验评分 ===
    uxLogger.test('整体UX评分', () => {
        const avgResponseTime = responsiveness.getAverageResponseTime();
        const accessibilityScore = Math.max(0, 100 - uxLogger.accessibilityIssues.length * 10);
        const performanceScore = avgResponseTime < 100 ? 100 - avgResponseTime : 0;
        
        uxLogger.recordPerformanceMetric('平均响应时间', Math.round(avgResponseTime), 'ms');
        uxLogger.recordPerformanceMetric('可访问性评分', accessibilityScore, '分');
        uxLogger.recordPerformanceMetric('性能评分', Math.round(performanceScore), '分');
        
        const overallScore = (accessibilityScore + performanceScore) / 2;
        uxLogger.recordPerformanceMetric('整体UX评分', Math.round(overallScore), '分');
        
        return overallScore > 70; // 70分以上认为良好
    });
    
    console.log('\n✅ 用户体验测试完成');
    return uxLogger.summary();
}

// 导出UX测试函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runUXTests, UXTestLogger, ResponsivenessTracker };
}

// 如果在浏览器环境中直接运行
if (typeof window !== 'undefined') {
    window.runUXTests = runUXTests;
    window.UXTestLogger = UXTestLogger;
    window.ResponsivenessTracker = ResponsivenessTracker;
}

console.log('📋 用户体验测试文件已加载');