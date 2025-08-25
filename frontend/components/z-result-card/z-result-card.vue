<template>
  <z-card
    :clickable="clickable"
    :shadow="shadow"
    class="z-result-card"
    :class="resultClass"
    @click="handleClick"
  >
    <!-- 卡片头部 -->
    <template #header>
      <view class="result-header">
        <view class="subject-info">
          <text class="subject-icon">{{ subjectInfo.icon }}</text>
          <view class="subject-text">
            <text class="subject-name">{{ subjectInfo.name }}</text>
            <text class="result-time">{{ formatTime(result.created_at) }}</text>
          </view>
        </view>
        <view class="score-badge" :class="scoreClass">
          <text class="score-text">{{ result.score }}/{{ result.total_score }}</text>
        </view>
      </view>
    </template>
    
    <!-- 卡片内容 -->
    <view class="result-content">
      <!-- 正确率统计 -->
      <view class="accuracy-section">
        <view class="accuracy-circle" :style="circleStyle">
          <text class="accuracy-text">{{ accuracyRate }}%</text>
          <text class="accuracy-label">正确率</text>
        </view>
        
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-value">{{ result.correct_count }}</text>
            <text class="stat-label">正确</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ result.wrong_count }}</text>
            <text class="stat-label">错误</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ result.total_count }}</text>
            <text class="stat-label">总题</text>
          </view>
        </view>
      </view>
      
      <!-- 错题预览 -->
      <view v-if="result.wrong_questions && result.wrong_questions.length > 0" class="wrong-preview">
        <view class="preview-header">
          <text class="preview-title">错题预览</text>
          <text class="preview-count">{{ result.wrong_questions.length }}道</text>
        </view>
        
        <scroll-view
          class="wrong-list"
          scroll-x
          :show-scrollbar="false"
        >
          <view class="wrong-items">
            <view
              v-for="(question, index) in result.wrong_questions.slice(0, 5)"
              :key="question.id"
              class="wrong-item"
              @click.stop="viewQuestion(question, index)"
            >
              <image
                :src="question.image_url"
                class="question-image"
                mode="aspectFit"
              />
              <text class="question-number">{{ index + 1 }}</text>
            </view>
            
            <!-- 更多按钮 -->
            <view
              v-if="result.wrong_questions.length > 5"
              class="wrong-item more-item"
              @click.stop="viewAllQuestions"
            >
              <text class="more-text">+{{ result.wrong_questions.length - 5 }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
      
      <!-- 知识点分析 -->
      <view v-if="result.knowledge_points" class="knowledge-section">
        <view class="knowledge-header">
          <text class="knowledge-title">知识点掌握情况</text>
        </view>
        
        <view class="knowledge-list">
          <view
            v-for="point in result.knowledge_points"
            :key="point.id"
            class="knowledge-item"
          >
            <view class="knowledge-info">
              <text class="knowledge-name">{{ point.name }}</text>
              <text class="knowledge-accuracy">{{ point.accuracy }}%</text>
            </view>
            <view class="knowledge-bar">
              <view
                class="knowledge-progress"
                :style="{ width: point.accuracy + '%' }"
                :class="getKnowledgeClass(point.accuracy)"
              />
            </view>
          </view>
        </view>
      </view>
      
      <!-- 建议区域 -->
      <view v-if="result.suggestions" class="suggestions-section">
        <view class="suggestions-header">
          <text class="suggestions-title">学习建议</text>
        </view>
        
        <view class="suggestions-content">
          <text class="suggestion-text">{{ result.suggestions }}</text>
        </view>
      </view>
    </view>
    
    <!-- 卡片底部操作 -->
    <template #footer>
      <view class="result-actions">
        <z-button
          v-if="result.wrong_questions && result.wrong_questions.length > 0"
          type="secondary"
          size="small"
          @click.stop="practiceWrongQuestions"
        >
          错题练习
        </z-button>
        
        <z-button
          type="primary"
          size="small"
          @click.stop="viewDetailReport"
        >
          查看详情
        </z-button>
      </view>
    </template>
  </z-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GradingResult, Subject } from '@/types/grading'

interface Props {
  result: GradingResult
  subject: Subject
  clickable?: boolean
  shadow?: 'none' | 'light' | 'normal' | 'heavy'
}

const props = withDefaults(defineProps<Props>(), {
  clickable: true,
  shadow: 'normal'
})

const emit = defineEmits<{
  click: [result: GradingResult]
  viewQuestion: [question: any, index: number]
  viewAllQuestions: []
  practiceWrongQuestions: []
  viewDetailReport: []
}>()

// 学科信息映射
const subjectMap = {
  math: { name: '数学', icon: '📐', color: '#007AFF' },
  chinese: { name: '语文', icon: '📚', color: '#FF3B30' },
  english: { name: '英语', icon: '🇺🇸', color: '#34C759' },
  physics: { name: '物理', icon: '⚛️', color: '#AF52DE' },
  chemistry: { name: '化学', icon: '⚗️', color: '#FF9500' },
  biology: { name: '生物', icon: '🧬', color: '#32D74B' }
}

// 计算属性
const subjectInfo = computed(() => subjectMap[props.subject] || subjectMap.math)

const accuracyRate = computed(() => {
  if (props.result.total_count === 0) return 0
  return Math.round((props.result.correct_count / props.result.total_count) * 100)
})

const scoreClass = computed(() => {
  const rate = accuracyRate.value
  if (rate >= 90) return 'score-excellent'
  if (rate >= 80) return 'score-good'
  if (rate >= 60) return 'score-normal'
  return 'score-poor'
})

const resultClass = computed(() => {
  return [
    `result-${props.subject}`,
    scoreClass.value
  ]
})

const circleStyle = computed(() => {
  const rate = accuracyRate.value
  const color = subjectInfo.value.color
  
  return {
    background: `conic-gradient(${color} ${rate * 3.6}deg, #f0f0f0 0deg)`
  }
})

// 方法
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString()
}

const getKnowledgeClass = (accuracy: number) => {
  if (accuracy >= 80) return 'knowledge-excellent'
  if (accuracy >= 60) return 'knowledge-good'
  return 'knowledge-poor'
}

// 事件处理
const handleClick = () => {
  emit('click', props.result)
}

const viewQuestion = (question: any, index: number) => {
  emit('viewQuestion', question, index)
}

const viewAllQuestions = () => {
  emit('viewAllQuestions')
}

const practiceWrongQuestions = () => {
  emit('practiceWrongQuestions')
}

const viewDetailReport = () => {
  emit('viewDetailReport')
}
</script>

<style lang="scss" scoped>
.z-result-card {
  margin-bottom: $spacing-base;
  overflow: hidden;
  
  // 学科主题色
  &.result-math {
    border-left: 6rpx solid $subject-math;
  }
  
  &.result-chinese {
    border-left: 6rpx solid $subject-chinese;
  }
  
  &.result-english {
    border-left: 6rpx solid $subject-english;
  }
  
  &.result-physics {
    border-left: 6rpx solid $subject-physics;
  }
  
  &.result-chemistry {
    border-left: 6rpx solid $subject-chemistry;
  }
  
  &.result-biology {
    border-left: 6rpx solid $subject-biology;
  }
}

.result-header {
  @include flex-between;
  align-items: center;
}

.subject-info {
  @include flex-start;
  align-items: center;
  gap: $spacing-sm;
}

.subject-icon {
  font-size: 48rpx;
}

.subject-text {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.subject-name {
  font-size: $font-size-lg;
  font-weight: $font-weight-medium;
  color: $text-color;
}

.result-time {
  font-size: $font-size-sm;
  color: $text-color-secondary;
}

.score-badge {
  padding: 8rpx 16rpx;
  border-radius: $radius-large;
  
  &.score-excellent {
    background-color: rgba(52, 199, 89, 0.1);
    color: $success-color;
  }
  
  &.score-good {
    background-color: rgba(0, 122, 255, 0.1);
    color: $primary-color;
  }
  
  &.score-normal {
    background-color: rgba(255, 149, 0, 0.1);
    color: $warning-color;
  }
  
  &.score-poor {
    background-color: rgba(255, 59, 48, 0.1);
    color: $error-color;
  }
}

.score-text {
  font-size: $font-size-lg;
  font-weight: $font-weight-medium;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.accuracy-section {
  @include flex-start;
  gap: $spacing-lg;
}

.accuracy-circle {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  @include flex-center;
  flex-direction: column;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    inset: 8rpx;
    background-color: $bg-color-white;
    border-radius: 50%;
  }
}

.accuracy-text {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: $text-color;
  z-index: 1;
}

.accuracy-label {
  font-size: $font-size-sm;
  color: $text-color-secondary;
  z-index: 1;
}

.stats-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-base;
}

.stat-item {
  @include flex-center;
  flex-direction: column;
  gap: 8rpx;
}

.stat-value {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: $text-color;
}

.stat-label {
  font-size: $font-size-sm;
  color: $text-color-secondary;
}

.wrong-preview {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.preview-header {
  @include flex-between;
  align-items: center;
}

.preview-title {
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
  color: $text-color;
}

.preview-count {
  font-size: $font-size-sm;
  color: $error-color;
  background-color: rgba(255, 59, 48, 0.1);
  padding: 4rpx 12rpx;
  border-radius: $radius-large;
}

.wrong-list {
  width: 100%;
}

.wrong-items {
  @include flex-start;
  gap: $spacing-sm;
  padding-bottom: $spacing-sm;
}

.wrong-item {
  position: relative;
  width: 120rpx;
  height: 120rpx;
  border-radius: $radius-medium;
  overflow: hidden;
  background-color: $gray-1;
  @include flex-center;
  flex-shrink: 0;
  
  &.more-item {
    background-color: $gray-2;
    border: 2rpx dashed $gray-4;
  }
}

.question-image {
  width: 100%;
  height: 100%;
}

.question-number {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  width: 32rpx;
  height: 32rpx;
  @include flex-center;
  background-color: rgba(255, 59, 48, 0.9);
  color: $text-color-white;
  font-size: 20rpx;
  border-radius: 50%;
}

.more-text {
  font-size: $font-size-sm;
  color: $text-color-secondary;
  font-weight: $font-weight-medium;
}

.knowledge-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.knowledge-header {
  @include flex-between;
  align-items: center;
}

.knowledge-title {
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
  color: $text-color;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.knowledge-item {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.knowledge-info {
  @include flex-between;
  align-items: center;
}

.knowledge-name {
  font-size: $font-size-sm;
  color: $text-color;
}

.knowledge-accuracy {
  font-size: $font-size-sm;
  color: $text-color-secondary;
  font-weight: $font-weight-medium;
}

.knowledge-bar {
  width: 100%;
  height: 8rpx;
  background-color: $gray-2;
  border-radius: 4rpx;
  overflow: hidden;
}

.knowledge-progress {
  height: 100%;
  border-radius: 4rpx;
  transition: width $animation-base ease;
  
  &.knowledge-excellent {
    background-color: $success-color;
  }
  
  &.knowledge-good {
    background-color: $primary-color;
  }
  
  &.knowledge-poor {
    background-color: $error-color;
  }
}

.suggestions-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.suggestions-header {
  @include flex-between;
  align-items: center;
}

.suggestions-title {
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
  color: $text-color;
}

.suggestions-content {
  padding: $spacing-base;
  background-color: $gray-1;
  border-radius: $radius-medium;
  border-left: 6rpx solid $primary-color;
}

.suggestion-text {
  font-size: $font-size-sm;
  color: $text-color-secondary;
  line-height: 1.6;
}

.result-actions {
  @include flex-end;
  gap: $spacing-sm;
}
</style>