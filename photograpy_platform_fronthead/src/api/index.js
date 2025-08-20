import axios from 'axios'

// 创建带认证的axios实例
const api = axios.create({
  baseURL: '/api', // 使用相对路径，通过Vite代理转发到后端
  timeout: 10000 // 将超时时间设置为30秒
})

// 创建不带认证的axios实例，用于公开接口
const publicApi = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器（带认证）- 使用查询参数传递用户ID
api.interceptors.request.use(
  config => {
    // 从localStorage获取用户ID
    const userId = localStorage.getItem('userId')
    if (userId) {
      // 将用户ID添加到查询参数中
      if (!config.params) {
        config.params = {}
      }
      config.params.user_id = userId
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('userId')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 用户相关API
export const userAPI = {
  // 用户注册
  register(data) {
    return api.post('/users/register', data)
  },
  
  // 用户登录
  login(data) {
    return api.post('/users/login', data)
  },
  
  // 更新用户资料
  updateProfile(data) {
    return api.put('/users/profile', data)
  },
  
  // 上传头像
  uploadAvatar(formData) {
    return api.post('/users/upload-avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 根据用户ID获取用户基础信息
  getUserInfoById(userId) {
    return publicApi.get(`/users/info/${userId}`)
  },
  
  // 根据用户名获取用户完整信息
  getUserByUsername(username) {
    return publicApi.get(`/users/${username}`)
  }
}

// 帖子相关API
export const postAPI = {
  // 发布帖子
  createPost(data) {
    return api.post('/posts/', data)
  },
  
  // 获取帖子列表（公开接口）
  getPosts(params) {
    return publicApi.get('/posts/', { params })
  },
  
  // 获取单个帖子（公开接口）
  getPost(id) {
    return publicApi.get(`/posts/${id}`)
  },
  
  // 更新帖子
  updatePost(id, data) {
    return api.put(`/posts/${id}`, data)
  },
  
  // 删除帖子
  deletePost(id) {
    return api.delete(`/posts/${id}`)
  },
  
  // 上传图片
  uploadImage(formData) {
    return api.post('/posts/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 评论相关API
export const commentAPI = {
  // 发布评论
  createComment(data) {
    return api.post('/comments/', data)
  },
  
  // 获取帖子评论列表
  getCommentsByPost(postId, params) {
    return api.get(`/comments/post/${postId}`, { params })
  },
  
  // 删除评论
  deleteComment(id) {
    return api.delete(`/comments/${id}`)
  }
}

// 点赞相关API
export const likeAPI = {
  // 点赞帖子
  likePost(data) {
    return api.post('/interactions/likes', data)
  },
  
  // 取消点赞
  unlikePost(postId) {
    return api.delete(`/interactions/likes?post_id=${postId}`)
  },
  
  // 检查是否已点赞
  checkLike(postId) {
    return api.get(`/interactions/likes/${postId}`)
  }
}

// 关注相关API
export const followAPI = {
  // 关注用户
  followUser(data) {
    return api.post('/follows/', data)
  },
  
  // 取消关注
  unfollowUser(id) {
    return api.delete(`/follows/${id}`)
  },
  
  // 检查是否已关注
  checkFollow(id) {
    return api.get(`/follows/${id}`)
  },
  
  // 获取用户统计数据（粉丝数等）
  getUserStats(userId) {
    return publicApi.get(`/follows/stats/${userId}`)
  }
}

// 评分相关API
export const ratingAPI = {
  // 创建评分
  createRating(data) {
    return api.post('/ratings/', data)
  },
  
  // 更新评分
  updateRating(postId, data) {
    return api.put(`/ratings/${postId}`, data)
  },
  
  // 删除评分
  deleteRating(postId) {
    return api.delete(`/ratings/${postId}`)
  },
  
  // 获取帖子评分统计信息
  getRatingStats(postId) {
    return api.get(`/ratings/${postId}/stats`)
  }
}

// 收藏相关API
export const collectionAPI = {
  // 收藏帖子
  collectPost(data) {
    return api.post('/collections/items/', data)
  },
  
  // 获取用户收藏夹列表
  getCollections(params) {
    return api.get('/collections/', { params })
  },
  
  // 创建收藏夹
  createCollection(data) {
    return api.post('/collections/', data)
  },
  
  // 更新收藏夹（重命名）
  updateCollection(id, data) {
    return api.put(`/collections/${id}`, data)
  },
  
  // 删除收藏夹
  deleteCollection(id) {
    return api.delete(`/collections/${id}`)
  },
  
  // 将帖子添加到指定收藏夹
  addToCollection(collectionId, data) {
    return api.post(`/collections/${collectionId}/items/`, data)
  },
  
  // 获取收藏夹中的帖子
  getCollectionItems(collectionId, params) {
    return api.get(`/collections/${collectionId}/items/`, { params })
  },
  
  // 从收藏夹中移除帖子
  removeItemFromCollection(collectionId, itemId) {
    return api.delete(`/collections/${collectionId}/items/${itemId}`)
  }
}

export default api