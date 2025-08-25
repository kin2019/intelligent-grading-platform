<template>
  <view v-if="visible" class="z-modal" :style="modalStyle" @click="handleMaskClick">
    <!-- 遮罩层 -->
    <view class="modal-mask" :class="{ 'modal-mask--visible': showMask }" />
    
    <!-- 模态框内容 -->
    <view
      class="modal-content"
      :class="modalContentClass"
      :style="contentStyle"
      @click.stop
    >
      <!-- 头部 -->
      <view v-if="$slots.header || title || showClose" class="modal-header">
        <slot name="header">
          <view class="modal-title">{{ title }}</view>
          <view v-if="showClose" class="modal-close" @click="handleClose">
            <text class="close-icon">×</text>
          </view>
        </slot>
      </view>
      
      <!-- 内容区域 -->
      <view class="modal-body">
        <slot />
      </view>
      
      <!-- 底部 -->
      <view v-if="$slots.footer || showFooter" class="modal-footer">
        <slot name="footer">
          <z-button
            v-if="showCancel"
            type="secondary"
            :text="cancelText"
            @click="handleCancel"
          />
          <z-button
            v-if="showConfirm"
            type="primary"
            :text="confirmText"
            :loading="confirmLoading"
            @click="handleConfirm"
          />
        </slot>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, watch, nextTick } from 'vue'

interface Props {
  visible?: boolean
  title?: string
  width?: string | number
  height?: string | number
  position?: 'center' | 'top' | 'bottom' | 'left' | 'right'
  maskClosable?: boolean
  showClose?: boolean
  showFooter?: boolean
  showCancel?: boolean
  showConfirm?: boolean
  cancelText?: string
  confirmText?: string
  confirmLoading?: boolean
  zIndex?: number
  round?: boolean
  fullscreen?: boolean
  closeOnClickModal?: boolean
  destroyOnClose?: boolean
  customClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  position: 'center',
  maskClosable: true,
  showClose: true,
  showFooter: true,
  showCancel: true,
  showConfirm: true,
  cancelText: '取消',
  confirmText: '确定',
  confirmLoading: false,
  zIndex: 1000,
  round: true,
  fullscreen: false,
  closeOnClickModal: true,
  destroyOnClose: false
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  open: []
  close: []
  cancel: []
  confirm: []
  maskClick: []
}>()

const showMask = computed(() => props.visible)

// 模态框样式
const modalStyle = computed(() => {
  return {
    zIndex: props.zIndex
  }
})

// 内容区样式类
const modalContentClass = computed(() => {
  const classes = ['modal-content']
  
  classes.push(`modal-content--${props.position}`)
  
  if (props.round) {
    classes.push('modal-content--round')
  }
  
  if (props.fullscreen) {
    classes.push('modal-content--fullscreen')
  }
  
  if (props.customClass) {
    classes.push(props.customClass)
  }
  
  return classes
})

// 内容区自定义样式
const contentStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}rpx` : props.width
  }
  
  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}rpx` : props.height
  }
  
  return style
})

// 监听显示状态
watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      emit('open')
      // 禁止页面滚动
      // #ifdef H5
      document.body.style.overflow = 'hidden'
      // #endif
    } else {
      emit('close')
      // 恢复页面滚动
      // #ifdef H5
      document.body.style.overflow = ''
      // #endif
    }
  }
)

// 遮罩点击事件
const handleMaskClick = () => {
  emit('maskClick')
  
  if (props.maskClosable && props.closeOnClickModal) {
    handleClose()
  }
}

// 关闭模态框
const handleClose = () => {
  emit('update:visible', false)
}

// 取消事件
const handleCancel = () => {
  emit('cancel')
  handleClose()
}

// 确认事件
const handleConfirm = () => {
  emit('confirm')
}
</script>

<style lang="scss" scoped>
.z-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity $animation-base ease;
  
  &--visible {
    opacity: 1;
  }
}

.modal-content {
  position: relative;
  background-color: $bg-color-white;
  box-shadow: $shadow-modal;
  max-width: 90%;
  max-height: 90%;
  overflow: hidden;
  animation: modal-fade-in $animation-base ease;
  
  // 位置样式
  &--center {
    // 默认居中
  }
  
  &--top {
    align-self: flex-start;
    margin-top: 10%;
  }
  
  &--bottom {
    align-self: flex-end;
    margin-bottom: 0;
    border-radius: $radius-large $radius-large 0 0;
    width: 100%;
    max-width: 100%;
  }
  
  &--left {
    align-self: stretch;
    margin-left: 0;
    border-radius: 0 $radius-large $radius-large 0;
    height: 100%;
    max-height: 100%;
  }
  
  &--right {
    align-self: stretch;
    margin-right: 0;
    border-radius: $radius-large 0 0 $radius-large;
    height: 100%;
    max-height: 100%;
  }
  
  // 圆角样式
  &--round {
    border-radius: $radius-large;
  }
  
  // 全屏样式
  &--fullscreen {
    width: 100%;
    height: 100%;
    max-width: 100%;
    max-height: 100%;
    border-radius: 0;
  }
}

.modal-header {
  @include flex-between;
  align-items: center;
  padding: $modal-padding;
  border-bottom: 1rpx solid $border-color-light;
  min-height: 88rpx;
}

.modal-title {
  font-size: $font-size-lg;
  font-weight: $font-weight-medium;
  color: $text-color;
  flex: 1;
}

.modal-close {
  width: 64rpx;
  height: 64rpx;
  @include flex-center;
  border-radius: 50%;
  transition: background-color $animation-fast ease;
  margin-right: -16rpx;
  
  &:active {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .close-icon {
    font-size: 48rpx;
    color: $text-color-secondary;
    line-height: 1;
  }
}

.modal-body {
  padding: $modal-padding;
  max-height: 60vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.modal-footer {
  padding: $spacing-base $modal-padding $modal-padding;
  @include flex-end;
  gap: $spacing-base;
  border-top: 1rpx solid $border-color-light;
  
  :deep(.z-button) {
    min-width: 160rpx;
  }
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

// 底部弹出样式
.modal-content--bottom {
  animation: modal-slide-up $animation-base ease;
}

@keyframes modal-slide-up {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

// 左侧弹出样式
.modal-content--left {
  animation: modal-slide-right $animation-base ease;
}

@keyframes modal-slide-right {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

// 右侧弹出样式
.modal-content--right {
  animation: modal-slide-left $animation-base ease;
}

@keyframes modal-slide-left {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}
</style>