/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { wechatLogin, getCurrentUser, refreshToken, getQuotaInfo, updateProfile } from '@/api/auth'
import type { UserInfo, QuotaInfo, LoginResponse, UpdateProfileRequest } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)
  const quotaInfo = ref<QuotaInfo | null>(null)
  const loginLoading = ref(false)

  // 计算属性
  const isLogin = computed(() => !!token.value && !!userInfo.value)
  const isParent = computed(() => userInfo.value?.role === 'parent')
  const isTeacher = computed(() => userInfo.value?.role === 'teacher')
  const isStudent = computed(() => userInfo.value?.role === 'student')
  const isVip = computed(() => userInfo.value?.is_vip || false)
  const hasQuota = computed(() => {
    if (!userInfo.value) return false
    if (isVip.value) return true
    return userInfo.value.daily_used < userInfo.value.daily_quota
  })

  /**
   * 设置Token
   */
  const setToken = async (newToken: string) => {
    token.value = newToken
    
    // 保存到本地存储
    uni.setStorageSync('token', newToken)
    
    // 获取用户信息
    if (newToken) {
      await fetchUserInfo()
    }
  }

  /**
   * 设置用户信息
   */
  const setUserInfo = (user: Partial<UserInfo>) => {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...user }
    } else {
      userInfo.value = user as UserInfo
    }
    
    // 保存到本地存储
    uni.setStorageSync('user_info', userInfo.value)
  }

  /**
   * 获取用户信息
   */
  const fetchUserInfo = async () => {
    try {
      if (!token.value) return
      
      const user = await getCurrentUser()
      userInfo.value = user
      
      // 保存到本地存储
      uni.setStorageSync('user_info', user)
      
      // 获取配额信息
      await fetchQuotaInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  /**
   * 获取配额信息
   */
  const fetchQuotaInfo = async () => {
    try {
      if (!token.value) return
      
      const quota = await getQuotaInfo()
      quotaInfo.value = quota
      
      // 更新用户信息中的配额数据
      if (userInfo.value) {
        userInfo.value.is_vip = quota.is_vip
        userInfo.value.daily_quota = quota.daily_quota
        userInfo.value.daily_used = quota.daily_used
        setUserInfo(userInfo.value)
      }
    } catch (error) {
      console.error('获取配额信息失败:', error)
    }
  }

  /**
   * 微信登录
   */
  const loginWithWeChat = async (code: string): Promise<LoginResponse> => {
    try {
      loginLoading.value = true
      
      // 调用登录接口
      const response = await wechatLogin({ code })
      
      // 保存Token
      await setToken(response.access_token)
      
      // 保存基本用户信息
      setUserInfo({
        openid: response.user.openid,
        nickname: response.user.nickname,
        avatar_url: response.user.avatar_url,
        role: 'student', // 默认角色，后续从后端获取完整信息
        is_vip: false
      })
      
      return response
    } catch (error: any) {
      console.error('微信登录失败:', error)
      throw error
    } finally {
      loginLoading.value = false
    }
  }

  /**
   * 刷新Token
   */
  const refreshTokenAction = async () => {
    try {
      if (!token.value) {
        throw new Error('没有登录令牌')
      }
      
      const response = await refreshToken()
      token.value = response.access_token
      
      // 保存新Token
      uni.setStorageSync('token', response.access_token)
      
      return response
    } catch (error) {
      console.error('刷新Token失败:', error)
      // 刷新失败，清除登录状态
      await logoutAction()
      throw error
    }
  }

  /**
   * 更新用户资料
   */
  const updateUserProfile = async (data: UpdateProfileRequest) => {
    try {
      const updatedUser = await updateProfile(data)
      setUserInfo(updatedUser)
      
      uni.showToast({
        title: '更新成功',
        icon: 'success'
      })
      
      return updatedUser
    } catch (error: any) {
      console.error('更新用户资料失败:', error)
      uni.showToast({
        title: error.message || '更新失败',
        icon: 'error'
      })
      throw error
    }
  }

  /**
   * 检查登录状态
   */
  const checkLoginStatus = async () => {
    try {
      // 从本地存储恢复状态
      const savedToken = uni.getStorageSync('token')
      const savedUserInfo = uni.getStorageSync('user_info')
      
      if (savedToken && savedUserInfo) {
        token.value = savedToken
        userInfo.value = savedUserInfo
        
        // 尝试刷新用户信息
        try {
          await fetchUserInfo()
        } catch (error) {
          // 如果获取用户信息失败，可能是token过期
          console.warn('Token可能已过期，尝试刷新')
          await refreshTokenAction()
        }
      }
    } catch (error) {
      console.error('检查登录状态失败:', error)
      // 如果检查失败，清除本地存储
      await logoutAction()
    }
  }

  /**
   * 登出
   */
  const logoutAction = async () => {
    try {
      // 清除状态
      token.value = ''
      userInfo.value = null
      quotaInfo.value = null
      
      // 清除本地存储
      uni.removeStorageSync('token')
      uni.removeStorageSync('user_info')
      
      // 跳转到登录页
      uni.reLaunch({
        url: '/pages/common/login/index'
      })
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  /**
   * 消费配额
   */
  const consumeQuota = async () => {
    if (userInfo.value && !isVip.value) {
      userInfo.value.daily_used += 1
      setUserInfo(userInfo.value)
      
      // 刷新配额信息
      await fetchQuotaInfo()
    }
  }

  /**
   * 检查配额
   */
  const checkQuota = () => {
    if (!userInfo.value) {
      uni.showModal({
        title: '提示',
        content: '请先登录',
        showCancel: false,
        success: () => {
          uni.navigateTo({
            url: '/pages/common/login/index'
          })
        }
      })
      return false
    }
    
    if (!hasQuota.value) {
      uni.showModal({
        title: '配额不足',
        content: '今日免费批改次数已用完，是否升级VIP获得更多次数？',
        confirmText: '升级VIP',
        success: (res) => {
          if (res.confirm) {
            uni.navigateTo({
              url: '/pages/common/payment/index'
            })
          }
        }
      })
      return false
    }
    
    return true
  }

  return {
    // 状态
    token,
    userInfo,
    quotaInfo,
    loginLoading,
    
    // 计算属性
    isLogin,
    isParent,
    isTeacher,
    isStudent,
    isVip,
    hasQuota,
    
    // 方法
    setToken,
    setUserInfo,
    fetchUserInfo,
    fetchQuotaInfo,
    loginWithWeChat,
    refreshTokenAction,
    updateUserProfile,
    checkLoginStatus,
    logoutAction,
    consumeQuota,
    checkQuota
  }
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user-store',
        storage: {
          getItem: (key: string) => uni.getStorageSync(key),
          setItem: (key: string, value: any) => uni.setStorageSync(key, value),
          removeItem: (key: string) => uni.removeStorageSync(key)
        }
      }
    ]
  }
})