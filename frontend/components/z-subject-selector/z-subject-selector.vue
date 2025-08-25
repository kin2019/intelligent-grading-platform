<template>
  <view class="z-subject-selector" :class="selectorClass">
    <!-- 网格布局 -->
    <view v-if="layout === 'grid'" class="subjects-grid">
      <view
        v-for="subject in availableSubjects"
        :key="subject.key"
        class="subject-item grid-item"
        :class="getSubjectClass(subject)"
        @click="handleSubjectSelect(subject)"
      >
        <view class="subject-icon-wrapper">
          <text class="subject-icon">{{ subject.icon }}</text>
          <view v-if="!subject.available" class="coming-soon">敬请期待</view>
        </view>
        <text class="subject-name">{{ subject.name }}</text>
        <text class="subject-desc">{{ subject.description }}</text>
        
        <!-- 选中标识 -->
        <view v-if="modelValue === subject.key" class="selected-indicator">
          <text class="check-icon">✓</text>
        </view>
      </view>
    </view>
    
    <!-- 水平滚动布局 -->
    <scroll-view
      v-else-if="layout === 'horizontal'"
      class="subjects-horizontal"
      scroll-x
      :show-scrollbar="false"
    >
      <view class="horizontal-container">
        <view
          v-for="subject in availableSubjects"
          :key="subject.key"
          class="subject-item horizontal-item"
          :class="getSubjectClass(subject)"
          @click="handleSubjectSelect(subject)"
        >
          <text class="subject-icon">{{ subject.icon }}</text>
          <text class="subject-name">{{ subject.name }}</text>
          
          <!-- 选中标识 -->
          <view v-if="modelValue === subject.key" class="selected-dot" />
        </view>
      </view>
    </scroll-view>
    
    <!-- 列表布局 -->
    <view v-else class="subjects-list">
      <view
        v-for="subject in availableSubjects"
        :key="subject.key"
        class="subject-item list-item"
        :class="getSubjectClass(subject)"
        @click="handleSubjectSelect(subject)"
      >
        <view class="item-left">
          <text class="subject-icon">{{ subject.icon }}</text>
          <view class="subject-info">
            <text class="subject-name">{{ subject.name }}</text>
            <text class="subject-desc">{{ subject.description }}</text>
          </view>
        </view>
        
        <view class="item-right">
          <view v-if="!subject.available" class="coming-tag">
            <text class="coming-text">敬请期待</text>
          </view>
          <view v-else-if="modelValue === subject.key" class="selected-check">
            <text class="check-icon">✓</text>
          </view>
          <text v-else class="arrow-icon">›</text>
        </view>
      </view>
    </view>
    
    <!-- 底部操作栏 -->
    <view v-if="showConfirm" class="selector-footer">
      <z-button
        type="primary"
        block
        :disabled="!modelValue"
        @click="handleConfirm"
      >
        确认选择
      </z-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import type { Subject } from '@/types/app'

interface Props {
  modelValue?: Subject | null
  layout?: 'grid' | 'horizontal' | 'list'
  size?: 'small' | 'medium' | 'large'
  showUnavailable?: boolean
  showConfirm?: boolean
  maxColumns?: number
  filterSubjects?: Subject[]
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'grid',
  size: 'medium',
  showUnavailable: true,
  showConfirm: false,
  maxColumns: 3
})

const emit = defineEmits<{
  'update:modelValue': [value: Subject | null]
  change: [value: Subject | null]
  confirm: [value: Subject | null]
  subjectClick: [subject: any]
}>()

const appStore = useAppStore()

// 计算可用学科
const availableSubjects = computed(() => {
  let subjects = appStore.subjects
  
  // 过滤指定学科
  if (props.filterSubjects && props.filterSubjects.length > 0) {
    subjects = subjects.filter(s => props.filterSubjects!.includes(s.key))
  }
  
  // 是否显示不可用学科
  if (!props.showUnavailable) {
    subjects = subjects.filter(s => s.available)
  }
  
  return subjects
})

// 计算样式类
const selectorClass = computed(() => {
  const classes = [`selector-${props.layout}`, `selector-${props.size}`]
  
  if (props.layout === 'grid') {
    classes.push(`grid-cols-${props.maxColumns}`)
  }
  
  return classes
})

// 获取学科样式类
const getSubjectClass = (subject: any) => {
  const classes = [`subject-${subject.key}`]
  
  if (props.modelValue === subject.key) {
    classes.push('subject-selected')
  }
  
  if (!subject.available) {
    classes.push('subject-disabled')
  }
  
  return classes
}

// 处理学科选择
const handleSubjectSelect = (subject: any) => {
  if (!subject.available) {
    uni.showToast({
      title: '该学科暂未开放',
      icon: 'none'
    })
    return
  }
  
  emit('update:modelValue', subject.key)
  emit('change', subject.key)
  emit('subjectClick', subject)
  
  // 触觉反馈
  uni.vibrateShort({
    type: 'light'
  })
}

// 确认选择
const handleConfirm = () => {
  emit('confirm', props.modelValue)
}
</script>

<style lang="scss" scoped>
.z-subject-selector {
  width: 100%;
  
  &.selector-small {
    .subject-icon {
      font-size: 32rpx;
    }
    
    .subject-name {
      font-size: $font-size-sm;
    }
    
    .subject-desc {
      font-size: 20rpx;
    }
  }
  
  &.selector-medium {
    .subject-icon {
      font-size: 48rpx;
    }
    
    .subject-name {
      font-size: $font-size-base;
    }
    
    .subject-desc {
      font-size: $font-size-sm;
    }
  }
  
  &.selector-large {
    .subject-icon {
      font-size: 64rpx;
    }
    
    .subject-name {
      font-size: $font-size-lg;
    }
    
    .subject-desc {
      font-size: $font-size-base;
    }
  }
}

// 网格布局
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(var(--columns, 3), 1fr);
  gap: $spacing-base;
  
  .grid-cols-2 & {
    --columns: 2;
  }
  
  .grid-cols-3 & {
    --columns: 3;
  }
  
  .grid-cols-4 & {
    --columns: 4;
  }
}

.grid-item {
  @include flex-center;
  flex-direction: column;
  gap: $spacing-sm;
  padding: $spacing-lg;
  background-color: $bg-color-white;
  border-radius: $radius-large;
  box-shadow: $shadow-card;
  transition: all $animation-base ease;
  position: relative;
  min-height: 200rpx;
  
  &:active {
    transform: scale(0.98);
  }
  
  &.subject-selected {
    transform: scale(1.02);
    box-shadow: $shadow-float;
  }
  
  &.subject-disabled {
    opacity: 0.6;
    
    .subject-icon-wrapper {
      position: relative;
    }
    
    .coming-soon {
      position: absolute;
      bottom: -8rpx;
      left: 50%;
      transform: translateX(-50%);
      background-color: $warning-color;
      color: $text-color-white;
      font-size: 18rpx;
      padding: 2rpx 8rpx;
      border-radius: $radius-small;
      white-space: nowrap;
    }
  }
}

.subject-icon-wrapper {
  position: relative;
  @include flex-center;
}

.subject-name {
  font-weight: $font-weight-medium;
  color: $text-color;
  text-align: center;
}

.subject-desc {
  color: $text-color-secondary;
  text-align: center;
  line-height: 1.4;
}

.selected-indicator {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 40rpx;
  height: 40rpx;
  @include flex-center;
  background-color: $success-color;
  border-radius: 50%;
  
  .check-icon {
    color: $text-color-white;
    font-size: 24rpx;
    font-weight: bold;
  }
}

// 水平滚动布局
.subjects-horizontal {
  width: 100%;
}

.horizontal-container {
  @include flex-start;
  gap: $spacing-base;
  padding: 0 $spacing-base $spacing-base 0;
}

.horizontal-item {
  @include flex-center;
  flex-direction: column;
  gap: 8rpx;
  padding: $spacing-base;
  background-color: $bg-color-white;
  border-radius: $radius-large;
  box-shadow: $shadow-card;
  transition: all $animation-base ease;
  position: relative;
  min-width: 120rpx;
  flex-shrink: 0;
  
  &:active {
    transform: scale(0.95);
  }
  
  &.subject-selected {
    background-color: $primary-color;
    color: $text-color-white;
    
    .subject-name {
      color: $text-color-white;
    }
  }
  
  &.subject-disabled {
    opacity: 0.6;
  }
}

.selected-dot {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  width: 16rpx;
  height: 16rpx;
  background-color: $text-color-white;
  border-radius: 50%;
}

// 列表布局
.subjects-list {
  background-color: $bg-color-white;
  border-radius: $radius-large;
  overflow: hidden;
}

.list-item {
  @include flex-between;
  align-items: center;
  padding: $spacing-lg;
  transition: background-color $animation-fast ease;
  border-bottom: 1rpx solid $border-color-light;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:active {
    background-color: $gray-1;
  }
  
  &.subject-selected {
    background-color: rgba(0, 122, 255, 0.05);
  }
  
  &.subject-disabled {
    opacity: 0.6;
  }
}

.item-left {
  @include flex-start;
  align-items: center;
  gap: $spacing-base;
  flex: 1;
}

.subject-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.item-right {
  @include flex-end;
  align-items: center;
}

.coming-tag {
  background-color: $warning-color;
  color: $text-color-white;
  padding: 4rpx 12rpx;
  border-radius: $radius-large;
  
  .coming-text {
    font-size: 20rpx;
  }
}

.selected-check {
  width: 40rpx;
  height: 40rpx;
  @include flex-center;
  background-color: $success-color;
  border-radius: 50%;
  
  .check-icon {
    color: $text-color-white;
    font-size: 24rpx;
    font-weight: bold;
  }
}

.arrow-icon {
  font-size: 32rpx;
  color: $text-color-secondary;
}

// 学科主题色
.subject-math {
  &.subject-selected {
    border-color: $subject-math;
    box-shadow: 0 0 0 4rpx rgba(0, 122, 255, 0.2);
  }
}

.subject-chinese {
  &.subject-selected {
    border-color: $subject-chinese;
    box-shadow: 0 0 0 4rpx rgba(255, 59, 48, 0.2);
  }
}

.subject-english {
  &.subject-selected {
    border-color: $subject-english;
    box-shadow: 0 0 0 4rpx rgba(52, 199, 89, 0.2);
  }
}

.subject-physics {
  &.subject-selected {
    border-color: $subject-physics;
    box-shadow: 0 0 0 4rpx rgba(175, 82, 222, 0.2);
  }
}

.subject-chemistry {
  &.subject-selected {
    border-color: $subject-chemistry;
    box-shadow: 0 0 0 4rpx rgba(255, 149, 0, 0.2);
  }
}

.subject-biology {
  &.subject-selected {
    border-color: $subject-biology;
    box-shadow: 0 0 0 4rpx rgba(50, 215, 75, 0.2);
  }
}

.selector-footer {
  margin-top: $spacing-lg;
  padding: $spacing-base;
  background-color: $bg-color-white;
  border-radius: $radius-large;
}
</style>