/**
 * 网络请求工具
 */
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'

// 请求配置
const REQUEST_CONFIG = {
  baseURL: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000/api/v1' 
    : 'https://api.zyjc.com/api/v1',
  timeout: 30000,
  retryCount: 3,
  retryDelay: 1000
}

// 请求接口
export interface RequestOptions {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  data?: any
  header?: Record<string, string>
  timeout?: number
  retry?: boolean
}

// 响应接口
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: number
  request_id?: string
}

// 错误接口
export interface ApiError {
  code: number
  message: string
  details?: any
}

/**
 * 统一请求方法
 */
export const request = <T = any>(options: RequestOptions): Promise<T> => {
  return new Promise((resolve, reject) => {
    const userStore = useUserStore()
    const appStore = useAppStore()
    
    // 构建完整URL
    const url = options.url.startsWith('http') 
      ? options.url 
      : REQUEST_CONFIG.baseURL + options.url
    
    // 构建请求头
    const header: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Platform': 'uniapp',
      'X-Version': appStore.appVersion,
      ...options.header
    }
    
    // 添加认证头
    if (userStore.token) {
      header['Authorization'] = `Bearer ${userStore.token}`
    }
    
    // 添加设备信息
    if (appStore.systemInfo) {
      header['X-Device-Id'] = appStore.systemInfo.platform
      header['X-Device-Type'] = appStore.systemInfo.system
    }
    
    // 显示加载
    if (options.method !== 'GET') {
      uni.showLoading({
        title: '请求中...',
        mask: true
      })
    }
    
    // 发送请求
    uni.request({
      url,
      method: options.method,
      data: options.data,
      header,
      timeout: options.timeout || REQUEST_CONFIG.timeout,
      success: (res) => {
        const response = res.data as ApiResponse<T>
        
        // 处理HTTP状态码
        if (res.statusCode !== 200) {
          handleHttpError(res.statusCode, response)
          reject(new Error(`HTTP ${res.statusCode}`))
          return
        }
        
        // 处理业务状态码
        // 后端直接返回数据，无需解包
        resolve(response as T)
      },
      fail: (error) => {
        console.error('请求失败:', error)
        
        // 网络错误处理
        if (error.errMsg?.includes('timeout')) {
          uni.showToast({
            title: '请求超时，请检查网络',
            icon: 'error'
          })
        } else if (error.errMsg?.includes('fail')) {
          uni.showToast({
            title: '网络连接失败',
            icon: 'error'
          })
        } else {
          uni.showToast({
            title: '请求失败',
            icon: 'error'
          })
        }
        
        // 重试机制
        if (options.retry !== false && shouldRetry(error)) {
          retryRequest(options, resolve, reject)
        } else {
          reject(error)
        }
      },
      complete: () => {
        // 隐藏加载
        if (options.method !== 'GET') {
          uni.hideLoading()
        }
      }
    })
  })
}

/**
 * 处理HTTP错误
 */
const handleHttpError = (statusCode: number, response?: ApiResponse) => {
  const userStore = useUserStore()
  
  switch (statusCode) {
    case 401:
      // 未授权，清除登录状态
      userStore.logoutAction()
      uni.showToast({
        title: '登录已过期，请重新登录',
        icon: 'error'
      })
      break
    case 403:
      uni.showToast({
        title: '没有权限访问',
        icon: 'error'
      })
      break
    case 404:
      uni.showToast({
        title: '请求的资源不存在',
        icon: 'error'
      })
      break
    case 429:
      uni.showToast({
        title: '请求过于频繁，请稍后再试',
        icon: 'error'
      })
      break
    case 500:
      uni.showToast({
        title: '服务器内部错误',
        icon: 'error'
      })
      break
    case 502:
    case 503:
    case 504:
      uni.showToast({
        title: '服务暂时不可用',
        icon: 'error'
      })
      break
    default:
      uni.showToast({
        title: response?.message || '请求失败',
        icon: 'error'
      })
  }
}

/**
 * 处理API错误
 */
const handleApiError = (response: ApiResponse) => {
  const userStore = useUserStore()
  
  switch (response.code) {
    case 10001:
      // Token无效
      userStore.logoutAction()
      break
    case 10002:
      // Token过期，尝试刷新
      userStore.refreshTokenAction().catch(() => {
        userStore.logoutAction()
      })
      break
    case 20001:
      // 配额不足
      uni.showModal({
        title: '提示',
        content: '今日免费次数已用完，是否升级VIP？',
        confirmText: '升级VIP',
        success: (res) => {
          if (res.confirm) {
            uni.navigateTo({
              url: '/pages/common/vip/index'
            })
          }
        }
      })
      break
    default:
      uni.showToast({
        title: response.message || '操作失败',
        icon: 'error'
      })
  }
}

/**
 * 判断是否应该重试
 */
const shouldRetry = (error: any): boolean => {
  // 网络错误或超时错误可以重试
  return error.errMsg?.includes('timeout') || 
         error.errMsg?.includes('fail') ||
         error.errMsg?.includes('abort')
}

/**
 * 重试请求
 */
const retryRequest = (
  options: RequestOptions,
  resolve: (value: any) => void,
  reject: (reason: any) => void,
  retryCount = 0
) => {
  if (retryCount >= REQUEST_CONFIG.retryCount) {
    reject(new Error('请求重试次数超限'))
    return
  }
  
  setTimeout(() => {
    request({ ...options, retry: false })
      .then(resolve)
      .catch((error) => {
        if (shouldRetry(error)) {
          retryRequest(options, resolve, reject, retryCount + 1)
        } else {
          reject(error)
        }
      })
  }, REQUEST_CONFIG.retryDelay * (retryCount + 1))
}

/**
 * GET请求
 */
export const get = <T = any>(url: string, data?: any, options?: Partial<RequestOptions>) => {
  return request<T>({
    url,
    method: 'GET',
    data,
    ...options
  })
}

/**
 * POST请求
 */
export const post = <T = any>(url: string, data?: any, options?: Partial<RequestOptions>) => {
  return request<T>({
    url,
    method: 'POST',
    data,
    ...options
  })
}

/**
 * PUT请求
 */
export const put = <T = any>(url: string, data?: any, options?: Partial<RequestOptions>) => {
  return request<T>({
    url,
    method: 'PUT',
    data,
    ...options
  })
}

/**
 * DELETE请求
 */
export const del = <T = any>(url: string, data?: any, options?: Partial<RequestOptions>) => {
  return request<T>({
    url,
    method: 'DELETE',
    data,
    ...options
  })
}

/**
 * 文件上传
 */
export const upload = (
  url: string,
  filePath: string,
  name = 'file',
  formData?: Record<string, any>
): Promise<any> => {
  return new Promise((resolve, reject) => {
    const userStore = useUserStore()
    const appStore = useAppStore()
    
    const fullUrl = url.startsWith('http') 
      ? url 
      : REQUEST_CONFIG.baseURL + url
    
    const header: Record<string, string> = {
      'X-Platform': 'uniapp',
      'X-Version': appStore.appVersion
    }
    
    if (userStore.token) {
      header['Authorization'] = `Bearer ${userStore.token}`
    }
    
    uni.uploadFile({
      url: fullUrl,
      filePath,
      name,
      formData,
      header,
      success: (res) => {
        try {
          const response = JSON.parse(res.data) as ApiResponse
          
          if (response.code === 0 || response.code === 200) {
            resolve(response.data)
          } else {
            handleApiError(response)
            reject(new Error(response.message))
          }
        } catch (error) {
          console.error('解析上传响应失败:', error)
          reject(new Error('上传失败'))
        }
      },
      fail: (error) => {
        console.error('文件上传失败:', error)
        uni.showToast({
          title: '上传失败',
          icon: 'error'
        })
        reject(error)
      }
    })
  })
}

/**
 * 下载文件
 */
export const download = (url: string, savePath?: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    const userStore = useUserStore()
    
    const fullUrl = url.startsWith('http') 
      ? url 
      : REQUEST_CONFIG.baseURL + url
    
    const header: Record<string, string> = {}
    
    if (userStore.token) {
      header['Authorization'] = `Bearer ${userStore.token}`
    }
    
    uni.downloadFile({
      url: fullUrl,
      header,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.tempFilePath)
        } else {
          reject(new Error('下载失败'))
        }
      },
      fail: (error) => {
        console.error('文件下载失败:', error)
        reject(error)
      }
    })
  })
}