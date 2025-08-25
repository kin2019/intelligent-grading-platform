/**
 * 学生端相关API
 */
import { get, post } from '@/utils/request'

// 学生仪表板数据
export interface StudentDashboard {
  user_info: {
    id: number
    nickname: string
    avatar_url?: string
    grade?: string
    level: string
    is_vip: boolean
    vip_expire_date?: string
  }
  daily_stats: {
    today_corrections: number
    today_errors: number
    accuracy_rate: number
    study_time: number
    daily_quota: number
    daily_used: number
    quota_reset_time: string
  }
  recent_homework: Array<{
    id: number
    subject: string
    title: string
    total_questions: number
    correct_count: number
    error_count: number
    accuracy_rate: number
    created_at: string
    status: string
  }>
  error_summary: {
    total_errors: number
    unreviewed_count: number
    this_week_errors: number
    top_error_subjects: Array<{
      subject: string
      count: number
    }>
  }
  announcements: Array<{
    id: number
    title: string
    content: string
    type: string
    created_at: string
    is_important: boolean
  }>
}

// 错题本数据
export interface ErrorBook {
  total_errors: number
  subject_stats: Array<{
    subject: string
    error_count: number
    unreviewed_count: number
    accuracy_rate: number
    improvement_rate: number
  }>
  recent_errors: Array<{
    id: number
    subject: string
    question_text: string
    user_answer: string
    correct_answer: string
    error_type: string
    knowledge_points: string[]
    difficulty_level: string
    is_reviewed: boolean
    review_count: number
    created_at: string
    last_review_at?: string
  }>
  knowledge_points: Array<{
    knowledge_point: string
    subject: string
    error_count: number
    mastery_level: number
    last_practice: string
  }>
}

// 学习计划
export interface StudyPlan {
  plan_id: string
  title: string
  created_at: string
  total_tasks: number
  completed_tasks: number
  estimated_time: number
  subjects: Array<{
    subject: string
    priority: string
    tasks: string[]
    estimated_time: number
  }>
  recommendations: string[]
}

// 反馈请求
export interface FeedbackRequest {
  feedback_type: string
  content: string
  rating: number
}

/**
 * 获取学生仪表板数据
 */
export const getStudentDashboard = () => {
  return get<StudentDashboard>('/student/dashboard')
}

/**
 * 获取错题本数据
 */
export const getErrorBook = (params?: {
  subject?: string
  page?: number
  limit?: number
}) => {
  return get<ErrorBook>('/student/error-book', params)
}

/**
 * 获取学习计划
 */
export const getStudyPlan = () => {
  return get<StudyPlan>('/student/study-plan')
}

/**
 * 提交学习反馈
 */
export const submitFeedback = (data: FeedbackRequest) => {
  return post('/student/feedback', data)
}