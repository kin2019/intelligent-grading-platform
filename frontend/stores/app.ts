/**
 * 应用状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SystemInfo, Subject } from '@/types/app'

export const useAppStore = defineStore('app', () => {
  // 状态
  const systemInfo = ref<SystemInfo | null>(null)
  const currentSubject = ref<Subject>('math')
  const globalLoading = ref(false)
  const networkStatus = ref(true)
  const appVersion = ref('1.0.0')
  const isFirstLaunch = ref(true)
  const themeMode = ref<'light' | 'dark' | 'auto'>('auto')
  const language = ref<'zh-CN' | 'en'>('zh-CN')

  // 学科配置
  const subjects = ref<Array<{
    key: Subject
    name: string
    color: string
    icon: string
    description: string
    available: boolean
  }>>([
    {
      key: 'math',
      name: '数学',
      color: '#007AFF',
      icon: '📐',
      description: '四则运算、代数、几何',
      available: true
    },
    {
      key: 'chinese',
      name: '语文',
      color: '#FF3B30',
      icon: '📚',
      description: '拼音、汉字、阅读理解',
      available: true
    },
    {
      key: 'english',
      name: '英语',
      color: '#34C759',
      icon: '🇺🇸',
      description: '单词、语法、发音',
      available: true
    },
    {
      key: 'physics',
      name: '物理',
      color: '#AF52DE',
      icon: '⚛️',
      description: '力学、电学、光学',
      available: true
    },
    {
      key: 'chemistry',
      name: '化学',
      color: '#FF9500',
      icon: '⚗️',
      description: '方程式、计算题',
      available: true
    },
    {
      key: 'biology',
      name: '生物',
      color: '#32D74B',
      icon: '🧬',
      description: '选择题、填空题',
      available: true
    }
  ])

  // 计算属性
  const availableSubjects = computed(() => subjects.value.filter(s => s.available))
  const currentSubjectInfo = computed(() => subjects.value.find(s => s.key === currentSubject.value))
  const isDarkMode = computed(() => {
    if (themeMode.value === 'auto') {
      // 根据系统时间判断
      const hour = new Date().getHours()
      return hour < 7 || hour > 19
    }
    return themeMode.value === 'dark'
  })
  const isOnline = computed(() => networkStatus.value)
  const statusBarHeight = computed(() => systemInfo.value?.statusBarHeight || 0)
  const safeAreaInsets = computed(() => systemInfo.value?.safeAreaInsets || {
    top: 0,
    bottom: 0,
    left: 0,
    right: 0
  })

  /**
   * 初始化应用状态
   */
  const initAppState = () => {
    // 获取系统信息
    getSystemInfoAction()
    
    // 监听网络状态
    watchNetworkStatus()
    
    // 检查是否首次启动
    checkFirstLaunch()
    
    // 恢复用户设置
    restoreUserSettings()
  }

  /**
   * 获取系统信息
   */
  const getSystemInfoAction = () => {
    try {
      const info = uni.getSystemInfoSync()
      systemInfo.value = {
        platform: info.platform,
        system: info.system,
        version: info.version,
        statusBarHeight: info.statusBarHeight || 0,
        windowWidth: info.windowWidth,
        windowHeight: info.windowHeight,
        safeAreaInsets: info.safeAreaInsets || { top: 0, bottom: 0, left: 0, right: 0 },
        devicePixelRatio: info.devicePixelRatio || 1
      }
    } catch (error) {
      console.error('获取系统信息失败:', error)
    }
  }

  /**
   * 监听网络状态
   */
  const watchNetworkStatus = () => {
    // 获取当前网络状态
    uni.getNetworkType({
      success: (res) => {
        networkStatus.value = res.networkType !== 'none'
      }
    })
    
    // 监听网络状态变化
    uni.onNetworkStatusChange((res) => {
      networkStatus.value = res.isConnected
      
      if (!res.isConnected) {
        uni.showToast({
          title: '网络连接断开',
          icon: 'error'
        })
      } else {
        uni.showToast({
          title: '网络已连接',
          icon: 'success'
        })
      }
    })
  }

  /**
   * 检查是否首次启动
   */
  const checkFirstLaunch = () => {
    const hasLaunched = uni.getStorageSync('has_launched')
    if (!hasLaunched) {
      isFirstLaunch.value = true
      uni.setStorageSync('has_launched', true)
    } else {
      isFirstLaunch.value = false
    }
  }

  /**
   * 恢复用户设置
   */
  const restoreUserSettings = () => {
    const savedSubject = uni.getStorageSync('current_subject')
    if (savedSubject) {
      currentSubject.value = savedSubject
    }
    
    const savedTheme = uni.getStorageSync('theme_mode')
    if (savedTheme) {
      themeMode.value = savedTheme
    }
    
    const savedLanguage = uni.getStorageSync('language')
    if (savedLanguage) {
      language.value = savedLanguage
    }
  }

  /**
   * 设置当前学科
   */
  const setCurrentSubject = (subject: Subject) => {
    currentSubject.value = subject
    uni.setStorageSync('current_subject', subject)
    
    // 触觉反馈
    // #ifdef APP-PLUS || MP-WEIXIN
    uni.vibrateShort({
      type: 'light'
    })
    // #endif
  }

  /**
   * 设置主题模式
   */
  const setThemeMode = (mode: 'light' | 'dark' | 'auto') => {
    themeMode.value = mode
    uni.setStorageSync('theme_mode', mode)
  }

  /**
   * 设置语言
   */
  const setLanguage = (lang: 'zh-CN' | 'en') => {
    language.value = lang
    uni.setStorageSync('language', lang)
  }

  /**
   * 显示全局加载
   */
  const showGlobalLoading = (title = '加载中...') => {
    globalLoading.value = true
    uni.showLoading({
      title,
      mask: true
    })
  }

  /**
   * 隐藏全局加载
   */
  const hideGlobalLoading = () => {
    globalLoading.value = false
    uni.hideLoading()
  }

  /**
   * 显示消息提示
   */
  const showToast = (options: {
    title: string
    icon?: 'success' | 'error' | 'loading' | 'none'
    duration?: number
    mask?: boolean
  }) => {
    uni.showToast({
      icon: 'none',
      duration: 2000,
      mask: false,
      ...options
    })
  }

  /**
   * 显示确认对话框
   */
  const showConfirm = (options: {
    title?: string
    content: string
    confirmText?: string
    cancelText?: string
    confirmColor?: string
  }) => {
    return new Promise<boolean>((resolve) => {
      uni.showModal({
        title: '提示',
        confirmText: '确定',
        cancelText: '取消',
        confirmColor: '#007AFF',
        ...options,
        success: (res) => {
          resolve(res.confirm)
        },
        fail: () => {
          resolve(false)
        }
      })
    })
  }

  /**
   * 页面跳转
   */
  const navigateTo = (url: string, params?: Record<string, any>) => {
    let targetUrl = url
    
    if (params) {
      const queryString = Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')
      targetUrl += `?${queryString}`
    }
    
    uni.navigateTo({
      url: targetUrl,
      fail: (error) => {
        console.error('页面跳转失败:', error)
        showToast({
          title: '页面跳转失败',
          icon: 'error'
        })
      }
    })
  }

  /**
   * 页面重定向
   */
  const redirectTo = (url: string, params?: Record<string, any>) => {
    let targetUrl = url
    
    if (params) {
      const queryString = Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')
      targetUrl += `?${queryString}`
    }
    
    uni.redirectTo({
      url: targetUrl,
      fail: (error) => {
        console.error('页面重定向失败:', error)
        showToast({
          title: '页面跳转失败',
          icon: 'error'
        })
      }
    })
  }

  /**
   * 切换页面
   */
  const switchTab = (url: string) => {
    uni.switchTab({
      url,
      fail: (error) => {
        console.error('切换页面失败:', error)
        showToast({
          title: '页面切换失败',
          icon: 'error'
        })
      }
    })
  }

  /**
   * 保存应用状态
   */
  const saveAppState = () => {
    uni.setStorageSync('current_subject', currentSubject.value)
    uni.setStorageSync('theme_mode', themeMode.value)
    uni.setStorageSync('language', language.value)
  }

  /**
   * 检查应用更新
   */
  const checkUpdate = () => {
    // #ifdef APP-PLUS
    plus.runtime.getProperty(plus.runtime.appid, (info) => {
      const currentVersion = info.version
      // 这里可以调用后端接口检查最新版本
      console.log('当前版本:', currentVersion)
    })
    // #endif
    
    // #ifdef MP-WEIXIN
    const updateManager = uni.getUpdateManager()
    
    updateManager.onCheckForUpdate((res) => {
      console.log('检查更新结果:', res.hasUpdate)
    })
    
    updateManager.onUpdateReady(() => {
      showConfirm({
        title: '更新提示',
        content: '新版本已准备好，是否重启应用？'
      }).then((confirm) => {
        if (confirm) {
          updateManager.applyUpdate()
        }
      })
    })
    
    updateManager.onUpdateFailed(() => {
      showToast({
        title: '更新失败',
        icon: 'error'
      })
    })
    // #endif
  }

  return {
    // 状态
    systemInfo,
    currentSubject,
    globalLoading,
    networkStatus,
    appVersion,
    isFirstLaunch,
    themeMode,
    language,
    subjects,
    
    // 计算属性
    availableSubjects,
    currentSubjectInfo,
    isDarkMode,
    isOnline,
    statusBarHeight,
    safeAreaInsets,
    
    // 方法
    initAppState,
    getSystemInfoAction,
    setCurrentSubject,
    setThemeMode,
    setLanguage,
    showGlobalLoading,
    hideGlobalLoading,
    showToast,
    showConfirm,
    navigateTo,
    redirectTo,
    switchTab,
    saveAppState,
    checkUpdate
  }
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'app-store',
        storage: {
          getItem: (key: string) => uni.getStorageSync(key),
          setItem: (key: string, value: any) => uni.setStorageSync(key, value),
          removeItem: (key: string) => uni.removeStorageSync(key)
        }
      }
    ]
  }
})