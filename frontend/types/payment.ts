/**
 * 支付相关类型定义
 */

export type VipType = 'free' | 'basic' | 'premium' | 'ultimate'

export interface VipPlan {
  id: string
  type: VipType
  name: string
  description: string
  price: number
  original_price?: number
  duration: number // 天数
  discount?: number
  benefits: string[]
  is_popular?: boolean
  is_recommended?: boolean
  features: {
    daily_grading_limit: number | 'unlimited'
    ai_analysis: boolean
    practice_generation: boolean
    export_reports: boolean
    priority_support: boolean
    ad_free: boolean
    tutoring_service?: boolean
    family_sharing?: boolean
  }
  metadata?: {
    color?: string
    badge?: string
    sort_order?: number
  }
}

export interface PaymentOrder {
  id: string
  user_id: number
  plan_id: string
  plan_name: string
  amount: number
  original_amount?: number
  discount_amount?: number
  payment_method: string
  status: 'pending' | 'paid' | 'failed' | 'cancelled' | 'refunded'
  
  // 订单信息
  order_number: string
  created_at: string
  paid_at?: string
  expired_at: string
  
  // 支付信息
  payment_params?: {
    trade_no?: string
    transaction_id?: string
    receipt_data?: string // Apple内购收据
  }
  
  // VIP信息
  vip_start_date?: string
  vip_end_date?: string
  
  // 退款信息
  refund_reason?: string
  refunded_at?: string
  refund_amount?: number
}

export interface PaymentMethod {
  id: string
  name: string
  icon: string
  enabled: boolean
  description: string
  fee_rate?: number
  min_amount?: number
  max_amount?: number
  supported_platforms?: string[]
}

export interface PaymentParams {
  plan_id: string
  payment_method: string
  coupon_code?: string
  return_url?: string
}

export interface PaymentResult {
  success: boolean
  order_id: string
  trade_no?: string
  message?: string
  error_code?: string
}

export interface VipInfo {
  type: VipType
  expire_date: string | null
  remaining_days: number
  benefits: string[]
  is_active: boolean
  auto_renew: boolean
  next_billing_date?: string
}

export interface Coupon {
  id: string
  code: string
  name: string
  description: string
  discount_type: 'percentage' | 'fixed'
  discount_value: number
  min_amount?: number
  max_discount?: number
  valid_from: string
  valid_until: string
  usage_limit?: number
  used_count: number
  applicable_plans: string[]
  is_active: boolean
}

export interface PaymentStats {
  total_revenue: number
  total_orders: number
  successful_payments: number
  refund_rate: number
  popular_plans: {
    plan_id: string
    plan_name: string
    sales_count: number
    revenue: number
  }[]
  payment_method_stats: {
    method: string
    count: number
    percentage: number
  }[]
  monthly_revenue: {
    month: string
    revenue: number
    order_count: number
  }[]
}

export interface Invoice {
  id: string
  order_id: string
  invoice_number: string
  amount: number
  tax_amount?: number
  issued_date: string
  due_date?: string
  status: 'draft' | 'sent' | 'paid' | 'overdue'
  download_url?: string
  billing_info: {
    company_name?: string
    tax_id?: string
    address?: string
    email: string
  }
}

export interface RefundRequest {
  id: string
  order_id: string
  reason: string
  amount: number
  status: 'pending' | 'approved' | 'rejected' | 'processed'
  requested_at: string
  processed_at?: string
  admin_notes?: string
}

// 支付配置
export interface PaymentConfig {
  wechat: {
    app_id: string
    mch_id: string
    enabled: boolean
  }
  alipay: {
    app_id: string
    enabled: boolean
  }
  apple: {
    app_id: string
    enabled: boolean
    sandbox: boolean
  }
  currencies: string[]
  default_currency: string
  minimum_amount: number
  maximum_amount: number
}