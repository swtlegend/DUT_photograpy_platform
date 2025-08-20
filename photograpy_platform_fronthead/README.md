# 摄影论坛前端项目

这是一个基于Vue 3 + Vite构建的摄影论坛前端项目，用户可以在平台上分享摄影作品、交流摄影技巧、互相点赞评论。

## 项目介绍

摄影论坛是一个为摄影爱好者打造的交流平台，用户可以：
- 用户注册和登录（基于学号系统）
- 发布摄影作品和心得
- 浏览他人作品
- 点赞和评论作品
- 关注其他用户
- 个人资料管理

## 技术栈

- [Vue 3](https://v3.vuejs.org/) - 渐进式JavaScript框架
- [Vite](https://vite.dev/) - 前端构建工具
- [Vue Router](https://router.vuejs.org/) - Vue.js官方路由管理器
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [Axios](https://axios-http.com/) - 基于Promise的HTTP客户端

## 项目结构

```
src/
├── api/              # API接口封装
├── components/       # 可复用组件
├── router/           # 路由配置
├── views/            # 页面视图
├── App.vue           # 根组件
└── main.js           # 入口文件
```

## 功能模块

### 用户系统
- 用户注册（学号、用户名、邮箱、密码）
- 用户登录
- 个人资料管理
- 头像和背景图片上传

### 帖子系统
- 发布新帖（标题、内容、图片）
- 浏览帖子列表
- 查看帖子详情
- 编辑和删除自己的帖子

### 社交功能
- 点赞/取消点赞帖子
- 评论帖子
- 关注/取消关注用户

## 开发环境搭建

### 环境要求
- Node.js >= 16.0
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

默认访问地址: http://localhost:5173

### 构建生产版本

```bash
npm run build
```

## 项目配置

### API代理配置
项目通过Vite的代理功能将API请求转发到后端服务：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://0.0.0.0:8000',
      changeOrigin: true,
    },
    '/images': {
      target: 'http://0.0.0.0:8000',
      changeOrigin: true,
    }
  }
}
```

### 路由配置
项目包含以下主要路由：
- `/` - 首页（帖子列表）
- `/login` - 登录页
- `/register` - 注册页
- `/post/:id` - 帖子详情页
- `/profile` - 个人中心
- `/user/:id` - 用户主页

## 认证机制

项目使用基于localStorage的简单认证机制：
1. 用户登录后，将用户ID和用户名存储在localStorage中
2. 每次API请求通过请求拦截器自动添加user_id参数
3. 未授权请求会被拦截并重定向到登录页

## 注意事项

1. 后端API服务需要单独运行，确保端口配置正确
2. 项目使用Element Plus组件库，所有UI组件均来自该库
3. 图片上传功能需要后端支持相应的文件处理接口

## 开发规范

- 使用Vue 3 `<script setup>`语法糖
- 组件拆分合理，保持可复用性
- API调用统一通过[src/api/index.js](file:///d:/github/photograpy_platform_fronthead/src/api/index.js)封装
- 使用Vue Router进行路由管理
- 状态管理使用localStorage存储用户信息
