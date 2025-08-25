<template>
  <view class="z-navbar" :style="navbarStyle">
    <!-- 状态栏占位 -->
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }" />
    
    <!-- 导航栏内容 -->
    <view class="navbar-content" :style="{ height: navBarHeight + 'px' }">
      <!-- 左侧内容 -->
      <view class="navbar-left" @click="handleLeftClick">
        <slot name="left">
          <view v-if="showBack" class="back-button">
            <text class="back-icon">←</text>
            <text v-if="backText" class="back-text">{{ backText }}</text>
          </view>
        </slot>
      </view>
      
      <!-- 中间标题 -->
      <view class="navbar-center">
        <slot name="center">
          <text class="navbar-title" :style="titleStyle">{{ title }}</text>
        </slot>
      </view>
      
      <!-- 右侧内容 -->
      <view class="navbar-right" @click="handleRightClick">
        <slot name="right">
          <text v-if="rightText" class="right-text">{{ rightText }}</text>
        </slot>
      </view>
    </view>
    
    <!-- 阴影分割线 -->
    <view v-if="shadow" class="navbar-shadow" />
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

interface Props {
  title?: string
  titleColor?: string
  background?: string
  showBack?: boolean
  backText?: string
  rightText?: string
  shadow?: boolean
  fixed?: boolean
  zIndex?: number
  transparent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  background: '#ffffff',
  showBack: true,
  shadow: true,
  fixed: true,
  zIndex: 1000,
  transparent: false
})

const emit = defineEmits<{
  leftClick: []
  rightClick: []
  backClick: []
}>()

const statusBarHeight = ref(0)
const navBarHeight = ref(44)

onMounted(() => {
  // 获取系统信息
  const systemInfo = uni.getSystemInfoSync()
  statusBarHeight.value = systemInfo.statusBarHeight || 0
  
  // 计算导航栏高度
  // #ifdef MP-WEIXIN
  const menuButton = uni.getMenuButtonBoundingClientRect()
  navBarHeight.value = (menuButton.top - statusBarHeight.value) * 2 + menuButton.height
  // #endif
  
  // #ifdef APP-PLUS
  navBarHeight.value = 44
  // #endif
  
  // #ifdef H5
  navBarHeight.value = 44
  // #endif
})

// 导航栏样式
const navbarStyle = computed(() => {
  const style: Record<string, any> = {}
  
  if (props.fixed) {
    style.position = 'fixed'
    style.top = 0
    style.left = 0
    style.right = 0
  }
  
  if (props.zIndex) {
    style.zIndex = props.zIndex
  }
  
  if (props.transparent) {
    style.backgroundColor = 'transparent'
  } else {
    style.backgroundColor = props.background
  }
  
  return style
})

// 标题样式
const titleStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.titleColor) {
    style.color = props.titleColor
  }
  
  return style
})

// 左侧点击事件
const handleLeftClick = () => {
  emit('leftClick')
  
  if (props.showBack) {
    emit('backClick')
    
    // 默认返回行为
    const pages = getCurrentPages()
    if (pages.length > 1) {
      uni.navigateBack()
    } else {
      uni.reLaunch({
        url: '/pages/student/index/index'
      })
    }
  }
}

// 右侧点击事件
const handleRightClick = () => {
  emit('rightClick')
}

// 获取导航栏总高度
const getNavbarHeight = () => {
  return statusBarHeight.value + navBarHeight.value
}

// 暴露方法给父组件
defineExpose({
  getNavbarHeight
})
</script>

<style lang="scss" scoped>
.z-navbar {
  background-color: $bg-color-white;
  position: relative;
}

.status-bar {
  width: 100%;
  background-color: inherit;
}

.navbar-content {
  @include flex-between;
  align-items: center;
  padding: 0 $container-padding;
  background-color: inherit;
}

.navbar-left {
  min-width: 120rpx;
  @include flex-start;
}

.back-button {
  @include flex-center;
  padding: 8rpx;
  border-radius: $radius-small;
  transition: background-color $animation-fast ease;
  
  &:active {
    background-color: rgba(0, 0, 0, 0.05);
  }
}

.back-icon {
  font-size: 36rpx;
  color: $text-color;
  margin-right: 4rpx;
}

.back-text {
  font-size: $font-size-base;
  color: $text-color;
}

.navbar-center {
  flex: 1;
  @include flex-center;
  padding: 0 $spacing-base;
}

.navbar-title {
  font-size: $font-size-lg;
  font-weight: $font-weight-medium;
  color: $text-color;
  @include text-ellipsis;
  max-width: 100%;
}

.navbar-right {
  min-width: 120rpx;
  @include flex-center;
  justify-content: flex-end;
}

.right-text {
  font-size: $font-size-base;
  color: $primary-color;
  padding: 8rpx 16rpx;
  border-radius: $radius-small;
  transition: background-color $animation-fast ease;
  
  &:active {
    background-color: rgba(0, 122, 255, 0.1);
  }
}

.navbar-shadow {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1rpx;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.05) 50%,
    transparent 100%
  );
}

/* 透明模式样式 */
.z-navbar.transparent {
  .back-icon,
  .back-text,
  .navbar-title {
    color: $text-color-white;
    text-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.3);
  }
  
  .right-text {
    color: $text-color-white;
    
    &:active {
      background-color: rgba(255, 255, 255, 0.2);
    }
  }
  
  .back-button:active {
    background-color: rgba(255, 255, 255, 0.2);
  }
}
</style>