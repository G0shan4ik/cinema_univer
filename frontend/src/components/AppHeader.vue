<template>
  <nav class="navbar navbar-expand-lg navbar-dark sticky-top border-bottom border-light-subtle bg-dark-subtle bg-opacity-75 app-navbar">
    <div class="container">
      <router-link class="navbar-brand fw-bold text-uppercase tracking-wide" to="/">
        Cinema Space
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#cinemaNav"
        aria-controls="cinemaNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="cinemaNav" class="collapse navbar-collapse">
        <ul class="navbar-nav mx-auto mb-3 mb-lg-0">
          <li v-for="item in navItems" :key="item.to" class="nav-item">
            <router-link class="nav-link" :to="item.to">
              {{ item.label }}
            </router-link>
          </li>
        </ul>

        <div class="d-flex flex-column flex-lg-row gap-2 align-items-lg-center">
          <span v-if="currentUser" class="badge text-bg-light px-3 py-2">
            {{ currentUser.name }} · {{ currentUser.role === 'admin' ? 'Админ' : 'Пользователь' }}
          </span>
          <router-link
            v-if="currentUser"
            class="btn btn-outline-light btn-sm"
            to="/profile"
          >
            Профиль
          </router-link>
          <button
            v-if="currentUser"
            class="btn btn-warning btn-sm"
            type="button"
            @click="logout"
          >
            Выйти
          </button>
          <router-link v-else class="btn btn-warning btn-sm" to="/auth">
            Войти
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { clearStoredUser, sessionState } from '@/store/session'
import { api } from '@/services/api'

export default {
  name: 'AppHeader',
  data() {
    return {
      sessionState,
      baseNavItems: [
        { label: 'Афиша', to: '/' },
        { label: 'Фильмы', to: '/movies' },
        { label: 'Поиск', to: '/search' },
        { label: 'Избранное', to: '/favorites' },
        { label: 'Профиль', to: '/profile' }
      ]
    }
  },
  computed: {
    currentUser() {
      return this.sessionState.user
    },
    navItems() {
      if (this.currentUser?.role === 'admin') {
        return [...this.baseNavItems, { label: 'Админка', to: '/admin' }]
      }

      return this.baseNavItems
    }
  },
  methods: {
    async logout() {
      try {
        if (this.currentUser?.refresh_token) {
          await api.logoutUser({
            refresh_token: this.currentUser.refresh_token
          })
        }
      } catch (error) {
        // Для локальной лабораторной достаточно тихо завершить сессию на клиенте.
      }

      clearStoredUser()
      this.$router.push('/')
    }
  }
}
</script>
