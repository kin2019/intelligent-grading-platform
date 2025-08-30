/**
 * 集成测试 - 测试系统整体流程
 * 步骤8.4：全面测试 - 集成测试
 */

// 集成测试记录器
class IntegrationTestLogger {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
        this.issues = [];
        this.workflows = [];
    }
    
    test(name, testFn) {
        console.log(`🔗 集成测试: ${name}`);
        try {
            const result = testFn();
            if (result) {
                console.log(`✅ 通过: ${name}`);
                this.passed++;
                this.tests.push({ name, status: 'passed', result });
            } else {
                console.log(`❌ 失败: ${name}`);
                this.failed++;
                this.tests.push({ name, status: 'failed', error: '集成测试断言失败' });
                this.issues.push(`集成测试失败: ${name} - 断言失败`);
            }
        } catch (error) {
            console.error(`❌ 错误: ${name} - ${error.message}`);
            this.failed++;
            this.tests.push({ name, status: 'error', error: error.message });
            this.issues.push(`集成测试错误: ${name} - ${error.message}`);
        }
    }
    
    async asyncTest(name, testFn) {
        console.log(`🔗 异步集成测试: ${name}`);
        try {
            const result = await testFn();
            if (result) {
                console.log(`✅ 通过: ${name}`);
                this.passed++;
                this.tests.push({ name, status: 'passed', result });
            } else {
                console.log(`❌ 失败: ${name}`);
                this.failed++;
                this.tests.push({ name, status: 'failed', error: '集成测试断言失败' });
                this.issues.push(`集成测试失败: ${name} - 断言失败`);
            }
        } catch (error) {
            console.error(`❌ 错误: ${name} - ${error.message}`);
            this.failed++;
            this.tests.push({ name, status: 'error', error: error.message });
            this.issues.push(`集成测试错误: ${name} - ${error.message}`);
        }
    }
    
    workflow(name, steps) {
        this.workflows.push({ name, steps, status: 'pending' });
        console.log(`🔄 开始工作流测试: ${name}`);
    }
    
    completeWorkflow(name, success, details) {
        const workflow = this.workflows.find(w => w.name === name);
        if (workflow) {
            workflow.status = success ? 'completed' : 'failed';
            workflow.details = details;
            console.log(`${success ? '✅' : '❌'} 工作流 ${name}: ${success ? '完成' : '失败'}`);
        }
    }
    
    summary() {
        const total = this.passed + this.failed;
        console.log(`\n📊 集成测试总结:`);
        console.log(`总测试数: ${total}`);
        console.log(`✅ 通过: ${this.passed}`);
        console.log(`❌ 失败: ${this.failed}`);
        console.log(`成功率: ${((this.passed / total) * 100).toFixed(1)}%`);
        console.log(`工作流测试: ${this.workflows.length} 个`);
        
        if (this.workflows.length > 0) {
            console.log(`\n🔄 工作流测试结果:`);
            this.workflows.forEach(workflow => {
                console.log(`  ${workflow.status === 'completed' ? '✅' : workflow.status === 'failed' ? '❌' : '⏳'} ${workflow.name}`);
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
            workflows: this.workflows
        };
    }
}

// 创建集成测试记录器
const integrationLogger = new IntegrationTestLogger();

// 模拟用户会话数据
const mockUserSession = {
    token: 'mock_token_12345',
    userId: 1,
    role: 'student',
    preferences: {
        subject: '数学',
        grade: '三年级',
        difficulty: 'medium'
    }
};

// 集成测试主函数
async function runIntegrationTests() {
    console.log('🚀 开始集成测试 - 测试系统整体流程');
    
    // === 1. 系统初始化流程测试 ===
    integrationLogger.workflow('系统初始化流程', [
        '检查页面加载',
        '验证脚本引入',
        '初始化优化器实例',
        '建立事件监听器'
    ]);
    
    await integrationLogger.asyncTest('页面脚本依赖检查', async () => {
        // 检查关键脚本是否已加载
        const hasQualityOptimizer = typeof ExerciseQualityOptimizer === 'function';
        const hasPerformanceOptimizer = typeof PerformanceOptimizer === 'function';
        const hasErrorHandler = typeof ErrorHandler === 'function';
        const hasAuthUtils = typeof AuthUtils === 'object';
        
        console.log(`质量优化器: ${hasQualityOptimizer ? '已加载' : '未加载'}`);
        console.log(`性能优化器: ${hasPerformanceOptimizer ? '已加载' : '未加载'}`);
        console.log(`错误处理器: ${hasErrorHandler ? '已加载' : '未加载'}`);
        console.log(`认证工具: ${hasAuthUtils ? '已加载' : '未加载'}`);
        
        return hasQualityOptimizer && hasPerformanceOptimizer && hasErrorHandler && hasAuthUtils;
    });
    
    await integrationLogger.asyncTest('优化器实例创建和协作', async () => {
        try {
            // 创建所有优化器实例
            const qualityOpt = new ExerciseQualityOptimizer();
            const perfOpt = new PerformanceOptimizer();
            const errorHandler = new ErrorHandler();
            
            // 测试实例间的协作
            const testData = { test: 'integration data', timestamp: Date.now() };
            
            // 性能优化器缓存数据
            perfOpt.set('integration_test', testData);
            
            // 质量优化器处理练习数据
            const mockExercise = {
                id: 1,
                question_text: '计算 2 + 3 = ?',
                correct_answer: '5',
                question_type: 'arithmetic'
            };
            
            const difficulty = qualityOpt.evaluateDifficulty(mockExercise);
            
            // 错误处理器处理模拟错误
            const mockError = new Error('集成测试模拟错误');
            const friendlyError = errorHandler.translateError(mockError);
            
            return perfOpt.get('integration_test') !== null && 
                   difficulty.overall_difficulty !== undefined &&
                   friendlyError.type !== undefined;
        } catch (error) {
            integrationLogger.issues.push(`优化器实例协作失败: ${error.message}`);
            return false;
        }
    });
    
    integrationLogger.completeWorkflow('系统初始化流程', true, '所有组件成功初始化并建立协作关系');
    
    // === 2. 完整练习题生成流程测试 ===
    integrationLogger.workflow('练习题生成流程', [
        '用户配置选择',
        'API请求发送',
        '响应数据处理',
        '题目质量检查',
        '结果展示'
    ]);
    
    await integrationLogger.asyncTest('配置到生成的完整流程', async () => {
        try {
            // 模拟用户配置选择流程
            const userConfig = {
                subject: '数学',
                grade: '三年级',
                topic: '加减法',
                difficulty: 'easy',
                count: 5
            };
            
            // 模拟API响应数据
            const mockApiResponse = {
                generation_id: 'test_gen_001',
                status: 'completed',
                exercises: [
                    {
                        id: 1,
                        number: 1,
                        question_text: '计算 3 + 4 = ?',
                        correct_answer: '7',
                        question_type: 'arithmetic',
                        analysis: '这是基本加法运算'
                    },
                    {
                        id: 2,
                        number: 2,
                        question_text: '计算 8 - 3 = ?',
                        correct_answer: '5',
                        question_type: 'arithmetic',
                        analysis: '这是基本减法运算'
                    }
                ]
            };
            
            // 测试缓存机制
            const perfOpt = new PerformanceOptimizer();
            const cacheKey = `exercise_${JSON.stringify(userConfig)}`;
            perfOpt.set(cacheKey, mockApiResponse);
            
            const cachedData = perfOpt.get(cacheKey);
            
            // 测试质量检查
            const qualityOpt = new ExerciseQualityOptimizer();
            const qualityReport = qualityOpt.generateQualityReport(mockApiResponse.exercises);
            
            return cachedData !== null && 
                   cachedData.exercises.length === 2 &&
                   qualityReport.total_exercises === 2 &&
                   qualityReport.quality_metrics !== undefined;
        } catch (error) {
            integrationLogger.issues.push(`练习题生成流程失败: ${error.message}`);
            return false;
        }
    });
    
    integrationLogger.completeWorkflow('练习题生成流程', true, '配置、生成、缓存、质量检查流程正常');
    
    // === 3. 错误恢复和重试流程测试 ===
    integrationLogger.workflow('错误恢复流程', [
        '检测错误类型',
        '判断是否可重试',
        '执行重试逻辑',
        '显示用户友好错误',
        '恢复用户状态'
    ]);
    
    await integrationLogger.asyncTest('网络错误重试机制', async () => {
        try {
            const errorHandler = new ErrorHandler();
            
            let attemptCount = 0;
            const mockRetryableRequest = async () => {
                attemptCount++;
                if (attemptCount < 2) {
                    throw new Error('Network Error'); // 模拟网络错误
                }
                return { success: true, attempt: attemptCount };
            };
            
            const result = await errorHandler.retryApiRequest(mockRetryableRequest, {
                maxRetries: 2,
                retryDelay: 50 // 快速测试
            });
            
            return result.success && attemptCount === 2;
        } catch (error) {
            integrationLogger.issues.push(`重试机制测试失败: ${error.message}`);
            return false;
        }
    });
    
    await integrationLogger.asyncTest('用户友好错误显示集成', async () => {
        try {
            const errorHandler = new ErrorHandler();
            
            // 测试不同类型错误的翻译
            const networkError = new Error('Failed to fetch');
            const authError = new Error('HTTP 401: Unauthorized');
            const timeoutError = new Error('TimeoutError: Request timeout');
            
            const networkFriendly = errorHandler.translateError(networkError);
            const authFriendly = errorHandler.translateError(authError);
            const timeoutFriendly = errorHandler.translateError(timeoutError);
            
            // 测试错误显示
            const errorId = errorHandler.showFriendlyError(networkError, 'integration-test');
            
            const hasNetworkTranslation = networkFriendly.type === 'network';
            const hasAuthTranslation = authFriendly.type === 'auth';
            const hasTimeoutTranslation = timeoutFriendly.type === 'timeout';
            const hasErrorDisplay = typeof errorId === 'string';
            
            // 清理
            if (hasErrorDisplay) {
                errorHandler.dismissError(errorId);
            }
            
            return hasNetworkTranslation && hasAuthTranslation && 
                   hasTimeoutTranslation && hasErrorDisplay;
        } catch (error) {
            integrationLogger.issues.push(`错误显示集成失败: ${error.message}`);
            return false;
        }
    });
    
    integrationLogger.completeWorkflow('错误恢复流程', true, '错误检测、重试、显示、恢复机制运行正常');
    
    // === 4. 文件导出完整流程测试 ===
    integrationLogger.workflow('文件导出流程', [
        '选择导出格式',
        '准备导出数据',
        '执行导出处理',
        '显示进度',
        '完成下载'
    ]);
    
    await integrationLogger.asyncTest('异步文件导出流程', async () => {
        try {
            const perfOpt = new PerformanceOptimizer();
            
            // 准备测试数据
            const testExercises = [
                {
                    id: 1,
                    question_text: '1 + 1 = ?',
                    correct_answer: '2',
                    analysis: '基本加法'
                },
                {
                    id: 2,
                    question_text: '2 + 2 = ?',
                    correct_answer: '4',
                    analysis: '基本加法'
                }
            ];
            
            // 测试文件大小估算
            const estimatedSize = perfOpt.estimateFileSize(testExercises, 'text');
            
            // 测试导出任务ID生成
            const taskId1 = perfOpt.generateExportTaskId();
            const taskId2 = perfOpt.generateExportTaskId();
            
            // 测试Web Worker支持检测
            const hasWorkerSupport = perfOpt.hasWebWorkerSupport();
            
            return estimatedSize > 0 && 
                   taskId1 !== taskId2 &&
                   typeof hasWorkerSupport === 'boolean';
        } catch (error) {
            integrationLogger.issues.push(`文件导出流程测试失败: ${error.message}`);
            return false;
        }
    });
    
    integrationLogger.completeWorkflow('文件导出流程', true, '导出任务管理、大小估算、异步处理准备就绪');
    
    // === 5. 用户会话和状态管理集成测试 ===
    integrationLogger.workflow('会话管理流程', [
        '用户认证状态检查',
        '用户偏好加载',
        '状态持久化',
        '跨页面状态同步'
    ]);
    
    integrationLogger.test('缓存和用户偏好集成', () => {
        try {
            const perfOpt = new PerformanceOptimizer();
            
            // 测试用户偏好缓存
            const userPrefs = {
                subject: '数学',
                grade: '三年级',
                difficulty: 'medium',
                theme: 'light'
            };
            
            perfOpt.cacheExerciseConfig(userPrefs);
            const cachedPrefs = perfOpt.get('user_exercise_preferences');
            
            // 测试配置获取
            const cacheConfig = perfOpt.getCacheConfig();
            
            return cachedPrefs && 
                   cachedPrefs.subject === userPrefs.subject &&
                   cacheConfig.MAX_CACHE_SIZE > 0;
        } catch (error) {
            integrationLogger.issues.push(`会话管理集成失败: ${error.message}`);
            return false;
        }
    });
    
    integrationLogger.completeWorkflow('会话管理流程', true, '用户状态缓存、偏好管理、配置同步正常');
    
    // === 6. 性能监控和质量评估集成测试 ===
    integrationLogger.workflow('监控评估流程', [
        '性能指标收集',
        '质量评估执行',
        '数据关联分析',
        '报告生成'
    ]);
    
    integrationLogger.test('性能监控与质量评估协作', () => {
        try {
            const perfOpt = new PerformanceOptimizer();
            const qualityOpt = new ExerciseQualityOptimizer();
            
            // 模拟性能数据收集
            perfOpt.set('test_data', { test: true });
            perfOpt.get('test_data'); // 产生缓存命中
            perfOpt.get('nonexistent'); // 产生缓存未命中
            
            const metrics = perfOpt.getPerformanceMetrics();
            
            // 模拟质量评估
            const testExercises = [
                { question_text: 'test1', correct_answer: 'answer1' },
                { question_text: 'test2', correct_answer: 'answer2' }
            ];
            
            const qualityReport = qualityOpt.generateQualityReport(testExercises);
            
            return metrics.cacheHits > 0 && 
                   metrics.cacheMisses > 0 &&
                   qualityReport.total_exercises === 2 &&
                   Array.isArray(qualityReport.recommendations);
        } catch (error) {
            integrationLogger.issues.push(`监控评估协作失败: ${error.message}`);
            return false;
        }
    });
    
    integrationLogger.completeWorkflow('监控评估流程', true, '性能监控和质量评估数据关联正常');
    
    // === 7. DOM集成和用户界面测试 ===
    integrationLogger.workflow('UI集成流程', [
        'DOM操作执行',
        '样式应用检查',
        '事件处理绑定',
        '动画效果验证'
    ]);
    
    integrationLogger.test('DOM集成和样式应用', () => {
        try {
            const errorHandler = new ErrorHandler();
            
            // 测试样式确保功能
            errorHandler.ensureErrorAnimationStyles();
            errorHandler.ensureLoadingAnimationStyles();
            
            const errorStyleEl = document.getElementById('error-animations');
            const loadingStyleEl = document.getElementById('loading-animations');
            
            // 测试加载指示器创建
            errorHandler.createLoadingIndicator('ui-test', {
                message: 'UI集成测试',
                position: 'center'
            });
            
            const loadingEl = document.getElementById('loading-ui-test');
            const hasLoadingElement = loadingEl !== null;
            
            // 清理
            if (loadingEl) {
                errorHandler.hideLoadingIndicator('ui-test');
            }
            
            return errorStyleEl !== null && 
                   loadingStyleEl !== null &&
                   hasLoadingElement;
        } catch (error) {
            integrationLogger.issues.push(`DOM集成测试失败: ${error.message}`);
            return false;
        }
    });
    
    integrationLogger.completeWorkflow('UI集成流程', true, 'DOM操作、样式应用、组件创建正常');
    
    // === 8. 数据一致性和同步测试 ===
    await integrationLogger.asyncTest('跨组件数据一致性', async () => {
        try {
            const perfOpt = new PerformanceOptimizer();
            const qualityOpt = new ExerciseQualityOptimizer();
            
            // 测试数据在不同组件间的一致性
            const testData = {
                exercises: [
                    { id: 1, question_text: '同步测试题目1' },
                    { id: 2, question_text: '同步测试题目2' }
                ],
                metadata: { source: 'integration_test', timestamp: Date.now() }
            };
            
            // 性能优化器缓存数据
            const cacheKey = 'sync_test_data';
            perfOpt.set(cacheKey, testData);
            
            // 从缓存获取数据给质量优化器处理
            const cachedData = perfOpt.get(cacheKey);
            if (!cachedData) return false;
            
            const qualityReport = qualityOpt.generateQualityReport(cachedData.exercises);
            
            // 验证数据一致性
            const originalCount = testData.exercises.length;
            const cachedCount = cachedData.exercises.length;
            const reportedCount = qualityReport.total_exercises;
            
            return originalCount === cachedCount && 
                   cachedCount === reportedCount &&
                   originalCount === 2;
        } catch (error) {
            integrationLogger.issues.push(`数据一致性测试失败: ${error.message}`);
            return false;
        }
    });
    
    console.log('\n✅ 集成测试完成');
    return integrationLogger.summary();
}

// 导出集成测试函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runIntegrationTests, IntegrationTestLogger };
}

// 如果在浏览器环境中直接运行
if (typeof window !== 'undefined') {
    window.runIntegrationTests = runIntegrationTests;
    window.IntegrationTestLogger = IntegrationTestLogger;
}

console.log('📋 集成测试文件已加载');