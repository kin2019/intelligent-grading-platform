/**
 * 支付相关API接口
 */
import { request } from '@/utils/request'
import type { 
  VipPlan, 
  PaymentOrder, 
  PaymentParams, 
  PaymentResult,
  VipInfo,
  Coupon,
  Invoice,
  RefundRequest
} from '@/types/payment'

/**
 * 获取VIP套餐列表
 */
export const getVipPlans = () => {
  return request<VipPlan[]>({
    url: '/payment/plans',
    method: 'GET'
  })
}

/**
 * 创建支付订单
 */
export const createOrder = (params: PaymentParams) => {
  return request<PaymentOrder>({
    url: '/payment/orders',
    method: 'POST',
    data: params
  })
}

/**
 * 获取支付结果
 */
export const getPaymentResult = (orderId: string) => {
  return request<PaymentResult>({
    url: `/payment/orders/${orderId}/result`,
    method: 'GET'
  })
}

/**
 * 获取订单历史
 */
export const getOrderHistory = (params?: {
  page?: number
  size?: number
  status?: string
}) => {
  return request<PaymentOrder[]>({
    url: '/payment/orders/history',
    method: 'GET',
    data: params
  })
}

/**
 * 取消订单
 */
export const cancelOrder = (orderId: string) => {
  return request<{ success: boolean }>({
    url: `/payment/orders/${orderId}/cancel`,
    method: 'POST'
  })
}

/**
 * 获取用户VIP信息
 */
export const getUserVipInfo = () => {
  return request<VipInfo>({
    url: '/payment/vip/info',
    method: 'GET'
  })
}

/**
 * 验证优惠券
 */
export const validateCoupon = (code: string, planId: string) => {
  return request<{
    valid: boolean
    coupon?: Coupon
    discount_amount?: number
    final_amount?: number
  }>({
    url: '/payment/coupons/validate',
    method: 'POST',
    data: { code, plan_id: planId }
  })
}

/**
 * 获取可用优惠券
 */
export const getAvailableCoupons = (planId?: string) => {
  return request<Coupon[]>({
    url: '/payment/coupons/available',
    method: 'GET',
    data: { plan_id: planId }
  })
}

/**
 * 微信支付统一下单
 */
export const createWechatOrder = (orderId: string) => {
  return request<{
    appId: string
    timeStamp: string
    nonceStr: string
    package: string
    signType: string
    paySign: string
  }>({
    url: `/payment/wechat/create/${orderId}`,
    method: 'POST'
  })
}

/**
 * 支付宝支付参数
 */
export const createAlipayOrder = (orderId: string) => {
  return request<{
    orderInfo: string
  }>({
    url: `/payment/alipay/create/${orderId}`,
    method: 'POST'
  })
}

/**
 * 验证Apple内购收据
 */
export const verifyAppleReceipt = (receiptData: string, orderId: string) => {
  return request<{
    success: boolean
    receipt?: any
    latest_receipt?: string
  }>({
    url: '/payment/apple/verify',
    method: 'POST',
    data: {
      receipt_data: receiptData,
      order_id: orderId
    }
  })
}

/**
 * 恢复Apple内购
 */
export const restoreApplePurchases = (receiptData: string) => {
  return request<{
    restored_purchases: any[]
    vip_info: VipInfo
  }>({
    url: '/payment/apple/restore',
    method: 'POST',
    data: { receipt_data: receiptData }
  })
}

/**
 * 获取发票信息
 */
export const getInvoice = (orderId: string) => {
  return request<Invoice>({
    url: `/payment/orders/${orderId}/invoice`,
    method: 'GET'
  })
}

/**
 * 申请发票
 */
export const requestInvoice = (orderId: string, billingInfo: any) => {
  return request<Invoice>({
    url: `/payment/orders/${orderId}/invoice`,
    method: 'POST',
    data: billingInfo
  })
}

/**
 * 申请退款
 */
export const requestRefund = (orderId: string, reason: string) => {
  return request<RefundRequest>({
    url: `/payment/orders/${orderId}/refund`,
    method: 'POST',
    data: { reason }
  })
}

/**
 * 获取退款状态
 */
export const getRefundStatus = (refundId: string) => {
  return request<RefundRequest>({
    url: `/payment/refunds/${refundId}`,
    method: 'GET'
  })
}

/**
 * 获取支付配置
 */
export const getPaymentConfig = () => {
  return request<{
    available_methods: string[]
    minimum_amount: number
    maximum_amount: number
    currencies: string[]
  }>({
    url: '/payment/config',
    method: 'GET'
  })
}

/**
 * 获取支付统计
 */
export const getPaymentStats = (params: {
  start_date?: string
  end_date?: string
}) => {
  return request<any>({
    url: '/payment/stats',
    method: 'GET',
    data: params
  })
}

/**
 * 设置自动续费
 */
export const setAutoRenew = (enabled: boolean) => {
  return request<{ success: boolean }>({
    url: '/payment/vip/auto-renew',
    method: 'POST',
    data: { enabled }
  })
}

/**
 * 获取续费提醒设置
 */
export const getRenewalSettings = () => {
  return request<{
    auto_renew: boolean
    reminder_days: number[]
    email_notifications: boolean
    push_notifications: boolean
  }>({
    url: '/payment/vip/renewal-settings',
    method: 'GET'
  })
}

/**
 * 更新续费提醒设置
 */
export const updateRenewalSettings = (settings: any) => {
  return request<{ success: boolean }>({
    url: '/payment/vip/renewal-settings',
    method: 'PUT',
    data: settings
  })
}