<template>
  <div class="requests-container">
    <div class="container">
      <h1>요청 관리</h1>
      
      <div v-if="loading" class="loading">
        요청 목록을 불러오는 중...
      </div>
      
      <div v-else>
        <!-- 멘토: 받은 요청 목록 -->
        <div v-if="userRole === 'mentor'">
          <h2>받은 매칭 요청</h2>
          
          <div v-if="incomingRequests.length === 0" class="no-requests">
            받은 요청이 없습니다.
          </div>
          
          <div v-else class="requests-list">
            <div 
              v-for="request in incomingRequests" 
              :key="request.id" 
              class="request-card"
            >
              <div class="request-header">
                <div class="mentee-info">
                  <img 
                    :src="getMenteeImageUrl(request.mentee)" 
                    :alt="`${request.mentee.name} 프로필`"
                    class="mentee-image"
                  >
                  <div>
                    <h4>{{ request.mentee.name }}</h4>
                    <p class="request-date">{{ formatDate(request.createdAt) }}</p>
                  </div>
                </div>
                <div class="request-status">
                  <span :class="`status-${request.status}`">
                    {{ getStatusText(request.status) }}
                  </span>
                </div>
              </div>
              
              <div class="request-message" :mentee="request.mentee.id">
                {{ request.message }}
              </div>
              
              <div v-if="request.status === 'pending'" class="request-actions">
                <button 
                  @click="acceptRequest(request.id)" 
                  id="accept"
                  class="btn btn-success"
                  :disabled="actionLoading"
                >
                  수락
                </button>
                <button 
                  @click="rejectRequest(request.id)" 
                  id="reject"
                  class="btn btn-danger"
                  :disabled="actionLoading"
                >
                  거절
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 멘티: 보낸 요청 목록 -->
        <div v-if="userRole === 'mentee'">
          <h2>보낸 매칭 요청</h2>
          
          <div v-if="outgoingRequests.length === 0" class="no-requests">
            보낸 요청이 없습니다.
          </div>
          
          <div v-else class="requests-list">
            <div 
              v-for="request in outgoingRequests" 
              :key="request.id" 
              class="request-card"
            >
              <div class="request-header">
                <div class="mentor-info">
                  <img 
                    :src="getMentorImageUrl(request.mentor)" 
                    :alt="`${request.mentor.name} 프로필`"
                    class="mentor-image"
                  >
                  <div>
                    <h4>{{ request.mentor.name }}</h4>
                    <p class="request-date">{{ formatDate(request.createdAt) }}</p>
                  </div>
                </div>
                <div class="request-status">
                  <span :class="`status-${request.status}`">
                    {{ getStatusText(request.status) }}
                  </span>
                </div>
              </div>
              
              <div class="request-message">
                {{ request.message }}
              </div>
              
              <div v-if="request.status === 'pending'" class="request-actions">
                <button 
                  @click="cancelRequest(request.id)" 
                  class="btn btn-danger"
                  :disabled="actionLoading"
                >
                  요청 취소
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'

export default {
  name: 'Requests',
  data() {
    return {
      userRole: null,
      incomingRequests: [],
      outgoingRequests: [],
      loading: true,
      actionLoading: false,
      error: '',
      success: ''
    }
  },
  async mounted() {
    this.getUserRole()
    await this.loadRequests()
  },
  methods: {
    getUserRole() {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          const decoded = jwtDecode(token)
          this.userRole = decoded.role
        } catch (error) {
          console.error('토큰 디코딩 실패:', error)
        }
      }
    },
    
    async loadRequests() {
      try {
        const token = localStorage.getItem('token')
        
        if (this.userRole === 'mentor') {
          const response = await axios.get('http://localhost:8080/api/match-requests/incoming', {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.incomingRequests = response.data
        } else if (this.userRole === 'mentee') {
          const response = await axios.get('http://localhost:8080/api/match-requests/outgoing', {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.outgoingRequests = response.data
        }
      } catch (error) {
        console.error('요청 목록 로딩 실패:', error)
        this.error = '요청 목록을 불러오는데 실패했습니다.'
      } finally {
        this.loading = false
      }
    },
    
    async acceptRequest(requestId) {
      this.actionLoading = true
      this.error = ''
      this.success = ''
      
      try {
        const token = localStorage.getItem('token')
        await axios.put(`http://localhost:8080/api/match-requests/${requestId}/accept`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.success = '요청을 수락했습니다.'
        await this.loadRequests()
      } catch (error) {
        console.error('요청 수락 실패:', error)
        this.error = '요청 수락에 실패했습니다.'
      } finally {
        this.actionLoading = false
      }
    },
    
    async rejectRequest(requestId) {
      this.actionLoading = true
      this.error = ''
      this.success = ''
      
      try {
        const token = localStorage.getItem('token')
        await axios.put(`http://localhost:8080/api/match-requests/${requestId}/reject`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.success = '요청을 거절했습니다.'
        await this.loadRequests()
      } catch (error) {
        console.error('요청 거절 실패:', error)
        this.error = '요청 거절에 실패했습니다.'
      } finally {
        this.actionLoading = false
      }
    },
    
    async cancelRequest(requestId) {
      this.actionLoading = true
      this.error = ''
      this.success = ''
      
      try {
        const token = localStorage.getItem('token')
        await axios.delete(`http://localhost:8080/api/match-requests/${requestId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.success = '요청을 취소했습니다.'
        await this.loadRequests()
      } catch (error) {
        console.error('요청 취소 실패:', error)
        this.error = '요청 취소에 실패했습니다.'
      } finally {
        this.actionLoading = false
      }
    },
    
    getMentorImageUrl(mentor) {
      if (mentor.image) {
        return `data:image/jpeg;base64,${mentor.image}`
      }
      return 'https://placehold.co/500x500.jpg?text=MENTOR'
    },
    
    getMenteeImageUrl(mentee) {
      if (mentee.image) {
        return `data:image/jpeg;base64,${mentee.image}`
      }
      return 'https://placehold.co/500x500.jpg?text=MENTEE'
    },
    
    getStatusText(status) {
      const statusMap = {
        pending: '대기 중',
        accepted: '수락됨',
        rejected: '거절됨'
      }
      return statusMap[status] || status
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.requests-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.request-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.mentee-info,
.mentor-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mentee-image,
.mentor-image {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e1e5e9;
}

.mentee-info h4,
.mentor-info h4 {
  margin: 0;
  color: #333;
}

.request-date {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.request-status {
  display: flex;
  align-items: center;
}

.status-pending {
  background: #ffc107;
  color: #856404;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-accepted {
  background: #28a745;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-rejected {
  background: #dc3545;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.request-message {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  color: #333;
  line-height: 1.5;
}

.request-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.no-requests,
.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

@media (max-width: 768px) {
  .request-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .request-actions {
    justify-content: stretch;
  }
  
  .request-actions button {
    flex: 1;
  }
}
</style>
