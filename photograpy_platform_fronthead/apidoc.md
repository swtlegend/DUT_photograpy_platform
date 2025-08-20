# 摄影论坛API接口文档

## 基础信息

- API基地址: `http://0.0.0.0:8000/api` (可通过本机IP从其他设备访问)
- 返回格式: JSON

## 认证机制

本系统使用简单的基于查询参数的用户认证机制。在需要认证的请求中，客户端需要在请求的查询参数中添加`user_id`字段来指定当前操作的用户ID。

**示例**：
```
POST /api/posts?user_id=2
```

对于需要用户身份验证的接口，如果未提供`user_id`参数，系统将返回422错误。

## 用户相关接口

### 用户注册

**接口地址**: `POST /users/register`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 |
| confirm_password | string | 是 | 确认密码 |
| id_number | string | 是 | 学号 |

**请求示例**:

```json
{
  "username": "photographer123",
  "email": "photo@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "id_number": "20230001"
}
```

**成功响应**:

```json
{
  "id": 1,
  "username": "photographer123",
  "email": "photo@example.com",
  "is_active": true,
  "id_number": "20230001"
}
```

**失败响应**:

```json
{
  "detail": "该学号已被注册"
}
```

**状态码**:
- 200: 注册成功
- 400: 学号已存在

### 用户登录

**接口地址**: `POST /users/login`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id_number | string | 是 | 学号 |
| password | string | 是 | 密码 |

**请求示例**:

```json
{
  "id_number": "20230001",
  "password": "password123"
}
```

**成功响应**:

```json
{
  "id": 1,
  "username": "photographer123",
  "email": "photo@example.com",
  "is_active": true,
  "id_number": "20230001"
}
```

**失败响应**:

```json
{
  "detail": "学号或密码错误"
}
```

**状态码**:
- 200: 登录成功
- 401: 学号或密码错误

### 忘记密码

**接口地址**: `POST /users/forgot-password`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id_number | string | 是 | 学号 |

**请求示例**:

```json
{
  "id_number": "20230001"
}
```

**成功响应**:

```json
{
  "message": "学号验证成功，请输入新密码"
}
```

**失败响应**:

```json
{
  "detail": "该学号未注册"
}
```

**状态码**:
- 200: 学号验证成功
- 404: 学号未注册

### 重置密码

**接口地址**: `POST /users/reset-password`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id_number | string | 是 | 学号 |
| new_password | string | 是 | 新密码 |

**请求示例**:

```json
{
  "id_number": "20230001",
  "new_password": "newpassword123"
}
```

**成功响应**:

```json
{
  "message": "密码重置成功"
}
```

**失败响应**:

```json
{
  "detail": "该学号未注册"
}
```

**状态码**:
- 200: 密码重置成功
- 404: 学号未注册

### 更新用户个人资料

**接口地址**: `PUT /users/profile`

**请求头参数**:
- `user-id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| avatar_url | string | 否 | 用户头像图片URL |
| background_url | string | 否 | 用户个人主页背景图片URL |

**请求示例**:

```json
{
  "avatar_url": "/images/avatar_1_a1b2c3d4e5f_20230101120000.jpg",
  "background_url": "/images/background_1_a1b2c3d4e5f_20230101120000.jpg"
}
```

**成功响应**:

```json
{
  "id": 1,
  "username": "photographer123",
  "email": "photo@example.com",
  "is_active": true,
  "avatar_url": "/images/avatar_1_a1b2c3d4e5f_20230101120000.jpg",
  "background_url": "/images/background_1_a1b2c3d4e5f_20230101120000.jpg"
}
```

**状态码**:
- 200: 更新成功
- 404: 用户未找到
- 500: 服务器内部错误

### 上传用户头像

**接口地址**: `POST /users/upload-avatar`

**请求头参数**:
- `user-id` (integer): 用户ID
- `Content-Type: multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | 头像图片文件 (支持jpg, jpeg, png格式) |

**请求示例**:

```
POST /api/users/upload-avatar
Content-Type: multipart/form-data

file: [头像图片文件]
```

**成功响应**:

``json
{
  "filename": "avatar_1_a1b2c3d4e5f_20230101120000.jpg",
  "url": "/images/avatar_1_a1b2c3d4e5f_20230101120000.jpg"
}
```

**失败响应**:

```json
{
  "detail": "不支持的文件格式，仅支持jpg、jpeg、png格式"
}
```

**状态码**:
- 200: 上传成功
- 400: 不支持的文件格式

### 上传个人主页背景图片

**接口地址**: `POST /users/upload-background`

**请求头参数**:
- `user-id` (integer): 用户ID
- `Content-Type: multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | 背景图片文件 (支持jpg, jpeg, png格式) |

**请求示例**:

```
POST /api/users/upload-background
Content-Type: multipart/form-data

file: [背景图片文件]
```

**成功响应**:

``json
{
  "filename": "background_1_a1b2c3d4e5f_20230101120000.jpg",
  "url": "/images/background_1_a1b2c3d4e5f_20230101120000.jpg",
  "message": "选出你拍出的最好一张图片做背景吧！"
}
```

**失败响应**:

```json
{
  "detail": "不支持的文件格式，仅支持jpg、jpeg、png格式"
}
```

**状态码**:
- 200: 上传成功
- 400: 不支持的文件格式

### 获取用户信息

**接口地址**: `GET /users/info/{user_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |

**请求示例**:

```
GET /api/users/info/1
```

**成功响应**:

```json
{
  "id": 1,
  "username": "photographer123",
  "email": "photo@example.com",
  "avatar_url": "/images/avatar_1_a1b2c3d4e5f_20230101120000.jpg"
}
```

**失败响应**:

```json
{
  "detail": "用户未找到"
}
```

**状态码**:
- 200: 获取成功
- 404: 用户未找到

### 通过用户名获取用户信息

**接口地址**: `GET /users/{username}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |

**请求示例**:

```
GET /api/users/photographer123
```

**成功响应**:

```json
{
  "id": 1,
  "username": "photographer123",
  "email": "photo@example.com",
  "is_active": true,
  "avatar_url": "/images/avatar_1_a1b2c3d4e5f_20230101120000.jpg",
  "background_url": "/images/background_1_a1b2c3d4e5f_20230101120000.jpg",
  "id_number": "20230001",
  "stats": {
    "followers_count": 10,
    "following_count": 5,
    "posts_count": 3,
    "likes_received": 25
  }
}
```

**失败响应**:

```json
{
  "detail": "用户未找到"
}
```

**状态码**:
- 200: 获取成功
- 404: 用户未找到

## 帖子相关接口

### 发布帖子

**接口地址**: `POST /posts/`

**查询参数**:
- `user_id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 是 | 帖子标题 |
| content | string | 是 | 帖子内容 |
| images | array | 否 | 图片URL数组 |
| visibility | integer | 否 | 帖子可见性设置 (0-全部人可见, 1-好友可见, 2-无时间限制, 3-三个月内可见, 4-一周内可见, 5-三天内可见) |

**请求示例**:

```
POST /api/posts?user_id=1
Content-Type: application/json

{
  "title": "我的第一次摄影之旅",
  "content": "今天我去了公园拍照，收获颇丰...",
  "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
  "visibility": 0
}
```

**成功响应**:

```json
{
  "id": 1,
  "title": "我的第一次摄影之旅",
  "content": "今天我去了公园拍照，收获颇丰...",
  "author_id": 1,
  "images": [],
  "visibility": 0,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": null,
  "author": {
    "id": 1,
    "username": "photographer123",
    "email": "photo@example.com",
    "is_active": true
  }
}
```

**状态码**:
- 200: 发布成功

### 上传图片

**接口地址**: `POST /posts/upload-image`

**请求头参数**:
- `user-id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | 图片文件 (支持jpg, jpeg, png, raw格式) |

**请求示例**:

```
POST /api/posts/upload-image
Content-Type: multipart/form-data

file: [图片文件]
```

**成功响应**:

```json
{
  "filename": "a1b2c3d4e5f_20230101120000.jpg",
  "url": "/images/a1b2c3d4e5f_20230101120000.jpg"
}
```

**失败响应**:

```json
{
  "detail": "不支持的文件格式"
}
```

**状态码**:
- 200: 上传成功
- 400: 不支持的文件格式

### 更新帖子

**接口地址**: `PUT /posts/{post_id}`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 否 | 帖子标题 |
| content | string | 否 | 帖子内容 |
| images | array | 否 | 图片URL数组 |
| visibility | integer | 否 | 帖子可见性设置 (0-全部人可见, 1-好友可见, 2-无时间限制, 3-三个月内可见, 4-一周内可见, 5-三天内可见) |

**请求示例**:

```
PUT /api/posts/1?user_id=1
Content-Type: application/json

{
  "title": "更新后的标题",
  "content": "更新后的内容...",
  "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
  "visibility": 3
}
```

**成功响应**:

```json
{
  "id": 1,
  "title": "更新后的标题",
  "content": "更新后的内容...",
  "author_id": 1,
  "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
  "visibility": 3,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-02T12:00:00",
  "author": {
    "id": 1,
    "username": "photographer123",
    "email": "photo@example.com",
    "is_active": true
  }
}
```

**失败响应**:

```json
{
  "detail": "帖子未找到"
}
```

**状态码**:
- 200: 更新成功
- 404: 帖子未找到

### 获取帖子列表

**接口地址**: `GET /posts/`

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为100 |

**排序规则**:
返回的帖子按创建时间倒序排列（最新的帖子在前面）。

**请求示例**:

```
GET /api/posts/?skip=0&limit=10
```

**成功响应**:

```json
[
  {
    "id": 1,
    "title": "我的第一次摄影之旅",
    "content": "今天我去了公园拍照，收获颇丰...",
    "author_id": 1,
    "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
    "visibility": 0,
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null,
    "author": {
      "id": 1,
      "username": "photographer123",
      "email": "photo@example.com",
      "is_active": true
    },
    "likes_count": 5,
    "comments_count": 3,
    "shares_count": 2
  }
]
```

**状态码**:
- 200: 获取成功

### 获取用户帖子列表

**接口地址**: `GET /posts/user/{user_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为100 |

**请求示例**:

```
GET /api/posts/user/1?skip=0&limit=10
```

**成功响应**:

```json
[
  {
    "id": 1,
    "title": "我的第一次摄影之旅",
    "content": "今天我去了公园拍照，收获颇丰...",
    "author_id": 1,
    "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
    "visibility": 0,
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null,
    "author": {
      "id": 1,
      "username": "photographer123",
      "email": "photo@example.com",
      "is_active": true
    },
    "likes_count": 5,
    "comments_count": 3,
    "shares_count": 2
  }
]
```

**状态码**:
- 200: 获取成功

### 获取单个帖子

**接口地址**: `GET /posts/{post_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:

```
GET /api/posts/1
```

**成功响应**:

```json
{
  "id": 1,
  "title": "我的第一次摄影之旅",
  "content": "今天我去了公园拍照，收获颇丰...",
  "author_id": 1,
  "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
  "visibility": 0,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": null,
  "author": {
    "id": 1,
    "username": "photographer123",
    "email": "photo@example.com",
    "is_active": true
  },
  "likes_count": 5,
  "comments_count": 3,
  "shares_count": 2
}
```

**失败响应**:

```json
{
  "detail": "帖子未找到"
}
```

**状态码**:
- 200: 获取成功
- 404: 帖子未找到

### 删除帖子

**接口地址**: `DELETE /posts/{post_id}`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:

```
DELETE /api/posts/1?user_id=1
```

**成功响应**:

```json
{
  "id": 1,
  "title": "我的第一次摄影之旅",
  "content": "今天我去了公园拍照，收获颇丰...",
  "author_id": 1,
  "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
  "visibility": 0,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": null
}
```

**失败响应**:

```json
{
  "detail": "帖子未找到"
}
```

**状态码**:
- 200: 删除成功
- 404: 帖子未找到

## 评论相关接口

### 发布评论

**接口地址**: `POST /comments/`

**查询参数**:
- `user_id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 评论内容 |
| post_id | integer | 是 | 帖子ID |

**请求示例**:
```
POST /api/comments/?user_id=2
Content-Type: application/json

{
  "content": "这是一条很棒的摄影作品！",
  "post_id": 1
}
```

**成功响应**:

```json
{
  "id": 1,
  "content": "这是一条很棒的摄影作品！",
  "author_id": 2,
  "post_id": 1,
  "created_at": "2023-01-01T12:00:00",
  "author": {
    "id": 2,
    "username": "viewer123",
    "email": "viewer@example.com",
    "is_active": true
  }
}
```

**状态码**:
- 200: 发布成功

### 获取帖子评论列表

**接口地址**: `GET /comments/post/{post_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为100 |

**请求示例**:

```
GET /api/comments/post/1?skip=0&limit=10
```

**成功响应**:

```json
[
  {
    "id": 1,
    "content": "这是一条很棒的摄影作品！",
    "author_id": 2,
    "post_id": 1,
    "created_at": "2023-01-01T12:00:00",
    "author": {
      "id": 2,
      "username": "viewer123",
      "email": "viewer@example.com",
      "is_active": true
    }
  }
]
```

**状态码**:
- 200: 获取成功

### 删除评论

**接口地址**: `DELETE /comments/{comment_id}`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| comment_id | integer | 是 | 评论ID |

**请求示例**:

```
DELETE /api/comments/1?user_id=2
```

**成功响应**:

```json
{
  "id": 1,
  "content": "这是一条很棒的摄影作品！",
  "author_id": 2,
  "post_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "评论未找到"
}
```

**状态码**:
- 200: 删除成功
- 404: 评论未找到

## 点赞相关接口

### 点赞帖子

**接口地址**: `POST /interactions/likes`

**查询参数**:
- `user_id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:
```
POST /api/interactions/likes?user_id=2
Content-Type: application/json

{
  "post_id": 1
}
```

**成功响应**:

```json
{
  "id": 1,
  "user_id": 2,
  "post_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**状态码**:
- 200: 点赞成功

### 取消点赞

**接口地址**: `DELETE /interactions/likes`

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |
| post_id | integer | 是 | 帖子ID |

**请求示例**:

```
DELETE /api/interactions/likes?user_id=2&post_id=1
```

**成功响应**:

```json
{
  "message": "取消点赞成功"
}
```

**状态码**:
- 200: 取消点赞成功

### 检查是否已点赞

**接口地址**: `GET /interactions/likes/{post_id}`

**查询参数**:
- `user_id` (integer, optional): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:

```
GET /api/interactions/likes/1?user_id=2
```

**成功响应**:

```json
true
```

**状态码**:
- 200: 获取成功

## 分享相关接口

### 分享帖子

**接口地址**: `POST /interactions/shares`

**请求头参数**:
- `user-id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:
```
POST /api/interactions/shares
Content-Type: application/json
user-id: 2

{
  "post_id": 1
}
```

**成功响应**:

```json
{
  "id": 1,
  "user_id": 2,
  "post_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**状态码**:
- 200: 分享成功

### 取消分享

**接口地址**: `DELETE /interactions/shares?post_id={post_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:

```
DELETE /api/interactions/shares?post_id=1
user-id: 2
```

**成功响应**:

```json
{
  "message": "取消分享成功"
}
```

**状态码**:
- 200: 取消分享成功

### 检查是否已分享

**接口地址**: `GET /interactions/shares/{post_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:

```
GET /api/interactions/shares/1
user-id: 2
```

**成功响应**:

```json
true
```

**状态码**:
- 200: 获取成功

## 关注相关接口

### 关注用户

**接口地址**: `POST /follows/`

**请求头参数**:
- `user-id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| following_id | integer | 是 | 被关注用户ID |

**请求示例**:
```
POST /api/follows/
Content-Type: application/json
user-id: 2

{
  "following_id": 1
}
```

**成功响应**:

```json
{
  "id": 1,
  "follower_id": 2,
  "following_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "不能关注自己"
}
```

**状态码**:
- 200: 关注成功
- 400: 不能关注自己

### 取消关注

**接口地址**: `DELETE /follows/{following_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| following_id | integer | 是 | 被关注用户ID |

**请求示例**:

```
DELETE /api/follows/1
user-id: 2
```

**成功响应**:

```json
{
  "message": "取消关注成功"
}
```

**状态码**:
- 200: 取消关注成功

### 检查是否已关注

**接口地址**: `GET /follows/{user_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 被关注用户ID |

**请求示例**:

```
GET /api/follows/1
user-id: 2
```

**成功响应**:

```json
true
```

**状态码**:
- 200: 获取成功

### 获取用户统计信息

**接口地址**: `GET /follows/stats/{user_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |

**请求示例**:

```
GET /api/follows/stats/1
```

**成功响应**:

```json
{
  "followers_count": 10,
  "total_likes_received": 50
}
```

**状态码**:
- 200: 获取成功

## 收藏相关接口

### 获取用户收藏夹列表

**接口地址**: `GET /collections/`

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为100 |

**请求示例**:

```
GET /api/collections/?user_id=2&skip=0&limit=10
```

**成功响应**:

```json
[
  {
    "id": 1,
    "name": "默认收藏夹",
    "user_id": 2,
    "is_default": true,
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null
  },
  {
    "id": 2,
    "name": "风景摄影",
    "user_id": 2,
    "is_default": false,
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null
  }
]
```

**状态码**:
- 200: 获取成功

### 创建收藏夹

**接口地址**: `POST /collections/`

**查询参数**:
- `user_id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 是 | 收藏夹名称 |

**请求示例**:
```
POST /api/collections/?user_id=2
Content-Type: application/json

{
  "name": "人像摄影"
}
```

**成功响应**:

```json
{
  "id": 3,
  "name": "人像摄影",
  "user_id": 2,
  "is_default": false,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": null
}
```

**状态码**:
- 200: 创建成功

### 更新收藏夹（重命名）

**接口地址**: `PUT /collections/{collection_id}`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 是 | 新的收藏夹名称 |

**请求示例**:
```
PUT /api/collections/2?user_id=2
Content-Type: application/json

{
  "name": "风光摄影"
}
```

**成功响应**:

```json
{
  "id": 2,
  "name": "风光摄影",
  "user_id": 2,
  "is_default": false,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-02T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "收藏夹不存在"
}
```

**状态码**:
- 200: 更新成功
- 404: 收藏夹不存在

### 删除收藏夹

**接口地址**: `DELETE /collections/{collection_id}`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**请求示例**:

```
DELETE /api/collections/2?user_id=2
```

**成功响应**:

```json
{
  "id": 2,
  "name": "风光摄影",
  "user_id": 2,
  "is_default": false,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-02T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "收藏夹不存在"
}
```

**状态码**:
- 200: 删除成功
- 404: 收藏夹不存在

### 收藏帖子

**接口地址**: `POST /collections/items/`

**查询参数**:
- `user_id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:
```
POST /api/collections/items/?user_id=2
Content-Type: application/json

{
  "post_id": 1
}
```

**成功响应**:

```json
{
  "id": 1,
  "post_id": 1,
  "user_id": 2,
  "collection_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "不能收藏自己的帖子"
}
```

**状态码**:
- 200: 收藏成功
- 400: 不能收藏自己的帖子

### 将帖子添加到指定收藏夹

**接口地址**: `POST /collections/{collection_id}/items/`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:
```
POST /api/collections/3/items/?user_id=2
Content-Type: application/json

{
  "post_id": 1
}
```

**成功响应**:

```json
{
  "id": 2,
  "post_id": 1,
  "user_id": 2,
  "collection_id": 3,
  "created_at": "2023-01-01T12:00:00"
}
```

**状态码**:
- 200: 添加成功

### 获取收藏夹中的帖子

**接口地址**: `GET /collections/{collection_id}/items/`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为100 |

**请求示例**:

```
GET /api/collections/1/items/?user_id=2&skip=0&limit=10
```

**成功响应**:

```json
[
  {
    "id": 1,
    "post_id": 1,
    "user_id": 2,
    "collection_id": 1,
    "created_at": "2023-01-01T12:00:00",
    "post": {
      "id": 1,
      "title": "我的第一次摄影之旅",
      "content": "今天我去了公园拍照，收获颇丰...",
      "author_id": 1,
      "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
      "created_at": "2023-01-01T12:00:00",
      "updated_at": null,
      "author": {
        "id": 1,
        "username": "photographer123",
        "email": "photo@example.com",
        "is_active": true
      }
    }
  }
]
```

**状态码**:
- 200: 获取成功

### 从收藏夹中移除帖子

**接口地址**: `DELETE /collections/{collection_id}/items/{item_id}`

**查询参数**:
- `user_id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |
| item_id | integer | 是 | 收藏项ID |

**请求示例**:

```
DELETE /api/collections/1/items/1?user_id=2
```

**成功响应**:

```json
{
  "id": 1,
  "post_id": 1,
  "user_id": 2,
  "collection_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**状态码**:
- 200: 移除成功

## 收藏相关接口

### 获取用户收藏夹列表

**接口地址**: `GET /collections/`

**请求头参数**:
- `user-id` (integer): 用户ID

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为100 |

**请求示例**:

```
GET /api/collections/?skip=0&limit=10
user-id: 2
```

**成功响应**:

```json
[
  {
    "id": 1,
    "name": "默认收藏夹",
    "user_id": 2,
    "is_default": true,
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null
  },
  {
    "id": 2,
    "name": "风景摄影",
    "user_id": 2,
    "is_default": false,
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null
  }
]
```

**状态码**:
- 200: 获取成功

### 创建收藏夹

**接口地址**: `POST /collections/`

**请求头参数**:
- `user-id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 是 | 收藏夹名称 |

**请求示例**:
```
POST /api/collections/
Content-Type: application/json
user-id: 2

{
  "name": "人像摄影"
}
```

**成功响应**:

```json
{
  "id": 3,
  "name": "人像摄影",
  "user_id": 2,
  "is_default": false,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": null
}
```

**状态码**:
- 200: 创建成功

### 更新收藏夹（重命名）

**接口地址**: `PUT /collections/{collection_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 是 | 新的收藏夹名称 |

**请求示例**:
```
PUT /api/collections/2
Content-Type: application/json
user-id: 2

{
  "name": "风光摄影"
}
```

**成功响应**:

```json
{
  "id": 2,
  "name": "风光摄影",
  "user_id": 2,
  "is_default": false,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-02T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "收藏夹不存在"
}
```

**状态码**:
- 200: 更新成功
- 404: 收藏夹不存在

### 删除收藏夹

**接口地址**: `DELETE /collections/{collection_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**请求示例**:

```
DELETE /api/collections/2
user-id: 2
```

**成功响应**:

```json
{
  "id": 2,
  "name": "风光摄影",
  "user_id": 2,
  "is_default": false,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-02T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "收藏夹不存在"
}
```

**状态码**:
- 200: 删除成功
- 404: 收藏夹不存在

### 收藏帖子

**接口地址**: `POST /collections/items/`

**请求头参数**:
- `user-id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:
```
POST /api/collections/items/
Content-Type: application/json
user-id: 2

{
  "post_id": 1
}
```

**成功响应**:

```json
{
  "id": 1,
  "post_id": 1,
  "user_id": 2,
  "collection_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**失败响应**:

```json
{
  "detail": "不能收藏自己的帖子"
}
```

**状态码**:
- 200: 收藏成功
- 400: 不能收藏自己的帖子

### 将帖子添加到指定收藏夹

**接口地址**: `POST /collections/{collection_id}/items/`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | integer | 是 | 帖子ID |

**请求示例**:
```
POST /api/collections/3/items/
Content-Type: application/json
user-id: 2

{
  "post_id": 1
}
```

**成功响应**:

```json
{
  "id": 2,
  "post_id": 1,
  "user_id": 2,
  "collection_id": 3,
  "created_at": "2023-01-01T12:00:00"
}
```

**状态码**:
- 200: 添加成功

### 获取收藏夹中的帖子

**接口地址**: `GET /collections/{collection_id}/items/`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为100 |

**请求示例**:

```
GET /api/collections/1/items/?skip=0&limit=10
user-id: 2
```

**成功响应**:

```json
[
  {
    "id": 1,
    "post_id": 1,
    "user_id": 2,
    "collection_id": 1,
    "created_at": "2023-01-01T12:00:00",
    "post": {
      "id": 1,
      "title": "我的第一次摄影之旅",
      "content": "今天我去了公园拍照，收获颇丰...",
      "author_id": 1,
      "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
      "created_at": "2023-01-01T12:00:00",
      "updated_at": null,
      "author": {
        "id": 1,
        "username": "photographer123",
        "email": "photo@example.com",
        "is_active": true
      }
    }
  }
]
```

**状态码**:
- 200: 获取成功

### 从收藏夹中移除帖子

**接口地址**: `DELETE /collections/{collection_id}/items/{item_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| collection_id | integer | 是 | 收藏夹ID |
| item_id | integer | 是 | 收藏项ID |

**请求示例**:

```
DELETE /api/collections/1/items/1
user-id: 2
```

**成功响应**:

```json
{
  "id": 1,
  "post_id": 1,
  "user_id": 2,
  "collection_id": 1,
  "created_at": "2023-01-01T12:00:00"
}
```

**状态码**:
- 200: 移除成功

## 错误响应格式

所有错误响应都遵循以下格式:

```json
{
  "detail": "错误信息"
}
```

## 评分相关接口

### 创建评分
- **URL**: `/api/ratings/`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `user-id: 用户ID` (用于标识当前用户)
- **Request Body**:
```json
{
  "post_id": 1,
  "score": 8.5
}
```
- **Response**:
```json
{
  "post_id": 1,
  "score": 8.5,
  "id": 1,
  "user_id": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### 更新评分
- **URL**: `/api/ratings/{post_id}`
- **Method**: `PUT`
- **Headers**: 
  - `Content-Type: application/json`
  - `user-id: 用户ID` (用于标识当前用户)
- **Request Body**:
```json
{
  "post_id": 1,
  "score": 9.0
}
```
- **Response**:
```json
{
  "post_id": 1,
  "score": 9.0,
  "id": 1,
  "user_id": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### 删除评分
- **URL**: `/api/ratings/{post_id}`
- **Method**: `DELETE`
- **Headers**: `user-id: 用户ID` (用于标识当前用户)
- **Response**:
```json
{
  "message": "评分已删除"
}
```

### 获取帖子评分统计信息
- **URL**: `/api/ratings/{post_id}/stats`
- **Method**: `GET`
- **Response**:
```json
{
  "rating_count": 10,
  "average_rating": 8.5
}
```

## 热门排行榜接口

### 获取热门帖子排行榜
- **URL**: `/api/leaderboard/hot`
- **Method**: `GET`
- **Query Parameters**:
  - `period` (string, optional): 排行榜周期 ("week", "month", "year")，默认为 "week"
  - `limit` (integer, optional): 返回帖子数量 (1-100)，默认为 10
- **Response**:
```json
[
  {
    "id": 1,
    "title": "我的第一次摄影之旅",
    "content": "今天我去了公园拍照，收获颇丰...",
    "author_id": 1,
    "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null,
    "author": {
      "id": 1,
      "username": "photographer123",
      "email": "photo@example.com",
      "is_active": true
    },
    "likes_count": 5,
    "comments_count": 3,
    "shares_count": 2,
    "collections_count": 1,
    "rating_count": 10,
    "average_rating": 8.5
  }
]
```

## 搜索接口

### 搜索帖子
- **URL**: `/api/posts/search/`
- **Method**: `GET`
- **Query Parameters**:
  - `query` (string, required): 搜索关键词
  - `skip` (integer, optional): 跳过的记录数，默认为 0
  - `limit` (integer, optional): 限制返回记录数，默认为 100
- **Response**:
```json
[
  {
    "id": 1,
    "title": "我的第一次摄影之旅",
    "content": "今天我去了公园拍照，收获颇丰...",
    "author_id": 1,
    "images": ["/images/a1b2c3d4e5f_20230101120000.jpg"],
    "created_at": "2023-01-01T12:00:00",
    "updated_at": null,
    "author": {
      "id": 1,
      "username": "photographer123",
      "email": "photo@example.com",
      "is_active": true
    },
    "likes_count": 5,
    "comments_count": 3,
    "shares_count": 2,
    "collections_count": 1,
    "rating_count": 10,
    "average_rating": 8.5
  }
]
```
当没有搜索到相关内容时，将返回空数组 `[]`。

## 私信相关接口

### 发送私信

**接口地址**: `POST /messages/`

**请求头参数**:
- `user-id` (integer): 用户ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| recipient_id | integer | 是 | 接收者用户ID |
| content | string | 是 | 消息内容，最多500字 |
| image_url | string | 否 | 图片URL |

**请求示例**:
```
POST /api/messages/
Content-Type: application/json
user-id: 1

{
  "recipient_id": 2,
  "content": "你好，我想了解一下你的摄影技巧",
  "image_url": null
}
```

**成功响应**:

```json
{
  "id": 1,
  "sender_id": 1,
  "recipient_id": 2,
  "content": "你好，我想了解一下你的摄影技巧",
  "image_url": null,
  "created_at": "2023-01-01T12:00:00",
  "sender": {
    "id": 1,
    "username": "photographer123",
    "email": "photo@example.com",
    "is_active": true
  },
  "recipient": {
    "id": 2,
    "username": "viewer123",
    "email": "viewer@example.com",
    "is_active": true
  }
}
```

**失败响应**:

```json
{
  "detail": "不能给自己发送消息"
}
```

**状态码**:
- 200: 发送成功
- 400: 不能给自己发送消息

### 上传私信图片

**接口地址**: `POST /messages/upload-image`

**请求头参数**:
- `user-id` (integer): 用户ID
- `Content-Type: multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | 图片文件 (支持jpg, jpeg, png格式) |

**请求示例**:

```
POST /api/messages/upload-image
Content-Type: multipart/form-data
user-id: 1

file: [图片文件]
```

**成功响应**:

```json
{
  "image_url": "/images/messages/msg_1_20230101120000.jpg"
}
```

**失败响应**:

```json
{
  "detail": "不支持的文件格式，仅支持jpg、jpeg、png格式"
}
```

**状态码**:
- 200: 上传成功
- 400: 不支持的文件格式

### 获取与指定用户的对话记录

**接口地址**: `GET /messages/conversation/{user_id}`

**请求头参数**:
- `user-id` (integer): 用户ID

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 对方用户ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为50 |

**请求示例**:

```
GET /api/messages/conversation/2?skip=0&limit=50
user-id: 1
```

**成功响应**:

```json
[
  {
    "id": 1,
    "sender_id": 1,
    "recipient_id": 2,
    "content": "你好，我想了解一下你的摄影技巧",
    "image_url": null,
    "created_at": "2023-01-01T12:00:00",
    "sender": {
      "id": 1,
      "username": "photographer123",
      "email": "photo@example.com",
      "is_active": true
    },
    "recipient": {
      "id": 2,
      "username": "viewer123",
      "email": "viewer@example.com",
      "is_active": true
    }
  }
]
```

**状态码**:
- 200: 获取成功

### 获取我的所有消息记录

**接口地址**: `GET /messages/`

**请求头参数**:
- `user-id` (integer): 用户ID

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 限制返回记录数，默认为50 |

**请求示例**:

```
GET /api/messages/?skip=0&limit=50
user-id: 1
```

**成功响应**:

```json
[
  {
    "id": 1,
    "sender_id": 1,
    "recipient_id": 2,
    "content": "你好，我想了解一下你的摄影技巧",
    "image_url": null,
    "created_at": "2023-01-01T12:00:00",
    "sender": {
      "id": 1,
      "username": "photographer123",
      "email": "photo@example.com",
      "is_active": true
    },
    "recipient": {
      "id": 2,
      "username": "viewer123",
      "email": "viewer@example.com",
      "is_active": true
    }
  }
]
```

**状态码**:
- 200: 获取成功
