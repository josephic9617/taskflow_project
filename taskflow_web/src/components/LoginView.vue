<template>
  <div class="login-wrapper">
    <div class="login-background"></div>
    <div class="login-card">
      <div class="login-header">
        <div class="welcome-logo-ring" style="width:64px;height:64px;border-radius:18px;margin:0 auto 16px;">
          <div class="welcome-logo-inner">
            <svg viewBox="0 0 24 24" width="32" height="32">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="white" />
            </svg>
          </div>
        </div>
        <h1 class="welcome-title" style="font-size:28px">Welcome Back</h1>
        <p class="welcome-subtitle" style="font-size:14px;margin-top:8px">Enter your credentials to access TaskFlow</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>Username</label>
          <input
            type="text"
            v-model="username"
            placeholder="admin"
            required
            autofocus
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label>Password</label>
          <input
            type="password"
            v-model="password"
            placeholder="••••••••"
            required
            :disabled="loading"
          />
        </div>

        <div v-if="errorMsg" class="error-msg fade-in">{{ errorMsg }}</div>

        <button type="submit" class="btn btn-primary login-btn" :disabled="loading || !username || !password">
          <span v-if="loading" class="spinner" style="width:16px;height:16px;border-width:2px;border-color:white;border-bottom-color:transparent;margin-right:8px;"></span>
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authApi, getErrorMessage } from '../services/api.js'

const emit = defineEmits(['login-success'])

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  if (!username.value || !password.value) return
  
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await authApi.login(username.value, password.value)
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    emit('login-success')
  } catch (error) {
    errorMsg.value = getErrorMessage(error, 'Invalid username or password')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  z-index: 1000;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 100vw; height: 100vh;
  background: radial-gradient(circle at 50% 50%, rgba(99,102,241,0.08) 0%, transparent 60%);
  pointer-events: none;
  animation: pulseGlow 8s ease-in-out infinite alternate;
}

.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 400px;
  background: rgba(30, 30, 42, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 40px 32px;
  box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.05);
  animation: fadeIn 0.4s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition);
  outline: none;
}

.form-group input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
  background: rgba(0, 0, 0, 0.4);
}

.form-group input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-btn {
  width: 100%;
  justify-content: center;
  padding: 14px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 8px;
}

.error-msg {
  padding: 12px;
  background: var(--red-soft);
  color: #fecaca;
  border-radius: var(--radius-md);
  font-size: 13px;
  text-align: center;
  border: 1px solid rgba(239, 68, 68, 0.2);
}
</style>
