<template>
  <view class="z-camera" :class="cameraClass">
    <!-- 相机预览区域 -->
    <camera
      v-if="!imageUrl"
      class="camera-preview"
      :device-position="devicePosition"
      :flash="flash"
      :frame="frame"
      @error="handleCameraError"
      @initdone="handleCameraInit"
      @scancode="handleScanCode"
    >
      <!-- 相机控制层 -->
      <cover-view class="camera-controls">
        <!-- 顶部控制栏 -->
        <cover-view class="controls-top">
          <!-- 关闭按钮 -->
          <cover-view class="control-btn close-btn" @tap="handleClose">
            <cover-image src="/static/icons/close.png" class="btn-icon" />
          </cover-view>
          
          <!-- 闪光灯切换 -->
          <cover-view class="control-btn flash-btn" @tap="toggleFlash">
            <cover-image 
              :src="flash === 'on' ? '/static/icons/flash-on.png' : '/static/icons/flash-off.png'" 
              class="btn-icon" 
            />
          </cover-view>
          
          <!-- 相机切换 -->
          <cover-view class="control-btn switch-btn" @tap="switchCamera">
            <cover-image src="/static/icons/camera-switch.png" class="btn-icon" />
          </cover-view>
        </cover-view>
        
        <!-- 拍照区域指示框 -->
        <cover-view class="photo-guide" :class="{ 'guide-active': showGuide }">
          <cover-view class="guide-corner guide-top-left" />
          <cover-view class="guide-corner guide-top-right" />
          <cover-view class="guide-corner guide-bottom-left" />
          <cover-view class="guide-corner guide-bottom-right" />
          <cover-text class="guide-text">{{ guideText }}</cover-text>
        </cover-view>
        
        <!-- 底部控制栏 -->
        <cover-view class="controls-bottom">
          <!-- 相册按钮 -->
          <cover-view class="control-btn album-btn" @tap="selectFromAlbum">
            <cover-image src="/static/icons/album.png" class="btn-icon" />
          </cover-view>
          
          <!-- 拍照按钮 -->
          <cover-view class="capture-btn" :class="{ 'capturing': capturing }" @tap="takePhoto">
            <cover-view class="capture-inner" />
          </cover-view>
          
          <!-- 设置按钮 -->
          <cover-view class="control-btn settings-btn" @tap="showSettings">
            <cover-image src="/static/icons/settings.png" class="btn-icon" />
          </cover-view>
        </cover-view>
      </cover-view>
    </camera>
    
    <!-- 图片预览区域 -->
    <view v-if="imageUrl" class="image-preview">
      <image :src="imageUrl" class="preview-image" mode="aspectFit" />
      
      <!-- 预览控制栏 -->
      <view class="preview-controls">
        <z-button type="secondary" @click="retakePhoto">重新拍摄</z-button>
        <z-button type="primary" :loading="uploading" @click="confirmPhoto">确认使用</z-button>
      </view>
    </view>
    
    <!-- 设置面板 -->
    <z-modal
      v-model:visible="settingsVisible"
      title="拍照设置"
      position="bottom"
    >
      <view class="settings-panel">
        <!-- 拍照质量 -->
        <view class="setting-item">
          <text class="setting-label">照片质量</text>
          <picker
            :value="qualityIndex"
            :range="qualityOptions"
            range-key="label"
            @change="onQualityChange"
          >
            <view class="setting-value">{{ qualityOptions[qualityIndex].label }}</view>
          </picker>
        </view>
        
        <!-- 自动识别 -->
        <view class="setting-item">
          <text class="setting-label">自动识别作业区域</text>
          <switch :checked="autoDetect" @change="onAutoDetectChange" />
        </view>
        
        <!-- 智能增强 -->
        <view class="setting-item">
          <text class="setting-label">智能图像增强</text>
          <switch :checked="smartEnhance" @change="onSmartEnhanceChange" />
        </view>
      </view>
    </z-modal>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  subject?: string
  autoCapture?: boolean
  quality?: 'low' | 'normal' | 'high'
  maxSize?: number
  showGuide?: boolean
  guideText?: string
}

const props = withDefaults(defineProps<Props>(), {
  subject: 'math',
  autoCapture: false,
  quality: 'high',
  maxSize: 2048,
  showGuide: true,
  guideText: '请将作业完整放入框内'
})

const emit = defineEmits<{
  close: []
  capture: [imageUrl: string, imageInfo: any]
  error: [error: any]
}>()

// 相机状态
const devicePosition = ref<'front' | 'back'>('back')
const flash = ref<'auto' | 'on' | 'off'>('auto')
const frame = ref<'normal' | 'square'>('normal')
const capturing = ref(false)
const imageUrl = ref('')
const uploading = ref(false)

// 设置状态
const settingsVisible = ref(false)
const qualityIndex = ref(2)
const autoDetect = ref(true)
const smartEnhance = ref(true)

const qualityOptions = [
  { label: '标准', value: 'low' },
  { label: '高清', value: 'normal' },
  { label: '超清', value: 'high' }
]

// 计算样式类
const cameraClass = computed(() => {
  const classes = []
  
  if (props.subject) {
    classes.push(`camera-${props.subject}`)
  }
  
  return classes
})

// 相机事件处理
const handleCameraError = (error: any) => {
  console.error('相机错误:', error)
  uni.showToast({
    title: '相机启动失败',
    icon: 'error'
  })
  emit('error', error)
}

const handleCameraInit = () => {
  console.log('相机初始化完成')
}

const handleScanCode = (event: any) => {
  console.log('扫码结果:', event)
}

// 拍照功能
const takePhoto = () => {
  if (capturing.value) return
  
  capturing.value = true
  
  const ctx = uni.createCameraContext()
  ctx.takePhoto({
    quality: qualityOptions[qualityIndex.value].value,
    success: (res) => {
      imageUrl.value = res.tempImagePath
      
      // 触觉反馈
      uni.vibrateShort()
      
      // 播放拍照音效
      playShutterSound()
    },
    fail: (error) => {
      console.error('拍照失败:', error)
      uni.showToast({
        title: '拍照失败',
        icon: 'error'
      })
    },
    complete: () => {
      capturing.value = false
    }
  })
}

// 重新拍摄
const retakePhoto = () => {
  imageUrl.value = ''
}

// 确认照片
const confirmPhoto = async () => {
  if (!imageUrl.value) return
  
  try {
    uploading.value = true
    
    // 如果开启智能增强，先处理图片
    let finalImageUrl = imageUrl.value
    if (smartEnhance.value) {
      finalImageUrl = await enhanceImage(imageUrl.value)
    }
    
    // 获取图片信息
    const imageInfo = await getImageInfo(finalImageUrl)
    
    emit('capture', finalImageUrl, imageInfo)
  } catch (error) {
    console.error('处理图片失败:', error)
    uni.showToast({
      title: '处理失败',
      icon: 'error'
    })
  } finally {
    uploading.value = false
  }
}

// 从相册选择
const selectFromAlbum = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album'],
    success: (res) => {
      imageUrl.value = res.tempFilePaths[0]
    },
    fail: (error) => {
      console.error('选择图片失败:', error)
    }
  })
}

// 控制功能
const handleClose = () => {
  emit('close')
}

const toggleFlash = () => {
  const flashModes: Array<'auto' | 'on' | 'off'> = ['auto', 'on', 'off']
  const currentIndex = flashModes.indexOf(flash.value)
  flash.value = flashModes[(currentIndex + 1) % flashModes.length]
}

const switchCamera = () => {
  devicePosition.value = devicePosition.value === 'back' ? 'front' : 'back'
}

const showSettings = () => {
  settingsVisible.value = true
}

// 设置处理
const onQualityChange = (event: any) => {
  qualityIndex.value = event.detail.value
}

const onAutoDetectChange = (event: any) => {
  autoDetect.value = event.detail.value
}

const onSmartEnhanceChange = (event: any) => {
  smartEnhance.value = event.detail.value
}

// 播放拍照音效
const playShutterSound = () => {
  // #ifdef APP-PLUS
  const audio = uni.createInnerAudioContext()
  audio.src = '/static/sounds/shutter.mp3'
  audio.play()
  // #endif
}

// 图片增强处理
const enhanceImage = async (imagePath: string): Promise<string> => {
  // 这里可以调用图像处理API
  return new Promise((resolve) => {
    // 模拟处理延迟
    setTimeout(() => {
      resolve(imagePath)
    }, 1000)
  })
}

// 获取图片信息
const getImageInfo = (imagePath: string): Promise<any> => {
  return new Promise((resolve, reject) => {
    uni.getImageInfo({
      src: imagePath,
      success: resolve,
      fail: reject
    })
  })
}

onMounted(() => {
  // 检查相机权限
  // #ifdef APP-PLUS
  plus.camera.getCamera()
  // #endif
})

onUnmounted(() => {
  // 清理资源
  if (imageUrl.value) {
    // 清理临时文件
  }
})
</script>

<style lang="scss" scoped>
.z-camera {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background-color: #000;
}

.camera-preview {
  width: 100%;
  height: 100%;
}

.camera-controls {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.controls-top {
  position: absolute;
  top: var(--status-bar-height, 44rpx);
  left: 0;
  right: 0;
  height: 120rpx;
  @include flex-between;
  padding: 0 $spacing-lg;
  z-index: 2;
}

.controls-bottom {
  position: absolute;
  bottom: var(--safe-area-inset-bottom, 0);
  left: 0;
  right: 0;
  height: 200rpx;
  @include flex-between;
  align-items: center;
  padding: 0 $spacing-xl;
  z-index: 2;
}

.control-btn {
  width: 80rpx;
  height: 80rpx;
  @include flex-center;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  backdrop-filter: blur(10rpx);
  -webkit-backdrop-filter: blur(10rpx);
  
  .btn-icon {
    width: 48rpx;
    height: 48rpx;
  }
}

.capture-btn {
  width: 120rpx;
  height: 120rpx;
  @include flex-center;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  border: 6rpx solid rgba(255, 255, 255, 0.3);
  transition: transform $animation-fast ease;
  
  &.capturing {
    transform: scale(0.9);
  }
  
  .capture-inner {
    width: 80rpx;
    height: 80rpx;
    background-color: #fff;
    border-radius: 50%;
  }
}

.photo-guide {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 600rpx;
  height: 400rpx;
  transform: translate(-50%, -50%);
  border: 4rpx dashed rgba(255, 255, 255, 0.6);
  border-radius: $radius-medium;
  transition: all $animation-base ease;
  
  &.guide-active {
    border-color: $primary-color;
    box-shadow: 0 0 20rpx rgba(0, 122, 255, 0.3);
  }
}

.guide-corner {
  position: absolute;
  width: 40rpx;
  height: 40rpx;
  border: 6rpx solid #fff;
  
  &.guide-top-left {
    top: -6rpx;
    left: -6rpx;
    border-right: none;
    border-bottom: none;
  }
  
  &.guide-top-right {
    top: -6rpx;
    right: -6rpx;
    border-left: none;
    border-bottom: none;
  }
  
  &.guide-bottom-left {
    bottom: -6rpx;
    left: -6rpx;
    border-right: none;
    border-top: none;
  }
  
  &.guide-bottom-right {
    bottom: -6rpx;
    right: -6rpx;
    border-left: none;
    border-top: none;
  }
}

.guide-text {
  position: absolute;
  bottom: -60rpx;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  font-size: 28rpx;
  text-align: center;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 16rpx 24rpx;
  border-radius: $radius-medium;
  backdrop-filter: blur(10rpx);
  -webkit-backdrop-filter: blur(10rpx);
}

.image-preview {
  width: 100%;
  height: 100%;
  @include flex-center;
  flex-direction: column;
  background-color: #000;
  position: relative;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.preview-controls {
  position: absolute;
  bottom: var(--safe-area-inset-bottom, 40rpx);
  left: 0;
  right: 0;
  @include flex-center;
  gap: $spacing-lg;
  padding: 0 $spacing-xl;
}

.settings-panel {
  padding: $spacing-base 0;
}

.setting-item {
  @include flex-between;
  align-items: center;
  padding: $spacing-lg $spacing-base;
  border-bottom: 1rpx solid $border-color-light;
  
  &:last-child {
    border-bottom: none;
  }
}

.setting-label {
  font-size: $font-size-base;
  color: $text-color;
}

.setting-value {
  font-size: $font-size-base;
  color: $primary-color;
  padding: 8rpx 16rpx;
  background-color: $gray-1;
  border-radius: $radius-small;
}

// 学科主题色
.camera-math {
  .guide-text {
    background-color: rgba(0, 122, 255, 0.8);
  }
  
  .photo-guide.guide-active {
    border-color: $subject-math;
    box-shadow: 0 0 20rpx rgba(0, 122, 255, 0.3);
  }
}

.camera-chinese {
  .guide-text {
    background-color: rgba(255, 59, 48, 0.8);
  }
  
  .photo-guide.guide-active {
    border-color: $subject-chinese;
    box-shadow: 0 0 20rpx rgba(255, 59, 48, 0.3);
  }
}

.camera-english {
  .guide-text {
    background-color: rgba(52, 199, 89, 0.8);
  }
  
  .photo-guide.guide-active {
    border-color: $subject-english;
    box-shadow: 0 0 20rpx rgba(52, 199, 89, 0.3);
  }
}
</style>