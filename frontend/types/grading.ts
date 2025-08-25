/**
 * 批改相关类型定义
 */

export type Subject = 'math' | 'chinese' | 'english' | 'physics' | 'chemistry' | 'biology'

export interface HomeworkSubmission {
  image_path: string
  subject: Subject
  student_id?: number
  upload_time: string
  homework_type?: 'exercise' | 'test' | 'homework'
  grade?: string
  chapter?: string
  description?: string
}

export interface GradingResult {
  id: string
  homework_id: string
  student_id: number
  subject: Subject
  status: 'processing' | 'completed' | 'failed'
  score: number
  total_score: number
  correct_count: number
  wrong_count: number
  total_count: number
  accuracy_rate: number
  
  // 错题信息
  wrong_questions?: WrongQuestion[]
  
  // 知识点分析
  knowledge_points?: KnowledgePoint[]
  
  // 学习建议
  suggestions?: string
  
  // 时间信息
  created_at: string
  completed_at?: string
  
  // 重批次数
  regrade_count?: number
  
  // 图片信息
  original_image: string
  result_image?: string
  
  // 元数据
  metadata?: {
    processing_time?: number
    confidence_score?: number
    ai_model_version?: string
  }
}

export interface WrongQuestion {
  id: string
  question_number: number
  question_content: string
  correct_answer: string
  user_answer: string
  explanation: string
  difficulty: 'easy' | 'medium' | 'hard'
  knowledge_points: string[]
  image_url?: string
  is_favorite?: boolean
  practice_count?: number
  mastered?: boolean
}

export interface KnowledgePoint {
  id: string
  name: string
  accuracy: number
  total_questions: number
  correct_questions: number
  difficulty_distribution: {
    easy: number
    medium: number
    hard: number
  }
  improvement_suggestions?: string[]
}

export interface PracticeQuestion {
  id: string
  original_question_id?: string
  question_content: string
  options?: string[]
  correct_answer: string
  explanation: string
  difficulty: 'easy' | 'medium' | 'hard'
  knowledge_points: string[]
  image_url?: string
  is_practice: boolean
  practice_id?: string
  completed?: boolean
  user_answers?: any[]
}

export interface GradingHistoryParams {
  page: number
  size: number
  subject?: Subject
  start_date?: string
  end_date?: string
  student_id?: number
}

export interface GradingHistoryResponse {
  data: GradingResult[]
  total: number
  page: number
  size: number
}

export interface SubjectStats {
  subject: Subject
  total_count: number
  accuracy_rate: number
  improvement_trend: number
  last_grading_time?: string
}

export interface LearningStats {
  daily_stats: {
    date: string
    grading_count: number
    accuracy_rate: number
  }[]
  weekly_summary: {
    total_grading: number
    average_accuracy: number
    improvement: number
    weak_points: string[]
  }
  monthly_trend: {
    month: string
    grading_count: number
    accuracy_rate: number
  }[]
  subject_performance: SubjectStats[]
}

export interface ErrorAnalysis {
  error_types: {
    type: string
    count: number
    percentage: number
    examples: string[]
  }[]
  frequent_mistakes: {
    knowledge_point: string
    error_count: number
    improvement_suggestions: string[]
  }[]
  difficulty_analysis: {
    easy: { total: number; correct: number; accuracy: number }
    medium: { total: number; correct: number; accuracy: number }
    hard: { total: number; correct: number; accuracy: number }
  }
}

export interface StudyPlan {
  id: string
  student_id: number
  subject: Subject
  target_accuracy: number
  current_accuracy: number
  plan_duration: number // 天数
  daily_tasks: {
    date: string
    tasks: {
      type: 'practice' | 'review' | 'new_content'
      content: string
      estimated_time: number // 分钟
      completed: boolean
    }[]
  }[]
  milestones: {
    date: string
    description: string
    achieved: boolean
  }[]
  created_at: string
  updated_at: string
}