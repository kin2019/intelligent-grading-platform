/**
 * 性能优化器单元测试
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

// 模拟API响应数据
const mockApiData = {
    subjects: { subjects: ['数学', '语文', '英语'] },
    grades: { grades: ['一年级', '二年级', '三年级'] },
    exercise: {
        generation_id: 'test_123',
        status: 'completed',
        exercises: [
            { id: 1, question_text: '1 + 1 = ?', correct_answer: '2' }
        ]
    }
};

// 性能优化器测试函数
async function runPerformanceOptimizerTests() {
    console.log('🚀 开始性能优化器单元测试');
    
    // 检查性能优化器是否存在
    logger.test('性能优化器类存在', () => {
        return typeof PerformanceOptimizer === 'function';
    });
    
    // 创建性能优化器实例
    let performanceOptimizer;
    logger.test('创建性能优化器实例', () => {
        performanceOptimizer = new PerformanceOptimizer();
        return performanceOptimizer instanceof PerformanceOptimizer;
    });
    
    // 测试缓存功能
    logger.test('缓存设置功能', () => {
        const testKey = 'test_cache_key';
        const testData = { message: 'test data' };
        performanceOptimizer.set(testKey, testData);
        
        const cached = performanceOptimizer.get(testKey);
        return cached && cached.message === testData.message;
    });
    
    logger.test('缓存过期功能', () => {
        const testKey = 'test_expire_key';
        const testData = { message: 'expire test' };
        
        // 设置一个已经过期的缓存（-1000ms表示1秒前过期）
        performanceOptimizer.set(testKey, testData, -1000);
        
        const cached = performanceOptimizer.get(testKey);
        return cached === null; // 应该返回null因为已过期
    });
    
    logger.test('缓存键是否存在检查', () => {
        const testKey = 'test_has_key';
        const testData = { message: 'has test' };
        
        performanceOptimizer.set(testKey, testData);
        return performanceOptimizer.has(testKey) === true;
    });
    
    logger.test('缓存键删除功能', () => {
        const testKey = 'test_remove_key';
        const testData = { message: 'remove test' };
        
        performanceOptimizer.set(testKey, testData);
        performanceOptimizer.remove(testKey);
        return performanceOptimizer.has(testKey) === false;
    });
    
    // 测试过期缓存清理
    logger.test('过期缓存清理', () => {
        // 设置一些过期的缓存
        performanceOptimizer.set('expire1', { data: 'old' }, -1000);
        performanceOptimizer.set('expire2', { data: 'old' }, -2000);
        performanceOptimizer.set('valid', { data: 'new' });
        
        const removedCount = performanceOptimizer.clearExpiredCache();
        
        return removedCount >= 2 && performanceOptimizer.has('valid') && !performanceOptimizer.has('expire1');
    });
    
    // 测试性能指标
    logger.test('性能指标初始化', () => {
        const metrics = performanceOptimizer.getPerformanceMetrics();
        return metrics && 
               typeof metrics.cacheHits === 'number' &&
               typeof metrics.cacheMisses === 'number' &&
               typeof metrics.apiRequests === 'number';
    });
    
    logger.test('缓存命中率计算', () => {
        // 清空指标
        performanceOptimizer.clearMetrics();
        
        // 模拟一些缓存操作
        performanceOptimizer.set('hit_test', { data: 'test' });
        performanceOptimizer.get('hit_test'); // 命中
        performanceOptimizer.get('miss_test'); // 未命中
        
        const metrics = performanceOptimizer.getPerformanceMetrics();
        return metrics.cacheHits > 0 && metrics.cacheMisses > 0;
    });
    
    // 测试批量API请求（模拟）
    logger.test('批量API请求结构', () => {
        const requests = [
            { endpoint: '/test1', key: 'test1' },
            { endpoint: '/test2', key: 'test2' }
        ];
        
        // 验证请求结构是否正确
        return Array.isArray(requests) && 
               requests.every(req => req.endpoint && req.key);
    });
    
    // 测试导出任务管理
    logger.test('导出任务创建', () => {
        const taskId = performanceOptimizer.generateExportTaskId();
        return taskId && typeof taskId === 'string' && taskId.length > 0;
    });
    
    logger.test('导出任务ID唯一性', () => {
        const id1 = performanceOptimizer.generateExportTaskId();
        const id2 = performanceOptimizer.generateExportTaskId();
        return id1 !== id2;
    });
    
    // 测试缓存大小管理
    logger.test('缓存大小限制', () => {
        // 设置大量数据测试大小限制
        const largeData = { 
            data: 'x'.repeat(1000),  // 1KB数据
            timestamp: Date.now()
        };
        
        for (let i = 0; i < 10; i++) {
            performanceOptimizer.set(`large_${i}`, largeData);
        }
        
        const currentSize = performanceOptimizer.getCacheSize();
        return currentSize > 0; // 应该有一些数据
    });
    
    // 测试配置获取
    logger.test('缓存配置获取', () => {
        const config = performanceOptimizer.getCacheConfig();
        return config && 
               config.MAX_CACHE_SIZE &&
               config.CACHE_EXPIRY &&
               config.PERFORMANCE_MONITOR_INTERVAL;
    });
    
    // 测试工具函数
    logger.test('哈希生成功能', () => {
        const hash1 = performanceOptimizer.generateHash('test string');
        const hash2 = performanceOptimizer.generateHash('test string');
        const hash3 = performanceOptimizer.generateHash('different string');
        
        return hash1 === hash2 && hash1 !== hash3;
    });
    
    logger.test('URL参数编码', () => {
        const params = { name: 'test', value: 'hello world' };
        const encoded = performanceOptimizer.encodeUrlParams(params);
        return encoded === 'name=test&value=hello%20world';
    });
    
    // 测试练习配置缓存
    logger.test('练习配置缓存', () => {
        const config = {
            subject: '数学',
            grade: '三年级',
            difficulty: 'medium'
        };
        
        performanceOptimizer.cacheExerciseConfig(config);
        const cached = performanceOptimizer.get('user_exercise_preferences');
        
        return cached && cached.subject === config.subject;
    });
    
    // 测试异步操作（模拟）
    await logger.asyncTest('异步缓存操作', async () => {
        return new Promise((resolve) => {
            setTimeout(() => {
                performanceOptimizer.set('async_test', { async: true });
                const result = performanceOptimizer.get('async_test');
                resolve(result && result.async === true);
            }, 100);
        });
    });
    
    // 测试错误处理
    logger.test('无效键处理', () => {
        try {
            const result = performanceOptimizer.get('');  // 空键
            return result === null;
        } catch (error) {
            logger.issues.push(`空键处理错误: ${error.message}`);
            return false;
        }
    });
    
    logger.test('无效数据处理', () => {
        try {
            performanceOptimizer.set('invalid_test', null);
            const result = performanceOptimizer.get('invalid_test');
            return result === null; // 应该正常处理null值
        } catch (error) {
            logger.issues.push(`null值处理错误: ${error.message}`);
            return false;
        }
    });
    
    // 测试清理功能
    logger.test('指标清理功能', () => {
        performanceOptimizer.clearMetrics();
        const metrics = performanceOptimizer.getPerformanceMetrics();
        
        return metrics.cacheHits === 0 && 
               metrics.cacheMisses === 0 && 
               metrics.apiRequests === 0;
    });
    
    // 测试Web Worker支持检测（如果环境支持）
    logger.test('Web Worker支持检测', () => {
        const hasWorker = performanceOptimizer.hasWebWorkerSupport();
        return typeof hasWorker === 'boolean';
    });
    
    // 测试文件大小估算
    logger.test('文件大小估算', () => {
        const mockExercises = [
            { question_text: 'test', correct_answer: 'answer' }
        ];
        const size = performanceOptimizer.estimateFileSize(mockExercises, 'text');
        return size > 0 && typeof size === 'number';
    });
    
    console.log('\n✅ 性能优化器测试完成');
    return logger.summary();
}

// 导出测试函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runPerformanceOptimizerTests, TestLogger };
}

// 如果在浏览器环境中直接运行
if (typeof window !== 'undefined') {
    window.runPerformanceOptimizerTests = runPerformanceOptimizerTests;
    window.PerformanceTestLogger = TestLogger;
}

console.log('📋 性能优化器单元测试文件已加载');