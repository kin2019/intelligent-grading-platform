/**
 * 题目质量优化工具
 * 步骤8.1：题目质量优化实现
 */

class ExerciseQualityOptimizer {
    constructor() {
        this.duplicateThreshold = 0.8; // 相似度阈值
        this.difficultyFactors = {
            // 数学公式复杂度权重
            formula: 0.3,
            // 步骤数量权重
            steps: 0.25,
            // 概念难度权重
            concepts: 0.25,
            // 计算复杂度权重
            computation: 0.2
        };
        
        // 初始化MathJax配置
        this.initMathJax();
    }

    /**
     * 1. 题目去重算法实现
     */
    
    // 计算两个题目的相似度
    calculateSimilarity(exercise1, exercise2) {
        const textSim = this.calculateTextSimilarity(exercise1.question_text, exercise2.question_text);
        const answerSim = this.calculateTextSimilarity(exercise1.correct_answer, exercise2.correct_answer);
        const typeSim = exercise1.question_type === exercise2.question_type ? 1.0 : 0.0;
        
        // 数学公式相似度（如果包含公式）
        const formulaSim = this.calculateFormulaSimilarity(exercise1, exercise2);
        
        return {
            overall: (textSim * 0.5 + answerSim * 0.3 + typeSim * 0.1 + formulaSim * 0.1),
            text: textSim,
            answer: answerSim,
            type: typeSim,
            formula: formulaSim
        };
    }
    
    // 文本相似度计算（使用编辑距离算法）
    calculateTextSimilarity(text1, text2) {
        if (!text1 || !text2) return 0;
        
        const len1 = text1.length;
        const len2 = text2.length;
        
        if (len1 === 0) return len2 === 0 ? 1 : 0;
        if (len2 === 0) return 0;
        
        // 创建矩阵
        const matrix = Array(len2 + 1).fill().map(() => Array(len1 + 1).fill(0));
        
        // 初始化第一行和第一列
        for (let i = 0; i <= len1; i++) matrix[0][i] = i;
        for (let j = 0; j <= len2; j++) matrix[j][0] = j;
        
        // 动态规划填充矩阵
        for (let j = 1; j <= len2; j++) {
            for (let i = 1; i <= len1; i++) {
                if (text1[i - 1] === text2[j - 1]) {
                    matrix[j][i] = matrix[j - 1][i - 1];
                } else {
                    matrix[j][i] = Math.min(
                        matrix[j - 1][i - 1] + 1, // 替换
                        matrix[j][i - 1] + 1,     // 插入
                        matrix[j - 1][i] + 1      // 删除
                    );
                }
            }
        }
        
        const maxLen = Math.max(len1, len2);
        return 1 - (matrix[len2][len1] / maxLen);
    }
    
    // 数学公式相似度计算
    calculateFormulaSimilarity(exercise1, exercise2) {
        const formulas1 = this.extractMathFormulas(exercise1.question_text);
        const formulas2 = this.extractMathFormulas(exercise2.question_text);
        
        if (formulas1.length === 0 && formulas2.length === 0) return 1.0;
        if (formulas1.length === 0 || formulas2.length === 0) return 0.0;
        
        let maxSimilarity = 0;
        for (const f1 of formulas1) {
            for (const f2 of formulas2) {
                const similarity = this.calculateTextSimilarity(f1, f2);
                maxSimilarity = Math.max(maxSimilarity, similarity);
            }
        }
        
        return maxSimilarity;
    }
    
    // 提取数学公式
    extractMathFormulas(text) {
        const formulas = [];
        
        // LaTeX格式公式 $...$, $$...$$
        const latexRegex = /\$\$(.*?)\$\$|\$(.*?)\$/g;
        let match;
        while ((match = latexRegex.exec(text)) !== null) {
            formulas.push(match[1] || match[2]);
        }
        
        // MathML格式公式
        const mathmlRegex = /<math[^>]*>(.*?)<\/math>/g;
        while ((match = mathmlRegex.exec(text)) !== null) {
            formulas.push(match[1]);
        }
        
        // 简单数学表达式
        const simpleRegex = /[0-9]+\s*[+\-*/^]\s*[0-9]+|[a-zA-Z]\s*[=]\s*[^,，。.!?]+/g;
        while ((match = simpleRegex.exec(text)) !== null) {
            formulas.push(match[0]);
        }
        
        return formulas;
    }
    
    // 批量去重处理
    removeDuplicates(exercises) {
        const uniqueExercises = [];
        const duplicateReport = [];
        
        for (let i = 0; i < exercises.length; i++) {
            let isDuplicate = false;
            
            for (let j = 0; j < uniqueExercises.length; j++) {
                const similarity = this.calculateSimilarity(exercises[i], uniqueExercises[j]);
                
                if (similarity.overall > this.duplicateThreshold) {
                    isDuplicate = true;
                    duplicateReport.push({
                        original_id: uniqueExercises[j].id,
                        duplicate_id: exercises[i].id,
                        similarity: similarity,
                        action: 'removed'
                    });
                    break;
                }
            }
            
            if (!isDuplicate) {
                uniqueExercises.push(exercises[i]);
            }
        }
        
        return {
            unique_exercises: uniqueExercises,
            removed_count: exercises.length - uniqueExercises.length,
            duplicate_report: duplicateReport
        };
    }

    /**
     * 2. 题目难度评估优化
     */
    
    // 综合难度评估
    evaluateDifficulty(exercise) {
        const factors = {
            formula: this.evaluateFormulaComplexity(exercise),
            steps: this.evaluateStepsComplexity(exercise),
            concepts: this.evaluateConceptsComplexity(exercise),
            computation: this.evaluateComputationComplexity(exercise)
        };
        
        // 加权计算总难度
        let totalDifficulty = 0;
        for (const [factor, weight] of Object.entries(this.difficultyFactors)) {
            totalDifficulty += factors[factor] * weight;
        }
        
        return {
            overall_difficulty: this.normalizeDifficulty(totalDifficulty),
            difficulty_factors: factors,
            difficulty_level: this.getDifficultyLevel(totalDifficulty),
            estimated_time: this.estimateCompletionTime(totalDifficulty),
            recommendations: this.generateDifficultyRecommendations(factors)
        };
    }
    
    // 数学公式复杂度评估
    evaluateFormulaComplexity(exercise) {
        const formulas = this.extractMathFormulas(exercise.question_text + ' ' + (exercise.correct_answer || ''));
        if (formulas.length === 0) return 0.3; // 无公式的基础分
        
        let complexity = 0;
        for (const formula of formulas) {
            // 运算符复杂度
            const operators = formula.match(/[+\-*/^√∫∑∏]/g) || [];
            complexity += operators.length * 0.1;
            
            // 函数复杂度
            const functions = formula.match(/sin|cos|tan|log|ln|exp|sqrt|frac/g) || [];
            complexity += functions.length * 0.2;
            
            // 嵌套复杂度
            const brackets = formula.match(/[\(\)\[\]\{\}]/g) || [];
            complexity += brackets.length * 0.05;
            
            // 变量数量
            const variables = formula.match(/[a-zA-Z]/g) || [];
            complexity += new Set(variables).size * 0.1;
        }
        
        return Math.min(complexity, 1.0);
    }
    
    // 解题步骤复杂度评估
    evaluateStepsComplexity(exercise) {
        const analysis = exercise.analysis || '';
        
        // 步骤标识词
        const stepKeywords = ['步骤', '首先', '然后', '接下来', '最后', '第一', '第二', '第三', '因此', '所以'];
        let stepCount = 0;
        
        stepKeywords.forEach(keyword => {
            const matches = analysis.match(new RegExp(keyword, 'g')) || [];
            stepCount += matches.length;
        });
        
        // 数字步骤标识
        const numberSteps = analysis.match(/[0-9]+\.|（[0-9]+）|\([0-9]+\)/g) || [];
        stepCount += numberSteps.length;
        
        return Math.min(stepCount * 0.15, 1.0);
    }
    
    // 概念复杂度评估
    evaluateConceptsComplexity(exercise) {
        const text = exercise.question_text + ' ' + (exercise.analysis || '');
        
        // 学科特定概念关键词
        const mathConcepts = ['微分', '积分', '导数', '极限', '矩阵', '向量', '概率', '统计', '几何', '代数'];
        const physicsConcepts = ['力', '能量', '动量', '电流', '磁场', '波', '光', '热', '压强'];
        const chemistryConcepts = ['原子', '分子', '化学键', '反应', '平衡', '酸碱', '氧化', '还原'];
        
        const allConcepts = [...mathConcepts, ...physicsConcepts, ...chemistryConcepts];
        
        let conceptCount = 0;
        allConcepts.forEach(concept => {
            if (text.includes(concept)) conceptCount++;
        });
        
        return Math.min(conceptCount * 0.1, 1.0);
    }
    
    // 计算复杂度评估
    evaluateComputationComplexity(exercise) {
        const text = exercise.question_text + ' ' + (exercise.correct_answer || '');
        
        // 大数字计算
        const largeNumbers = text.match(/[0-9]{4,}/g) || [];
        let complexity = largeNumbers.length * 0.1;
        
        // 小数计算
        const decimals = text.match(/[0-9]+\.[0-9]+/g) || [];
        complexity += decimals.length * 0.1;
        
        // 分数计算
        const fractions = text.match(/\d+\/\d+/g) || [];
        complexity += fractions.length * 0.15;
        
        // 开方运算
        const roots = text.match(/√|sqrt/g) || [];
        complexity += roots.length * 0.2;
        
        return Math.min(complexity, 1.0);
    }
    
    // 标准化难度分数
    normalizeDifficulty(score) {
        return Math.max(0, Math.min(1, score));
    }
    
    // 获取难度等级
    getDifficultyLevel(score) {
        if (score < 0.3) return { level: 'easy', name: '简单', color: '#48bb78' };
        if (score < 0.7) return { level: 'medium', name: '中等', color: '#ed8936' };
        return { level: 'hard', name: '困难', color: '#e53e3e' };
    }
    
    // 预估完成时间
    estimateCompletionTime(difficulty) {
        const baseTime = 5; // 基础时间（分钟）
        const additionalTime = difficulty * 15; // 根据难度增加的时间
        return Math.round(baseTime + additionalTime);
    }
    
    // 生成难度优化建议
    generateDifficultyRecommendations(factors) {
        const recommendations = [];
        
        if (factors.formula > 0.8) {
            recommendations.push('建议简化数学公式表达，降低公式复杂度');
        }
        if (factors.steps > 0.8) {
            recommendations.push('建议减少解题步骤，或提供中间提示');
        }
        if (factors.concepts > 0.8) {
            recommendations.push('建议减少概念数量，专注核心知识点');
        }
        if (factors.computation > 0.8) {
            recommendations.push('建议简化数值计算，或提供计算工具');
        }
        
        if (recommendations.length === 0) {
            recommendations.push('题目难度适中，无需调整');
        }
        
        return recommendations;
    }

    /**
     * 3. 数学公式显示优化
     */
    
    // 初始化MathJax配置
    initMathJax() {
        // 检查是否已经加载MathJax
        if (window.MathJax) {
            console.log('MathJax already loaded');
            return;
        }
        
        // 配置MathJax
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true,
                tags: 'ams',
                tagSide: 'right'
            },
            options: {
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process',
                renderActions: {
                    findScript: [10, function (doc) {
                        for (const node of document.querySelectorAll('script[type^="math/tex"]')) {
                            const display = !!node.type.match(/; *mode=display/);
                            const math = new doc.options.MathItem(node.textContent, doc.inputJax[0], display);
                            const text = document.createTextNode('');
                            node.parentNode.replaceChild(text, node);
                            math.start = {node: text, delim: '', n: 0};
                            math.end = {node: text, delim: '', n: 0};
                            doc.math.push(math);
                        }
                    }, '']
                }
            },
            svg: {
                fontCache: 'global',
                displayAlign: 'center',
                displayIndent: '0'
            },
            startup: {
                ready: () => {
                    MathJax.startup.defaultReady();
                    console.log('MathJax initialized for exercise quality optimization');
                }
            }
        };
        
        // 动态加载MathJax
        const script = document.createElement('script');
        script.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6';
        script.onload = () => {
            const mathJaxScript = document.createElement('script');
            mathJaxScript.id = 'MathJax-script';
            mathJaxScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
            document.head.appendChild(mathJaxScript);
        };
        document.head.appendChild(script);
    }
    
    // 优化数学公式显示
    optimizeMathDisplay(element) {
        if (!element) return;
        
        // 查找并处理所有数学公式
        const mathElements = element.querySelectorAll('.math-formula, .exercise-question, .exercise-answer, .exercise-analysis');
        
        mathElements.forEach(mathEl => {
            // 预处理公式文本
            let content = mathEl.innerHTML;
            content = this.preprocessMathContent(content);
            mathEl.innerHTML = content;
            
            // 添加数学公式样式类
            mathEl.classList.add('math-content');
        });
        
        // 重新渲染MathJax
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([element]).then(() => {
                console.log('MathJax rendering complete');
                this.addMathInteractivity(element);
            }).catch(err => {
                console.error('MathJax rendering failed:', err);
            });
        }
    }
    
    // 预处理数学内容
    preprocessMathContent(content) {
        // 转换常见的数学符号
        const replacements = {
            '±': '\\pm',
            '×': '\\times',
            '÷': '\\div',
            '≤': '\\leq',
            '≥': '\\geq',
            '≠': '\\neq',
            '√': '\\sqrt',
            'π': '\\pi',
            '∞': '\\infty',
            '∑': '\\sum',
            '∫': '\\int',
            '∂': '\\partial',
            'α': '\\alpha',
            'β': '\\beta',
            'γ': '\\gamma',
            'δ': '\\delta',
            'θ': '\\theta',
            'λ': '\\lambda',
            'μ': '\\mu',
            'σ': '\\sigma',
            'φ': '\\phi',
            'ω': '\\omega'
        };
        
        for (const [symbol, latex] of Object.entries(replacements)) {
            content = content.replace(new RegExp(symbol, 'g'), latex);
        }
        
        // 处理分数形式 a/b -> \frac{a}{b}
        content = content.replace(/(\d+)\/(\d+)/g, '\\frac{$1}{$2}');
        
        // 处理上下标
        content = content.replace(/\^(\w+)/g, '^{$1}');
        content = content.replace(/_(\w+)/g, '_{$1}');
        
        // 确保公式被适当的分隔符包围
        content = this.ensureMathDelimiters(content);
        
        return content;
    }
    
    // 确保数学分隔符正确
    ensureMathDelimiters(content) {
        // 如果内容包含LaTeX命令但没有分隔符，添加分隔符
        if (content.includes('\\') && !content.includes('$')) {
            // 检查是否为显示模式公式
            const displayCommands = ['\\frac', '\\sum', '\\int', '\\begin'];
            const isDisplay = displayCommands.some(cmd => content.includes(cmd));
            
            if (isDisplay) {
                content = '$$' + content + '$$';
            } else {
                content = '$' + content + '$';
            }
        }
        
        return content;
    }
    
    // 添加数学公式交互性
    addMathInteractivity(element) {
        const mathElements = element.querySelectorAll('.MathJax');
        
        mathElements.forEach(mathEl => {
            // 添加悬停效果
            mathEl.style.transition = 'transform 0.2s ease';
            
            mathEl.addEventListener('mouseenter', () => {
                mathEl.style.transform = 'scale(1.1)';
                mathEl.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
                mathEl.style.borderRadius = '4px';
                mathEl.style.padding = '2px 4px';
            });
            
            mathEl.addEventListener('mouseleave', () => {
                mathEl.style.transform = 'scale(1)';
                mathEl.style.backgroundColor = 'transparent';
                mathEl.style.padding = '0';
            });
            
            // 添加复制功能
            mathEl.addEventListener('click', () => {
                const mathContent = mathEl.textContent || mathEl.innerText;
                this.copyMathToClipboard(mathContent);
            });
        });
    }
    
    // 复制数学公式到剪贴板
    copyMathToClipboard(mathContent) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(mathContent).then(() => {
                this.showToast('公式已复制到剪贴板');
            }).catch(err => {
                console.error('复制失败:', err);
            });
        }
    }
    
    // 显示提示消息
    showToast(message) {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #48bb78;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        setTimeout(() => toast.style.opacity = '1', 100);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 2000);
    }

    /**
     * 综合质量报告
     */
    generateQualityReport(exercises) {
        const report = {
            timestamp: new Date().toISOString(),
            total_exercises: exercises.length,
            quality_metrics: {
                duplicates: this.removeDuplicates(exercises),
                difficulty_analysis: exercises.map(ex => this.evaluateDifficulty(ex)),
                math_formulas: exercises.reduce((sum, ex) => 
                    sum + this.extractMathFormulas(ex.question_text).length, 0)
            },
            recommendations: [],
            optimizations_applied: []
        };
        
        // 生成总体建议
        if (report.quality_metrics.duplicates.removed_count > 0) {
            report.recommendations.push(
                `检测到 ${report.quality_metrics.duplicates.removed_count} 道重复题目，已自动去除`
            );
        }
        
        const avgDifficulty = report.quality_metrics.difficulty_analysis
            .reduce((sum, analysis) => sum + analysis.overall_difficulty, 0) / exercises.length;
        
        if (avgDifficulty < 0.3) {
            report.recommendations.push('整体题目偏简单，建议增加难度');
        } else if (avgDifficulty > 0.8) {
            report.recommendations.push('整体题目偏难，建议降低难度');
        }
        
        return report;
    }
}

// 导出为全局可用
window.ExerciseQualityOptimizer = ExerciseQualityOptimizer;