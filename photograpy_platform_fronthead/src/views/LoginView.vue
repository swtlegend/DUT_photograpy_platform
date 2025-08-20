<template>
  <div class="login">
    <div class="login-form">
      <el-card class="login-card" shadow="always">
        <template #header>
          <div class="card-header">
            <h2>📸 用户登录</h2>
          </div>
        </template>
        <el-form :model="loginForm" @submit.prevent="handleLogin">
          <el-form-item label="学号">
            <el-input 
              v-model="loginForm.id_number" 
              placeholder="请输入学号"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          <el-form-item label="密码">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleLogin" 
              :loading="loading"
              style="width: 100%"
              size="large"
              round
            >
              登录
            </el-button>
          </el-form-item>
          <div class="form-footer">
            <el-link @click="$router.push('/register')" type="primary">还没有账号？立即注册</el-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userAPI } from '../api'

const router = useRouter()

const loginForm = ref({
  id_number: '',
  password: ''
})

const loading = ref(false)

const handleLogin = async () => {
  if (!loginForm.value.id_number || !loginForm.value.password) {
    ElMessage.warning('请填写学号和密码')
    return
  }
  
  loading.value = true
  
  try {
    const response = await userAPI.login(loginForm.value)
    // 保存用户信息到localStorage
    localStorage.setItem('userId', response.data.id)
    localStorage.setItem('username', response.data.username)
    
    ElMessage.success('登录成功')
    // 根据用户偏好设置，登录成功后跳转到首页
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error) // 添加日志以便调试
    if (error.response && error.response.data && error.response.data.detail) {
      ElMessage.error('登录失败：' + error.response.data.detail)
    } else {
      ElMessage.error('登录失败：请检查学号和密码或网络连接')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-form {
  width: 100%;
  max-width: 450px;
}

.login-card {
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #409eff;
  font-weight: 600;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

@media (max-width: 768px) {
  .login {
    padding: 15px;
  }
  
  .login-card {
    border-radius: 10px;
  }
}
</style>