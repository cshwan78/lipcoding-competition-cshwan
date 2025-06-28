<template>
  <div class="signup-container">
    <div class="container signup-form">
      <h1>회원가입</h1>
      
      <form @submit.prevent="signup">
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
        
        <div class="form-group">
          <label for="name" class="form-label">이름</label>
          <input 
            type="text" 
            id="name" 
            v-model="form.name" 
            class="form-input" 
            required
          >
        </div>
        
        <div class="form-group">
          <label for="role" class="form-label">역할</label>
          <select 
            id="role" 
            v-model="form.role" 
            class="form-input" 
            required
          >
            <option value="">역할을 선택하세요</option>
            <option value="mentor">멘토</option>
            <option value="mentee">멘티</option>
          </select>
        </div>
        
        <button type="submit" id="signup" class="btn" :disabled="loading">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
      </form>
      
      <p class="login-link">
        이미 계정이 있으신가요? 
        <router-link to="/login">로그인</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Signup',
  data() {
    return {
      form: {
        email: '',
        password: '',
        name: '',
        role: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    async signup() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        await axios.post('http://localhost:8080/api/signup', this.form)
        
        this.success = '회원가입이 완료되었습니다. 로그인 페이지로 이동합니다.'
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (error) {
        console.error('회원가입 실패:', error)
        if (error.response?.status === 400) {
          this.error = '입력 정보가 올바르지 않습니다.'
        } else {
          this.error = '회원가입 중 오류가 발생했습니다.'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.signup-form {
  width: 100%;
  max-width: 400px;
}

.signup-form h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
