<template>
  <div class="collection-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的收藏夹</span>
          <el-button 
            type="primary" 
            size="small" 
            @click="showCreateDialog = true"
          >
            新建收藏夹
          </el-button>
        </div>
      </template>
      
      <div v-if="collections.length === 0" class="no-collections">
        <p>暂无收藏夹</p>
      </div>
      
      <div v-else class="collections-list">
        <el-table :data="collections" style="width: 100%">
          <el-table-column prop="name" label="收藏夹名称" />
          <el-table-column prop="created_at" label="创建时间">
            <template #default="scope">
              {{ new Date(scope.row.created_at).toLocaleDateString() }}
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button 
                size="small" 
                @click="renameCollection(scope.row)"
              >
                重命名
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteCollection(scope.row)"
              >
                删除
              </el-button>
              <el-button 
                size="small" 
                type="primary" 
                @click="viewCollectionItems(scope.row)"
              >
                查看内容
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <!-- 新建收藏夹对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建收藏夹" width="30%">
      <el-form @submit.prevent="createCollection">
        <el-form-item label="收藏夹名称">
          <el-input 
            v-model="newCollectionName" 
            placeholder="请输入收藏夹名称"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createCollection">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重命名收藏夹对话框 -->
    <el-dialog v-model="showRenameDialog" title="重命名收藏夹" width="30%">
      <el-form @submit.prevent="updateCollection">
        <el-form-item label="收藏夹名称">
          <el-input 
            v-model="currentCollection.name" 
            placeholder="请输入收藏夹名称"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRenameDialog = false">取消</el-button>
          <el-button type="primary" @click="updateCollection">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 收藏夹内容对话框 -->
    <el-dialog v-model="showItemsDialog" :title="currentCollection.name" width="50%">
      <div v-if="collectionItems.length === 0" class="no-items">
        <p>该收藏夹暂无内容</p>
      </div>
      <div v-else class="collection-items">
        <el-card 
          v-for="item in collectionItems" 
          :key="item.id" 
          class="item-card"
        >
          <div class="item-content">
            <h4>{{ item.post.title }}</h4>
            <p>{{ item.post.content.substring(0, 100) }}{{ item.post.content.length > 100 ? '...' : '' }}</p>
            <div class="item-actions">
              <el-button 
                size="small" 
                type="danger" 
                @click="removeFromCollection(item)"
              >
                移出收藏夹
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showItemsDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { collectionAPI } from '@/api/index.js'

// 数据
const collections = ref([])
const showCreateDialog = ref(false)
const showRenameDialog = ref(false)
const showItemsDialog = ref(false)
const newCollectionName = ref('')
const currentCollection = ref({})
const collectionItems = ref([])

// 获取收藏夹列表
const fetchCollections = async () => {
  try {
    const response = await collectionAPI.getCollections({ skip: 0, limit: 100 })
    collections.value = response.data
  } catch (error) {
    ElMessage.error('获取收藏夹列表失败: ' + (error.response?.data?.detail || '请稍后重试'))
  }
}

// 创建收藏夹
const createCollection = async () => {
  if (!newCollectionName.value.trim()) {
    ElMessage.warning('请输入收藏夹名称')
    return
  }
  
  try {
    await collectionAPI.createCollection({ name: newCollectionName.value })
    ElMessage.success('创建收藏夹成功')
    showCreateDialog.value = false
    newCollectionName.value = ''
    fetchCollections()
  } catch (error) {
    ElMessage.error('创建收藏夹失败: ' + (error.response?.data?.detail || '请稍后重试'))
  }
}

// 重命名收藏夹
const renameCollection = (collection) => {
  currentCollection.value = { ...collection }
  showRenameDialog.value = true
}

// 更新收藏夹
const updateCollection = async () => {
  if (!currentCollection.value.name.trim()) {
    ElMessage.warning('请输入收藏夹名称')
    return
  }
  
  try {
    await collectionAPI.updateCollection(currentCollection.value.id, { 
      name: currentCollection.value.name 
    })
    ElMessage.success('更新收藏夹成功')
    showRenameDialog.value = false
    fetchCollections()
  } catch (error) {
    ElMessage.error('更新收藏夹失败: ' + (error.response?.data?.detail || '请稍后重试'))
  }
}

// 删除收藏夹
const deleteCollection = (collection) => {
  ElMessageBox.confirm(`确定要删除收藏夹 "${collection.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await collectionAPI.deleteCollection(collection.id)
      ElMessage.success('删除收藏夹成功')
      fetchCollections()
    } catch (error) {
      ElMessage.error('删除收藏夹失败: ' + (error.response?.data?.detail || '请稍后重试'))
    }
  }).catch(() => {
    // 取消删除
  })
}

// 查看收藏夹内容
const viewCollectionItems = async (collection) => {
  try {
    currentCollection.value = collection
    const response = await collectionAPI.getCollectionItems(collection.id, { skip: 0, limit: 100 })
    collectionItems.value = response.data
    showItemsDialog.value = true
  } catch (error) {
    ElMessage.error('获取收藏夹内容失败: ' + (error.response?.data?.detail || '请稍后重试'))
  }
}

// 从收藏夹移除
const removeFromCollection = (item) => {
  ElMessageBox.confirm('确定要将该帖子移出收藏夹吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await collectionAPI.removeItemFromCollection(currentCollection.value.id, item.id)
      ElMessage.success('移出收藏夹成功')
      // 重新获取收藏夹内容
      viewCollectionItems(currentCollection.value)
    } catch (error) {
      ElMessage.error('移出收藏夹失败: ' + (error.response?.data?.detail || '请稍后重试'))
    }
  }).catch(() => {
    // 取消移除
  })
}

onMounted(() => {
  fetchCollections()
})
</script>

<style scoped>
.collection-manager {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.no-collections {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.item-card {
  margin-bottom: 15px;
}

.item-content h4 {
  margin: 0 0 10px 0;
}

.item-content p {
  margin: 0 0 15px 0;
  color: #666;
}

.item-actions {
  text-align: right;
}

.no-items {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
</style>
