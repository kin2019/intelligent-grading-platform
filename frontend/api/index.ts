/**
 * API接口统一导出
 */

// 认证相关
export * from './auth'

// 用户相关
export * from './user'

// 学生相关
export * from './student'

// 批改相关
export * from './grading'

// 支付相关
export * from './payment'

// 导出请求工具
export { request, get, post, put, del, upload, download } from '@/utils/request'

// API基础配置
export const API_CONFIG = {
  // 开发环境
  DEV_BASE_URL: 'http://localhost:8000/api',
  
  // 生产环境
  PROD_BASE_URL: 'https://api.zyjc.com/api',
  
  // 请求超时时间
  TIMEOUT: 30000,
  
  // 重试次数
  RETRY_COUNT: 3,
  
  // 分页默认大小
  DEFAULT_PAGE_SIZE: 20
}

// 错误码定义
export const ERROR_CODES = {
  // 通用错误
  SUCCESS: 0,
  SYSTEM_ERROR: 10000,
  
  // 认证错误
  INVALID_TOKEN: 10001,
  TOKEN_EXPIRED: 10002,
  PERMISSION_DENIED: 10003,
  
  // 用户错误
  USER_NOT_FOUND: 11001,
  USER_DISABLED: 11002,
  
  // 业务错误
  QUOTA_EXCEEDED: 20001,
  VIP_REQUIRED: 20002,
  INVALID_SUBJECT: 20003,
  
  // 支付错误
  PAYMENT_FAILED: 30001,
  ORDER_NOT_FOUND: 30002,
  REFUND_FAILED: 30003
} as const

// 业务状态码映射
export const STATUS_CODE_MAP = {
  [ERROR_CODES.SUCCESS]: '操作成功',
  [ERROR_CODES.SYSTEM_ERROR]: '系统错误',
  [ERROR_CODES.INVALID_TOKEN]: '登录状态无效',
  [ERROR_CODES.TOKEN_EXPIRED]: '登录已过期',
  [ERROR_CODES.PERMISSION_DENIED]: '权限不足',
  [ERROR_CODES.USER_NOT_FOUND]: '用户不存在',
  [ERROR_CODES.USER_DISABLED]: '用户已被禁用',
  [ERROR_CODES.QUOTA_EXCEEDED]: '使用次数已达上限',
  [ERROR_CODES.VIP_REQUIRED]: '需要VIP权限',
  [ERROR_CODES.INVALID_SUBJECT]: '不支持的学科',
  [ERROR_CODES.PAYMENT_FAILED]: '支付失败',
  [ERROR_CODES.ORDER_NOT_FOUND]: '订单不存在',
  [ERROR_CODES.REFUND_FAILED]: '退款失败'
} as const