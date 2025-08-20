#赛题：智享生活

#问题发现：在校园墙频繁看到同学们求摄影佳作，沟通效率低下。作为同样热爱摄影的DUT学子，我们决定联手打造一个专属平台，让校园美景的分享更便捷、更专业。

# 摄影论坛前端项目

这是一个基于Vue 3 + Vite构建的摄影论坛前端项目，用户可以在平台上分享摄影作品、交流摄影技巧、互相点赞评论。

项目运行后可以通过以下地址访问：
- 本地开发环境: http://localhost:5173
- 如果需要从其他设备访问，可以使用运行设备的IP地址，如: http://192.168.1.100:5173

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


  # 摄影论坛后端API

这是一个使用FastAPI框架构建的简单摄影论坛后端系统。

## 项目结构

```
.
├── main.py              # 应用入口文件
├── models.py            # 数据模型定义
├── database.py          # 数据库配置和模型
├── crud.py              # 数据库操作
├── dependencies.py      # 依赖项
├── requirements.txt     # 项目依赖
├── run.py               # 运行脚本
├── apidoc.md            # API文档
├── routers/             # 路由目录
│   ├── users.py         # 用户相关路由
│   ├── posts.py         # 帖子相关路由
│   ├── comments.py      # 评论相关路由
│   ├── interactions.py  # 互动（点赞、分享）相关路由
│   ├── follows.py       # 关注相关路由
│   ├── collections.py   # 收藏相关路由
│   ├── ratings.py       # 评分相关路由
└── README.md            # 项目说明文件
```

## 功能说明

1. 用户注册和登录（使用学号作为唯一标识）
   - 用户使用学号注册账户，每个学号只能注册一个账户
   - 用户登录时使用学号和密码进行身份验证
   - 提供忘记密码功能，用户可以通过学号重置密码
2. 发布、查看、更新和删除帖子
3. 上传和管理图片
4. 按用户筛选帖子
5. 评论功能
6. 点赞功能
7. 分享功能
8. 关注功能
9. 收藏功能
   - 用户可以创建、重命名和删除收藏夹
   - 用户可以将帖子收藏到默认收藏夹或指定收藏夹
   - 用户可以从收藏夹中移除帖子
10. 评分功能




## 用户相关API端点

- `POST /api/users/register` - 用户注册（使用学号）
- `POST /api/users/login` - 用户登录（使用学号）
- `POST /api/users/forgot-password` - 忘记密码验证学号
- `POST /api/users/reset-password` - 重置密码
- `PUT /api/users/profile` - 更新用户个人资料
- `GET /api/users/profile/{user_id}` - 获取用户个人资料

## 环境管理

本项目可以在虚拟环境中运行，包括但不限于conda环境。如果使用conda环境(如DL环境)，请在安装依赖前激活相应环境：

```bash
conda activate DL
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行项目

```bash
python run.py
项目将在 `http://0.0.0.0:8000` 上运行，可以通过本机IP地址从其他设备访问。

例如，如果本机IP地址是192.168.1.100，则可以从其他设备通过 `http://192.168.1.100:8000` 访问API。
```

或者

```bash
uvicorn main:app --reload
```
项目将在http://127.0.0.1:8000上运行


## 认证机制

本系统使用简单的基于HTTP头部的用户认证机制。在需要认证的请求中，客户端需要在请求头中添加`user-id`字段来指定当前操作的用户ID。

示例：
```
user-id: 2
```

如果未提供`user-id`头部，系统将默认使用ID为1的用户。

## API接口

### 用户相关

- `POST /api/users/register` - 用户注册
- `POST /api/users/login` - 用户登录
- `PUT /api/users/profile` - 更新用户个人资料（头像、背景图片）
- `POST /api/users/upload-avatar` - 上传用户头像
- `POST /api/users/upload-background` - 上传个人主页背景图片

### 帖子相关

- `POST /api/posts/` - 创建新帖子
- `GET /api/posts/` - 获取帖子列表
- `GET /api/posts/{post_id}` - 获取单个帖子
- `PUT /api/posts/{post_id}` - 更新帖子（包括可见性设置）
- `DELETE /api/posts/{post_id}` - 删除帖子
- `GET /api/posts/user/{user_id}` - 获取指定用户的帖子
- `POST /api/posts/upload-image` - 上传图片
- `GET /api/posts/search/` - 搜索帖子

### 评论相关

- `POST /api/comments/` - 创建新评论
- `GET /api/comments/post/{post_id}` - 获取指定帖子的评论列表
- `DELETE /api/comments/{comment_id}` - 删除评论

### 互动相关（点赞、分享）

- `POST /api/interactions/likes` - 点赞帖子
- `DELETE /api/interactions/likes?post_id={post_id}` - 取消点赞
- `GET /api/interactions/likes/{post_id}` - 检查是否已点赞
- `POST /api/interactions/shares` - 分享帖子
- `DELETE /api/interactions/shares?post_id={post_id}` - 取消分享
- `GET /api/interactions/shares/{post_id}` - 检查是否已分享

### 关注相关

- `POST /api/follows/` - 关注用户
- `DELETE /api/follows/{following_id}` - 取消关注
- `GET /api/follows/{user_id}` - 检查是否已关注
- `GET /api/follows/stats/{user_id}` - 获取用户统计信息

### 收藏相关

- `GET /api/collections/` - 获取用户收藏夹列表
- `POST /api/collections/` - 创建新收藏夹
- `PUT /api/collections/{collection_id}` - 更新收藏夹（重命名）
- `DELETE /api/collections/{collection_id}` - 删除收藏夹
- `POST /api/collections/items/` - 收藏帖子（自动分配到默认收藏夹）
- `POST /api/collections/{collection_id}/items/` - 将帖子添加到指定收藏夹
- `GET /api/collections/{collection_id}/items/` - 获取收藏夹中的帖子
- `DELETE /api/collections/{collection_id}/items/{item_id}` - 从收藏夹中移除帖子

### 评分相关

- `POST /api/ratings/` - 创建评分
- `PUT /api/ratings/{post_id}` - 更新评分
- `DELETE /api/ratings/{post_id}` - 删除评分
- `GET /api/ratings/{post_id}/stats` - 获取帖子评分统计信息
### 图片访问

上传的图片可以通过 `/images/{filename}` 路径访问。

## 数据库

项目使用SQLite数据库，数据文件为`forum.db`，会在首次运行时自动创建。

数据库包含以下表：
- `users` - 存储用户信息（包含头像和背景图片URL）
- `posts` - 存储帖子信息，包括与用户的关联关系（包含可见性设置）
- `comments` - 存储评论信息
- `likes` - 存储点赞信息
- `shares` - 存储分享信息
- `follows` - 存储关注信息
- `collections` - 存储收藏夹信息
- `collection_items` - 存储收藏记录信息
- `ratings` - 存储评分信息
- `messages` - 存储私信信息

数据库表会在应用启动时自动创建，并且支持自动迁移以添加新字段。
