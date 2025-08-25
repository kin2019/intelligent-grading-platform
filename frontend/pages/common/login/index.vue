<template>
  <view class="login-page">
    <!-- 背景 -->
    <view class="bg-container">
      <view class="bg-shape shape1"></view>
      <view class="bg-shape shape2"></view>
      <view class="bg-shape shape3"></view>
    </view>
    
    <!-- 主要内容 -->
    <view class="content">
      <!-- Logo区域 -->
      <view class="logo-section">
        <view class="logo">
          <image src="/static/logo.png" mode="aspectFit" />
        </view>
        <view class="title">ZYJC智能批改</view>
        <view class="subtitle">中小学全学科智能批改平台</view>
      </view>
      
      <!-- 特色功能展示 -->
      <view class="features">
        <view class="feature-item">
          <view class="feature-icon">📷</view>
          <view class="feature-text">拍照即批改</view>
        </view>
        <view class="feature-item">
          <view class="feature-icon">📚</view>
          <view class="feature-text">错题智能分析</view>
        </view>
        <view class="feature-item">
          <view class="feature-icon">📊</view>
          <view class="feature-text">学习进度跟踪</view>
        </view>
      </view>
      
      <!-- 登录按钮 -->
      <view class="login-section">
        <button 
          class="login-btn"
          :loading="isLoading"
          @click="handleWechatLogin"
          open-type="getUserInfo"
          @getuserinfo="onGetUserInfo"
        >
          <text class="btn-icon">👤</text>
          <text class="btn-text">微信一键登录</text>
        </button>
        
        <view class="login-tips">
          <text>登录即表示同意</text>
          <text class="link" @click="showPrivacyPolicy">《隐私政策》</text>
          <text>和</text>
          <text class="link" @click="showUserAgreement">《用户协议》</text>
        </view>
      </view>
    </view>
    
    <!-- 协议弹窗 -->
    <z-modal 
      v-model:show="showAgreement"
      title="用户协议"
      @confirm="agreeProtocol"
      @cancel="cancelProtocol"
    >
      <view class="agreement-content">
        <text>欢迎使用ZYJC智能批改平台...</text>
      </view>
    </z-modal>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { wechatLogin } from '@/api/auth'

const userStore = useUserStore()
const appStore = useAppStore()

const isLoading = ref(false)
const showAgreement = ref(false)

// 页面加载完成
onMounted(() => {
  // 检查是否已登录
  if (userStore.isLogin) {
    navigateToHome()
  }
})

/**
 * 微信登录
 */
const handleWechatLogin = () => {
  if (isLoading.value) return
  
  // 检查网络状态
  uni.getNetworkType({
    success: (res) => {
      if (res.networkType === 'none') {
        uni.showToast({
          title: '网络连接异常',
          icon: 'error'
        })
        return
      }
      
      performLogin()
    }
  })
}

/**
 * 执行登录流程
 */
const performLogin = () => {
  isLoading.value = true
  
  // 获取微信授权码
  uni.login({
    provider: 'weixin',
    success: async (loginRes) => {
      try {
        console.log('微信登录成功:', loginRes)
        
        // 调用后端登录接口
        const response = await wechatLogin({
          code: loginRes.code
        })
        
        console.log('后端登录响应:', response)
        
        // 保存用户信息
        await userStore.setToken(response.access_token)
        await userStore.setUserInfo({
          openid: response.user.openid,
          nickname: response.user.nickname,
          avatar_url: response.user.avatar_url,
          role: 'student', // 默认角色
          is_vip: false,
          daily_quota: 5,
          daily_used: 0
        })
        
        uni.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        // 延迟跳转，让用户看到成功提示
        setTimeout(() => {
          navigateToHome()
        }, 1500)
        
      } catch (error) {
        console.error('登录失败:', error)
        uni.showToast({
          title: '登录失败，请重试',
          icon: 'error'
        })
      }
    },
    fail: (error) => {
      console.error('微信登录失败:', error)
      uni.showToast({
        title: '微信登录失败',
        icon: 'error'
      })
    },
    complete: () => {
      isLoading.value = false
    }
  })
}

/**
 * 获取用户信息回调
 */
const onGetUserInfo = (e: any) => {
  console.log('获取用户信息:', e.detail)
  
  if (e.detail.userInfo) {
    // 用户同意授权
    console.log('用户同意授权')
  } else {
    // 用户拒绝授权
    uni.showModal({
      title: '提示',
      content: '需要获取您的基本信息才能使用完整功能',
      showCancel: false
    })
  }
}

/**
 * 跳转到首页
 */
const navigateToHome = () => {
  const userInfo = userStore.userInfo
  
  // 根据用户角色跳转到对应首页
  let url = '/pages/student/index/index' // 默认学生端
  
  if (userInfo?.role === 'parent') {
    url = '/pages/parent/dashboard/index'
  } else if (userInfo?.role === 'teacher') {
    url = '/pages/teacher/classes/index'
  }
  
  uni.reLaunch({ url })
}

/**
 * 显示隐私政策
 */
const showPrivacyPolicy = () => {
  uni.navigateTo({
    url: '/pages/common/policy/index?type=privacy'
  })
}

/**
 * 显示用户协议
 */
const showUserAgreement = () => {
  showAgreement.value = true
}

/**
 * 同意协议
 */
const agreeProtocol = () => {
  showAgreement.value = false
  uni.showToast({
    title: '感谢您的同意',
    icon: 'success'
  })
}

/**
 * 拒绝协议
 */
const cancelProtocol = () => {
  showAgreement.value = false
  uni.showModal({
    title: '提示',
    content: '需要同意用户协议才能使用本应用',
    showCancel: false
  })
}
</script>

<style lang="scss" scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.bg-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  
  &.shape1 {
    width: 200px;
    height: 200px;
    top: -100px;
    right: -100px;
    animation: float 6s ease-in-out infinite;
  }
  
  &.shape2 {
    width: 150px;
    height: 150px;
    bottom: 100px;
    left: -75px;
    animation: float 8s ease-in-out infinite reverse;
  }
  
  &.shape3 {
    width: 100px;
    height: 100px;
    top: 200px;
    left: 50px;
    animation: float 10s ease-in-out infinite;
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

.content {
  position: relative;
  z-index: 1;
  padding: 80px 40px 40px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.logo-section {
  text-align: center;
  margin-bottom: 80px;
}

.logo {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  image {
    width: 60px;
    height: 60px;
  }
}

.title {
  font-size: 32px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.features {
  display: flex;
  justify-content: space-around;
  margin-bottom: 80px;
}

.feature-item {
  text-align: center;
  color: #ffffff;
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.feature-text {
  font-size: 14px;
  opacity: 0.9;
}

.login-section {
  margin-top: auto;
}

.login-btn {
  width: 100%;
  height: 56px;
  background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%);
  border-radius: 28px;
  border: none;
  color: #ffffff;
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(238, 90, 36, 0.3);
  margin-bottom: 24px;
  
  &:active {
    transform: translateY(1px);
    box-shadow: 0 4px 12px rgba(238, 90, 36, 0.3);
  }
}

.btn-icon {
  margin-right: 8px;
  font-size: 20px;
}

.login-tips {
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

.link {
  color: #ffffff;
  text-decoration: underline;
}

.agreement-content {
  padding: 20px;
  max-height: 400px;
  line-height: 1.6;
  color: #333;
}
</style>