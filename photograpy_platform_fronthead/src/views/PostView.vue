<template>
  <div class="post-detail">
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
          <el-card v-if="post" class="post-card" shadow="hover">
            <template #header>
              <div class="post-header">
                <div class="post-author-info" @click="viewUser(post.author.id)" style="cursor: pointer;">
                  <el-avatar 
                    :size="40" 
                    :src="post.author.avatar_url || ''"
                    class="author-avatar"
                  >
                    {{ post.author.username?.substring(0, 1) || 'U' }}
                  </el-avatar>
                  <div class="author-details">
                    <div class="author-name">{{ post.author.username }}</div>
                    <el-button 
                      size="small"
                      :type="isFollowing ? 'danger' : 'default'"
                      @click.stop="toggleFollow"
                      :loading="followLoading"
                      round
                    >
                      {{ isFollowing ? '已关注' : '关注' }}
                    </el-button>
                  </div>
                </div>
                <h2 class="post-title">{{ post.title }}</h2>
                <div class="post-meta">
                  <span>{{ new Date(post.created_at).toLocaleString() }}</span>
                </div>
              </div>
            </template>
            
            <div class="post-content">
              <p>{{ post.content }}</p>
              
              <div v-if="post.images && post.images.length > 0" class="post-images">
                <el-image
                  v-for="(image, index) in post.images"
                  :key="index"
                  :src="image"
                  :preview-src-list="post.images"
                  class="post-image"
                  fit="cover"
                  :zoom-rate="1.2"
                  :preview-teleported="true"
                />
              </div>
            </div>
            
            <!-- 评分显示区域 -->
            <div class="rating-section">
              <div class="rating-info">
                <span class="rating-label">评分:</span>
                <span v-if="ratingStats.rating_count > 0" class="rating-value">
                  {{ ratingStats.average_rating.toFixed(1) }}分
                </span>
                <span v-else class="rating-value">无评分</span>
                <span class="rating-count">({{ ratingStats.rating_count }}人评分)</span>
              </div>
              
              <div v-if="isLoggedIn" class="rating-input">
                <el-input
                  v-model="ratingInput"
                  placeholder="输入0-10分"
                  style="width: 120px"
                  @keyup.enter="submitRating"
                >
                  <template #append>
                    <el-button @click="submitRating" :loading="ratingLoading" type="primary">确认</el-button>
                  </template>
                </el-input>
                <el-button 
                  v-if="userRating !== null" 
                  @click="removeRating" 
                  type="danger" 
                  style="margin-left: 10px"
                  round
                >
                  撤回评分
                </el-button>
              </div>
              <div v-else class="login-prompt">
                <el-link @click="$router.push('/login')" type="primary">登录</el-link>后可进行评分
              </div>
            </div>
            
            <div class="post-actions">
              <el-button 
                :type="isLiked ? 'danger' : 'default'" 
                @click="toggleLike"
                :loading="likeLoading"
                class="action-button"
                round
              >
                <el-icon><Star /></el-icon>
                <span>点赞 ({{ post.likes_count || 0 }})</span>
              </el-button>
              
              <el-button 
                @click="toggleCollect"
                :loading="collectLoading"
                class="action-button"
                type="primary"
                round
              >
                <el-icon><Collection /></el-icon>
                <span>收藏</span>
              </el-button>
              
              <el-button 
                @click="sharePost" 
                :loading="shareLoading"
                class="action-button"
                type="success"
                round
              >
                <el-icon><Share /></el-icon>
                <span>分享</span>
              </el-button>
            </div>
          </el-card>
          
          <div class="comments-section">
            <el-card shadow="never">
              <template #header>
                <div class="card-header">
                  <h3>💬 评论 ({{ comments.length }})</h3>
                </div>
              </template>
              
              <div v-if="isLoggedIn" class="comment-form">
                <el-form :model="newComment" @submit.prevent="submitComment">
                  <el-form-item>
                    <el-input 
                      v-model="newComment.content" 
                      type="textarea" 
                      :rows="3"
                      placeholder="请输入评论内容"
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="submitComment" 
                      :loading="commentLoading"
                      round
                    >
                      发表评论
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
              
              <div v-else class="login-prompt">
                <p>请先 <el-link @click="$router.push('/login')" type="primary">登录</el-link> 后发表评论</p>
              </div>
              
              <div class="comments-list">
                <el-card 
                  v-for="comment in comments" 
                  :key="comment.id" 
                  class="comment-card"
                  shadow="hover"
                >
                  <div class="comment-header">
                    <span class="comment-author">{{ comment.author.username }}</span>
                    <span class="comment-time">{{ new Date(comment.created_at).toLocaleString() }}</span>
                  </div>
                  <div class="comment-content">
                    {{ comment.content }}
                  </div>
                </el-card>
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, Collection, Share } from '@element-plus/icons-vue'
import { postAPI, commentAPI, likeAPI, followAPI, collectionAPI } from '../api'
import { ratingAPI } from '../api'

const route = useRoute()
const router = useRouter()

// 用户状态
const isLoggedIn = ref(!!localStorage.getItem('userId'))

// 数据
const post = ref(null)
const comments = ref([])
const newComment = ref({
  content: ''
})
const ratingStats = ref({
  rating_count: 0,
  average_rating: null
})
const userRating = ref(null)
const ratingInput = ref('')

// 状态
const isLiked = ref(false)
const isFollowing = ref(false)
const likeLoading = ref(false)
const followLoading = ref(false)
const shareLoading = ref(false)
const commentLoading = ref(false)
const collectLoading = ref(false)
const ratingLoading = ref(false)

// 获取帖子详情
const fetchPost = async () => {
  try {
    const response = await postAPI.getPost(route.params.id)
    post.value = response.data
    
    // 检查是否已点赞
    checkLikeStatus()
    
    // 检查是否已关注作者
    checkFollowStatus()
    
    // 获取评分统计信息
    fetchRatingStats()
    
    // 检查用户评分
    checkUserRating()
  } catch (error) {
    ElMessage.error('获取帖子失败: ' + (error.response?.data?.detail || '请稍后重试'))
    router.push('/')
  }
}

// 获取评论列表
const fetchComments = async () => {
  try {
    const response = await commentAPI.getCommentsByPost(route.params.id, { skip: 0, limit: 100 })
    comments.value = response.data
  } catch (error) {
    ElMessage.error('获取评论失败: ' + (error.response?.data?.detail || '请稍后重试'))
  }
}

// 获取评分统计信息
const fetchRatingStats = async () => {
  try {
    const response = await ratingAPI.getRatingStats(route.params.id)
    ratingStats.value = response.data
  } catch (error) {
    // 忽略错误
  }
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

// 检查点赞状态
const checkLikeStatus = async () => {
  if (!isLoggedIn.value) return
  
  try {
    const response = await likeAPI.checkLike(route.params.id)
    isLiked.value = response.data
  } catch (error) {
    // 忽略错误
  }
}

// 检查关注状态
const checkFollowStatus = async () => {
  if (!isLoggedIn.value || !post.value) return
  
  try {
    const response = await followAPI.checkFollow(post.value.author.id)
    isFollowing.value = response.data
  } catch (error) {
    // 忽略错误
  }
}

// 检查用户评分
const checkUserRating = async () => {
  if (!isLoggedIn.value) return
  
  try {
    // 这里需要一个API来检查用户是否已经评分，暂时留空
    // 根据API文档，没有直接检查用户评分的接口，我们通过尝试获取来判断
  } catch (error) {
    // 忽略错误
  }
}

// 切换点赞状态
const toggleLike = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  likeLoading.value = true
  
  try {
    if (isLiked.value) {
      // 取消点赞
      await likeAPI.unlikePost(route.params.id)
      isLiked.value = false
      post.value.likes_count = (post.value.likes_count || 0) - 1
      ElMessage.success('已取消点赞')
    } else {
      // 点赞
      await likeAPI.likePost({ post_id: parseInt(route.params.id) })
      isLiked.value = true
      post.value.likes_count = (post.value.likes_count || 0) + 1
      ElMessage.success('点赞成功')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    likeLoading.value = false
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
      await followAPI.unfollowUser(post.value.author.id)
      isFollowing.value = false
      ElMessage.success('已取消关注')
    } else {
      // 关注
      await followAPI.followUser({ following_id: post.value.author.id })
      isFollowing.value = true
      ElMessage.success('关注成功')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    followLoading.value = false
  }
}

// 收藏帖子
const toggleCollect = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  collectLoading.value = true
  
  try {
    await collectionAPI.collectPost({ post_id: parseInt(route.params.id) })
    ElMessage.success('收藏成功')
  } catch (error) {
    ElMessage.error('收藏失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    collectLoading.value = false
  }
}

// 分享帖子
const sharePost = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  shareLoading.value = true
  
  try {
    // 这里可以调用分享API
    ElMessage.success('分享成功')
  } catch (error) {
    ElMessage.error('分享失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    shareLoading.value = false
  }
}

// 发表评论
const submitComment = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (!newComment.value.content.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  
  commentLoading.value = true
  
  try {
    await commentAPI.createComment({
      content: newComment.value.content,
      post_id: parseInt(route.params.id)
    })
    
    ElMessage.success('评论发表成功')
    newComment.value.content = ''
    fetchComments() // 重新获取评论列表
  } catch (error) {
    ElMessage.error('发表评论失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    commentLoading.value = false
  }
}

// 提交评分
const submitRating = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (!ratingInput.value) {
    ElMessage.warning('请输入评分')
    return
  }
  
  const ratingValue = parseFloat(ratingInput.value)
  if (isNaN(ratingValue) || ratingValue < 0 || ratingValue > 10) {
    ElMessage.warning('评分必须是0到10之间的数字')
    return
  }
  
  // 检查小数点后是否只有一位
  if (!/^\d+(\.\d)?$/.test(ratingInput.value)) {
    ElMessage.warning('评分只能保留小数点后一位')
    return
  }
  
  ratingLoading.value = true
  
  try {
    const ratingData = {
      post_id: parseInt(route.params.id),
      score: ratingValue
    }
    
    if (userRating.value) {
      // 更新评分
      await ratingAPI.updateRating(route.params.id, ratingData)
      ElMessage.success('评分更新成功')
    } else {
      // 创建评分
      await ratingAPI.createRating(ratingData)
      ElMessage.success('评分成功')
    }
    
    userRating.value = ratingValue
    ratingInput.value = ''
    
    // 重新获取评分统计信息
    await fetchRatingStats()
  } catch (error) {
    ElMessage.error('评分失败: ' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    ratingLoading.value = false
  }
}

// 撤回评分
const removeRating = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  try {
    await ratingAPI.deleteRating(route.params.id)
    ElMessage.success('评分已撤回')
    userRating.value = null
    
    // 重新获取评分统计信息
    await fetchRatingStats()
  } catch (error) {
    ElMessage.error('撤回评分失败: ' + (error.response?.data?.detail || '请稍后重试'))
  }
}

onMounted(() => {
  fetchPost()
  fetchComments()
})
</script>

<style scoped>
.post-detail {
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

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.post-card {
  margin-bottom: 30px;
  border-radius: 15px;
  overflow: hidden;
}

.post-header {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.post-author-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.author-name {
  font-weight: 600;
  font-size: 1.2rem;
  color: #409eff;
}

.post-title {
  margin: 0;
  color: #303133;
  font-size: 1.8rem;
}

.post-meta {
  font-size: 0.9rem;
  color: #909399;
}

.post-content {
  padding: 20px 0;
  line-height: 1.8;
  font-size: 1.1rem;
  color: #606266;
}

.post-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.post-image {
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.post-image:hover {
  transform: scale(1.02);
}

.rating-section {
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.rating-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rating-label {
  font-weight: 600;
  color: #303133;
}

.rating-value {
  font-weight: 600;
  font-size: 1.2rem;
  color: #e6a23c;
}

.rating-count {
  color: #909399;
}

.post-actions {
  display: flex;
  gap: 15px;
  padding-top: 20px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 5px;
}

.comments-section {
  border-radius: 15px;
  overflow: hidden;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.comment-form {
  margin-bottom: 30px;
}

.comment-card {
  margin-bottom: 15px;
  border-radius: 10px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.comment-author {
  font-weight: 600;
  color: #409eff;
}

.comment-time {
  font-size: 0.85rem;
  color: #909399;
}

.comment-content {
  line-height: 1.6;
  color: #606266;
}

.login-prompt {
  text-align: center;
  padding: 20px 0;
  color: #909399;
}

.spacer {
  width: 68px; /* 与返回按钮宽度大致相同，用于居中logo */
}

@media (max-width: 768px) {
  .header-content {
    padding: 15px;
  }
  
  .main-content {
    padding: 15px;
  }
  
  .post-title {
    font-size: 1.5rem;
  }
  
  .post-images {
    grid-template-columns: 1fr;
  }
  
  .rating-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .post-actions {
    flex-wrap: wrap;
  }
  
  .action-button {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
}
</style>