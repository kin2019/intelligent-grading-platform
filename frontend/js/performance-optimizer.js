/**
 * 性能优化工具
 * 步骤8.2：性能优化实现
 * - 题目生成缓存机制
 * - 文件导出异步处理
 * - 数据库查询优化
 */

class PerformanceOptimizer {
    constructor() {
        this.cacheConfig = {
            // 缓存过期时间（毫秒）
            CACHE_EXPIRY: {
                CONFIG_DATA: 30 * 60 * 1000, // 配置数据30分钟
                EXERCISES: 60 * 60 * 1000,   // 练习题1小时
                USER_PREFS: 24 * 60 * 60 * 1000, // 用户偏好24小时
                API_RESPONSES: 10 * 60 * 1000     // API响应10分钟
            }
        };

        this.exportQueue = new Map(); // 导出任务队列
        this.batchRequestQueue = []; // 批量请求队列
        this.batchTimer = null;
        
        // 初始化性能监控
        this.performanceMetrics = {
            cacheHits: 0,
            cacheMisses: 0,
            apiRequests: 0,
            batchedRequests: 0,
            exportTasks: 0
        };

        this.initServiceWorker();
    }

    /**
     * 1. 题目生成缓存机制实现
     */
    
    // 智能缓存管理
    set(key, data, customExpiry = null) {
        const item = {
            data: data,
            timestamp: Date.now(),
            expiry: customExpiry || this.cacheConfig.CACHE_EXPIRY.API_RESPONSES
        };
        
        try {
            localStorage.setItem(`cache_${key}`, JSON.stringify(item));
            console.log(`✅ 缓存数据: ${key} (过期时间: ${customExpiry || this.cacheConfig.CACHE_EXPIRY.API_RESPONSES}ms)`);
        } catch (error) {
            console.warn('缓存存储失败，可能是空间不足:', error);
            this.clearExpiredCache(); // 清理过期缓存后重试
            try {
                localStorage.setItem(`cache_${key}`, JSON.stringify(item));
            } catch (retryError) {
                console.error('缓存存储重试失败:', retryError);
            }
        }
    }
    
    // 智能缓存获取
    get(key) {
        try {
            const item = localStorage.getItem(`cache_${key}`);
            if (!item) {
                this.performanceMetrics.cacheMisses++;
                return null;
            }
            
            const parsed = JSON.parse(item);
            const now = Date.now();
            
            // 检查是否过期
            if (now - parsed.timestamp > parsed.expiry) {
                localStorage.removeItem(`cache_${key}`);
                this.performanceMetrics.cacheMisses++;
                console.log(`⚠️ 缓存过期: ${key}`);
                return null;
            }
            
            this.performanceMetrics.cacheHits++;
            console.log(`✅ 缓存命中: ${key}`);
            return parsed.data;
        } catch (error) {
            console.error('缓存读取失败:', error);
            this.performanceMetrics.cacheMisses++;
            return null;
        }
    }
    
    // 预加载常用配置数据
    async preloadConfigData() {
        console.log('🚀 开始预加载配置数据...');
        
        const configEndpoints = [
            { key: 'subjects', endpoint: '/exercise/config/subjects', expiry: this.cacheConfig.CACHE_EXPIRY.CONFIG_DATA },
            { key: 'grades', endpoint: '/exercise/config/grades', expiry: this.cacheConfig.CACHE_EXPIRY.CONFIG_DATA },
            { key: 'difficulty_levels', endpoint: '/exercise/config/difficulty-levels', expiry: this.cacheConfig.CACHE_EXPIRY.CONFIG_DATA },
            { key: 'question_types', endpoint: '/exercise/config/question-types', expiry: this.cacheConfig.CACHE_EXPIRY.CONFIG_DATA }
        ];
        
        // 批量预加载
        const loadPromises = configEndpoints.map(async ({ key, endpoint, expiry }) => {
            try {
                // 检查缓存
                const cached = this.get(key);
                if (cached) {
                    console.log(`📋 使用缓存数据: ${key}`);
                    return { key, data: cached, fromCache: true };
                }
                
                // 从API获取
                const data = await this.apiRequest(endpoint);
                this.set(key, data, expiry);
                console.log(`🌐 从API加载: ${key}`);
                return { key, data, fromCache: false };
            } catch (error) {
                console.error(`❌ 加载${key}失败:`, error);
                return { key, error, fromCache: false };
            }
        });
        
        const results = await Promise.all(loadPromises);
        
        const successCount = results.filter(r => !r.error).length;
        const cacheHitCount = results.filter(r => r.fromCache).length;
        
        console.log(`✅ 配置数据预加载完成: ${successCount}/${results.length} 成功, ${cacheHitCount} 来自缓存`);
        return results;
    }
    
    // 练习题配置缓存
    cacheExerciseConfig(config) {
        const configKey = this.generateConfigHash(config);
        this.set(`exercise_config_${configKey}`, config, this.cacheConfig.CACHE_EXPIRY.EXERCISES);
        
        // 缓存用户偏好
        const userPrefs = {
            subject: config.subject,
            grade: config.grade,
            difficulty: config.difficulty_level,
            favorite_types: config.question_types,
            last_used: Date.now()
        };
        this.set('user_exercise_preferences', userPrefs, this.cacheConfig.CACHE_EXPIRY.USER_PREFS);
    }
    
    // 获取缓存的练习配置
    getCachedExerciseConfig(configHash) {
        return this.get(`exercise_config_${configHash}`);
    }
    
    // 生成配置哈希
    generateConfigHash(config) {
        const hashString = JSON.stringify({
            subject: config.subject,
            grade: config.grade,
            difficulty: config.difficulty_level,
            types: config.question_types?.sort(),
            count: config.question_count
        });
        return this.simpleHash(hashString);
    }
    
    // 简单哈希函数
    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // 转换为32位整数
        }
        return Math.abs(hash).toString(36);
    }
    
    // 清理过期缓存
    clearExpiredCache() {
        const now = Date.now();
        let clearedCount = 0;
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('cache_')) {
                try {
                    const item = JSON.parse(localStorage.getItem(key));
                    if (now - item.timestamp > item.expiry) {
                        localStorage.removeItem(key);
                        clearedCount++;
                    }
                } catch (error) {
                    // 损坏的缓存项，直接删除
                    localStorage.removeItem(key);
                    clearedCount++;
                }
            }
        }
        
        if (clearedCount > 0) {
            console.log(`🗑️ 清理了${clearedCount}个过期缓存项`);
        }
    }

    /**
     * 2. 文件导出异步处理
     */
    
    // 异步文件导出处理
    async exportFile(generationId, format, config, onProgress = null) {
        const taskId = `export_${generationId}_${format}_${Date.now()}`;
        console.log(`📤 开始异步导出任务: ${taskId}`);
        
        // 添加到导出队列
        const task = {
            id: taskId,
            generationId,
            format,
            config,
            status: 'pending',
            progress: 0,
            startTime: Date.now(),
            onProgress
        };
        
        this.exportQueue.set(taskId, task);
        this.performanceMetrics.exportTasks++;
        
        try {
            // 更新进度：准备阶段
            this.updateExportProgress(taskId, 10, '准备导出数据...');
            
            // 检查是否有缓存的导出结果
            const cacheKey = `export_${generationId}_${format}_${this.generateConfigHash(config)}`;
            const cached = this.get(cacheKey);
            if (cached && cached.downloadUrl) {
                console.log(`📋 使用缓存的导出文件: ${taskId}`);
                this.updateExportProgress(taskId, 100, '使用缓存文件');
                return {
                    success: true,
                    downloadUrl: cached.downloadUrl,
                    fileName: cached.fileName,
                    fromCache: true
                };
            }
            
            // 更新进度：开始处理
            this.updateExportProgress(taskId, 20, '正在处理练习题数据...');
            
            // 使用Web Worker处理导出（如果支持）
            if (window.Worker && this.serviceWorkerSupported) {
                return await this.exportWithWorker(task);
            } else {
                return await this.exportWithFallback(task);
            }
            
        } catch (error) {
            console.error(`❌ 导出任务失败: ${taskId}`, error);
            this.updateExportProgress(taskId, -1, `导出失败: ${error.message}`);
            throw error;
        } finally {
            // 清理已完成的任务（延迟清理，允许用户查看状态）
            setTimeout(() => {
                this.exportQueue.delete(taskId);
            }, 30000); // 30秒后清理
        }
    }
    
    // 使用Web Worker进行导出
    async exportWithWorker(task) {
        const { id, generationId, format, config } = task;
        
        return new Promise((resolve, reject) => {
            // 创建专用的导出Worker
            const workerCode = this.createExportWorkerCode();
            const blob = new Blob([workerCode], { type: 'application/javascript' });
            const worker = new Worker(URL.createObjectURL(blob));
            
            worker.onmessage = (e) => {
                const { type, progress, message, result, error } = e.data;
                
                if (type === 'progress') {
                    this.updateExportProgress(id, progress, message);
                } else if (type === 'success') {
                    this.updateExportProgress(id, 100, '导出完成');
                    
                    // 缓存导出结果
                    const cacheKey = `export_${generationId}_${format}_${this.generateConfigHash(config)}`;
                    this.set(cacheKey, {
                        downloadUrl: result.downloadUrl,
                        fileName: result.fileName,
                        exportTime: Date.now()
                    }, 60 * 60 * 1000); // 缓存1小时
                    
                    worker.terminate();
                    URL.revokeObjectURL(blob);
                    resolve(result);
                } else if (type === 'error') {
                    worker.terminate();
                    URL.revokeObjectURL(blob);
                    reject(new Error(error));
                }
            };
            
            worker.onerror = (error) => {
                worker.terminate();
                URL.revokeObjectURL(blob);
                reject(error);
            };
            
            // 发送导出任务到Worker
            worker.postMessage({
                generationId,
                format,
                config,
                apiBase: window.API_BASE || 'http://localhost:8000/api/v1',
                authToken: localStorage.getItem('authToken')
            });
        });
    }
    
    // 创建导出Worker代码
    createExportWorkerCode() {
        return `
            self.onmessage = async function(e) {
                const { generationId, format, config, apiBase, authToken } = e.data;
                
                try {
                    // 进度更新函数
                    const updateProgress = (progress, message) => {
                        self.postMessage({ type: 'progress', progress, message });
                    };
                    
                    updateProgress(30, '请求导出API...');
                    
                    // 调用导出API
                    const response = await fetch(\`\${apiBase}/exercise/generation/\${generationId}/export\`, {
                        method: 'POST',
                        headers: {
                            'Authorization': \`Bearer \${authToken}\`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(config)
                    });
                    
                    if (!response.ok) {
                        throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
                    }
                    
                    updateProgress(60, '处理导出结果...');
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateProgress(90, '准备下载链接...');
                        
                        const downloadUrl = \`\${apiBase}/exercise/download/\${result.download_id}\`;
                        
                        self.postMessage({
                            type: 'success',
                            result: {
                                success: true,
                                downloadUrl: downloadUrl,
                                fileName: result.file_name,
                                downloadId: result.download_id
                            }
                        });
                    } else {
                        throw new Error('导出失败');
                    }
                } catch (error) {
                    self.postMessage({
                        type: 'error',
                        error: error.message
                    });
                }
            };
        `;
    }
    
    // 降级导出方式
    async exportWithFallback(task) {
        const { id, generationId, format, config } = task;
        
        // 模拟进度更新
        const progressSteps = [30, 50, 70, 90];
        const messages = ['请求导出API...', '处理数据...', '生成文件...', '准备下载...'];
        
        for (let i = 0; i < progressSteps.length; i++) {
            this.updateExportProgress(id, progressSteps[i], messages[i]);
            await this.delay(500); // 模拟处理时间
        }
        
        // 实际API调用
        const response = await fetch(`${window.API_BASE || 'http://localhost:8000/api/v1'}/exercise/generation/${generationId}/export`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            const downloadUrl = `${window.API_BASE || 'http://localhost:8000/api/v1'}/exercise/download/${result.download_id}`;
            
            // 缓存结果
            const cacheKey = `export_${generationId}_${format}_${this.generateConfigHash(config)}`;
            this.set(cacheKey, {
                downloadUrl: downloadUrl,
                fileName: result.file_name,
                exportTime: Date.now()
            }, 60 * 60 * 1000);
            
            return {
                success: true,
                downloadUrl: downloadUrl,
                fileName: result.file_name,
                downloadId: result.download_id,
                fromCache: false
            };
        } else {
            throw new Error('导出失败');
        }
    }
    
    // 更新导出进度
    updateExportProgress(taskId, progress, message) {
        const task = this.exportQueue.get(taskId);
        if (task) {
            task.progress = progress;
            task.message = message;
            task.lastUpdate = Date.now();
            
            if (task.onProgress) {
                task.onProgress(progress, message);
            }
            
            // 发送自定义事件
            if (typeof window !== 'undefined') {
                window.dispatchEvent(new CustomEvent('exportProgress', {
                    detail: { taskId, progress, message }
                }));
            }
        }
    }
    
    // 获取导出任务状态
    getExportTaskStatus(taskId) {
        return this.exportQueue.get(taskId);
    }
    
    // 取消导出任务
    cancelExportTask(taskId) {
        const task = this.exportQueue.get(taskId);
        if (task) {
            task.status = 'cancelled';
            this.updateExportProgress(taskId, -1, '导出已取消');
            this.exportQueue.delete(taskId);
            return true;
        }
        return false;
    }

    /**
     * 3. 数据库查询优化
     */
    
    // 批量API请求优化
    async batchApiRequest(requests) {
        this.performanceMetrics.batchedRequests++;
        console.log(`📦 批量API请求: ${requests.length} 个请求`);
        
        // 检查缓存
        const results = [];
        const uncachedRequests = [];
        
        for (let i = 0; i < requests.length; i++) {
            const request = requests[i];
            const cacheKey = `api_${request.endpoint}_${this.simpleHash(JSON.stringify(request.options || {}))}`;
            const cached = this.get(cacheKey);
            
            if (cached) {
                results[i] = { data: cached, fromCache: true };
                console.log(`📋 批量请求缓存命中: ${request.endpoint}`);
            } else {
                uncachedRequests.push({ index: i, ...request });
            }
        }
        
        // 并发处理未缓存的请求
        if (uncachedRequests.length > 0) {
            const promises = uncachedRequests.map(async (request) => {
                try {
                    const startTime = Date.now();
                    const response = await this.apiRequest(request.endpoint, request.options);
                    const duration = Date.now() - startTime;
                    
                    // 缓存结果
                    const cacheKey = `api_${request.endpoint}_${this.simpleHash(JSON.stringify(request.options || {}))}`;
                    this.set(cacheKey, response, this.cacheConfig.CACHE_EXPIRY.API_RESPONSES);
                    
                    console.log(`🌐 批量API请求完成: ${request.endpoint} (${duration}ms)`);
                    
                    return {
                        index: request.index,
                        data: response,
                        fromCache: false,
                        duration
                    };
                } catch (error) {
                    console.error(`❌ 批量API请求失败: ${request.endpoint}`, error);
                    return {
                        index: request.index,
                        error: error.message,
                        fromCache: false
                    };
                }
            });
            
            const batchResults = await Promise.all(promises);
            
            // 合并结果
            batchResults.forEach(result => {
                results[result.index] = result;
            });
        }
        
        const successCount = results.filter(r => !r.error).length;
        const cacheCount = results.filter(r => r.fromCache).length;
        
        console.log(`✅ 批量API请求完成: ${successCount}/${results.length} 成功, ${cacheCount} 来自缓存`);
        
        return results;
    }
    
    // 分页查询优化
    async paginatedRequest(endpoint, options = {}) {
        const { pageSize = 50, maxPages = 10, cacheKey = null } = options;
        let allData = [];
        let page = 1;
        let hasMore = true;
        
        console.log(`📄 开始分页查询: ${endpoint}`);
        
        while (hasMore && page <= maxPages) {
            const pageEndpoint = `${endpoint}?page=${page}&size=${pageSize}`;
            const pageCacheKey = cacheKey ? `${cacheKey}_page_${page}` : null;
            
            try {
                let pageData;
                
                // 检查页面缓存
                if (pageCacheKey) {
                    pageData = this.get(pageCacheKey);
                    if (pageData) {
                        console.log(`📋 分页缓存命中: ${pageEndpoint}`);
                    }
                }
                
                if (!pageData) {
                    pageData = await this.apiRequest(pageEndpoint, options.requestOptions);
                    if (pageCacheKey) {
                        this.set(pageCacheKey, pageData, this.cacheConfig.CACHE_EXPIRY.API_RESPONSES);
                    }
                    console.log(`🌐 分页请求: ${pageEndpoint}`);
                }
                
                if (pageData.data && Array.isArray(pageData.data)) {
                    allData = allData.concat(pageData.data);
                    hasMore = pageData.data.length === pageSize;
                } else {
                    hasMore = false;
                }
                
                page++;
                
                // 避免过快请求
                if (hasMore) {
                    await this.delay(100);
                }
                
            } catch (error) {
                console.error(`❌ 分页请求失败: ${pageEndpoint}`, error);
                break;
            }
        }
        
        console.log(`✅ 分页查询完成: ${endpoint}, 共${allData.length}条数据, ${page - 1}页`);
        
        return {
            data: allData,
            totalPages: page - 1,
            totalItems: allData.length
        };
    }
    
    // 延迟函数
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 4. Service Worker 支持
     */
    
    // 初始化Service Worker
    initServiceWorker() {
        if ('serviceWorker' in navigator) {
            this.serviceWorkerSupported = true;
            console.log('🔧 Service Worker支持已启用');
        } else {
            this.serviceWorkerSupported = false;
            console.log('⚠️ Service Worker不支持，使用降级方案');
        }
    }

    /**
     * 5. 性能监控和统计
     */
    
    // 获取性能统计
    getPerformanceMetrics() {
        const cacheEfficiency = this.performanceMetrics.cacheHits + this.performanceMetrics.cacheMisses > 0 
            ? (this.performanceMetrics.cacheHits / (this.performanceMetrics.cacheHits + this.performanceMetrics.cacheMisses) * 100).toFixed(2)
            : 0;
        
        return {
            ...this.performanceMetrics,
            cacheEfficiency: `${cacheEfficiency}%`,
            totalCacheOperations: this.performanceMetrics.cacheHits + this.performanceMetrics.cacheMisses,
            activeExportTasks: this.exportQueue.size
        };
    }
    
    // 清理性能数据
    clearMetrics() {
        this.performanceMetrics = {
            cacheHits: 0,
            cacheMisses: 0,
            apiRequests: 0,
            batchedRequests: 0,
            exportTasks: 0
        };
        console.log('📊 性能统计数据已清理');
    }
    
    // API请求包装器（用于统计）
    async apiRequest(endpoint, options = {}) {
        this.performanceMetrics.apiRequests++;
        const startTime = Date.now();
        
        try {
            const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';
            const authToken = localStorage.getItem('authToken');
            
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const duration = Date.now() - startTime;
            console.log(`🌐 API请求完成: ${endpoint} (${duration}ms)`);
            
            return await response.json();
        } catch (error) {
            const duration = Date.now() - startTime;
            console.error(`❌ API请求失败: ${endpoint} (${duration}ms)`, error);
            throw error;
        }
    }
}

// 导出为全局可用
window.PerformanceOptimizer = PerformanceOptimizer;

// 创建全局实例
window.performanceOptimizer = new PerformanceOptimizer();

// 页面加载完成后自动预加载配置数据
document.addEventListener('DOMContentLoaded', () => {
    if (window.performanceOptimizer) {
        // 延迟预加载，避免阻塞主要内容
        setTimeout(() => {
            window.performanceOptimizer.preloadConfigData().catch(console.error);
            
            // 清理过期缓存
            window.performanceOptimizer.clearExpiredCache();
        }, 1000);
    }
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (window.performanceOptimizer) {
        window.performanceOptimizer.clearExpiredCache();
    }
});

console.log('🚀 性能优化器加载完成');