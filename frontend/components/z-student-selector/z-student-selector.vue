<template>
  <view class="z-student-selector" :class="selectorClass">
    <!-- 当前选中的学生 -->
    <view v-if="layout === 'dropdown'" class="current-student" @click="toggleDropdown">
      <view class="student-info">
        <image
          :src="currentStudent?.avatar || defaultAvatar"
          class="student-avatar"
          mode="aspectFill"
        />
        <view class="student-details">
          <text class="student-name">{{ currentStudent?.name || '请选择学生' }}</text>
          <text v-if="currentStudent" class="student-grade">{{ currentStudent.grade }}{{ currentStudent.class_name }}</text>
        </view>
      </view>
      
      <view class="dropdown-arrow" :class="{ 'arrow-up': dropdownVisible }">
        <text class="arrow-icon">▼</text>
      </view>
    </view>
    
    <!-- 下拉列表 -->
    <view v-if="layout === 'dropdown' && dropdownVisible" class="dropdown-list">
      <view
        v-for="student in students"
        :key="student.id"
        class="dropdown-item"
        :class="{ 'item-selected': modelValue === student.id }"
        @click="handleStudentSelect(student)"
      >
        <image
          :src="student.avatar || defaultAvatar"
          class="item-avatar"
          mode="aspectFill"
        />
        <view class="item-info">
          <text class="item-name">{{ student.name }}</text>
          <text class="item-grade">{{ student.grade }}{{ student.class_name }}</text>
        </view>
        
        <view v-if="modelValue === student.id" class="item-check">
          <text class="check-icon">✓</text>
        </view>
      </view>
      
      <!-- 添加学生 -->
      <view class="dropdown-item add-student" @click="handleAddStudent">
        <view class="add-avatar">
          <text class="add-icon">+</text>
        </view>
        <view class="item-info">
          <text class="item-name">添加学生</text>
          <text class="item-grade">绑定新的学生账号</text>
        </view>
      </view>
    </view>
    
    <!-- 标签页布局 -->
    <scroll-view
      v-if="layout === 'tabs'"
      class="students-tabs"
      scroll-x
      :show-scrollbar="false"
    >
      <view class="tabs-container">
        <view
          v-for="student in students"
          :key="student.id"
          class="tab-item"
          :class="{ 'tab-selected': modelValue === student.id }"
          @click="handleStudentSelect(student)"
        >
          <image
            :src="student.avatar || defaultAvatar"
            class="tab-avatar"
            mode="aspectFill"
          />
          <text class="tab-name">{{ student.name }}</text>
        </view>
        
        <!-- 添加按钮 -->
        <view class="tab-item add-tab" @click="handleAddStudent">
          <view class="add-avatar small">
            <text class="add-icon">+</text>
          </view>
          <text class="tab-name">添加</text>
        </view>
      </view>
    </scroll-view>
    
    <!-- 卡片布局 -->
    <view v-if="layout === 'cards'" class="students-cards">
      <view
        v-for="student in students"
        :key="student.id"
        class="student-card"
        :class="{ 'card-selected': modelValue === student.id }"
        @click="handleStudentSelect(student)"
      >
        <image
          :src="student.avatar || defaultAvatar"
          class="card-avatar"
          mode="aspectFill"
        />
        <view class="card-info">
          <text class="card-name">{{ student.name }}</text>
          <text class="card-grade">{{ student.grade }}{{ student.class_name }}</text>
          <text class="card-school">{{ student.school_name }}</text>
        </view>
        
        <!-- 选中标识 -->
        <view v-if="modelValue === student.id" class="card-selected-badge">
          <text class="badge-text">当前</text>
        </view>
        
        <!-- 学习统计 -->
        <view class="card-stats">
          <view class="stat-item">
            <text class="stat-value">{{ student.total_homework || 0 }}</text>
            <text class="stat-label">作业</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ student.accuracy_rate || 0 }}%</text>
            <text class="stat-label">正确率</text>
          </view>
        </view>
      </view>
      
      <!-- 添加学生卡片 -->
      <view class="student-card add-card" @click="handleAddStudent">
        <view class="add-avatar large">
          <text class="add-icon">+</text>
        </view>
        <view class="card-info">
          <text class="card-name">添加学生</text>
          <text class="card-desc">绑定新的学生账号</text>
        </view>
      </view>
    </view>
    
    <!-- 遮罩层 -->
    <view
      v-if="layout === 'dropdown' && dropdownVisible"
      class="dropdown-mask"
      @click="closeDropdown"
    />
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Student } from '@/types/user'

interface Props {
  modelValue?: number | null
  students?: Student[]
  layout?: 'dropdown' | 'tabs' | 'cards'
  size?: 'small' | 'medium' | 'large'
  showAddButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  students: () => [],
  layout: 'dropdown',
  size: 'medium',
  showAddButton: true
})

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  change: [student: Student | null]
  addStudent: []
}>()

const dropdownVisible = ref(false)
const defaultAvatar = '/static/images/default-avatar.png'

// 计算当前选中的学生
const currentStudent = computed(() => {
  return props.students.find(s => s.id === props.modelValue) || null
})

// 计算样式类
const selectorClass = computed(() => {
  return [`selector-${props.layout}`, `selector-${props.size}`]
})

// 切换下拉菜单
const toggleDropdown = () => {
  dropdownVisible.value = !dropdownVisible.value
}

// 关闭下拉菜单
const closeDropdown = () => {
  dropdownVisible.value = false
}

// 选择学生
const handleStudentSelect = (student: Student) => {
  emit('update:modelValue', student.id)
  emit('change', student)
  
  if (props.layout === 'dropdown') {
    closeDropdown()
  }
  
  // 触觉反馈
  uni.vibrateShort({
    type: 'light'
  })
}

// 添加学生
const handleAddStudent = () => {
  emit('addStudent')
  
  if (props.layout === 'dropdown') {
    closeDropdown()
  }
}
</script>

<style lang="scss" scoped>
.z-student-selector {
  position: relative;
  
  &.selector-small {
    .student-avatar, .item-avatar, .tab-avatar {
      width: 64rpx;
      height: 64rpx;
    }
    
    .card-avatar {
      width: 80rpx;
      height: 80rpx;
    }
    
    .student-name, .item-name, .tab-name, .card-name {
      font-size: $font-size-sm;
    }
  }
  
  &.selector-medium {
    .student-avatar, .item-avatar, .tab-avatar {
      width: 80rpx;
      height: 80rpx;
    }
    
    .card-avatar {
      width: 100rpx;
      height: 100rpx;
    }
    
    .student-name, .item-name, .tab-name, .card-name {
      font-size: $font-size-base;
    }
  }
  
  &.selector-large {
    .student-avatar, .item-avatar, .tab-avatar {
      width: 96rpx;
      height: 96rpx;
    }
    
    .card-avatar {
      width: 120rpx;
      height: 120rpx;
    }
    
    .student-name, .item-name, .tab-name, .card-name {
      font-size: $font-size-lg;
    }
  }
}

// 下拉选择器
.current-student {
  @include flex-between;
  align-items: center;
  padding: $spacing-base $spacing-lg;
  background-color: $bg-color-white;
  border-radius: $radius-large;
  box-shadow: $shadow-card;
  transition: all $animation-fast ease;
  
  &:active {
    transform: scale(0.99);
  }
}

.student-info {
  @include flex-start;
  align-items: center;
  gap: $spacing-base;
  flex: 1;
}

.student-avatar {
  border-radius: 50%;
  background-color: $gray-2;
}

.student-details {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.student-name {
  font-weight: $font-weight-medium;
  color: $text-color;
}

.student-grade {
  font-size: $font-size-sm;
  color: $text-color-secondary;
}

.dropdown-arrow {
  width: 48rpx;
  height: 48rpx;
  @include flex-center;
  transition: transform $animation-fast ease;
  
  &.arrow-up {
    transform: rotate(180deg);
  }
}

.arrow-icon {
  font-size: 24rpx;
  color: $text-color-secondary;
}

.dropdown-list {
  position: absolute;
  top: calc(100% + 8rpx);
  left: 0;
  right: 0;
  background-color: $bg-color-white;
  border-radius: $radius-large;
  box-shadow: $shadow-modal;
  overflow: hidden;
  z-index: 100;
  animation: dropdown-slide-down $animation-base ease;
}

.dropdown-item {
  @include flex-between;
  align-items: center;
  padding: $spacing-base $spacing-lg;
  transition: background-color $animation-fast ease;
  border-bottom: 1rpx solid $border-color-light;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:active {
    background-color: $gray-1;
  }
  
  &.item-selected {
    background-color: rgba(0, 122, 255, 0.05);
  }
  
  &.add-student {
    border-top: 1rpx solid $border-color-light;
  }
}

.item-avatar {
  border-radius: 50%;
  background-color: $gray-2;
}

.item-info {
  @include flex-start;
  flex-direction: column;
  gap: 4rpx;
  margin-left: $spacing-base;
  flex: 1;
}

.item-name {
  font-weight: $font-weight-medium;
  color: $text-color;
}

.item-grade {
  font-size: $font-size-sm;
  color: $text-color-secondary;
}

.item-check {
  width: 40rpx;
  height: 40rpx;
  @include flex-center;
  background-color: $primary-color;
  border-radius: 50%;
  
  .check-icon {
    color: $text-color-white;
    font-size: 24rpx;
    font-weight: bold;
  }
}

.add-avatar {
  @include flex-center;
  background-color: $gray-2;
  border: 2rpx dashed $gray-4;
  border-radius: 50%;
  
  &.small {
    width: 64rpx;
    height: 64rpx;
  }
  
  &.large {
    width: 120rpx;
    height: 120rpx;
  }
  
  .add-icon {
    font-size: 32rpx;
    color: $gray-5;
    font-weight: bold;
  }
}

.dropdown-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}

// 标签页布局
.students-tabs {
  width: 100%;
}

.tabs-container {
  @include flex-start;
  gap: $spacing-base;
  padding: 0 $spacing-base $spacing-base 0;
}

.tab-item {
  @include flex-center;
  flex-direction: column;
  gap: 8rpx;
  padding: $spacing-base;
  background-color: $bg-color-white;
  border-radius: $radius-large;
  box-shadow: $shadow-card;
  transition: all $animation-base ease;
  min-width: 120rpx;
  flex-shrink: 0;
  
  &:active {
    transform: scale(0.95);
  }
  
  &.tab-selected {
    background-color: $primary-color;
    color: $text-color-white;
    transform: translateY(-4rpx);
    
    .tab-name {
      color: $text-color-white;
    }
  }
  
  &.add-tab {
    background-color: $gray-1;
    border: 2rpx dashed $gray-3;
  }
}

.tab-avatar {
  border-radius: 50%;
  background-color: $gray-2;
}

.tab-name {
  font-size: $font-size-sm;
  color: $text-color;
  text-align: center;
  font-weight: $font-weight-medium;
}

// 卡片布局
.students-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300rpx, 1fr));
  gap: $spacing-base;
}

.student-card {
  position: relative;
  padding: $spacing-lg;
  background-color: $bg-color-white;
  border-radius: $radius-large;
  box-shadow: $shadow-card;
  transition: all $animation-base ease;
  
  &:active {
    transform: scale(0.98);
  }
  
  &.card-selected {
    border: 2rpx solid $primary-color;
    box-shadow: $shadow-float;
    transform: scale(1.02);
  }
  
  &.add-card {
    @include flex-center;
    flex-direction: column;
    gap: $spacing-base;
    border: 2rpx dashed $gray-3;
    background-color: $gray-1;
    min-height: 240rpx;
  }
}

.card-avatar {
  border-radius: 50%;
  background-color: $gray-2;
  margin-bottom: $spacing-base;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-bottom: $spacing-base;
}

.card-name {
  font-weight: $font-weight-medium;
  color: $text-color;
}

.card-grade {
  font-size: $font-size-sm;
  color: $text-color-secondary;
}

.card-school {
  font-size: $font-size-sm;
  color: $text-color-secondary;
}

.card-desc {
  font-size: $font-size-sm;
  color: $text-color-secondary;
  text-align: center;
}

.card-selected-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  background-color: $primary-color;
  color: $text-color-white;
  padding: 4rpx 12rpx;
  border-radius: $radius-large;
  
  .badge-text {
    font-size: 20rpx;
    font-weight: $font-weight-medium;
  }
}

.card-stats {
  @include flex-between;
  gap: $spacing-sm;
}

.stat-item {
  @include flex-center;
  flex-direction: column;
  gap: 4rpx;
  flex: 1;
  padding: $spacing-sm;
  background-color: $gray-1;
  border-radius: $radius-medium;
}

.stat-value {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: $primary-color;
}

.stat-label {
  font-size: $font-size-xs;
  color: $text-color-secondary;
}

@keyframes dropdown-slide-down {
  from {
    opacity: 0;
    transform: translateY(-20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>