<template>
  <div id="app">
    <!-- 路由视图 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'

const userStore = useUserStore()
const appStore = useAppStore()

onMounted(() => {
  initApp()
})

/**
 * 初始化应用
 */
const initApp = async () => {
  try {
    // 初始化应用状态
    appStore.initAppState()
    
    // 恢复用户登录状态
    await userStore.checkLoginStatus()
    
  } catch (error) {
    console.error('应用初始化失败:', error)
    uni.showToast({
      title: '初始化失败',
      icon: 'error'
    })
  }
}
</script>

<style lang="scss">
/* 全局样式重置 */
* {
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
}

#app {
  height: 100%;
  background-color: $bg-color;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 页面基础样式 */
page {
  background-color: $bg-color;
  color: $text-color;
  font-size: $font-size-base;
  line-height: 1.6;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 0;
  background: transparent;
}

/* 通用原子类 */
.flex {
  display: flex;
}

.flex-center {
  @include flex-center;
}

.flex-between {
  @include flex-between;
}

.flex-start {
  @include flex-start;
}

.flex-column {
  flex-direction: column;
}

.flex-wrap {
  flex-wrap: wrap;
}

.flex-1 {
  flex: 1;
}

/* 文字样式 */
.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

.text-ellipsis {
  @include text-ellipsis;
}

.text-ellipsis-2 {
  @include text-ellipsis-multi(2);
}

.text-ellipsis-3 {
  @include text-ellipsis-multi(3);
}

/* 字体大小 */
.text-xs {
  font-size: $font-size-xs;
}

.text-sm {
  font-size: $font-size-sm;
}

.text-base {
  font-size: $font-size-base;
}

.text-lg {
  font-size: $font-size-lg;
}

.text-xl {
  font-size: $font-size-xl;
}

.text-2xl {
  font-size: $font-size-2xl;
}

.text-3xl {
  font-size: $font-size-3xl;
}

/* 字体颜色 */
.text-primary {
  color: $primary-color;
}

.text-secondary {
  color: $text-color-secondary;
}

.text-success {
  color: $success-color;
}

.text-warning {
  color: $warning-color;
}

.text-error {
  color: $error-color;
}

.text-white {
  color: $text-color-white;
}

/* 字体粗细 */
.font-light {
  font-weight: $font-weight-light;
}

.font-normal {
  font-weight: $font-weight-normal;
}

.font-medium {
  font-weight: $font-weight-medium;
}

.font-bold {
  font-weight: $font-weight-bold;
}

.font-heavy {
  font-weight: $font-weight-heavy;
}

/* 间距类 */
.m-xs {
  margin: $spacing-xs;
}

.m-sm {
  margin: $spacing-sm;
}

.m-base {
  margin: $spacing-base;
}

.m-lg {
  margin: $spacing-lg;
}

.m-xl {
  margin: $spacing-xl;
}

.p-xs {
  padding: $spacing-xs;
}

.p-sm {
  padding: $spacing-sm;
}

.p-base {
  padding: $spacing-base;
}

.p-lg {
  padding: $spacing-lg;
}

.p-xl {
  padding: $spacing-xl;
}

/* 边距方向 */
.mt-xs {
  margin-top: $spacing-xs;
}

.mt-sm {
  margin-top: $spacing-sm;
}

.mt-base {
  margin-top: $spacing-base;
}

.mt-lg {
  margin-top: $spacing-lg;
}

.mt-xl {
  margin-top: $spacing-xl;
}

.mb-xs {
  margin-bottom: $spacing-xs;
}

.mb-sm {
  margin-bottom: $spacing-sm;
}

.mb-base {
  margin-bottom: $spacing-base;
}

.mb-lg {
  margin-bottom: $spacing-lg;
}

.mb-xl {
  margin-bottom: $spacing-xl;
}

.pt-xs {
  padding-top: $spacing-xs;
}

.pt-sm {
  padding-top: $spacing-sm;
}

.pt-base {
  padding-top: $spacing-base;
}

.pt-lg {
  padding-top: $spacing-lg;
}

.pt-xl {
  padding-top: $spacing-xl;
}

.pb-xs {
  padding-bottom: $spacing-xs;
}

.pb-sm {
  padding-bottom: $spacing-sm;
}

.pb-base {
  padding-bottom: $spacing-base;
}

.pb-lg {
  padding-bottom: $spacing-lg;
}

.pb-xl {
  padding-bottom: $spacing-xl;
}

/* 背景颜色 */
.bg-white {
  background-color: $bg-color-white;
}

.bg-gray-1 {
  background-color: $gray-1;
}

.bg-gray-2 {
  background-color: $gray-2;
}

.bg-primary {
  background-color: $primary-color;
}

.bg-success {
  background-color: $success-color;
}

.bg-warning {
  background-color: $warning-color;
}

.bg-error {
  background-color: $error-color;
}

/* 圆角 */
.rounded-sm {
  border-radius: $radius-small;
}

.rounded {
  border-radius: $radius-medium;
}

.rounded-lg {
  border-radius: $radius-large;
}

.rounded-xl {
  border-radius: $radius-xlarge;
}

.rounded-full {
  border-radius: 50%;
}

/* 阴影 */
.shadow-card {
  box-shadow: $shadow-card;
}

.shadow-float {
  box-shadow: $shadow-float;
}

.shadow-modal {
  box-shadow: $shadow-modal;
}

/* 隐藏显示 */
.hidden {
  display: none !important;
}

.invisible {
  visibility: hidden;
}

.opacity-0 {
  opacity: 0;
}

.opacity-50 {
  opacity: 0.5;
}

.opacity-100 {
  opacity: 1;
}

/* 位置 */
.relative {
  position: relative;
}

.absolute {
  position: absolute;
}

.fixed {
  position: fixed;
}

.sticky {
  position: sticky;
}

/* 宽高 */
.w-full {
  width: 100%;
}

.h-full {
  height: 100%;
}

/* 安全区域适配 */
.safe-area-top {
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);
}

.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

/* 学科主题色 */
.subject-math {
  color: $subject-math;
}

.subject-chinese {
  color: $subject-chinese;
}

.subject-english {
  color: $subject-english;
}

.subject-physics {
  color: $subject-physics;
}

.subject-chemistry {
  color: $subject-chemistry;
}

.subject-biology {
  color: $subject-biology;
}

/* 动画类 */
.fade-in {
  animation: fadeIn $animation-base ease-in-out;
}

.slide-up {
  animation: slideUp $animation-base ease-out;
}

.bounce-in {
  animation: bounceIn $animation-slow ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>