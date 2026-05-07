<template>
  <section class="container">
    <div class="row g-4">
      <div class="col-xl-5">
        <div class="card bg-dark-subtle border-0 shadow-sm h-100">
          <div class="card-body p-4 p-lg-5">
            <span class="badge rounded-pill text-bg-warning mb-3">Вход</span>
            <h1 class="h2 text-white">Добро пожаловать обратно</h1>
            <p class="text-secondary mb-4">Войди в аккаунт, чтобы смотреть билеты, избранное и профиль.</p>

            <form class="row g-3" @submit.prevent="login">
              <div class="col-12">
                <label class="form-label text-secondary">Email</label>
                <input v-model="loginForm.email" type="email" class="form-control form-control-lg" required>
              </div>
              <div class="col-12">
                <label class="form-label text-secondary">Пароль</label>
                <input v-model="loginForm.password" type="password" class="form-control form-control-lg" required>
              </div>
              <div class="col-12">
                <button class="btn btn-warning btn-lg w-100" type="submit" :disabled="loading">
                  {{ loading ? 'Входим...' : 'Войти' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-7">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4 p-lg-5">
            <div class="d-flex flex-wrap justify-content-between gap-3 align-items-start mb-4">
              <div>
                <span class="badge rounded-pill text-bg-secondary mb-3">Регистрация</span>
                <h2 class="h3 text-white">Создать новый аккаунт</h2>
                <p class="text-secondary mb-0">После регистрации мы автоматически авторизуем пользователя в приложении.</p>
              </div>

            </div>

            <form class="row g-3 mb-4" @submit.prevent="register">
              <div class="col-md-6">
                <label class="form-label text-secondary">Имя</label>
                <input v-model="registerForm.name" type="text" class="form-control" required>
              </div>
              <div class="col-md-6">
                <label class="form-label text-secondary">Email</label>
                <input v-model="registerForm.email" type="email" class="form-control" required>
              </div>
              <div class="col-md-6">
                <label class="form-label text-secondary">Пароль</label>
                <input v-model="registerForm.password" type="password" class="form-control" required>
                <div class="form-text text-secondary">
                  {{ passwordRulesLabel }}
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label text-secondary">Повторите пароль</label>
                <input v-model="registerForm.confirmPassword" type="password" class="form-control" required>
              </div>
              <div class="col-md-6">
                <label class="form-label text-secondary">Секретный вопрос</label>
                <select v-model="registerForm.secretQuestion" class="form-select">
                  <option value="">Выберите вопрос</option>
                  <option v-for="question in securityQuestions" :key="question" :value="question">{{ question }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label text-secondary">Ответ на секретный вопрос</label>
                <input v-model="registerForm.secretAnswer" type="text" class="form-control" placeholder="Введите ответ">
              </div>
              <div class="col-12">
                <button class="btn btn-outline-warning w-100" type="submit" :disabled="loading">
                  {{ loading ? 'Создаем аккаунт...' : 'Зарегистрироваться' }}
                </button>
              </div>
            </form>

            <hr class="border-secondary-subtle my-4">

            <h3 class="h5 text-white">Восстановление пароля</h3>
            <form class="row g-3" @submit.prevent="recoverPassword">
              <div class="col-md-3">
                <label class="form-label text-secondary">Email</label>
                <input v-model="recoveryForm.email" type="email" class="form-control" required>
              </div>
              <div class="col-md-3">
                <label class="form-label text-secondary">Секретный вопрос</label>
                <select v-model="recoveryForm.secretQuestion" class="form-select" required>
                  <option value="">Выберите вопрос</option>
                  <option v-for="question in securityQuestions" :key="question" :value="question">{{ question }}</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label text-secondary">Ответ</label>
                <input v-model="recoveryForm.secretAnswer" type="text" class="form-control" required>
              </div>
              <div class="col-md-3">
                <label class="form-label text-secondary">Новый пароль</label>
                <input v-model="recoveryForm.newPassword" type="password" class="form-control" required>
                <div class="form-text text-secondary">
                  {{ passwordRulesLabel }}
                </div>
              </div>
              <div class="col-12">
                <button class="btn btn-outline-light" type="submit">Сменить пароль</button>
              </div>
            </form>

            <div v-if="successMessage" class="alert alert-success mt-4 mb-0">{{ successMessage }}</div>
            <div v-if="errorMessage" class="alert alert-danger mt-4 mb-0">{{ errorMessage }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { api } from '@/services/api'
import { SECURITY_QUESTIONS } from '@/constants/securityQuestions'
import { setStoredUser } from '@/store/session'
import { PASSWORD_RULES, validatePassword } from '@/utils/passwordValidation'

export default {
  name: 'AuthView',
  data() {
    return {
      loading: false,
      errorMessage: '',
      successMessage: '',
      loginForm: {
        email: '',
        password: ''
      },
      registerForm: {
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        secretQuestion: '',
        secretAnswer: ''
      },
      recoveryForm: {
        email: '',
        secretQuestion: '',
        secretAnswer: '',
        newPassword: ''
      },
      securityQuestions: SECURITY_QUESTIONS,
      passwordRulesLabel: PASSWORD_RULES.join(', ')
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.errorMessage = ''
      this.successMessage = ''

      try {
        const user = await api.loginUser(this.loginForm)
        setStoredUser(user)
        this.successMessage = 'Вход выполнен успешно.'
        const redirect = this.$route.query.redirect || (user.role === 'admin' ? '/admin' : '/profile')
        this.$router.push(redirect)
      } catch (error) {
        this.errorMessage = error.message
      } finally {
        this.loading = false
      }
    },
    async register() {
      this.loading = true
      this.errorMessage = ''
      this.successMessage = ''

      try {
        if (this.registerForm.password !== this.registerForm.confirmPassword) {
          throw new Error('Пароли не совпадают.')
        }

        const passwordError = validatePassword(this.registerForm.password)
        if (passwordError) {
          throw new Error(passwordError)
        }

        const hasPartialSecretData = this.registerForm.secretQuestion.trim() || this.registerForm.secretAnswer.trim()
        if (hasPartialSecretData && (!this.registerForm.secretQuestion.trim() || !this.registerForm.secretAnswer.trim())) {
          throw new Error('Для восстановления укажите и вопрос, и ответ.')
        }

        await api.registerUser({
          email: this.registerForm.email,
          name: this.registerForm.name,
          password: this.registerForm.password,
          secret_question: this.registerForm.secretQuestion || null,
          secret_answer: this.registerForm.secretAnswer || null
        })

        const user = await api.loginUser({
          email: this.registerForm.email,
          password: this.registerForm.password
        })

        setStoredUser(user)
        this.successMessage = 'Аккаунт успешно создан.'
        this.$router.push('/profile')
      } catch (error) {
        this.errorMessage = error.message
      } finally {
        this.loading = false
      }
    },
    async recoverPassword() {
      this.errorMessage = ''
      this.successMessage = ''

      try {
        const passwordError = validatePassword(this.recoveryForm.newPassword)
        if (passwordError) {
          throw new Error(passwordError)
        }

        await api.recoverPassword({
          email: this.recoveryForm.email,
          secret_question: this.recoveryForm.secretQuestion,
          secret_answer: this.recoveryForm.secretAnswer,
          new_password: this.recoveryForm.newPassword
        })
        this.successMessage = 'Пароль успешно обновлен. Теперь можно войти.'
      } catch (error) {
        this.errorMessage = error.message
      }
    }
  }
}
</script>
