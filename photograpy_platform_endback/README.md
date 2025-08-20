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
│   ├── messages.py      # 私信相关路由
│   └── leaderboard.py   # 排行榜相关路由
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
   - 用户可以查看收藏夹中的帖子
   - 用户可以从收藏夹中移除帖子
10. 评分功能
11. 热门排行榜功能
12. 帖子搜索功能（根据标题匹配并按热度排序）
13. 个人主页自定义功能
    - 用户可以设置头像和背景图片
    - 用户可以设置帖子的可见性（全部人可见、好友可见、无时间限制、三个月内可见、一周内可见、三天内可见）
14. 私信功能

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

### 热门排行榜

- `GET /api/leaderboard/hot` - 获取热门帖子排行榜

### 私信相关

- `POST /api/messages/` - 发送私信给指定用户
- `POST /api/messages/upload-image` - 上传私信图片
- `GET /api/messages/conversation/{user_id}` - 获取与指定用户的对话记录
- `GET /api/messages/` - 获取我的所有消息记录

### 搜索

- `GET /api/posts/search/` - 搜索帖子

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