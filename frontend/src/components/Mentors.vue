<template>
  <div class="mentors-container">
    <div class="container">
      <h1>멘토 목록</h1>
      
      <div class="search-controls">
        <div class="form-group">
          <label for="search" class="form-label">기술 스택 검색</label>
          <input 
            type="text" 
            id="search" 
            v-model="searchKeyword" 
            @input="searchMentors"
            class="form-input" 
            placeholder="검색할 기술 스택을 입력하세요"
          >
        </div>
        
        <div class="sort-controls">
          <label class="form-label">정렬 기준</label>
          <div class="radio-group">
            <label>
              <input 
                type="radio" 
                id="name" 
                value="name" 
                v-model="sortBy" 
                @change="sortMentors"
              >
              이름순
            </label>
            <label>
              <input 
                type="radio" 
                id="skill" 
                value="skill" 
                v-model="sortBy" 
                @change="sortMentors"
              >
              기술 스택순
            </label>
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        멘토 목록을 불러오는 중...
      </div>
      
      <div v-else-if="mentors.length === 0" class="no-mentors">
        조건에 맞는 멘토가 없습니다.
      </div>
      
      <div v-else class="mentors-grid">
        <div 
          v-for="mentor in mentors" 
          :key="mentor.id" 
          class="mentor mentor-card"
        >
          <div class="mentor-photo">
            <img 
              :src="getMentorImageUrl(mentor)" 
              :alt="`${mentor.name} 프로필`"
              class="mentor-image"
            >
          </div>
          
          <div class="mentor-info">
            <h3>{{ mentor.name }}</h3>
            <p class="mentor-bio">{{ mentor.bio || '소개가 없습니다.' }}</p>
            
            <div v-if="mentor.skills && mentor.skills.length > 0" class="mentor-skills">
              <span 
                v-for="skill in mentor.skills" 
                :key="skill" 
                class="skill-tag"
              >
                {{ skill }}
              </span>
            </div>
            
            <div class="mentor-actions">
              <button 
                @click="openRequestModal(mentor)" 
                class="btn btn-primary"
                :disabled="hasActiveRequest"
              >
                {{ hasActiveRequest ? '요청 대기 중' : '매칭 요청' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="error" class="error-message">{{ error }}</div>
    </div>
    
    <!-- 요청 모달 -->
    <div v-if="showRequestModal" class="modal-overlay" @click="closeRequestModal">
      <div class="modal" @click.stop>
        <h3>{{ selectedMentor?.name }}님에게 매칭 요청</h3>
        
        <div class="form-group">
          <label for="message" class="form-label">요청 메시지</label>
          <textarea 
            id="message"
            :data-mentor-id="selectedMentor?.id"
            :data-testid="`message-${selectedMentor?.id}`"
            v-model="requestMessage" 
            class="form-input" 
            rows="4"
            placeholder="멘토님께 보낼 메시지를 입력하세요"
            required
          ></textarea>
        </div>
        
        <div class="modal-actions">
          <button @click="closeRequestModal" class="btn btn-secondary">취소</button>
          <button 
            @click="sendRequest" 
            id="request"
            class="btn btn-primary" 
            :disabled="!requestMessage.trim() || requestLoading"
          >
            {{ requestLoading ? '전송 중...' : '요청 보내기' }}
          </button>
        </div>
        
        <div v-if="requestError" class="error-message">{{ requestError }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Mentors',
  data() {
    return {
      mentors: [],
      allMentors: [],
      searchKeyword: '',
      sortBy: 'name',
      loading: true,
      error: '',
      showRequestModal: false,
      selectedMentor: null,
      requestMessage: '',
      requestLoading: false,
      requestError: '',
      hasActiveRequest: false
    }
  },
  async mounted() {
    await this.loadMentors()
    await this.checkActiveRequest()
  },
  methods: {
    async loadMentors() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8080/api/mentors', {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.allMentors = response.data
        this.mentors = [...this.allMentors]
        this.sortMentors()
      } catch (error) {
        console.error('멘토 목록 로딩 실패:', error)
        this.error = '멘토 목록을 불러오는데 실패했습니다.'
      } finally {
        this.loading = false
      }
    },
    
    async checkActiveRequest() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8080/api/match-requests/outgoing', {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        // 대기 중인 요청이 있는지 확인
        this.hasActiveRequest = response.data.some(request => request.status === 'pending')
      } catch (error) {
        console.error('요청 상태 확인 실패:', error)
      }
    },
    
    searchMentors() {
      if (!this.searchKeyword.trim()) {
        this.mentors = [...this.allMentors]
      } else {
        this.mentors = this.allMentors.filter(mentor => 
          mentor.skills?.some(skill => 
            skill.toLowerCase().includes(this.searchKeyword.toLowerCase())
          )
        )
      }
      this.sortMentors()
    },
    
    sortMentors() {
      if (this.sortBy === 'name') {
        this.mentors.sort((a, b) => a.name.localeCompare(b.name))
      } else if (this.sortBy === 'skill') {
        this.mentors.sort((a, b) => {
          const aSkills = a.skills?.join(', ') || ''
          const bSkills = b.skills?.join(', ') || ''
          return aSkills.localeCompare(bSkills)
        })
      }
    },
    
    getMentorImageUrl(mentor) {
      if (mentor.image) {
        return `data:image/jpeg;base64,${mentor.image}`
      }
      return 'https://placehold.co/500x500.jpg?text=MENTOR'
    },
    
    openRequestModal(mentor) {
      if (this.hasActiveRequest) return
      
      this.selectedMentor = mentor
      this.requestMessage = ''
      this.requestError = ''
      this.showRequestModal = true
    },
    
    closeRequestModal() {
      this.showRequestModal = false
      this.selectedMentor = null
      this.requestMessage = ''
      this.requestError = ''
    },
    
    async sendRequest() {
      if (!this.requestMessage.trim()) return
      
      this.requestLoading = true
      this.requestError = ''
      
      try {
        const token = localStorage.getItem('token')
        await axios.post('http://localhost:8080/api/match-requests', {
          mentorId: this.selectedMentor.id,
          message: this.requestMessage
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.closeRequestModal()
        this.hasActiveRequest = true
        alert('매칭 요청이 성공적으로 전송되었습니다!')
      } catch (error) {
        console.error('요청 전송 실패:', error)
        if (error.response?.status === 400) {
          this.requestError = '이미 요청을 보낸 멘토이거나 잘못된 요청입니다.'
        } else {
          this.requestError = '요청 전송에 실패했습니다.'
        }
      } finally {
        this.requestLoading = false
      }
    }
  }
}
</script>

<style scoped>
.search-controls {
  margin-bottom: 2rem;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2rem;
  align-items: end;
}

.sort-controls {
  display: flex;
  flex-direction: column;
}

.radio-group {
  display: flex;
  gap: 1rem;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
}

.mentors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.mentor-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.mentor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.mentor-photo {
  text-align: center;
  margin-bottom: 1rem;
}

.mentor-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e1e5e9;
}

.mentor-info h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.mentor-bio {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.mentor-skills {
  margin-bottom: 1rem;
}

.skill-tag {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}

.mentor-actions {
  text-align: center;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a6fd8;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading, .no-mentors {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-bottom: 1rem;
  color: #333;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .search-controls {
    grid-template-columns: 1fr;
  }
  
  .mentors-grid {
    grid-template-columns: 1fr;
  }
}
</style>
