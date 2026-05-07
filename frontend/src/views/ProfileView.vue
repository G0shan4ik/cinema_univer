<template>
  <section class="container">
    <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-end gap-3 mb-4">
      <div>
        <span class="text-uppercase text-warning small fw-semibold">Личный кабинет</span>
        <h1 class="text-white mb-1">Профиль пользователя</h1>
        <p class="text-secondary mb-0">Здесь можно обновить имя, email и данные для восстановления пароля.</p>
      </div>
      <router-link class="btn btn-outline-light" to="/profile/tickets">Мои билеты</router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

    <div class="row g-4">
      <div class="col-xl-7">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4">
            <h2 class="h4 text-white mb-3">Основная информация</h2>
            <form class="row g-3" @submit.prevent="saveProfile">
              <div class="col-md-6">
                <label class="form-label text-secondary">Имя</label>
                <input v-model="profileForm.name" type="text" class="form-control" required>
              </div>
              <div class="col-md-6">
                <label class="form-label text-secondary">Email</label>
                <input v-model="profileForm.email" type="email" class="form-control" required>
              </div>
              <div class="col-12 d-flex flex-wrap gap-2 align-items-center">
                <button class="btn btn-warning" type="submit" :disabled="loading">
                  {{ loading ? 'Сохраняем...' : 'Сохранить изменения' }}
                </button>
                <span class="text-secondary">Роль: {{ currentUser?.role === 'admin' ? 'Администратор' : 'Пользователь' }}</span>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-5">
        <div class="card bg-dark-subtle border-0 shadow-sm h-100">
          <div class="card-body p-4">
            <h2 class="h4 text-white mb-3">Восстановление пароля</h2>
            <p class="text-secondary">Сохрани вопрос и ответ, чтобы потом можно было восстановить пароль на странице входа.</p>
            <form class="row g-3" @submit.prevent="saveKeyword">
              <div class="col-12">
                <label class="form-label text-secondary">Секретный вопрос</label>
                <select v-model="secretQuestion" class="form-select" required>
                  <option value="">Выберите вопрос</option>
                  <option v-for="question in securityQuestions" :key="question" :value="question">{{ question }}</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label text-secondary">Ответ</label>
                <input v-model="secretAnswer" type="text" class="form-control" required>
              </div>
              <div class="col-12">
                <button class="btn btn-outline-warning" type="submit">Сохранить вопрос и ответ</button>
              </div>
            </form>

          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { api } from '@/services/api'
import { SECURITY_QUESTIONS } from '@/constants/securityQuestions'
import { sessionState, setStoredUser } from '@/store/session'

export default {
  name: 'ProfileView',
  data() {
    const user = sessionState.user

    return {
      sessionState,
      loading: false,
      error: '',
      successMessage: '',
      secretQuestion: '',
      secretAnswer: '',
      securityQuestions: SECURITY_QUESTIONS,
      profileForm: {
        name: user?.name || '',
        email: user?.email || ''
      }
    }
  },
  computed: {
    currentUser() {
      return this.sessionState.user
    }
  },
  methods: {
    async saveProfile() {
      this.loading = true
      this.error = ''
      this.successMessage = ''

      try {
        await api.updateUser(this.currentUser.id, this.profileForm)
        const updatedUser = {
          ...this.currentUser,
          ...this.profileForm
        }
        setStoredUser(updatedUser)
        this.successMessage = 'Профиль обновлен.'
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async saveKeyword() {
      this.error = ''
      this.successMessage = ''

      try {
        await api.setKeyword({
          user_id: this.currentUser.id,
          secret_question: this.secretQuestion,
          secret_answer: this.secretAnswer
        })
        this.successMessage = 'Секретный вопрос и ответ сохранены.'
        this.secretQuestion = ''
        this.secretAnswer = ''
      } catch (error) {
        this.error = error.message
      }
    }
  }
}
</script>
