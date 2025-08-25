/**
 * 组件库统一导出
 */

// 基础组件
export { default as ZButton } from './z-button/z-button.vue'
export { default as ZCard } from './z-card/z-card.vue'
export { default as ZInput } from './z-input/z-input.vue'
export { default as ZLoading } from './z-loading/z-loading.vue'
export { default as ZModal } from './z-modal/z-modal.vue'
export { default as ZToast } from './z-toast/z-toast.vue'
export { default as ZNavbar } from './z-navbar/z-navbar.vue'

// 业务组件
export { default as ZCamera } from './z-camera/z-camera.vue'
export { default as ZResultCard } from './z-result-card/z-result-card.vue'
export { default as ZSubjectSelector } from './z-subject-selector/z-subject-selector.vue'
export { default as ZStudentSelector } from './z-student-selector/z-student-selector.vue'

// 组件类型定义
export interface ComponentProps {
  // 按钮组件属性
  ButtonProps: {
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
  
  // 卡片组件属性
  CardProps: {
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
  
  // 输入框组件属性
  InputProps: {
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
  }
  
  // 加载组件属性
  LoadingProps: {
    type?: 'circular' | 'dots' | 'pulse' | 'square'
    size?: 'mini' | 'small' | 'medium' | 'large' | number
    color?: string
    textColor?: string
    text?: string
    vertical?: boolean
    strokeWidth?: number
  }
  
  // 模态框组件属性
  ModalProps: {
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
  
  // 提示组件属性
  ToastProps: {
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
  
  // 导航栏组件属性
  NavbarProps: {
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
}

// 组件安装函数（可选）
export const install = (app: any) => {
  // 这里可以添加全局组件注册逻辑
  // app.component('ZButton', ZButton)
  // app.component('ZCard', ZCard)
  // 等等...
}

export default {
  install
}