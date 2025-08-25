/**
 * 批改状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { uploadHomework, getGradingResult, getGradingHistory } from '@/api/grading'
import type { GradingResult, HomeworkSubmission, Subject } from '@/types/grading'

export const useGradingStore = defineStore('grading', () => {
  // 状态
  const currentHomework = ref<HomeworkSubmission | null>(null)
  const gradingResults = ref<GradingResult[]>([])
  const currentResult = ref<GradingResult | null>(null)
  const gradingHistory = ref<GradingResult[]>([])
  const uploading = ref(false)
  const grading = ref(false)
  const uploadProgress = ref(0)
  
  // 分页状态
  const historyPage = ref(1)
  const historyTotal = ref(0)
  const historyLoading = ref(false)
  const historyHasMore = computed(() => {
    return gradingHistory.value.length < historyTotal.value
  })
  
  // 统计数据
  const todayCount = ref(0)
  const weekCount = ref(0)
  const monthCount = ref(0)
  const totalCount = ref(0)
  const accuracyRate = ref(0)
  
  // 错题相关
  const wrongQuestions = ref<any[]>([])
  const practiceQuestions = ref<any[]>([])
  const practiceLoading = ref(false)
  
  /**
   * 上传作业图片
   */
  const uploadHomeworkImage = async (imagePath: string, subject: Subject, studentId?: number) => {
    try {
      uploading.value = true
      uploadProgress.value = 0
      
      const submission: HomeworkSubmission = {
        image_path: imagePath,
        subject,
        student_id: studentId,
        upload_time: new Date().toISOString()
      }
      
      currentHomework.value = submission
      
      // 模拟上传进度
      const progressTimer = setInterval(() => {
        if (uploadProgress.value < 90) {
          uploadProgress.value += Math.random() * 20
        }
      }, 100)
      
      const result = await uploadHomework(submission)
      
      clearInterval(progressTimer)
      uploadProgress.value = 100
      
      // 开始批改
      await startGrading(result.homework_id)
      
      return result
    } catch (error) {
      console.error('上传作业失败:', error)
      throw error
    } finally {
      uploading.value = false
      uploadProgress.value = 0
    }
  }
  
  /**
   * 开始批改
   */
  const startGrading = async (homeworkId: string) => {
    try {
      grading.value = true
      
      // 轮询获取批改结果
      const pollResult = async (): Promise<GradingResult> => {
        const result = await getGradingResult(homeworkId)
        
        if (result.status === 'processing') {
          // 继续轮询
          await new Promise(resolve => setTimeout(resolve, 2000))
          return pollResult()
        }
        
        return result
      }
      
      const result = await pollResult()
      
      currentResult.value = result
      gradingResults.value.unshift(result)
      
      // 更新统计数据
      updateStats()
      
      // 提取错题
      if (result.wrong_questions) {
        wrongQuestions.value = result.wrong_questions
      }
      
      return result
    } catch (error) {
      console.error('批改失败:', error)
      throw error
    } finally {
      grading.value = false
    }
  }
  
  /**
   * 获取批改历史
   */
  const loadGradingHistory = async (reset = false) => {
    if (historyLoading.value) return
    
    try {
      historyLoading.value = true
      
      if (reset) {
        historyPage.value = 1
        gradingHistory.value = []
      }
      
      const response = await getGradingHistory({
        page: historyPage.value,
        size: 20
      })
      
      if (reset) {
        gradingHistory.value = response.data
      } else {
        gradingHistory.value.push(...response.data)
      }
      
      historyTotal.value = response.total
      historyPage.value += 1
      
    } catch (error) {
      console.error('加载历史记录失败:', error)
    } finally {
      historyLoading.value = false
    }
  }
  
  /**
   * 获取错题练习
   */
  const generatePracticeQuestions = async (subject: Subject, knowledgePoints?: string[]) => {
    try {
      practiceLoading.value = true
      
      // 这里应该调用生成错题练习的API
      // const questions = await generatePractice({ subject, knowledgePoints })
      
      // 模拟数据
      const questions = wrongQuestions.value.map(q => ({
        ...q,
        is_practice: true,
        practice_id: Date.now() + Math.random()
      }))
      
      practiceQuestions.value = questions
      return questions
      
    } catch (error) {
      console.error('生成练习题失败:', error)
      throw error
    } finally {
      practiceLoading.value = false
    }
  }
  
  /**
   * 提交练习结果
   */
  const submitPracticeResult = async (practiceId: string, answers: any[]) => {
    try {
      // 这里应该调用提交练习结果的API
      // await submitPractice({ practiceId, answers })
      
      // 更新练习状态
      practiceQuestions.value = practiceQuestions.value.map(q => {
        if (q.practice_id === practiceId) {
          return {
            ...q,
            completed: true,
            user_answers: answers
          }
        }
        return q
      })
      
    } catch (error) {
      console.error('提交练习结果失败:', error)
      throw error
    }
  }
  
  /**
   * 收藏错题
   */
  const favoriteQuestion = async (questionId: string) => {
    try {
      // 调用收藏API
      // await favoriteQuestionApi(questionId)
      
      // 更新本地状态
      wrongQuestions.value = wrongQuestions.value.map(q => {
        if (q.id === questionId) {
          return { ...q, is_favorite: true }
        }
        return q
      })
      
    } catch (error) {
      console.error('收藏错题失败:', error)
      throw error
    }
  }
  
  /**
   * 取消收藏错题
   */
  const unfavoriteQuestion = async (questionId: string) => {
    try {
      // 调用取消收藏API
      // await unfavoriteQuestionApi(questionId)
      
      // 更新本地状态
      wrongQuestions.value = wrongQuestions.value.map(q => {
        if (q.id === questionId) {
          return { ...q, is_favorite: false }
        }
        return q
      })
      
    } catch (error) {
      console.error('取消收藏失败:', error)
      throw error
    }
  }
  
  /**
   * 删除批改记录
   */
  const deleteGradingResult = async (resultId: string) => {
    try {
      // 调用删除API
      // await deleteGradingApi(resultId)
      
      // 更新本地状态
      gradingResults.value = gradingResults.value.filter(r => r.id !== resultId)
      gradingHistory.value = gradingHistory.value.filter(r => r.id !== resultId)
      
      if (currentResult.value?.id === resultId) {
        currentResult.value = null
      }
      
      // 更新统计
      updateStats()
      
    } catch (error) {
      console.error('删除记录失败:', error)
      throw error
    }
  }
  
  /**
   * 重新批改
   */
  const regrade = async (homeworkId: string) => {
    try {
      // 调用重新批改API
      // const result = await regradeApi(homeworkId)
      
      // 模拟重新批改
      grading.value = true
      await new Promise(resolve => setTimeout(resolve, 3000))
      grading.value = false
      
      // 更新结果
      const updatedResult = gradingResults.value.find(r => r.homework_id === homeworkId)
      if (updatedResult) {
        updatedResult.regrade_count = (updatedResult.regrade_count || 0) + 1
        currentResult.value = updatedResult
      }
      
    } catch (error) {
      console.error('重新批改失败:', error)
      throw error
    }
  }
  
  /**
   * 更新统计数据
   */
  const updateStats = () => {
    const now = new Date()
    const today = now.toDateString()
    const thisWeek = getWeekStart(now).getTime()
    const thisMonth = new Date(now.getFullYear(), now.getMonth(), 1).getTime()
    
    const results = gradingResults.value
    
    todayCount.value = results.filter(r => 
      new Date(r.created_at).toDateString() === today
    ).length
    
    weekCount.value = results.filter(r => 
      new Date(r.created_at).getTime() >= thisWeek
    ).length
    
    monthCount.value = results.filter(r => 
      new Date(r.created_at).getTime() >= thisMonth
    ).length
    
    totalCount.value = results.length
    
    // 计算平均正确率
    if (results.length > 0) {
      const totalAccuracy = results.reduce((sum, r) => {
        return sum + (r.total_count > 0 ? (r.correct_count / r.total_count) * 100 : 0)
      }, 0)
      accuracyRate.value = Math.round(totalAccuracy / results.length)
    } else {
      accuracyRate.value = 0
    }
  }
  
  /**
   * 获取周开始时间
   */
  const getWeekStart = (date: Date) => {
    const d = new Date(date)
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1)
    return new Date(d.setDate(diff))
  }
  
  /**
   * 清空当前批改
   */
  const clearCurrentGrading = () => {
    currentHomework.value = null
    currentResult.value = null
    uploading.value = false
    grading.value = false
    uploadProgress.value = 0
  }
  
  /**
   * 按学科筛选结果
   */
  const getResultsBySubject = (subject: Subject) => {
    return gradingResults.value.filter(r => r.subject === subject)
  }
  
  /**
   * 按日期筛选结果
   */
  const getResultsByDate = (startDate: string, endDate: string) => {
    const start = new Date(startDate).getTime()
    const end = new Date(endDate).getTime()
    
    return gradingResults.value.filter(r => {
      const date = new Date(r.created_at).getTime()
      return date >= start && date <= end
    })
  }
  
  /**
   * 获取知识点统计
   */
  const getKnowledgePointStats = () => {
    const stats: Record<string, { total: number; correct: number; accuracy: number }> = {}
    
    gradingResults.value.forEach(result => {
      if (result.knowledge_points) {
        result.knowledge_points.forEach(kp => {
          if (!stats[kp.name]) {
            stats[kp.name] = { total: 0, correct: 0, accuracy: 0 }
          }
          
          stats[kp.name].total += kp.total_questions || 1
          stats[kp.name].correct += Math.round((kp.accuracy / 100) * (kp.total_questions || 1))
          stats[kp.name].accuracy = stats[kp.name].total > 0 
            ? Math.round((stats[kp.name].correct / stats[kp.name].total) * 100)
            : 0
        })
      }
    })
    
    return Object.entries(stats).map(([name, data]) => ({
      name,
      ...data
    }))
  }
  
  return {
    // 状态
    currentHomework,
    gradingResults,
    currentResult,
    gradingHistory,
    uploading,
    grading,
    uploadProgress,
    
    // 分页状态
    historyLoading,
    historyHasMore,
    
    // 统计数据
    todayCount,
    weekCount,
    monthCount,
    totalCount,
    accuracyRate,
    
    // 错题相关
    wrongQuestions,
    practiceQuestions,
    practiceLoading,
    
    // 方法
    uploadHomeworkImage,
    startGrading,
    loadGradingHistory,
    generatePracticeQuestions,
    submitPracticeResult,
    favoriteQuestion,
    unfavoriteQuestion,
    deleteGradingResult,
    regrade,
    clearCurrentGrading,
    getResultsBySubject,
    getResultsByDate,
    getKnowledgePointStats
  }
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'grading-store',
        storage: {
          getItem: (key: string) => uni.getStorageSync(key),
          setItem: (key: string, value: any) => uni.setStorageSync(key, value),
          removeItem: (key: string) => uni.removeStorageSync(key)
        },
        paths: ['gradingResults', 'currentResult', 'wrongQuestions', 'todayCount', 'weekCount', 'monthCount', 'totalCount', 'accuracyRate']
      }
    ]
  }
})