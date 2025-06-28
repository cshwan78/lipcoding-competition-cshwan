<template>
  <div class="profile-container">
    <div class="container">
      <h1>프로필</h1>
      
      <div v-if="user" class="profile-content">
        <div class="profile-photo-section">
          <img 
            :src="profileImageUrl" 
            alt="프로필 사진" 
            id="profile-photo"
            class="profile-photo"
          >
          <div class="form-group">
            <label for="profile" class="form-label">프로필 사진 변경</label>
            <input 
              type="file" 
              id="profile" 
              @change="handleImageUpload" 
              accept=".jpg,.jpeg,.png"
              class="form-input"
            >
          </div>
        </div>
        
        <form @submit.prevent="updateProfile" class="profile-form">
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
            <label for="bio" class="form-label">소개</label>
            <textarea 
              id="bio" 
              v-model="form.bio" 
              class="form-input" 
              rows="4"
              placeholder="자기소개를 입력하세요"
            ></textarea>
          </div>
          
          <div v-if="user.role === 'mentor'" class="form-group">
            <label for="skillsets" class="form-label">기술 스택</label>
            <input 
              type="text" 
              id="skillsets" 
              v-model="skillsetsInput" 
              class="form-input" 
              placeholder="기술 스택을 쉼표로 구분하여 입력하세요 (예: React, Vue, Node.js)"
            >
          </div>
          
          <button type="submit" id="save" class="btn" :disabled="loading">
            {{ loading ? '저장 중...' : '저장' }}
          </button>
          
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </form>
      </div>
      
      <div v-else class="loading">
        프로필을 불러오는 중...
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'

export default {
  name: 'Profile',
  data() {
    return {
      user: null,
      form: {
        name: '',
        bio: '',
        image: null,
        skills: []
      },
      skillsetsInput: '',
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    profileImageUrl() {
      if (this.form.image) {
        return `data:image/jpeg;base64,${this.form.image}`
      }
      
      if (this.user?.role === 'mentor') {
        return 'https://placehold.co/500x500.jpg?text=MENTOR'
      } else {
        return 'https://placehold.co/500x500.jpg?text=MENTEE'
      }
    }
  },
  async mounted() {
    await this.loadProfile()
  },
  methods: {
    async loadProfile() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8080/api/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.user = response.data
        this.form.name = this.user.name || ''
        this.form.bio = this.user.bio || ''
        this.form.image = this.user.image
        this.form.skills = this.user.skills || []
        this.skillsetsInput = this.form.skills.join(', ')
      } catch (error) {
        console.error('프로필 로딩 실패:', error)
        this.error = '프로필을 불러오는데 실패했습니다.'
      }
    },
    
    handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 파일 크기 검증 (1MB)
      if (file.size > 1024 * 1024) {
        this.error = '이미지 크기는 1MB 이하여야 합니다.'
        return
      }
      
      // 파일 형식 검증
      if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
        this.error = 'JPG 또는 PNG 형식의 이미지만 업로드 가능합니다.'
        return
      }
      
      const reader = new FileReader()
      reader.onload = (e) => {
        // Base64에서 data:image/... 부분 제거
        const base64 = e.target.result.split(',')[1]
        this.form.image = base64
      }
      reader.readAsDataURL(file)
    },
    
    async updateProfile() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        const token = localStorage.getItem('token')
        const profileData = {
          id: this.user.id,
          name: this.form.name,
          role: this.user.role,
          bio: this.form.bio,
          image: this.form.image
        }
        
        if (this.user.role === 'mentor') {
          profileData.skills = this.skillsetsInput
            .split(',')
            .map(skill => skill.trim())
            .filter(skill => skill.length > 0)
        }
        
        await axios.put('http://localhost:8080/api/profile', profileData, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.success = '프로필이 성공적으로 업데이트되었습니다.'
      } catch (error) {
        console.error('프로필 업데이트 실패:', error)
        this.error = '프로필 업데이트에 실패했습니다.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.profile-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  align-items: start;
}

.profile-photo-section {
  text-align: center;
}

.profile-photo {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #e1e5e9;
  margin-bottom: 1rem;
}

.profile-form {
  flex: 1;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
}
</style>
