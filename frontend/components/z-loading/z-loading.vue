<template>
  <view :class="loadingClass" :style="loadingStyle">
    <!-- 圆形加载动画 -->
    <view v-if="type === 'circular'" class="loading-circular">
      <svg class="circular" viewBox="25 25 50 50">
        <circle
          class="path"
          cx="50"
          cy="50"
          r="20"
          fill="none"
          :stroke="computedColor"
          :stroke-width="strokeWidth"
          stroke-miterlimit="10"
        />
      </svg>
    </view>
    
    <!-- 点状加载动画 -->
    <view v-else-if="type === 'dots'" class="loading-dots">
      <view
        v-for="i in 3"
        :key="i"
        class="dot"
        :style="{ backgroundColor: computedColor, animationDelay: `${(i - 1) * 0.1}s` }"
      />
    </view>
    
    <!-- 脉冲加载动画 -->
    <view v-else-if="type === 'pulse'" class="loading-pulse">
      <view class="pulse-dot" :style="{ backgroundColor: computedColor }" />
    </view>
    
    <!-- 旋转方形加载动画 -->
    <view v-else-if="type === 'square'" class="loading-square">
      <view class="square" :style="{ borderColor: computedColor }" />
    </view>
    
    <!-- 加载文本 -->
    <text v-if="text" class="loading-text" :style="{ color: textColor }">{{ text }}</text>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'circular' | 'dots' | 'pulse' | 'square'
  size?: 'mini' | 'small' | 'medium' | 'large' | number
  color?: string
  textColor?: string
  text?: string
  vertical?: boolean
  strokeWidth?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'circular',
  size: 'medium',
  color: '#007AFF',
  vertical: false,
  strokeWidth: 2
})

// 计算加载器样式类
const loadingClass = computed(() => {
  const classes = ['z-loading']
  
  // 尺寸样式
  if (typeof props.size === 'string') {
    classes.push(`z-loading--${props.size}`)
  }
  
  // 布局方式
  if (props.vertical) {
    classes.push('z-loading--vertical')
  }
  
  return classes.join(' ')
})

// 计算自定义样式
const loadingStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (typeof props.size === 'number') {
    style.width = `${props.size}rpx`
    style.height = `${props.size}rpx`
  }
  
  return style
})

// 计算颜色
const computedColor = computed(() => {
  return props.color || '#007AFF'
})
</script>

<style lang="scss" scoped>
.z-loading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  
  // 尺寸样式
  &--mini {
    width: 32rpx;
    height: 32rpx;
    
    .loading-text {
      font-size: 20rpx;
      margin-left: 8rpx;
    }
  }
  
  &--small {
    width: 48rpx;
    height: 48rpx;
    
    .loading-text {
      font-size: 24rpx;
      margin-left: 12rpx;
    }
  }
  
  &--medium {
    width: 64rpx;
    height: 64rpx;
    
    .loading-text {
      font-size: 28rpx;
      margin-left: 16rpx;
    }
  }
  
  &--large {
    width: 96rpx;
    height: 96rpx;
    
    .loading-text {
      font-size: 32rpx;
      margin-left: 20rpx;
    }
  }
  
  // 垂直布局
  &--vertical {
    flex-direction: column;
    
    .loading-text {
      margin-left: 0;
      margin-top: 16rpx;
    }
  }
}

// 圆形加载动画
.loading-circular {
  width: 100%;
  height: 100%;
  
  .circular {
    width: 100%;
    height: 100%;
    animation: rotate 2s linear infinite;
  }
  
  .path {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: 0;
    stroke-linecap: round;
    animation: dash 1.5s ease-in-out infinite;
  }
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

// 点状加载动画
.loading-dots {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  
  .dot {
    width: 20%;
    height: 20%;
    border-radius: 50%;
    animation: dot-bounce 1.4s ease-in-out infinite both;
  }
}

@keyframes dot-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

// 脉冲加载动画
.loading-pulse {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .pulse-dot {
    width: 60%;
    height: 60%;
    border-radius: 50%;
    animation: pulse-scale 1s ease-in-out infinite;
  }
}

@keyframes pulse-scale {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

// 方形加载动画
.loading-square {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .square {
    width: 70%;
    height: 70%;
    border: 4rpx solid;
    border-radius: 8rpx;
    animation: square-rotate 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  }
}

@keyframes square-rotate {
  0% {
    transform: perspective(120px) rotateX(0deg) rotateY(0deg);
  }
  50% {
    transform: perspective(120px) rotateX(-180.1deg) rotateY(0deg);
  }
  100% {
    transform: perspective(120px) rotateX(-180deg) rotateY(-179.9deg);
  }
}

// 加载文本
.loading-text {
  color: $text-color-secondary;
  white-space: nowrap;
  line-height: 1;
}
</style>