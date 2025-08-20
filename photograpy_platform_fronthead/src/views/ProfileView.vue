<template>
  <div class="profile">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <el-button @click="$router.go(-1)" type="primary" round>返回</el-button>
          <h1 class="logo">📸 摄影论坛</h1>
          <div class="spacer"></div>
        </div>
      </el-header>
      
      <el-main>
        <div class="main-content">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="profile-card" shadow="hover">
                <div class="profile-header">
                  <el-avatar :size="80" :src="userProfile.avatar_url || ''" class="user-avatar">
                    {{ userProfile.username?.substring(0, 1) || 'U' }}
                  </el-avatar>
                  <h3>{{ userProfile.username || '未登录' }}</h3>
                  <p>{{ userProfile.email || '' }}</p>
                </div>
                
                <div class="profile-stats">
                  <div class="stat-item">
                    <div class="stat-value">{{ postCount }}</div>
                    <div class="stat-label">帖子</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ likeCount }}</div>
                    <div class="stat-label">获赞</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ followerCount }}</div>
                    <div class="stat-label">粉丝</div>
                  </div>
                </div>
                
                <div class="profile-actions" v-if="isLoggedIn && !isOwnProfile">
                  <el-button 
                    :type="isFollowing ? 'danger' : 'primary'" 
                    @click="toggleFollow"
                    :loading="followLoading"
                    round
                    size="large"
                  >
                    {{ isFollowing ? '已关注' : '关注' }}
                  </el-button>
                </div>
                
                <div class="profile-actions" v-if="isOwnProfile">
                  <el-button 
                    type="danger" 
                    @click="handleLogout"
                    round
                    size="large"
                  >
                    退出登录
                  </el-button>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="16">
              <el-tabs type="border-card" class="profile-tabs">
                <el-tab-pane :label="isOwnProfile ? '我的帖子' : '他的帖子'">
                  <div v-if="userPosts.length === 0" class="no-posts">
                    <p>暂无帖子</p>
                  </div>
                  
                  <div v-else class="posts-list">
                    <el-card 
                      v-for="post in userPosts" 
                      :key="post.id" 
                      class="post-card"
                      @click="viewPost(post.id)"
                      shadow="hover"
                    >
                      <template #header>
                        <div class="post-header">
                          <span class="post-title">{{ post.title }}</span>
                          <div class="post-date">
                            {{ new Date(post.created_at).toLocaleDateString() }}
                          </div>
                        </div>
                      </template>
                      <div class="post-content">
                        <p>{{ post.content.substring(0, 100) }}{{ post.content.length > 100 ? '...' : '' }}</p>
                      </div>
                      <div class="post-stats">
                        <span class="stat-item"><el-icon><ChatDotRound /></el-icon> {{ post.comments_count || 0 }}</span>
                        <span class="stat-item"><el-icon><Star /></el-icon> {{ post.likes_count || 0 }}</span>
                        <span class="stat-item"><el-icon><Share /></el-icon> {{ post.shares_count || 0 }}</span>
                      </div>
                      
                      <div class="post-actions" v-if="isLoggedIn && !isOwnProfile">
                        <el-button 
                          :type="post.isLiked ? 'danger' : 'default'" 
                          @click.stop="togglePostLike(post)"
                          :loading="post.likeLoading"
                          size="small"
                          round
                        >
                          <el-icon><Star /></el-icon>
                          {{ post.isLiked ? '已点赞' : '点赞' }}
                        </el-button>
                      </div>
                    </el-card>
                  </div>
                </el-tab-pane>
                
                <el-tab-pane label="收藏">
                  <CollectionManager />
                </el-tab-pane>
              </el-tabs>
            </el-col>
          </el-row>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, Star, Share, Collection } from '@element-plus/icons-vue'
import { postAPI, likeAPI, followAPI, userAPI } from '../api'
import CollectionManager from '@/components/CollectionManager.vue'

const route = useRoute()
const router = useRouter()

// 用户信息
const userProfile = ref({
  id: null,
  username: '',
  email: '',
  avatar_url: ''
})

// 数据
const userPosts = ref([])
const postCount = ref(0)
const likeCount = ref(0)
const followerCount = ref(0)
const isFollowing = ref(false)
const followLoading = ref(false)

// 计算属性
const isLoggedIn = computed(() => !!localStorage.getItem('userId'))
const currentUserId = computed(() => localStorage.getItem('userId'))

// 判断是否是查看自己的个人中心
const isOwnProfile = computed(() => {
  return !route.params.id || route.params.id == currentUserId.value
})

// 获取用户信息
const fetchUserProfile = async () => {
  try {
    // 如果是查看自己的个人中心
    if (isOwnProfile.value) {
      userProfile.value = {
        id: currentUserId.value,
        username: localStorage.getItem('username') || '未知用户',
        email: '',
        avatar_url: ''
      }
    } else {
      // 查看其他用户的个人中心
      // 先通过 /api/users/info/{user_id} 接口获取用户基础信息（包含用户名）
      const userInfoResponse = await userAPI.getUserInfoById(route.params.id)
      
      // 确保响应数据存在且包含用户名
      if (!userInfoResponse.data || typeof userInfoResponse.data !== 'object' || !userInfoResponse.data.username) {
        throw new Error('无法获取用户名')
      }
      
      const username = userInfoResponse.data.username
      
      // 使用获取到的用户名调用 /api/users/{username} 接口获取完整用户信息
      const response = await userAPI.getUserByUsername(username)
      
      // 确保响应数据包含必要的字段
      if (response.data && typeof response.data === 'object' && response.data.username) {
        // 验证并设置用户信息
        userProfile.value = {
          id: response.data.id || route.params.id,
          username: response.data.username || '',
          email: response.data.email || '',
          avatar_url: response.data.avatar_url || ''
        }
      } else {
        // 如果响应数据不完整，设置默认值
        userProfile.value = {
          id: route.params.id,
          username: username || '未知用户',
          email: '',
          avatar_url: ''
        }
      }
      // 检查关注状态
      checkFollowStatus()
    }
  } catch (error) {
    ElMessage.error('获取用户信息失败: ' + (error.response?.data?.detail || '请稍后重试'))
    
    // 设置默认用户信息以避免显示"未登录"
    if (!isOwnProfile.value) {
      userProfile.value = {
        id: route.params.id,
        username: '未知用户',
        email: '',
        avatar_url: ''
      }
    }
  }
}

// 检查关注状态
const checkFollowStatus = async () => {
  if (!isLoggedIn.value || isOwnProfile.value) return
  
  try {
    const response = await followAPI.checkFollow(userProfile.value.id)
    isFollowing.value = response.data
  } catch (error) {
    // 忽略错误
  }
}

// 获取用户帖子
const fetchUserPosts = async () => {
  try {
    let posts = []
    
    // 如果是查看自己的个人中心
    if (isOwnProfile.value) {
      if (!currentUserId.value) {
        router.push('/login')
        return
      }
      
      // 获取所有帖子，然后过滤出当前用户的帖子
      const response = await postAPI.getPosts({ skip: 0, limit: 100 })
      posts = response.data.filter(post => post.author_id == currentUserId.value)
    } else {
      // 查看其他用户的帖子
      const response = await postAPI.getPosts({ skip: 0, limit: 100 })
      posts = response.data.filter(post => post.author_id == route.params.id)
    }
    
    // 为每个帖子添加状态属性
    userPosts.value = posts.map(post => ({
      ...post,
      isLiked: false,
      likeLoading: false,
      collectLoading: false
    }))
    
    postCount.value = userPosts.value.length
    
    // 计算获赞总数
    likeCount.value = userPosts.value.reduce((total, post) => total + (post.likes_count || 0), 0)
    
    // 获取真实的粉丝数
    try {
      const statsResponse = await followAPI.getUserStats(route.params.id || currentUserId.value)
      followerCount.value = statsResponse.data.followers_count || 0
    } catch (error) {
      // 如果获取失败，设置默认粉丝数为0
      followerCount.value = 0
    }
    
    // 检查点赞状态
    checkLikeStatuses()
  } catch (error) {
    ElMessage.error('获取用户帖子失败: ' + (error.response?.data?.detail || '请稍后重试'))
  }
}

// 检查所有帖子的点赞状态
const checkLikeStatuses = async () => {
  if (!isLoggedIn.value) return
  
  for (const post of userPosts.value) {
    try {
      const response = await likeAPI.checkLike(post.id)
      post.isLiked = response.data
    } catch (error) {
      // 忽略错误
    }
  }
}

// 切换关注状态
const toggleFollow = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  followLoading.value = true
  
  try {
    if (isFollowing.value) {
      // 取消关注
      await followAPI.unfollowUser(userProfile.value.id)
      isFollowing.value = false
      ElMessage.success('已取消关注')
      // 更新粉丝数
      followerCount.value = Math.max(0, followerCount.value - 1)
    } else {
      // 关注
      await followAPI.followUser({ following_id: userProfile.value.id })
      isFollowing.value = true
      ElMessage.success('关注成功')
      // 更新粉丝数
      followerCount.value = followerCount.value + 1
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    followLoading.value = false
  }
}

// 切换帖子点赞状态
const togglePostLike = async (post) => {
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
      likeCount.value = Math.max(0, likeCount.value - 1)
      ElMessage.success('已取消点赞')
    } else {
      // 点赞
      await likeAPI.likePost({ post_id: post.id })
      post.isLiked = true
      post.likes_count = (post.likes_count || 0) + 1
      likeCount.value += 1
      ElMessage.success('点赞成功')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    post.likeLoading = false
  }
}

// 收藏帖子
const collectPost = async (post) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  post.collectLoading = true
  
  try {
    // 这里需要调用收藏API
    ElMessage.success('收藏成功')
  } catch (error) {
    ElMessage.error('收藏失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    post.collectLoading = false
  }
}

// 查看帖子详情
const viewPost = (postId) => {
  router.push(`/post/${postId}`)
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {
    // 取消退出
  })
}

// 监听路由变化
const watchRoute = () => {
  fetchUserProfile()
  fetchUserPosts()
}

onMounted(() => {
  if (!isOwnProfile.value || localStorage.getItem('userId')) {
    fetchUserProfile()
    fetchUserPosts()
  } else {
    router.push('/login')
  }
})
</script>

<style scoped>
.profile {
  height: 100%;
  background-color: #f5f7fa;
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

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
  border-radius: 15px;
  text-align: center;
  overflow: hidden;
  border: 1px solid #ebeef5;
  background-color: white;
}

.profile-header {
  padding: 20px 0;
}

.user-avatar {
  margin-bottom: 15px;
}

.profile-header h3 {
  margin: 10px 0 5px;
  font-size: 1.5rem;
  color: #303133;
}

.profile-header p {
  margin: 0;
  color: #909399;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #409eff;
}

.stat-label {
  color: #909399;
  margin-top: 5px;
}

.profile-actions {
  padding: 20px 0;
}

.profile-tabs {
  border-radius: 15px;
  overflow: hidden;
}

.post-card {
  margin-bottom: 15px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
  background-color: white;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-title {
  font-weight: 600;
  color: #303133;
}

.post-date {
  font-size: 0.85rem;
  color: #909399;
}

.post-content {
  padding: 15px 0;
}

.post-content p {
  line-height: 1.6;
  color: #606266;
  margin: 0;
}

.post-stats {
  display: flex;
  gap: 20px;
  padding: 10px 0;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 0.9rem;
}

.no-posts {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

.spacer {
  width: 68px;
}

@media (max-width: 768px) {
  .header-content {
    padding: 15px;
  }
  
  .main-content {
    padding: 15px;
  }
  
  .el-col {
    width: 100%;
  }
  
  .profile-stats {
    padding: 15px 0;
  }
  
  .stat-value {
    font-size: 1.2rem;
  }
}
</style>
