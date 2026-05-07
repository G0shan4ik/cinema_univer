<template>
  <section class="container">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3 mb-4">
      <div>
        <span class="text-uppercase text-warning small fw-semibold">Поиск</span>
        <h1 class="text-white mb-1">Найти фильм</h1>
        <p class="text-secondary mb-0">Ищи по названию, жанру или ключевым словам в описании.</p>
      </div>
      <span class="badge text-bg-dark px-3 py-2">{{ movies.length }} результатов</span>
    </div>

    <form class="card bg-dark-subtle border-0 shadow-sm p-3 p-lg-4 mb-4" @submit.prevent="searchMovies">
      <div class="row g-3 align-items-end">
        <div class="col-lg-10">
          <label class="form-label text-secondary">Поиск по названию или жанру</label>
          <input v-model="query" type="search" class="form-control form-control-lg" placeholder="Например, Дюна или Animation">
        </div>
        <div class="col-lg-2 d-grid">
          <button class="btn btn-warning btn-lg" type="submit">Искать</button>
        </div>
      </div>
    </form>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="loading" class="text-secondary">Ищем фильмы...</div>

    <div v-else class="row g-4">
      <div v-for="movie in movies" :key="movie.id" class="col-md-6 col-xl-4">
        <MovieCard
          :movie="movie"
          :favorite-enabled="true"
          :is-favorite="isFavorite(movie.id)"
          :favorite-loading="favoriteLoadingId === movie.id"
          @toggle-favorite="toggleFavorite"
        />
      </div>
      <div v-if="!movies.length" class="col-12">
        <div class="alert alert-secondary mb-0">По запросу ничего не найдено.</div>
      </div>
    </div>
  </section>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'
import { api } from '@/services/api'
import { sessionState } from '@/store/session'

export default {
  name: 'SearchView',
  components: {
    MovieCard
  },
  data() {
    return {
      sessionState,
      query: this.$route.query.q || '',
      movies: [],
      favoriteMovies: [],
      favoriteLoadingId: null,
      loading: false,
      error: ''
    }
  },
  async mounted() {
    await this.searchMovies()
  },
  methods: {
    async searchMovies() {
      this.loading = true
      this.error = ''

      try {
        const response = await api.getMovies({ search: this.query, limit: 24, offset: 0 })
        this.movies = response.items
        await this.loadFavorites()
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async loadFavorites() {
      if (!this.sessionState.user) {
        this.favoriteMovies = []
        return
      }

      try {
        this.favoriteMovies = await api.getFavorites(this.sessionState.user.id)
      } catch (error) {
        this.favoriteMovies = []
      }
    },
    isFavorite(movieId) {
      return this.favoriteMovies.some((movie) => movie.movie_id === movieId)
    },
    async toggleFavorite(movie) {
      if (!this.sessionState.user) {
        this.$router.push({
          name: 'auth',
          query: {
            redirect: this.$route.fullPath
          }
        })
        return
      }

      this.favoriteLoadingId = movie.id

      try {
        if (this.isFavorite(movie.id)) {
          await api.removeFavorite({
            user_id: this.sessionState.user.id,
            movie_id: movie.id
          })
        } else {
          await api.addFavorite({
            user_id: this.sessionState.user.id,
            movie_id: movie.id
          })
        }

        await this.loadFavorites()
      } catch (error) {
        this.error = error.message
      } finally {
        this.favoriteLoadingId = null
      }
    }
  }
}
</script>
