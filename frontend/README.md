# ZYJC智能批改平台 - 前端文档

## 项目概述

ZYJC智能批改平台是一个基于AI技术的作业智能批改系统，为学生、家长和教师提供高效的学习管理工具。前端采用现代HTML5、CSS3和JavaScript技术栈，提供优秀的用户体验。

## 技术栈

- **HTML5**: 语义化标签，支持现代浏览器特性
- **CSS3**: 模块化样式设计，支持响应式布局
- **JavaScript ES6+**: 现代JavaScript语法，原生开发
- **CSS Variables**: 主题定制和设计系统
- **Flexbox & Grid**: 现代布局技术
- **Service Worker**: PWA支持（规划中）

## 项目结构

```
frontend/
├── css/
│   └── common.css              # 通用样式系统
├── js/
│   └── common.js               # 通用工具函数库
├── login.html                  # 登录页面
├── student-home.html           # 学生端首页
├── parent-home.html            # 家长端首页
├── homework-submit.html        # 作业提交页面
├── homework-result.html        # 批改结果页面
├── error-book.html             # 错题本页面
├── study-plan.html             # 学习计划页面
├── vip-center.html             # VIP中心页面
├── profile.html                # 个人中心页面
├── INTEGRATION_TEST_REPORT.md  # 集成测试报告
└── README.md                   # 项目文档
```

## 核心功能模块

### 1. 用户认证系统
- **微信登录**: 支持学生、家长角色切换
- **JWT认证**: 安全的用户身份验证
- **会话管理**: 自动登录、登出处理

### 2. 学生端功能
- **学习仪表盘**: 学习数据概览、作业统计
- **作业提交**: 拍照上传、OCR文字识别
- **批改结果**: AI分析结果展示、错题解析
- **错题本**: 错题收集、复习管理、进度跟踪
- **学习计划**: AI推荐、任务管理、进度监控

### 3. 家长端功能
- **家庭概览**: 多子女学习情况统计
- **学习报告**: 详细的学习分析报告
- **通知系统**: 实时学习动态推送
- **进度监控**: 可视化学习时长图表

### 4. 通用功能
- **VIP会员**: 多层级会员体系、支付集成
- **个人中心**: 用户资料、设置管理
- **响应式设计**: 支持手机、平板、桌面设备

## 设计系统

### 色彩体系
```css
/* 主色调 */
--primary-color: #007AFF;      /* 主品牌色 */
--secondary-color: #667eea;    /* 辅助色 */
--success-color: #4CAF50;      /* 成功色 */
--warning-color: #FF9500;      /* 警告色 */
--error-color: #FF3B30;        /* 错误色 */

/* 学科色彩 */
--subject-math: #FF6B35;       /* 数学 */
--subject-chinese: #4CAF50;    /* 语文 */
--subject-english: #2196F3;    /* 英语 */
--subject-physics: #9C27B0;    /* 物理 */
--subject-chemistry: #FF9800;  /* 化学 */
--subject-biology: #8BC34A;    /* 生物 */
```

### 间距系统
```css
--spacing-xs: 4px;    /* 超小间距 */
--spacing-sm: 8px;    /* 小间距 */
--spacing-md: 12px;   /* 中等间距 */
--spacing-lg: 16px;   /* 大间距 */
--spacing-xl: 20px;   /* 超大间距 */
--spacing-2xl: 24px;  /* 特大间距 */
```

### 字体系统
```css
--font-xs: 10px;      /* 超小字号 */
--font-sm: 12px;      /* 小字号 */
--font-base: 14px;    /* 基础字号 */
--font-lg: 16px;      /* 大字号 */
--font-xl: 18px;      /* 超大字号 */
--font-2xl: 20px;     /* 特大字号 */
```

## API集成

### 基础配置
```javascript
const API_BASE = 'http://localhost:8000/api/v1';
```

### 主要端点
- `POST /auth/wechat/login` - 微信登录
- `GET /auth/me` - 获取用户信息
- `GET /student/dashboard` - 学生仪表盘
- `GET /student/error-book` - 错题本数据
- `GET /student/study-plan` - 学习计划
- `POST /image/ocr` - 图片OCR识别
- `POST /payment/create-order` - 创建支付订单

### 错误处理
- **网络异常**: 自动降级到模拟数据
- **认证失败**: 自动跳转登录页面
- **参数错误**: 友好的错误提示
- **服务器错误**: 优雅的错误展示

## 性能优化

### 1. 代码优化
- **模块化设计**: 通用功能抽取为公共模块
- **工具函数复用**: 减少重复代码
- **事件委托**: 优化事件处理性能
- **防抖节流**: 避免频繁API调用

### 2. 资源优化
- **图片压缩**: 自动压缩上传图片
- **缓存策略**: 合理使用localStorage缓存
- **懒加载**: 按需加载页面内容
- **CDN支持**: 静态资源CDN分发

### 3. 用户体验优化
- **加载状态**: 完整的loading状态显示
- **错误反馈**: 清晰的错误提示信息
- **动画效果**: 流畅的页面转场动画
- **离线支持**: 网络异常时的降级体验

## 浏览器兼容性

### 支持的浏览器
- **Chrome**: 60+
- **Firefox**: 60+  
- **Safari**: 12+
- **Edge**: 79+
- **Mobile Safari**: iOS 12+
- **Chrome Mobile**: 60+

### 兼容性处理
- CSS Grid/Flexbox降级
- ES6语法转换
- Promise polyfill
- Fetch API polyfill

## 部署指南

### 开发环境
1. 启动后端服务器 (http://localhost:8000)
2. 使用Live Server或类似工具启动前端
3. 访问 http://localhost:3000

### 生产环境
1. 压缩HTML、CSS、JavaScript文件
2. 配置HTTPS证书
3. 设置CDN加速
4. 配置缓存策略

## 测试

### 功能测试
- ✅ 用户登录/登出流程
- ✅ 页面跳转和导航
- ✅ API数据加载和展示
- ✅ 表单提交和验证
- ✅ 错误处理和降级

### 兼容性测试
- ✅ 多浏览器兼容性
- ✅ 响应式设计测试
- ✅ 移动端适配验证
- ✅ 性能基准测试

### 集成测试
详见 [集成测试报告](./INTEGRATION_TEST_REPORT.md)

## 安全考虑

### 数据安全
- JWT Token安全存储
- 敏感信息本地加密
- 防XSS攻击处理
- CSRF保护机制

### 网络安全
- HTTPS强制跳转
- API请求头安全设置
- 文件上传类型验证
- 输入数据过滤净化

## 维护指南

### 代码规范
- ESLint代码检查
- Prettier代码格式化
- 命名规范统一
- 注释完整清晰

### 版本管理
- 语义化版本号
- Git Flow工作流
- 代码审查流程
- 自动化测试

### 监控运维
- 错误日志收集
- 性能指标监控
- 用户行为分析
- A/B测试支持

## 更新日志

### v1.0.0 (2025-08-20)
- ✅ 完整的用户认证系统
- ✅ 学生端核心功能模块
- ✅ 家长端管理功能
- ✅ VIP会员体系
- ✅ 响应式设计适配
- ✅ API集成和错误处理
- ✅ 性能优化和代码重构

## 联系方式

- **项目负责人**: Claude
- **技术支持**: claude@anthropic.com
- **问题反馈**: GitHub Issues

---

*文档最后更新: 2025-08-20*

# ZYJC智能批改系统

## 启动说明

1. 安装依赖
   
首先安装必要的依赖包：
```bash
npm install http-server -g
```

2. 启动服务

在项目根目录(frontend)下运行：
```bash
http-server -p 3000
```

服务将在 http://localhost:3000 启动

3. 配置后端API

确保后端API服务运行在 http://localhost:8000

## 项目结构

```
frontend/
  ├── js/
  │   └── auth-utils.js    # 认证相关工具
  ├── profile.html         # 个人中心
  ├── login.html          # 登录页面
  └── ...其他页面
```

## 开发说明

- 本项目是纯前端项目，使用原生HTML、CSS和JavaScript开发
- 使用http-server作为开发服务器
- API基地址默认为 http://localhost:8000/api/v1

# ZYJC Frontend Server

## 命令行启动说明

1. 进入项目根目录：
```bash
cd d:\work\project\zyjc
```

2. 安装http-server（如果未安装）：
```bash
npm install http-server -g
```

3. 直接启动服务器：
```bash
# 在项目根目录启动，这样可以正确访问frontend目录
http-server . -p 8080
```

4. 使用start.bat启动（推荐）：
```bash
cd frontend
start.bat
```

## 快速启动指南

如果你当前在 `D:\work\project\zyjc\frontend` 目录下：

1. 安装http-server（如果未安装）：
```bash
npm install http-server -g
```

2. 使用以下任一命令启动服务：
```bash
# 方式1：直接启动（推荐）
http-server ..

# 方式2：指定端口启动
http-server .. -p 8080

# 方式3：使用批处理文件启动
start.bat
```

3. 访问页面：
- http://localhost:8080/frontend/login.html
- http://localhost:8080/frontend/student-home.html
- http://localhost:8080/frontend/parent-home.html
- http://localhost:8080/frontend/profile.html

注意：
- 使用 `http-server ..` 是因为需要将服务器根目录设置为项目根目录
- 确保URL中包含 `/frontend/` 路径
- 默认端口为8080，可以通过 `-p` 参数修改

## 访问说明

服务器启动后，通过以下URL访问：

- 登录页面：http://localhost:8080/frontend/login.html
- 学生首页：http://localhost:8080/frontend/student-home.html
- 家长首页：http://localhost:8080/frontend/parent-home.html
- 个人中心：http://localhost:8080/frontend/profile.html

注意：
- 确保在项目根目录（zyjc）下启动服务器
- 所有页面URL都需要包含 `/frontend/` 路径
- 后端API默认运行在 http://localhost:8000

## 目录结构
```
zyjc/                      # 项目根目录
├── frontend/             # 前端代码目录
│   ├── js/
│   ├── css/
│   ├── login.html
│   └── ...
└── backend/             # 后端代码目录
```