<template>
  <div class="register">
    <div class="register-form">
      <el-card class="register-card" shadow="always">
        <template #header>
          <div class="card-header">
            <h2>📸 用户注册</h2>
          </div>
        </template>
        <el-form :model="registerForm" @submit.prevent="handleRegister">
          <el-form-item label="用户名">
            <el-input 
              v-model="registerForm.username" 
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          <el-form-item label="学号">
            <el-input 
              v-model="registerForm.id_number" 
              placeholder="请输入学号"
              size="large"
              prefix-icon="School"
            />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input 
              v-model="registerForm.email" 
              placeholder="请输入邮箱"
              size="large"
              prefix-icon="Message"
            />
          </el-form-item>
          <el-form-item label="密码">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input 
              v-model="registerForm.confirm_password" 
              type="password" 
              placeholder="请再次输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleRegister" 
              :loading="loading"
              style="width: 100%"
              size="large"
              round
            >
              注册
            </el-button>
          </el-form-item>
          <div class="form-footer">
            <el-link @click="$router.push('/login')" type="primary">已有账号？立即登录</el-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userAPI } from '../api'

const router = useRouter()

const registerForm = ref({
  username: '',
  id_number: '',
  email: '',
  password: '',
  confirm_password: ''
})

const loading = ref(false)

// 监听密码确认字段
watch(() => registerForm.value.confirm_password, (newVal) => {
  if (newVal && registerForm.value.password && newVal !== registerForm.value.password) {
    ElMessage.warning('两次输入的密码不一致')
  }
})

const handleRegister = async () => {
  // 表单验证
  if (!registerForm.value.username) {
    ElMessage.warning('请输入用户名')
    return
  }
  
  if (!registerForm.value.id_number) {
    ElMessage.warning('请输入学号')
    return
  }
  
  if (!registerForm.value.email) {
    ElMessage.warning('请输入邮箱')
    return
  }
  
  if (!registerForm.value.password) {
    ElMessage.warning('请输入密码')
    return
  }
  
  if (registerForm.value.password !== registerForm.value.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  loading.value = true
  
  try {
    const response = await userAPI.register(registerForm.value)
    ElMessage.success('注册成功')
    // 注册成功后跳转到登录页
    router.push('/login')
  } catch (error) {
    ElMessage.error('注册失败：' + (error.response?.data?.detail || '请检查输入信息'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.register-form {
  width: 100%;
  max-width: 450px;
}

.register-card {
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
  .register {
    padding: 15px;
  }
  
  .register-card {
    border-radius: 10px;
  }
}
</style>