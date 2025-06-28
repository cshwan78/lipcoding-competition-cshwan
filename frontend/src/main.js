import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './components/Login.vue'
import Signup from './components/Signup.vue'
import Profile from './components/Profile.vue'
import Mentors from './components/Mentors.vue'
import Requests from './components/Requests.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/signup', component: Signup },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/mentors', component: Mentors, meta: { requiresAuth: true } },
  { path: '/requests', component: Requests, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 인증 가드
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (token && (to.path === '/login' || to.path === '/')) {
    next('/profile')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
