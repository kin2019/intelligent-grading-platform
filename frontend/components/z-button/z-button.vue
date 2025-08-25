<template>
  <button
    :class="buttonClass"
    :style="buttonStyle"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- 加载动画 -->
    <view v-if="loading" class="loading-icon">
      <z-loading size="small" color="currentColor" />
    </view>
    
    <!-- 图标 -->
    <view v-if="icon && !loading" :class="`icon-${icon}`" class="button-icon" />
    
    <!-- 文字内容 -->
    <text v-if="$slots.default || text" class="button-text">
      <slot>{{ text }}</slot>
    </text>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'text'
  size?: 'mini' | 'small' | 'medium' | 'large'
  shape?: 'square' | 'round' | 'circle'
  plain?: boolean
  disabled?: boolean
  loading?: boolean
  block?: boolean
  text?: string
  icon?: string
  color?: string
  bgColor?: string
  borderColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  shape: 'round',
  plain: false,
  disabled: false,
  loading: false,
  block: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 按钮样式类
const buttonClass = computed(() => {
  const classes = ['z-button']
  
  // 类型样式
  classes.push(`z-button--${props.type}`)
  
  // 尺寸样式
  classes.push(`z-button--${props.size}`)
  
  // 形状样式
  classes.push(`z-button--${props.shape}`)
  
  // 其他状态
  if (props.plain) classes.push('z-button--plain')
  if (props.disabled) classes.push('z-button--disabled')
  if (props.loading) classes.push('z-button--loading')
  if (props.block) classes.push('z-button--block')
  
  return classes.join(' ')
})

// 自定义样式
const buttonStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.color) {
    style.color = props.color
  }
  
  if (props.bgColor) {
    style.backgroundColor = props.bgColor
  }
  
  if (props.borderColor) {
    style.borderColor = props.borderColor
  }
  
  return style
})

// 点击事件处理
const handleClick = (event: MouseEvent) => {
  if (props.disabled || props.loading) return
  
  // 触觉反馈
  // #ifdef APP-PLUS || MP-WEIXIN
  uni.vibrateShort({
    type: 'light'
  })
  // #endif
  
  emit('click', event)
}
</script>

<style lang="scss" scoped>
.z-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  min-width: 0;
  border: 1rpx solid transparent;
  cursor: pointer;
  outline: none;
  text-decoration: none;
  user-select: none;
  -webkit-appearance: none;
  -webkit-text-size-adjust: 100%;
  transition: all $animation-base ease;
  
  &::before {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    background-color: currentColor;
    border: inherit;
    border-color: currentColor;
    border-radius: inherit;
    transform: translate(-50%, -50%);
    opacity: 0;
    content: ' ';
    transition: opacity $animation-fast ease;
  }
  
  &:active::before {
    opacity: 0.1;
  }
  
  // 尺寸样式
  &--mini {
    padding: 8rpx 12rpx;
    font-size: 20rpx;
    border-radius: $radius-small;
    
    .button-icon {
      font-size: 24rpx;
    }
  }
  
  &--small {
    padding: 12rpx 24rpx;
    font-size: 24rpx;
    border-radius: $radius-small;
    
    .button-icon {
      font-size: 28rpx;
    }
  }
  
  &--medium {
    padding: 16rpx 32rpx;
    font-size: 28rpx;
    border-radius: $radius-medium;
    
    .button-icon {
      font-size: 32rpx;
    }
  }
  
  &--large {
    padding: 20rpx 40rpx;
    font-size: 32rpx;
    border-radius: $radius-medium;
    
    .button-icon {
      font-size: 36rpx;
    }
  }
  
  // 形状样式
  &--square {
    border-radius: 0;
  }
  
  &--circle {
    border-radius: 50%;
  }
  
  // 类型样式
  &--primary {
    color: $text-color-white;
    background-color: $primary-color;
    border-color: $primary-color;
    
    &:disabled {
      background-color: $gray-3;
      border-color: $gray-3;
    }
    
    &.z-button--plain {
      color: $primary-color;
      background-color: transparent;
      
      &:disabled {
        color: $gray-5;
        background-color: $gray-1;
        border-color: $gray-3;
      }
    }
  }
  
  &--secondary {
    color: $text-color;
    background-color: $gray-2;
    border-color: $gray-2;
    
    &:disabled {
      color: $gray-5;
      background-color: $gray-1;
      border-color: $gray-3;
    }
    
    &.z-button--plain {
      color: $text-color-secondary;
      background-color: transparent;
      border-color: $gray-3;
      
      &:disabled {
        color: $gray-5;
        border-color: $gray-3;
      }
    }
  }
  
  &--success {
    color: $text-color-white;
    background-color: $success-color;
    border-color: $success-color;
    
    &:disabled {
      background-color: $gray-3;
      border-color: $gray-3;
    }
    
    &.z-button--plain {
      color: $success-color;
      background-color: transparent;
      
      &:disabled {
        color: $gray-5;
        background-color: $gray-1;
        border-color: $gray-3;
      }
    }
  }
  
  &--warning {
    color: $text-color-white;
    background-color: $warning-color;
    border-color: $warning-color;
    
    &:disabled {
      background-color: $gray-3;
      border-color: $gray-3;
    }
    
    &.z-button--plain {
      color: $warning-color;
      background-color: transparent;
      
      &:disabled {
        color: $gray-5;
        background-color: $gray-1;
        border-color: $gray-3;
      }
    }
  }
  
  &--error {
    color: $text-color-white;
    background-color: $error-color;
    border-color: $error-color;
    
    &:disabled {
      background-color: $gray-3;
      border-color: $gray-3;
    }
    
    &.z-button--plain {
      color: $error-color;
      background-color: transparent;
      
      &:disabled {
        color: $gray-5;
        background-color: $gray-1;
        border-color: $gray-3;
      }
    }
  }
  
  &--text {
    color: $primary-color;
    background-color: transparent;
    border-color: transparent;
    
    &:disabled {
      color: $gray-5;
    }
  }
  
  // 状态样式
  &--disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
  
  &--loading {
    cursor: default;
  }
  
  &--block {
    width: 100%;
    display: flex;
  }
  
  &--plain {
    background-color: transparent;
  }
}

.button-icon {
  margin-right: 8rpx;
  
  &:last-child {
    margin-right: 0;
  }
}

.button-text {
  line-height: 1;
}

.loading-icon {
  margin-right: 8rpx;
  
  &:last-child {
    margin-right: 0;
  }
}
</style>