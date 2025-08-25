<template>
  <view v-if="visible" class="z-toast" :class="toastClass" :style="toastStyle">
    <!-- 图标 -->
    <view v-if="icon || type !== 'none'" class="toast-icon">
      <text v-if="type === 'success'" class="icon success-icon">✓</text>
      <text v-else-if="type === 'error'" class="icon error-icon">✕</text>
      <text v-else-if="type === 'warning'" class="icon warning-icon">!</text>
      <text v-else-if="type === 'info'" class="icon info-icon">i</text>
      <z-loading v-else-if="type === 'loading'" size="small" color="currentColor" />
      <text v-else-if="icon" class="icon custom-icon">{{ icon }}</text>
    </view>
    
    <!-- 消息文本 -->
    <text class="toast-text">{{ message }}</text>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

interface Props {
  visible?: boolean
  type?: 'success' | 'error' | 'warning' | 'info' | 'loading' | 'none'
  message?: string
  icon?: string
  duration?: number
  position?: 'top' | 'center' | 'bottom'
  zIndex?: number
  mask?: boolean
  forbidClick?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  type: 'none',
  message: '',
  duration: 2000,
  position: 'center',
  zIndex: 2000,
  mask: false,
  forbidClick: false
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  close: []
}>()

let timer: ReturnType<typeof setTimeout> | null = null

// 计算样式类
const toastClass = computed(() => {
  const classes = ['z-toast']
  
  classes.push(`z-toast--${props.position}`)
  
  if (props.mask) {
    classes.push('z-toast--mask')
  }
  
  if (props.forbidClick) {
    classes.push('z-toast--forbid-click')
  }
  
  return classes
})

// 计算样式
const toastStyle = computed(() => {
  return {
    zIndex: props.zIndex
  }
})

// 监听显示状态
watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      startTimer()
    } else {
      clearTimer()
    }
  }
)

// 开始计时器
const startTimer = () => {
  if (props.duration > 0 && props.type !== 'loading') {
    timer = setTimeout(() => {
      handleClose()
    }, props.duration)
  }
}

// 清除计时器
const clearTimer = () => {
  if (timer) {
    clearTimeout(timer)
    timer = null
  }
}

// 关闭提示
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

onMounted(() => {
  if (props.visible) {
    startTimer()
  }
})

onUnmounted(() => {
  clearTimer()
})
</script>

<style lang="scss" scoped>
.z-toast {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  min-width: 200rpx;
  max-width: 80%;
  padding: 24rpx 32rpx;
  background-color: rgba(0, 0, 0, 0.8);
  color: $text-color-white;
  border-radius: $radius-large;
  @include flex-center;
  flex-direction: column;
  gap: 16rpx;
  backdrop-filter: blur(10rpx);
  -webkit-backdrop-filter: blur(10rpx);
  animation: toast-fade-in 0.3s ease;
  z-index: 2000;
  
  // 位置样式
  &--top {
    top: 20%;
  }
  
  &--center {
    top: 50%;
    transform: translate(-50%, -50%);
  }
  
  &--bottom {
    bottom: 20%;
  }
  
  // 遮罩样式
  &--mask {
    &::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: transparent;
      z-index: -1;
    }
  }
  
  // 禁止点击样式
  &--forbid-click {
    pointer-events: none;
  }
}

.toast-icon {
  @include flex-center;
  
  .icon {
    font-size: 48rpx;
    font-weight: bold;
    line-height: 1;
    
    &.success-icon {
      color: $success-color;
    }
    
    &.error-icon {
      color: $error-color;
    }
    
    &.warning-icon {
      color: $warning-color;
    }
    
    &.info-icon {
      color: $info-color;
    }
    
    &.custom-icon {
      color: currentColor;
    }
  }
}

.toast-text {
  font-size: $font-size-base;
  color: inherit;
  text-align: center;
  line-height: 1.4;
  word-break: break-all;
}

// 只有文本的样式
.z-toast:not(:has(.toast-icon)) {
  flex-direction: row;
  gap: 0;
  min-height: 64rpx;
}

@keyframes toast-fade-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20rpx);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

// 居中位置的动画
.z-toast--center {
  @keyframes toast-fade-in {
    from {
      opacity: 0;
      transform: translate(-50%, -50%) scale(0.8);
    }
    to {
      opacity: 1;
      transform: translate(-50%, -50%) scale(1);
    }
  }
}
</style>