/**
 * 支付状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getVipPlans, createOrder, getPaymentResult, getOrderHistory } from '@/api/payment'
import type { VipPlan, PaymentOrder, PaymentMethod } from '@/types/payment'

export const usePaymentStore = defineStore('payment', () => {
  // 状态
  const vipPlans = ref<VipPlan[]>([])
  const currentOrder = ref<PaymentOrder | null>(null)
  const orderHistory = ref<PaymentOrder[]>([])
  const loading = ref(false)
  const paying = ref(false)
  
  // VIP相关
  const userVipInfo = ref({
    type: 'free' as 'free' | 'basic' | 'premium' | 'ultimate',
    expire_date: null as string | null,
    remaining_days: 0,
    benefits: [] as string[]
  })
  
  // 支付方式
  const availablePaymentMethods = ref<PaymentMethod[]>([
    {
      id: 'wechat',
      name: '微信支付',
      icon: '💳',
      enabled: true,
      description: '安全便捷的微信支付'
    },
    {
      id: 'alipay',
      name: '支付宝',
      icon: '🏦',
      enabled: true,
      description: '支付宝快速支付'
    },
    {
      id: 'apple',
      name: 'Apple Pay',
      icon: '🍎',
      enabled: false, // 根据平台动态设置
      description: 'Apple内购支付'
    }
  ])
  
  // 计算属性
  const isVip = computed(() => userVipInfo.value.type !== 'free')
  const vipExpired = computed(() => {
    if (!userVipInfo.value.expire_date) return false
    return new Date(userVipInfo.value.expire_date) < new Date()
  })
  const vipStatus = computed(() => {
    if (!isVip.value) return 'free'
    if (vipExpired.value) return 'expired'
    return 'active'
  })
  
  /**
   * 加载VIP套餐
   */
  const loadVipPlans = async () => {
    try {
      loading.value = true
      const plans = await getVipPlans()
      vipPlans.value = plans
      return plans
    } catch (error) {
      console.error('加载VIP套餐失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 创建支付订单
   */
  const createPaymentOrder = async (planId: string, paymentMethod: string) => {
    try {
      loading.value = true
      
      const order = await createOrder({
        plan_id: planId,
        payment_method: paymentMethod
      })
      
      currentOrder.value = order
      return order
      
    } catch (error) {
      console.error('创建订单失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 微信支付
   */
  const payWithWechat = async (orderId: string) => {
    try {
      paying.value = true
      
      // 调用微信支付
      const paymentParams = await uni.requestPayment({
        provider: 'wxpay',
        orderInfo: {
          // 微信支付参数
        }
      })
      
      // 检查支付结果
      const result = await checkPaymentResult(orderId)
      
      if (result.success) {
        // 支付成功，更新VIP状态
        await updateVipStatus()
        
        uni.showToast({
          title: '支付成功',
          icon: 'success'
        })
      }
      
      return result
      
    } catch (error) {
      console.error('微信支付失败:', error)
      
      if (error.errMsg?.includes('cancel')) {
        uni.showToast({
          title: '支付已取消',
          icon: 'none'
        })
      } else {
        uni.showToast({
          title: '支付失败',
          icon: 'error'
        })
      }
      
      throw error
    } finally {
      paying.value = false
    }
  }
  
  /**
   * 支付宝支付
   */
  const payWithAlipay = async (orderId: string) => {
    try {
      paying.value = true
      
      // 调用支付宝支付
      const paymentParams = await uni.requestPayment({
        provider: 'alipay',
        orderInfo: {
          // 支付宝支付参数
        }
      })
      
      // 检查支付结果
      const result = await checkPaymentResult(orderId)
      
      if (result.success) {
        await updateVipStatus()
        
        uni.showToast({
          title: '支付成功',
          icon: 'success'
        })
      }
      
      return result
      
    } catch (error) {
      console.error('支付宝支付失败:', error)
      
      if (error.errMsg?.includes('cancel')) {
        uni.showToast({
          title: '支付已取消',
          icon: 'none'
        })
      } else {
        uni.showToast({
          title: '支付失败',
          icon: 'error'
        })
      }
      
      throw error
    } finally {
      paying.value = false
    }
  }
  
  /**
   * Apple内购支付
   */
  const payWithApple = async (orderId: string, productId: string) => {
    try {
      paying.value = true
      
      // #ifdef APP-PLUS
      // 调用Apple内购
      const iap = uni.requireNativePlugin('iap')
      const result = await iap.requestPayment({
        productid: productId
      })
      
      if (result.code === 0) {
        // 验证收据
        const verifyResult = await verifyAppleReceipt(result.receipt)
        
        if (verifyResult.success) {
          await updateVipStatus()
          
          uni.showToast({
            title: '购买成功',
            icon: 'success'
          })
        }
      }
      
      return result
      // #endif
      
    } catch (error) {
      console.error('Apple支付失败:', error)
      throw error
    } finally {
      paying.value = false
    }
  }
  
  /**
   * 检查支付结果
   */
  const checkPaymentResult = async (orderId: string) => {
    try {
      const result = await getPaymentResult(orderId)
      
      if (result.success) {
        // 更新订单状态
        if (currentOrder.value?.id === orderId) {
          currentOrder.value.status = 'paid'
          currentOrder.value.paid_at = new Date().toISOString()
        }
        
        // 添加到历史记录
        orderHistory.value.unshift(currentOrder.value!)
      }
      
      return result
      
    } catch (error) {
      console.error('检查支付结果失败:', error)
      throw error
    }
  }
  
  /**
   * 验证Apple收据
   */
  const verifyAppleReceipt = async (receipt: string) => {
    try {
      // 调用后端验证Apple收据
      // const result = await verifyAppleReceiptApi(receipt)
      
      // 模拟验证结果
      return { success: true }
      
    } catch (error) {
      console.error('验证Apple收据失败:', error)
      throw error
    }
  }
  
  /**
   * 更新VIP状态
   */
  const updateVipStatus = async () => {
    try {
      // 从服务器获取最新VIP状态
      // const vipInfo = await getUserVipInfo()
      
      // 模拟更新VIP状态
      const plan = vipPlans.value.find(p => p.id === currentOrder.value?.plan_id)
      if (plan) {
        userVipInfo.value = {
          type: plan.type,
          expire_date: new Date(Date.now() + plan.duration * 24 * 60 * 60 * 1000).toISOString(),
          remaining_days: plan.duration,
          benefits: plan.benefits
        }
      }
      
    } catch (error) {
      console.error('更新VIP状态失败:', error)
    }
  }
  
  /**
   * 加载订单历史
   */
  const loadOrderHistory = async () => {
    try {
      loading.value = true
      const orders = await getOrderHistory()
      orderHistory.value = orders
      return orders
    } catch (error) {
      console.error('加载订单历史失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 取消订单
   */
  const cancelOrder = async (orderId: string) => {
    try {
      // 调用取消订单API
      // await cancelOrderApi(orderId)
      
      // 更新本地状态
      if (currentOrder.value?.id === orderId) {
        currentOrder.value.status = 'cancelled'
      }
      
      orderHistory.value = orderHistory.value.map(order => {
        if (order.id === orderId) {
          return { ...order, status: 'cancelled' }
        }
        return order
      })
      
    } catch (error) {
      console.error('取消订单失败:', error)
      throw error
    }
  }
  
  /**
   * 恢复购买（iOS）
   */
  const restorePurchases = async () => {
    try {
      // #ifdef APP-PLUS
      const iap = uni.requireNativePlugin('iap')
      const result = await iap.restoreCompletedTransactions()
      
      if (result.code === 0 && result.transactions?.length > 0) {
        // 处理恢复的购买
        for (const transaction of result.transactions) {
          await verifyAppleReceipt(transaction.receipt)
        }
        
        await updateVipStatus()
        
        uni.showToast({
          title: '恢复购买成功',
          icon: 'success'
        })
      } else {
        uni.showToast({
          title: '没有可恢复的购买',
          icon: 'none'
        })
      }
      // #endif
      
    } catch (error) {
      console.error('恢复购买失败:', error)
      uni.showToast({
        title: '恢复购买失败',
        icon: 'error'
      })
      throw error
    }
  }
  
  /**
   * 获取VIP特权描述
   */
  const getVipBenefits = (type: string) => {
    const benefitsMap = {
      free: [
        '每日5次免费批改',
        '基础错题分析',
        '广告显示'
      ],
      basic: [
        '每日50次批改',
        '详细错题分析',
        '错题练习生成',
        '无广告体验'
      ],
      premium: [
        '无限制批改',
        '智能学习建议',
        '个性化练习题',
        '学习报告导出',
        '优先客服支持'
      ],
      ultimate: [
        '无限制批改',
        '一对一学习指导',
        '专属学习顾问',
        '家长端详细分析',
        '学习计划定制',
        '24小时客服支持'
      ]
    }
    
    return benefitsMap[type as keyof typeof benefitsMap] || []
  }
  
  /**
   * 检查特权权限
   */
  const hasPermission = (feature: string) => {
    const permissions = {
      unlimited_grading: ['premium', 'ultimate'],
      export_reports: ['premium', 'ultimate'],
      ai_tutoring: ['ultimate'],
      priority_support: ['premium', 'ultimate']
    }
    
    const requiredTypes = permissions[feature as keyof typeof permissions]
    return requiredTypes?.includes(userVipInfo.value.type) || false
  }
  
  /**
   * 清空当前订单
   */
  const clearCurrentOrder = () => {
    currentOrder.value = null
  }
  
  return {
    // 状态
    vipPlans,
    currentOrder,
    orderHistory,
    loading,
    paying,
    userVipInfo,
    availablePaymentMethods,
    
    // 计算属性
    isVip,
    vipExpired,
    vipStatus,
    
    // 方法
    loadVipPlans,
    createPaymentOrder,
    payWithWechat,
    payWithAlipay,
    payWithApple,
    checkPaymentResult,
    updateVipStatus,
    loadOrderHistory,
    cancelOrder,
    restorePurchases,
    getVipBenefits,
    hasPermission,
    clearCurrentOrder
  }
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'payment-store',
        storage: {
          getItem: (key: string) => uni.getStorageSync(key),
          setItem: (key: string, value: any) => uni.setStorageSync(key, value),
          removeItem: (key: string) => uni.removeStorageSync(key)
        },
        paths: ['userVipInfo', 'orderHistory']
      }
    ]
  }
})