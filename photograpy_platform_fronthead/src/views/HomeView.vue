<template>
  <div class="home">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="logo">📸 摄影论坛</h1>
          <div class="user-actions">
            <el-button v-if="!isLoggedIn" @click="$router.push('/login')" type="primary" round>登录</el-button>
            <el-button v-if="!isLoggedIn" @click="$router.push('/register')" type="success" round>注册</el-button>
            <div v-else class="user-dropdown">
              <el-dropdown @command="handleUserCommand">
                <el-button type="primary">
                  {{ currentUser.username || '用户' }}
                  <el-icon class="el-icon--right">
                    <arrow-down />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <div class="main-content">
          <div class="post-form" v-if="isLoggedIn">
            <el-card class="post-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>发表新帖</span>
                </div>
              </template>
              <el-form :model="newPost" @submit.prevent="submitPost">
                <el-form-item label="标题">
                  <el-input v-model="newPost.title" placeholder="输入帖子标题" />
                </el-form-item>
                <el-form-item label="内容">
                  <el-input 
                    v-model="newPost.content" 
                    type="textarea" 
                    :rows="4"
                    placeholder="分享你的摄影心得..."
                  />
                </el-form-item>
                
                <!-- 图片上传部分 -->
                <el-form-item label="图片">
                  <div class="image-upload-section">
                    <el-button @click="handleFileSelect" :loading="postLoading" type="primary" plain>
                      选择图片
                    </el-button>
                    <input 
                      ref="fileInputRef"
                      type="file" 
                      multiple 
                      accept="image/*" 
                      @change="handleFileChange" 
                      style="display: none;"
                    />
                    
                    <!-- 已选择的图片预览 -->
                    <div v-if="newPost.images && newPost.images.length > 0" class="image-preview">
                      <div 
                        v-for="(image, index) in newPost.images" 
                        :key="index" 
                        class="image-preview-item"
                      >
                        <el-image 
                          :src="image" 
                          class="preview-image" 
                          fit="cover" 
                          :preview-src-list="newPost.images"
                        />
                        <el-button 
                          type="danger" 
                          size="small" 
                          @click="removeImage(index)" 
                          circle
                          class="remove-image-btn"
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                    </div>
                  </div>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="submitPost" :loading="postLoading" round>发布</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
          
          <div class="posts-header">
            <h2>📸 最新帖子</h2>
            <el-button @click="retryFetchPosts" type="primary" :loading="loadingPosts" round>
              {{ loadingPosts ? '刷新中...' : '刷新' }}
            </el-button>
          </div>
          
          <div class="posts-list">
            <el-card 
              v-for="post in posts" 
              :key="post.id" 
              class="post-card"
              shadow="hover"
            >
              <template #header>
                <div class="post-header">
                  <div class="post-author-info" @click="viewUser(post.author.id)" style="cursor: pointer;">
                    <el-avatar 
                      :size="30" 
                      :src="post.author.avatar_url || ''"
                      class="author-avatar"
                    >
                      {{ post.author.username?.substring(0, 1) || 'U' }}
                    </el-avatar>
                    <div class="author-details">
                      <div class="author-name">{{ post.author.username }}</div>
                    </div>
                  </div>
                  <h3 class="post-title">{{ post.title }}</h3>
                  <div class="post-meta">
                    <span>{{ new Date(post.created_at).toLocaleString() }}</span>
                  </div>
                </div>
              </template>
              <div class="post-content" @click="viewPost(post.id)">
                <p>{{ post.content.substring(0, 100) }}{{ post.content.length > 100 ? '...' : '' }}</p>
                
                <!-- 帖子图片显示 -->
                <div v-if="post.images && post.images.length > 0" class="post-images">
                  <el-image
                    v-for="(image, index) in post.images.slice(0, 3)"
                    :key="index"
                    :src="getImageUrl(image)"
                    :preview-src-list="post.images.map(getImageUrl)"
                    class="post-image"
                    fit="cover"
                    lazy
                  />
                  <div v-if="post.images.length > 3" class="more-images">
                    +{{ post.images.length - 3 }} 更多
                  </div>
                </div>
              </div>
              <div class="post-footer">
                <div class="post-stats">
                  <span class="stat-item"><el-icon><ChatDotRound /></el-icon> {{ post.comments_count || 0 }}</span>
                  <span class="stat-item"><el-icon><Star /></el-icon> {{ post.likes_count || 0 }}</span>
                  <span class="stat-item"><el-icon><Share /></el-icon> {{ post.shares_count || 0 }}</span>
                </div>
                <div class="post-actions">
                  <el-button 
                    size="small"
                    :type="post.isLiked ? 'danger' : 'default'"
                    @click.stop="toggleLike(post)"
                    :loading="post.likeLoading"
                    circle
                  >
                    <el-icon>
                      <Star v-if="!post.isLiked" />
                      <StarFilled v-if="post.isLiked" />
                    </el-icon>
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, ChatDotRound, Star, StarFilled, Share, Delete } from '@element-plus/icons-vue'
import { postAPI, likeAPI } from '../api'

const router = useRouter()

// 用户状态
const isLoggedIn = ref(!!localStorage.getItem('userId'))
const currentUser = ref({
  username: localStorage.getItem('username') || ''
})

// 帖子数据
const posts = ref([])
const newPost = ref({
  title: '',
  content: '',
  images: [] // 添加图片数组
})
const postLoading = ref(false)
const loadingPosts = ref(false)
const fileInputRef = ref(null) // 文件输入引用

// 获取帖子列表
const fetchPosts = async () => {
  loadingPosts.value = true;
  try {
    const response = await postAPI.getPosts({ skip: 0, limit: 10 });
    posts.value = response.data.map(post => ({
      ...post,
      isLiked: false,
      likeLoading: false
    })).sort((a, b) => new Date(b.created_at) - new Date(a.created_at)); // 按创建时间倒序排列
    
    // 检查点赞状态
    checkLikeStatuses();
  } catch (error) {
    console.error('获取帖子失败:', error);
    
    // 更详细的错误处理
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接或稍后重试');
    } else if (!error.response) {
      ElMessage.error('无法连接到服务器，请确保后端服务已启动');
    } else {
      ElMessage.error('获取帖子失败: ' + (error.response?.data?.detail || '请稍后重试'));
    }
  } finally {
    loadingPosts.value = false;
  }
}

// 添加重试机制
const retryFetchPosts = async (retryCount = 3) => {
  loadingPosts.value = true
  for (let i = 0; i < retryCount; i++) {
    try {
      await fetchPosts()
      ElMessage.success('刷新成功')
      return true
    } catch (error) {
      if (i === retryCount - 1) {
        // 最后一次重试仍然失败
        throw error
      }
      // 等待一段时间再重试
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
    }
  }
  loadingPosts.value = false
}

// 检查所有帖子的点赞状态
const checkLikeStatuses = async () => {
  if (!isLoggedIn.value) return
  
  for (const post of posts.value) {
    try {
      const response = await likeAPI.checkLike(post.id)
      post.isLiked = response.data
    } catch (error) {
      // 忽略错误
    }
  }
}

// 切换点赞状态
const toggleLike = async (post) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  post.likeLoading = true
  
  try {
    if (post.isLiked) {
      // 取消点赞
      await likeAPI.unlikePost(post.id)
      post.isLiked = false
      post.likes_count = (post.likes_count || 0) - 1
      ElMessage.success('已取消点赞')
    } else {
      // 点赞
      await likeAPI.likePost({ post_id: post.id })
      post.isLiked = true
      post.likes_count = (post.likes_count || 0) + 1
      ElMessage.success('点赞成功')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    post.likeLoading = false
  }
}

// 发布帖子
const submitPost = async () => {
  if (!newPost.value.title.trim() || !newPost.value.content.trim()) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  
  postLoading.value = true
  
  try {
    // 准备帖子数据，包含图片
    const postData = {
      title: newPost.value.title,
      content: newPost.value.content,
      images: newPost.value.images // 包含图片URL数组
    }
    
    // 调试信息
    console.log('发送的帖子数据:', postData)
    
    await postAPI.createPost(postData)
    ElMessage.success('发布成功')
    newPost.value = { title: '', content: '', images: [] } // 重置图片数组
    fetchPosts() // 重新获取帖子列表
  } catch (error) {
    console.error('发布失败:', error)
    
    // 更详细的错误处理
    let errorMessage = '发布失败，请稍后重试'
    if (error.response) {
      if (error.response.status === 422) {
        // 处理验证错误
        const detail = error.response.data.detail
        console.log('验证错误详情:', detail) // 调试信息
        
        if (typeof detail === 'object' && detail !== null) {
          // 如果detail是对象，尝试提取有用信息
          if (Array.isArray(detail)) {
            // 如果是数组，可能是多个错误
            if (detail.length > 0) {
              if (typeof detail[0] === 'object' && detail[0].loc && detail[0].msg) {
                // Pydantic验证错误格式
                errorMessage = '数据验证失败：' + detail.map(item => `${item.loc.join('.')}: ${item.msg}`).join(', ')
              } else {
                // 其他数组格式
                errorMessage = '数据验证失败：' + detail.map(item => item.msg || JSON.stringify(item)).join(', ')
              }
            } else {
              errorMessage = '数据验证失败'
            }
          } else if (detail.msg) {
            // 如果有msg字段
            errorMessage = '数据验证失败：' + detail.msg
          } else if (typeof detail === 'string') {
            // 如果是字符串
            errorMessage = '数据验证失败：' + detail
          } else {
            // 其他情况，尝试转换为字符串
            errorMessage = '数据验证失败：' + JSON.stringify(detail)
          }
        } else if (detail) {
          errorMessage = '数据验证失败：' + detail
        } else {
          errorMessage = '数据验证失败'
        }
      } else if (error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail
      }
    } else if (error.request) {
      errorMessage = '网络连接失败，请检查网络设置'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    postLoading.value = false
  }
}

// 查看帖子详情
const viewPost = (postId) => {
  router.push(`/post/${postId}`)
}

// 查看用户个人中心
const viewUser = (userId) => {
  const currentUserId = localStorage.getItem('userId')
  if (userId == currentUserId) {
    router.push('/profile')
  } else {
    router.push(`/user/${userId}`)
  }
}

// 用户操作处理
const handleUserCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    isLoggedIn.value = false
    currentUser.value = {}
    ElMessage.success('已退出登录')
    router.go(0) // 刷新页面
  }
}

// 处理文件选择
const handleFileSelect = () => {
  fileInputRef.value.click()
}

// 处理文件变化
const handleFileChange = async (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      continue
    }

    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', file)

    try {
      // 上传图片
      const response = await postAPI.uploadImage(formData)
      // 将返回的图片URL添加到数组中
      newPost.value.images.push(response.data.url)
      ElMessage.success(`图片 ${file.name} 上传成功`)
    } catch (error) {
      console.error('上传失败:', error)
      ElMessage.error('上传失败: ' + (error.response?.data?.detail || '请稍后重试'))
    }
  }

  // 清空文件输入框
  event.target.value = ''
}

// 移除已选择的图片
const removeImage = (index) => {
  newPost.value.images.splice(index, 1)
}

// 获取完整图片URL
const getImageUrl = (url) => {
  // 如果URL以http://或https://开头，则直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  // 否则拼接成完整URL
  return `${import.meta.env.VITE_API_BASE_URL}/${url}`;
};

onMounted(() => {
  retryFetchPosts().catch(error => {
    console.error('获取帖子失败:', error)
  })
})
</script>

<style scoped>
.home {
  height: 100%;
}

.app-header {
  background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.post-form {
  margin-bottom: 30px;
}

.post-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.post-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.post-author-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #409eff;
}

.post-title {
  margin: 10px 0;
  font-size: 1.3rem;
  color: #303133;
}

.post-meta {
  font-size: 0.85rem;
  color: #909399;
}

.post-content {
  cursor: pointer;
  padding: 15px 0;
}

.post-content p {
  line-height: 1.6;
  color: #606266;
}

.post-images {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.post-image {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
}

.more-images {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 150px;
  height: 150px;
  background-color: #f5f7fa;
  border-radius: 8px;
  color: #909399;
  font-weight: 500;
}

.image-preview {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.image-preview-item {
  position: relative;
  width: 100px;
  height: 100px;
}

.preview-image {
  width: 100%;
  height: 100%;
  border-radius: 6px;
}

.remove-image-btn {
  position: absolute;
  top: -8px;
  right: -8px;
}

.posts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.posts-header h2 {
  margin: 0;
  color: #303133;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.post-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 0.9rem;
}

.user-dropdown {
  margin-left: 10px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
  }
  
  .main-content {
    padding: 15px;
  }
  
  .posts-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .post-image {
    width: 100px;
    height: 100px;
  }
  
  .more-images {
    width: 100px;
    height: 100px;
  }
}
</style>