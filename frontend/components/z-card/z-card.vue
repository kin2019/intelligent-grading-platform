<template>
  <view :class="cardClass" :style="cardStyle" @click="handleClick">
    <!-- 卡片头部 -->
    <view v-if="$slots.header || title" class="z-card__header">
      <slot name="header">
        <view class="z-card__title">
          <text class="title-text">{{ title }}</text>
          <text v-if="subtitle" class="subtitle-text">{{ subtitle }}</text>
        </view>
        <view v-if="extra" class="z-card__extra">
          <slot name="extra">{{ extra }}</slot>
        </view>
      </slot>
    </view>
    
    <!-- 卡片内容 -->
    <view class="z-card__body">
      <slot />
    </view>
    
    <!-- 卡片底部 -->
    <view v-if="$slots.footer" class="z-card__footer">
      <slot name="footer" />
    </view>
    
    <!-- 角标 -->
    <view v-if="badge" class="z-card__badge" :style="badgeStyle">
      {{ badge }}
    </view>
    
    <!-- 加载状态 -->
    <view v-if="loading" class="z-card__loading">
      <z-loading />
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  extra?: string
  shadow?: 'none' | 'light' | 'normal' | 'heavy'
  round?: boolean
  padding?: string | number
  margin?: string | number
  background?: string
  borderColor?: string
  clickable?: boolean
  loading?: boolean
  badge?: string | number
  badgeColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'normal',
  round: true,
  clickable: false,
  loading: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 卡片样式类
const cardClass = computed(() => {
  const classes = ['z-card']
  
  // 阴影样式
  classes.push(`z-card--shadow-${props.shadow}`)
  
  // 圆角样式
  if (props.round) classes.push('z-card--round')
  
  // 可点击样式
  if (props.clickable) classes.push('z-card--clickable')
  
  // 加载状态
  if (props.loading) classes.push('z-card--loading')
  
  return classes.join(' ')
})

// 卡片自定义样式
const cardStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.padding) {
    const padding = typeof props.padding === 'number' ? `${props.padding}rpx` : props.padding
    style.padding = padding
  }
  
  if (props.margin) {
    const margin = typeof props.margin === 'number' ? `${props.margin}rpx` : props.margin
    style.margin = margin
  }
  
  if (props.background) {
    style.backgroundColor = props.background
  }
  
  if (props.borderColor) {
    style.borderColor = props.borderColor
    style.borderWidth = '1rpx'
    style.borderStyle = 'solid'
  }
  
  return style
})

// 角标样式
const badgeStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.badgeColor) {
    style.backgroundColor = props.badgeColor
  }
  
  return style
})

// 点击事件处理
const handleClick = (event: MouseEvent) => {
  if (!props.clickable || props.loading) return
  
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
.z-card {
  position: relative;
  background-color: $bg-color-white;
  border-radius: $radius-medium;
  overflow: hidden;
  transition: all $animation-base ease;
  
  // 阴影样式
  &--shadow-none {
    box-shadow: none;
  }
  
  &--shadow-light {
    box-shadow: $shadow-light;
  }
  
  &--shadow-normal {
    box-shadow: $shadow-card;
  }
  
  &--shadow-heavy {
    box-shadow: $shadow-float;
  }
  
  // 圆角样式
  &--round {
    border-radius: $radius-large;
  }
  
  // 可点击样式
  &--clickable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2rpx);
      box-shadow: $shadow-float;
    }
    
    &:active {
      transform: translateY(0);
    }
  }
  
  // 加载状态
  &--loading {
    pointer-events: none;
  }
}

.z-card__header {
  @include flex-between;
  padding: $card-padding $card-padding 0;
  border-bottom: 1rpx solid $border-color-light;
  margin-bottom: $spacing-base;
}

.z-card__title {
  flex: 1;
  
  .title-text {
    display: block;
    font-size: $font-size-lg;
    font-weight: $font-weight-medium;
    color: $text-color;
    line-height: 1.4;
  }
  
  .subtitle-text {
    display: block;
    font-size: $font-size-sm;
    color: $text-color-secondary;
    margin-top: 4rpx;
    line-height: 1.4;
  }
}

.z-card__extra {
  margin-left: $spacing-base;
  font-size: $font-size-sm;
  color: $text-color-secondary;
}

.z-card__body {
  padding: $card-padding;
  position: relative;
}

.z-card__footer {
  padding: 0 $card-padding $card-padding;
  border-top: 1rpx solid $border-color-light;
  margin-top: $spacing-base;
  padding-top: $spacing-base;
}

.z-card__badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  min-width: 32rpx;
  height: 32rpx;
  padding: 0 8rpx;
  background-color: $error-color;
  color: $text-color-white;
  font-size: 20rpx;
  line-height: 32rpx;
  text-align: center;
  border-radius: 16rpx;
  z-index: 1;
}

.z-card__loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  @include flex-center;
  z-index: 10;
}
</style>