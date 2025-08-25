/**
 * 批改相关API接口
 */
import { request } from '@/utils/request'
import type { 
  HomeworkSubmission, 
  GradingResult, 
  GradingHistoryParams, 
  GradingHistoryResponse,
  PracticeQuestion,
  Subject
} from '@/types/grading'

/**
 * 上传作业图片
 */
export const uploadHomework = (submission: HomeworkSubmission) => {
  return request<{ homework_id: string }>({
    url: '/grading/upload',
    method: 'POST',
    data: submission
  })
}

/**
 * 获取批改结果
 */
export const getGradingResult = (homeworkId: string) => {
  return request<GradingResult>({
    url: `/grading/result/${homeworkId}`,
    method: 'GET'
  })
}

/**
 * 获取批改历史
 */
export const getGradingHistory = (params: GradingHistoryParams) => {
  return request<GradingHistoryResponse>({
    url: '/grading/history',
    method: 'GET',
    data: params
  })
}

/**
 * 重新批改
 */
export const regradeHomework = (homeworkId: string) => {
  return request<GradingResult>({
    url: `/grading/regrade/${homeworkId}`,
    method: 'POST'
  })
}

/**
 * 删除批改记录
 */
export const deleteGradingRecord = (resultId: string) => {
  return request<{ success: boolean }>({
    url: `/grading/result/${resultId}`,
    method: 'DELETE'
  })
}

/**
 * 生成练习题
 */
export const generatePracticeQuestions = (params: {
  subject: Subject
  knowledge_points?: string[]
  difficulty?: 'easy' | 'medium' | 'hard'
  count?: number
}) => {
  return request<PracticeQuestion[]>({
    url: '/grading/practice/generate',
    method: 'POST',
    data: params
  })
}

/**
 * 提交练习结果
 */
export const submitPracticeResult = (params: {
  practice_id: string
  answers: any[]
}) => {
  return request<{ score: number; analysis: any }>({
    url: '/grading/practice/submit',
    method: 'POST',
    data: params
  })
}

/**
 * 收藏错题
 */
export const favoriteQuestion = (questionId: string) => {
  return request<{ success: boolean }>({
    url: `/grading/question/${questionId}/favorite`,
    method: 'POST'
  })
}

/**
 * 取消收藏错题
 */
export const unfavoriteQuestion = (questionId: string) => {
  return request<{ success: boolean }>({
    url: `/grading/question/${questionId}/favorite`,
    method: 'DELETE'
  })
}

/**
 * 获取收藏的错题
 */
export const getFavoriteQuestions = (params: {
  subject?: Subject
  page?: number
  size?: number
}) => {
  return request<{
    data: any[]
    total: number
  }>({
    url: '/grading/questions/favorites',
    method: 'GET',
    data: params
  })
}

/**
 * 获取学习统计
 */
export const getLearningStats = (params: {
  student_id?: number
  start_date?: string
  end_date?: string
}) => {
  return request<any>({
    url: '/grading/stats',
    method: 'GET',
    data: params
  })
}

/**
 * 获取错题分析
 */
export const getErrorAnalysis = (params: {
  student_id?: number
  subject?: Subject
  time_range?: 'week' | 'month' | 'quarter'
}) => {
  return request<any>({
    url: '/grading/analysis/errors',
    method: 'GET',
    data: params
  })
}

/**
 * 导出学习报告
 */
export const exportLearningReport = (params: {
  student_id?: number
  subject?: Subject
  start_date: string
  end_date: string
  format?: 'pdf' | 'excel'
}) => {
  return request<{ download_url: string }>({
    url: '/grading/export/report',
    method: 'POST',
    data: params
  })
}

/**
 * 获取知识点掌握情况
 */
export const getKnowledgePointMastery = (params: {
  student_id?: number
  subject: Subject
}) => {
  return request<any[]>({
    url: '/grading/knowledge-points',
    method: 'GET',
    data: params
  })
}

/**
 * 批量上传作业
 */
export const batchUploadHomework = (submissions: HomeworkSubmission[]) => {
  return request<{ 
    success_count: number
    failed_count: number
    results: { homework_id: string; status: string }[]
  }>({
    url: '/grading/batch-upload',
    method: 'POST',
    data: { submissions }
  })
}