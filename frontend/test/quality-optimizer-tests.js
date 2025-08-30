/**
 * 题目质量优化器单元测试
 * 步骤8.4：全面测试 - 单元测试
 */

// 测试记录器
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

// 模拟题目数据
const mockExercises = [
    {
        id: 1,
        number: 1,
        question_text: "计算 2 + 3 = ?",
        correct_answer: "5",
        question_type: "arithmetic",
        analysis: "这是基本的加法运算"
    },
    {
        id: 2,
        number: 2,
        question_text: "计算 2 + 3 = ?",  // 重复题目
        correct_answer: "5",
        question_type: "arithmetic",
        analysis: "这是基本的加法运算"
    },
    {
        id: 3,
        number: 3,
        question_text: "计算 $\\frac{1}{2} + \\frac{1}{3} = ?$",
        correct_answer: "$\\frac{5}{6}$",
        question_type: "fraction",
        analysis: "分数加法需要通分"
    },
    {
        id: 4,
        number: 4,
        question_text: "解方程：$x^2 - 4x + 3 = 0$",
        correct_answer: "$x = 1$ 或 $x = 3$",
        question_type: "equation",
        analysis: "这是一个二次方程，可以因式分解"
    }
];

// 质量优化器测试函数
async function runQualityOptimizerTests() {
    console.log('🚀 开始质量优化器单元测试');
    
    // 检查质量优化器是否存在
    logger.test('质量优化器类存在', () => {
        return typeof ExerciseQualityOptimizer === 'function';
    });
    
    // 创建质量优化器实例
    let qualityOptimizer;
    logger.test('创建质量优化器实例', () => {
        qualityOptimizer = new ExerciseQualityOptimizer();
        return qualityOptimizer instanceof ExerciseQualityOptimizer;
    });
    
    // 测试文本相似度计算
    logger.test('文本相似度计算 - 相同文本', () => {
        const similarity = qualityOptimizer.calculateTextSimilarity("测试文本", "测试文本");
        return similarity === 1.0;
    });
    
    logger.test('文本相似度计算 - 不同文本', () => {
        const similarity = qualityOptimizer.calculateTextSimilarity("测试文本", "完全不同的内容");
        return similarity < 0.5;
    });
    
    logger.test('文本相似度计算 - 相似文本', () => {
        const similarity = qualityOptimizer.calculateTextSimilarity("计算 2 + 3", "计算 2 + 3 = ?");
        return similarity > 0.5 && similarity < 1.0;
    });
    
    // 测试数学公式提取
    logger.test('数学公式提取 - 包含公式', () => {
        const formulas = qualityOptimizer.extractMathFormulas("计算 $\\frac{1}{2}$ 的值");
        return formulas.length > 0 && formulas.includes('\\frac{1}{2}');
    });
    
    logger.test('数学公式提取 - 不包含公式', () => {
        const formulas = qualityOptimizer.extractMathFormulas("这是普通文本");
        return formulas.length === 0;
    });
    
    // 测试题目相似度计算
    logger.test('题目相似度计算 - 相同题目', () => {
        const similarity = qualityOptimizer.calculateSimilarity(mockExercises[0], mockExercises[1]);
        return similarity.overall > 0.8; // 应该很相似
    });
    
    logger.test('题目相似度计算 - 不同题目', () => {
        const similarity = qualityOptimizer.calculateSimilarity(mockExercises[0], mockExercises[3]);
        return similarity.overall < 0.5; // 应该不相似
    });
    
    // 测试去重功能
    logger.test('题目去重功能 - 检测重复', () => {
        const result = qualityOptimizer.removeDuplicates(mockExercises);
        return result.removed_count > 0 && result.unique_exercises.length < mockExercises.length;
    });
    
    logger.test('题目去重功能 - 保留唯一题目', () => {
        const result = qualityOptimizer.removeDuplicates(mockExercises);
        // 验证去重后的题目确实不重复
        const uniqueQuestions = result.unique_exercises.map(ex => ex.question_text);
        const uniqueSet = new Set(uniqueQuestions);
        return uniqueSet.size === result.unique_exercises.length;
    });
    
    // 测试难度评估
    logger.test('难度评估 - 简单题目', () => {
        const difficulty = qualityOptimizer.evaluateDifficulty(mockExercises[0]);
        return difficulty.overall_difficulty < 0.5; // 简单加法应该是容易的
    });
    
    logger.test('难度评估 - 复杂题目', () => {
        const difficulty = qualityOptimizer.evaluateDifficulty(mockExercises[3]);
        return difficulty.overall_difficulty > 0.6; // 方程应该更难
    });
    
    logger.test('难度评估 - 包含时间估计', () => {
        const difficulty = qualityOptimizer.evaluateDifficulty(mockExercises[0]);
        return difficulty.estimated_time > 0 && difficulty.estimated_time < 10; // 应该有合理的时间估计
    });
    
    // 测试难度等级获取
    logger.test('难度等级获取 - 简单', () => {
        const level = qualityOptimizer.getDifficultyLevel(0.3);
        return level.level === 'easy';
    });
    
    logger.test('难度等级获取 - 中等', () => {
        const level = qualityOptimizer.getDifficultyLevel(0.6);
        return level.level === 'medium';
    });
    
    logger.test('难度等级获取 - 困难', () => {
        const level = qualityOptimizer.getDifficultyLevel(0.8);
        return level.level === 'hard';
    });
    
    // 测试质量报告生成
    logger.test('质量报告生成', () => {
        const report = qualityOptimizer.generateQualityReport(mockExercises);
        return report.total_exercises === mockExercises.length &&
               report.quality_metrics &&
               report.quality_metrics.duplicates &&
               report.recommendations &&
               Array.isArray(report.recommendations);
    });
    
    // 测试数学公式优化
    logger.test('数学公式显示优化 - DOM操作', () => {
        // 创建模拟DOM元素
        const testDiv = document.createElement('div');
        testDiv.innerHTML = '<div class="math-content">$x^2 + 1$</div>';
        
        try {
            qualityOptimizer.optimizeMathDisplay(testDiv);
            return true; // 如果没有抛出错误就算成功
        } catch (error) {
            logger.issues.push(`数学公式优化失败: ${error.message}`);
            return false;
        }
    });
    
    // 测试编辑距离计算
    logger.test('编辑距离计算 - 相同字符串', () => {
        const distance = qualityOptimizer.editDistance("test", "test");
        return distance === 0;
    });
    
    logger.test('编辑距离计算 - 不同字符串', () => {
        const distance = qualityOptimizer.editDistance("kitten", "sitting");
        return distance === 3; // kitten -> sitting 需要3次编辑
    });
    
    // 测试公式复杂度计算
    logger.test('公式复杂度计算 - 简单公式', () => {
        const complexity = qualityOptimizer.calculateFormulaComplexity("x + 1");
        return complexity < 0.5;
    });
    
    logger.test('公式复杂度计算 - 复杂公式', () => {
        const complexity = qualityOptimizer.calculateFormulaComplexity("\\frac{x^2 + 3x + 2}{x - 1}");
        return complexity > 0.5;
    });
    
    console.log('\n✅ 质量优化器测试完成');
    return logger.summary();
}

// 导出测试函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runQualityOptimizerTests, TestLogger };
}

// 如果在浏览器环境中直接运行
if (typeof window !== 'undefined') {
    window.runQualityOptimizerTests = runQualityOptimizerTests;
    window.QualityTestLogger = TestLogger;
}

console.log('📋 质量优化器单元测试文件已加载');