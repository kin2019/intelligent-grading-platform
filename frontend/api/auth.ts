/**
 * 认证相关API
 */
import { get, post, put } from '@/utils/request'

// 登录请求参数
export interface LoginRequest {
  code: string
}

// 登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    openid: string
    nickname: string
    avatar_url: string
  }
}

// 用户信息
export interface UserInfo {
  id: number
  openid: string
  nickname: string
  avatar_url?: string
  phone?: string
  email?: string
  role: string
  grade?: string
  created_at?: string
  last_login_at?: string
  is_vip: boolean
  daily_quota: number
  daily_used: number
}

// 用户额度信息
export interface QuotaInfo {
  is_vip: boolean
  vip_type: string
  daily_quota: number
  daily_used: number
  monthly_quota: number
  monthly_used: number
  quota_reset_time: string
}

// 更新资料请求
export interface UpdateProfileRequest {
  nickname?: string
  avatar_url?: string
  gender?: number
  city?: string
}

/**
 * 微信小程序登录
 */
export const wechatLogin = (data: LoginRequest) => {
  return post<LoginResponse>('/auth/wechat/login', data)
}

/**
 * 刷新访问令牌
 */
export const refreshToken = () => {
  return post<{ access_token: string; token_type: string }>('/auth/refresh')
}

/**
 * 获取当前用户信息
 */
export const getCurrentUser = () => {
  return get<UserInfo>('/auth/me')
}

/**
 * 获取用户额度信息
 */
export const getQuotaInfo = () => {
  return get<QuotaInfo>('/auth/quota')
}

/**
 * 更新用户资料
 */
export const updateProfile = (data: UpdateProfileRequest) => {
  return put<UserInfo>('/auth/profile', data)
}