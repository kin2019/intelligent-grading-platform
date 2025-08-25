<template>
  <view :class="inputWrapperClass" :style="wrapperStyle">
    <!-- 标签 -->
    <view v-if="label" class="input-label">
      <text class="label-text">{{ label }}</text>
      <text v-if="required" class="label-required">*</text>
    </view>
    
    <!-- 输入框容器 -->
    <view class="input-container" :class="containerClass">
      <!-- 前缀图标 -->
      <view v-if="prefixIcon" class="input-prefix">
        <text class="prefix-icon">{{ prefixIcon }}</text>
      </view>
      
      <!-- 输入框 -->
      <input
        v-if="!textarea"
        class="input-field"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :placeholder-class="'input-placeholder'"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        :focus="focus"
        :confirm-type="confirmType"
        :cursor-spacing="cursorSpacing"
        :selection-start="selectionStart"
        :selection-end="selectionEnd"
        :adjust-position="adjustPosition"
        :hold-keyboard="holdKeyboard"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @confirm="handleConfirm"
        @keyboardheightchange="handleKeyboardHeightChange"
      />
      
      <!-- 多行文本框 -->
      <textarea
        v-else
        class="input-field textarea-field"
        :value="modelValue"
        :placeholder="placeholder"
        :placeholder-class="'input-placeholder'"
        :disabled="disabled"
        :maxlength="maxlength"
        :focus="focus"
        :auto-height="autoHeight"
        :cursor-spacing="cursorSpacing"
        :selection-start="selectionStart"
        :selection-end="selectionEnd"
        :adjust-position="adjustPosition"
        :hold-keyboard="holdKeyboard"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @confirm="handleConfirm"
        @linechange="handleLineChange"
        @keyboardheightchange="handleKeyboardHeightChange"
      />
      
      <!-- 后缀内容 -->
      <view v-if="$slots.suffix || suffixIcon || showClear || showPassword" class="input-suffix">
        <slot name="suffix">
          <!-- 清除按钮 -->
          <view v-if="showClear && modelValue && !disabled" class="suffix-item clear-btn" @click="handleClear">
            <text class="clear-icon">×</text>
          </view>
          
          <!-- 密码显示切换 -->
          <view v-if="showPassword" class="suffix-item password-btn" @click="togglePassword">
            <text class="password-icon">{{ passwordVisible ? '👁' : '👁‍🗨' }}</text>
          </view>
          
          <!-- 后缀图标 -->
          <view v-if="suffixIcon" class="suffix-item suffix-icon">
            <text class="icon">{{ suffixIcon }}</text>
          </view>
        </slot>
      </view>
    </view>
    
    <!-- 错误信息 -->
    <view v-if="errorMessage" class="input-error">
      <text class="error-text">{{ errorMessage }}</text>
    </view>
    
    <!-- 帮助信息 -->
    <view v-if="helpText" class="input-help">
      <text class="help-text">{{ helpText }}</text>
    </view>
    
    <!-- 字符计数 -->
    <view v-if="showCount && maxlength" class="input-count">
      <text class="count-text">{{ (modelValue || '').length }}/{{ maxlength }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'number' | 'idcard' | 'digit' | 'password' | 'tel' | 'email'
  textarea?: boolean
  label?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  maxlength?: number
  showCount?: boolean
  showClear?: boolean
  showPassword?: boolean
  prefixIcon?: string
  suffixIcon?: string
  errorMessage?: string
  helpText?: string
  size?: 'small' | 'medium' | 'large'
  variant?: 'outlined' | 'filled' | 'underlined'
  focus?: boolean
  confirmType?: string
  cursorSpacing?: number
  selectionStart?: number
  selectionEnd?: number
  adjustPosition?: boolean
  holdKeyboard?: boolean
  autoHeight?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  textarea: false,
  disabled: false,
  readonly: false,
  required: false,
  maxlength: 140,
  showCount: false,
  showClear: false,
  showPassword: false,
  size: 'medium',
  variant: 'outlined',
  focus: false,
  confirmType: 'done',
  cursorSpacing: 0,
  selectionStart: -1,
  selectionEnd: -1,
  adjustPosition: true,
  holdKeyboard: false,
  autoHeight: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  input: [event: Event]
  focus: [event: Event]
  blur: [event: Event]
  confirm: [event: Event]
  clear: []
  linechange: [event: Event]
  keyboardheightchange: [event: Event]
}>()

const passwordVisible = ref(false)

// 计算输入框类型
const inputType = computed(() => {
  if (props.type === 'password') {
    return passwordVisible.value ? 'text' : 'password'
  }
  return props.type
})

// 包装器样式类
const inputWrapperClass = computed(() => {
  const classes = ['z-input']
  
  classes.push(`z-input--${props.size}`)
  classes.push(`z-input--${props.variant}`)
  
  if (props.disabled) classes.push('z-input--disabled')
  if (props.readonly) classes.push('z-input--readonly')
  if (props.errorMessage) classes.push('z-input--error')
  
  return classes
})

// 容器样式类
const containerClass = computed(() => {
  const classes = ['input-container']
  
  if (props.prefixIcon) classes.push('has-prefix')
  if (props.suffixIcon || props.showClear || props.showPassword) classes.push('has-suffix')
  
  return classes
})

// 包装器样式
const wrapperStyle = computed(() => {
  const style: Record<string, string> = {}
  return style
})

// 输入事件处理
const handleInput = (event: any) => {
  const value = event.detail.value
  emit('update:modelValue', value)
  emit('input', event)
}

// 聚焦事件处理
const handleFocus = (event: Event) => {
  emit('focus', event)
}

// 失焦事件处理
const handleBlur = (event: Event) => {
  emit('blur', event)
}

// 确认事件处理
const handleConfirm = (event: Event) => {
  emit('confirm', event)
}

// 清除输入
const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
}

// 切换密码显示
const togglePassword = () => {
  passwordVisible.value = !passwordVisible.value
}

// 行变化事件处理（仅textarea）
const handleLineChange = (event: Event) => {
  emit('linechange', event)
}

// 键盘高度变化事件处理
const handleKeyboardHeightChange = (event: Event) => {
  emit('keyboardheightchange', event)
}
</script>

<style lang="scss" scoped>
.z-input {
  display: flex;
  flex-direction: column;
  
  // 尺寸样式
  &--small {
    .input-container {
      height: 64rpx;
    }
    
    .input-field {
      font-size: 24rpx;
    }
    
    .input-label .label-text {
      font-size: 24rpx;
    }
  }
  
  &--medium {
    .input-container {
      height: 80rpx;
    }
    
    .input-field {
      font-size: 28rpx;
    }
    
    .input-label .label-text {
      font-size: 28rpx;
    }
  }
  
  &--large {
    .input-container {
      height: 96rpx;
    }
    
    .input-field {
      font-size: 32rpx;
    }
    
    .input-label .label-text {
      font-size: 32rpx;
    }
  }
  
  // 变体样式
  &--outlined {
    .input-container {
      border: 2rpx solid $border-color;
      border-radius: $radius-medium;
      background-color: $bg-color-white;
      
      &:focus-within {
        border-color: $primary-color;
      }
    }
  }
  
  &--filled {
    .input-container {
      border: none;
      border-radius: $radius-medium;
      background-color: $gray-1;
      
      &:focus-within {
        background-color: $bg-color-white;
        box-shadow: 0 0 0 2rpx $primary-color;
      }
    }
  }
  
  &--underlined {
    .input-container {
      border: none;
      border-bottom: 2rpx solid $border-color;
      border-radius: 0;
      background-color: transparent;
      
      &:focus-within {
        border-bottom-color: $primary-color;
      }
    }
  }
  
  // 状态样式
  &--disabled {
    .input-container {
      background-color: $gray-1;
      border-color: $gray-3;
    }
    
    .input-field {
      color: $text-color-disabled;
    }
  }
  
  &--readonly {
    .input-container {
      background-color: $gray-1;
    }
  }
  
  &--error {
    .input-container {
      border-color: $error-color;
    }
  }
}

.input-label {
  @include flex-start;
  margin-bottom: 12rpx;
  
  .label-text {
    color: $text-color;
    font-weight: $font-weight-medium;
  }
  
  .label-required {
    color: $error-color;
    margin-left: 4rpx;
  }
}

.input-container {
  @include flex-between;
  align-items: center;
  padding: 0 24rpx;
  position: relative;
  transition: all $animation-fast ease;
  
  &.has-prefix {
    padding-left: 16rpx;
  }
  
  &.has-suffix {
    padding-right: 16rpx;
  }
}

.input-prefix {
  margin-right: 16rpx;
  
  .prefix-icon {
    font-size: 32rpx;
    color: $text-color-secondary;
  }
}

.input-field {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: $text-color;
  line-height: 1.4;
  
  &.textarea-field {
    min-height: 120rpx;
    resize: none;
  }
}

.input-placeholder {
  color: $text-color-placeholder;
}

.input-suffix {
  @include flex-center;
  gap: 16rpx;
  margin-left: 16rpx;
  
  .suffix-item {
    @include flex-center;
    width: 48rpx;
    height: 48rpx;
    border-radius: 50%;
    cursor: pointer;
    transition: background-color $animation-fast ease;
    
    &:active {
      background-color: rgba(0, 0, 0, 0.05);
    }
  }
  
  .clear-icon,
  .password-icon,
  .icon {
    font-size: 32rpx;
    color: $text-color-secondary;
    line-height: 1;
  }
  
  .clear-icon {
    font-size: 36rpx;
    font-weight: bold;
  }
}

.input-error {
  margin-top: 8rpx;
  
  .error-text {
    font-size: 24rpx;
    color: $error-color;
  }
}

.input-help {
  margin-top: 8rpx;
  
  .help-text {
    font-size: 24rpx;
    color: $text-color-secondary;
  }
}

.input-count {
  margin-top: 8rpx;
  @include flex-end;
  
  .count-text {
    font-size: 24rpx;
    color: $text-color-secondary;
  }
}
</style>