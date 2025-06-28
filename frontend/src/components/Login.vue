<template>
  <div class="login-container">
    <div class="container login-form">
      <h1>로그인</h1>
      
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email" class="form-label">이메일</label>
          <input 
            type="email" 
            id="email" 
            v-model="form.email" 
            class="form-input" 
            required
          >
        </div>
        
        <div class="form-group">
          <label for="password" class="form-label">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model="form.password" 
            class="form-input" 
            required
          >
        </div>
        
        <button type="submit" id="login" class="btn" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
        
        <div v-if="error" class="error-message">{{ error }}</div>
      </form>
      
      <p class="signup-link">
        계정이 없으신가요? 
        <router-link to="/signup">회원가입</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.error = ''
      
      try {
        const response = await axios.post('http://localhost:8080/api/login', {
          email: this.form.email,
          password: this.form.password
        })
        
        localStorage.setItem('token', response.data.token)
        // 로그인 성공 후 메인 페이지로 이동
        window.location.href = '/index.html'
      } catch (error) {
        console.error('로그인 실패:', error)
        if (error.response?.status === 401) {
          this.error = '이메일 또는 비밀번호가 올바르지 않습니다.'
        } else {
          this.error = '로그인 중 오류가 발생했습니다.'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.login-form {
  width: 100%;
  max-width: 400px;
}

.login-form h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.signup-link {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}

.signup-link a {
  color: #667eea;
  text-decoration: none;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>
