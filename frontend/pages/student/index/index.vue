<template>
  <view class="student-home">
    <!-- 自定义导航栏 -->
    <z-navbar 
      title="智能批改" 
      :show-back="false"
      background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    >
      <template #right>
        <view class="nav-avatar" @click="goToProfile">
          <image 
            :src="userStore.userInfo?.avatar_url || '/static/avatar-default.png'" 
            mode="aspectFill"
          />
        </view>
      </template>
    </z-navbar>
    
    <!-- 页面内容 -->
    <view class="page-content">
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <view class="user-info">
          <view class="avatar">
            <image 
              :src="userStore.userInfo?.avatar_url || '/static/avatar-default.png'" 
              mode="aspectFill"
            />
          </view>
          <view class="info">
            <view class="name">{{ userStore.userInfo?.nickname || '未登录' }}</view>
            <view class="role">{{ userStore.userInfo?.role || '学生' }}</view>
          </view>
        </view>
        
        <view class="quota-info">
          <view class="quota-text">今日额度</view>
          <view class="quota-count">
            {{ userStore.userInfo?.daily_used || 0 }}/{{ userStore.userInfo?.daily_quota || 5 }}
          </view>
        </view>
      </view>
      
      <!-- 功能入口 -->
      <view class="function-grid">
        <view class="function-item" @click="goToHomeworkSubmit">
          <view class="function-icon">📷</view>
          <view class="function-text">拍照批改</view>
        </view>
        
        <view class="function-item" @click="goToErrorBook">
          <view class="function-icon">📚</view>
          <view class="function-text">错题本</view>
        </view>
        
        <view class="function-item" @click="goToStudyPlan">
          <view class="function-icon">📋</view>
          <view class="function-text">学习计划</view>
        </view>
        
        <view class="function-item" @click="goToParentBind">
          <view class="function-icon">👨‍👩‍👧‍👦</view>
          <view class="function-text">家长绑定</view>
        </view>
      </view>
      
      <!-- 学习数据 -->
      <view class="stats-section" v-if="dashboardData">
        <view class="section-title">今日学习</view>
        
        <view class="stats-grid">
          <view class="stat-item">
            <view class="stat-number">{{ dashboardData.daily_stats.today_corrections }}</view>
            <view class="stat-label">已批改</view>
          </view>
          
          <view class="stat-item">
            <view class="stat-number">{{ dashboardData.daily_stats.today_errors }}</view>
            <view class="stat-label">错题数</view>
          </view>
          
          <view class="stat-item">
            <view class="stat-number">{{ Math.round(dashboardData.daily_stats.accuracy_rate * 100) }}%</view>
            <view class="stat-label">正确率</view>
          </view>
          
          <view class="stat-item">
            <view class="stat-number">{{ Math.round(dashboardData.daily_stats.study_time / 60) }}</view>
            <view class="stat-label">学习时长(分)</view>
          </view>
        </view>
      </view>
      
      <!-- 最近作业 -->
      <view class="homework-section" v-if="dashboardData?.recent_homework?.length">
        <view class="section-title">最近作业</view>
        
        <view class="homework-list">
          <view 
            class="homework-item" 
            v-for="homework in dashboardData.recent_homework.slice(0, 3)" 
            :key="homework.id"
            @click="goToHomeworkDetail(homework.id)"
          >
            <view class="homework-info">
              <view class="homework-title">{{ homework.title }}</view>
              <view class="homework-meta">
                {{ homework.subject }} · {{ homework.total_questions }}题
              </view>
            </view>
            
            <view class="homework-stats">
              <view class="accuracy">{{ Math.round(homework.accuracy_rate * 100) }}%</view>
              <view class="status" :class="homework.status">
                {{ getStatusText(homework.status) }}
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 错题统计 -->
      <view class="error-section" v-if="dashboardData?.error_summary">
        <view class="section-title">错题统计</view>
        
        <view class="error-summary">
          <view class="error-stats">
            <view class="error-item">
              <view class="error-number">{{ dashboardData.error_summary.total_errors }}</view>
              <view class="error-label">总错题</view>
            </view>
            
            <view class="error-item">
              <view class="error-number">{{ dashboardData.error_summary.unreviewed_count }}</view>
              <view class="error-label">未复习</view>
            </view>
            
            <view class="error-item">
              <view class="error-number">{{ dashboardData.error_summary.this_week_errors }}</view>
              <view class="error-label">本周新增</view>
            </view>
          </view>
          
          <view class="error-subjects" v-if="dashboardData.error_summary.top_error_subjects?.length">
            <view class="subject-title">易错学科</view>
            <view class="subject-list">
              <view 
                class="subject-item" 
                v-for="subject in dashboardData.error_summary.top_error_subjects.slice(0, 3)"
                :key="subject.subject"
              >
                <view class="subject-name">{{ subject.subject }}</view>
                <view class="subject-count">{{ subject.count }}题</view>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 公告通知 -->
      <view class="announcement-section" v-if="dashboardData?.announcements?.length">
        <view class="section-title">最新公告</view>
        
        <view class="announcement-list">
          <view 
            class="announcement-item" 
            v-for="announcement in dashboardData.announcements.slice(0, 2)" 
            :key="announcement.id"
            :class="{ important: announcement.is_important }"
            @click="goToAnnouncementDetail(announcement.id)"
          >
            <view class="announcement-title">
              <text v-if="announcement.is_important" class="important-tag">重要</text>
              {{ announcement.title }}
            </view>
            <view class="announcement-content">{{ announcement.content }}</view>
            <view class="announcement-time">{{ formatTime(announcement.created_at) }}</view>
          </view>
        </view>
      </view>
      
      <!-- 测试区域 (开发阶段显示) -->
      <view class="test-section" v-if="showTestSection">
        <view class="section-title">API测试</view>
        
        <view class="test-buttons">
          <button class="test-btn" @click="testGetUserInfo">
            获取用户信息
          </button>
          
          <button class="test-btn" @click="testGetQuota">
            获取配额信息
          </button>
          
          <button class="test-btn" @click="testGetDashboard">
            获取仪表板数据
          </button>
          
          <button class="test-btn danger" @click="testLogout">
            退出登录
          </button>
        </view>
        
        <view class="result-section" v-if="testResult">
          <view class="section-title">测试结果</view>
          <view class="result-content">
            <text>{{ testResult }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getStudentDashboard, getErrorBook, getStudyPlan } from '@/api/student'
import type { StudentDashboard, ErrorBook, StudyPlan } from '@/api/student'

const userStore = useUserStore()
const testResult = ref('')
const dashboardData = ref<StudentDashboard | null>(null)
const errorBookData = ref<ErrorBook | null>(null)
const studyPlanData = ref<StudyPlan | null>(null)
const loading = ref(false)
const showTestSection = ref(process.env.NODE_ENV === 'development')

// 页面加载
onMounted(async () => {
  console.log('学生首页加载')
  
  // 检查登录状态
  if (!userStore.isLogin) {
    uni.showModal({
      title: '提示',
      content: '请先登录',
      showCancel: false,
      success: () => {
        uni.reLaunch({
          url: '/pages/common/login/index'
        })
      }
    })
    return
  }
  
  console.log('当前用户信息:', userStore.userInfo)
  
  // 加载仪表板数据
  await loadDashboardData()
})

/**
 * 加载仪表板数据
 */
const loadDashboardData = async () => {
  try {
    loading.value = true
    const data = await getStudentDashboard()
    dashboardData.value = data
    console.log('仪表板数据:', data)
  } catch (error: any) {
    console.error('加载仪表板数据失败:', error)
    uni.showToast({
      title: '加载数据失败',
      icon: 'error'
    })
  } finally {
    loading.value = false
  }
}

/**
 * 测试获取用户信息
 */
const testGetUserInfo = async () => {
  try {
    uni.showLoading({ title: '测试中...' })
    
    await userStore.fetchUserInfo()
    testResult.value = `✅ 获取用户信息成功:\n${JSON.stringify(userStore.userInfo, null, 2)}`
    
    uni.showToast({
      title: '测试成功',
      icon: 'success'
    })
  } catch (error: any) {
    testResult.value = `❌ 获取用户信息失败:\n${error.message}`
    
    uni.showToast({
      title: '测试失败',
      icon: 'error'
    })
  } finally {
    uni.hideLoading()
  }
}

/**
 * 测试获取配额信息
 */
const testGetQuota = async () => {
  try {
    uni.showLoading({ title: '测试中...' })
    
    await userStore.fetchQuotaInfo()
    testResult.value = `✅ 获取配额信息成功:\n${JSON.stringify(userStore.quotaInfo, null, 2)}`
    
    uni.showToast({
      title: '测试成功',
      icon: 'success'
    })
  } catch (error: any) {
    testResult.value = `❌ 获取配额信息失败:\n${error.message}`
    
    uni.showToast({
      title: '测试失败',
      icon: 'error'
    })
  } finally {
    uni.hideLoading()
  }
}

/**
 * 测试获取仪表板数据
 */
const testGetDashboard = async () => {
  try {
    uni.showLoading({ title: '测试中...' })
    
    const data = await getStudentDashboard()
    dashboardData.value = data
    testResult.value = `✅ 获取仪表板数据成功:\n${JSON.stringify(data, null, 2)}`
    
    uni.showToast({
      title: '测试成功',
      icon: 'success'
    })
  } catch (error: any) {
    testResult.value = `❌ 获取仪表板数据失败:\n${error.message}`
    
    uni.showToast({
      title: '测试失败',
      icon: 'error'
    })
  } finally {
    uni.hideLoading()
  }
}

/**
 * 测试退出登录
 */
const testLogout = () => {
  uni.showModal({
    title: '确认',
    content: '确定要退出登录吗？',
    success: async (res) => {
      if (res.confirm) {
        await userStore.logoutAction()
      }
    }
  })
}

/**
 * 页面导航方法
 */
const goToProfile = () => {
  uni.navigateTo({
    url: '/pages/student/profile/index'
  })
}

const goToHomeworkSubmit = () => {
  uni.navigateTo({
    url: '/pages/student/homework/submit/index'
  })
}

const goToErrorBook = () => {
  uni.navigateTo({
    url: '/pages/student/error-book/index'
  })
}

const goToStudyPlan = () => {
  uni.navigateTo({
    url: '/pages/student/study-plan/index'
  })
}

const goToParentBind = () => {
  uni.navigateTo({
    url: '/pages/student/parent-bind/index'
  })
}

const goToHomeworkDetail = (homeworkId: number) => {
  uni.navigateTo({
    url: `/pages/student/homework/detail/index?id=${homeworkId}`
  })
}

const goToAnnouncementDetail = (announcementId: number) => {
  uni.navigateTo({
    url: `/pages/common/announcement/detail/index?id=${announcementId}`
  })
}

/**
 * 工具方法
 */
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'completed': '已完成',
    'pending': '待批改',
    'reviewing': '批改中',
    'submitted': '已提交'
  }
  return statusMap[status] || status
}

const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天'
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}
</script>

<style lang="scss" scoped>
.student-home {
  min-height: 100vh;
  background: #f5f5f5;
}

.nav-avatar {
  width: 32px;
  height: 32px;
  border-radius: 16px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
  
  image {
    width: 100%;
    height: 100%;
  }
}

.page-content {
  padding: 20px;
}

.user-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 30px;
  overflow: hidden;
  margin-right: 16px;
  
  image {
    width: 100%;
    height: 100%;
  }
}

.info {
  .name {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 4px;
  }
  
  .role {
    font-size: 14px;
    color: #666;
  }
}

.quota-info {
  text-align: right;
  
  .quota-text {
    font-size: 12px;
    color: #999;
    margin-bottom: 4px;
  }
  
  .quota-count {
    font-size: 16px;
    font-weight: bold;
    color: #007AFF;
  }
}

.test-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
}

.test-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.test-btn {
  height: 44px;
  background: #007AFF;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  
  &.danger {
    background: #ff3b30;
  }
  
  &:active {
    opacity: 0.8;
  }
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.function-item {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  
  &:active {
    transform: scale(0.98);
  }
}

.function-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.function-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.stats-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #007AFF;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.homework-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.homework-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.homework-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: background 0.2s ease;
  
  &:active {
    background: #e9ecef;
  }
}

.homework-info {
  flex: 1;
}

.homework-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.homework-meta {
  font-size: 12px;
  color: #666;
}

.homework-stats {
  text-align: right;
}

.accuracy {
  font-size: 14px;
  font-weight: bold;
  color: #007AFF;
  margin-bottom: 4px;
}

.status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  
  &.completed {
    background: #d4edda;
    color: #155724;
  }
  
  &.pending {
    background: #fff3cd;
    color: #856404;
  }
  
  &.reviewing {
    background: #d1ecf1;
    color: #0c5460;
  }
}

.error-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.error-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.error-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.error-item {
  text-align: center;
  
  .error-number {
    font-size: 20px;
    font-weight: bold;
    color: #ff3b30;
    margin-bottom: 4px;
  }
  
  .error-label {
    font-size: 12px;
    color: #666;
  }
}

.error-subjects {
  .subject-title {
    font-size: 14px;
    font-weight: 500;
    color: #333;
    margin-bottom: 12px;
  }
  
  .subject-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .subject-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 6px;
    
    .subject-name {
      font-size: 14px;
      color: #333;
    }
    
    .subject-count {
      font-size: 12px;
      color: #ff3b30;
      font-weight: 500;
    }
  }
}

.announcement-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.announcement-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007AFF;
  transition: background 0.2s ease;
  
  &.important {
    border-left-color: #ff3b30;
    background: #fff5f5;
  }
  
  &:active {
    background: #e9ecef;
  }
}

.announcement-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
  
  .important-tag {
    background: #ff3b30;
    color: #ffffff;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    margin-right: 6px;
  }
}

.announcement-content {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.announcement-time {
  font-size: 12px;
  color: #999;
}

.result-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.result-content {
  background: #f8f8f8;
  border-radius: 8px;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  color: #333;
  max-height: 300px;
  overflow-y: auto;
}
</style>