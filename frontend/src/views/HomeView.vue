<template>
  <section class="container">
    <div class="row g-4 align-items-stretch">
      <div class="col-lg-7">
        <div class="hero-panel p-4 p-lg-5 h-100 rounded-4 border border-light-subtle shadow-sm">
          <span class="badge rounded-pill text-bg-warning mb-3">Кинотеатр нового формата</span>
          <h1 class="display-5 fw-bold text-white mb-3">Афиша, билеты и любимые фильмы в одном месте</h1>
          <p class="lead text-secondary mb-4">
            Следи за премьерами, смотри ближайшие сеансы и бронируй места онлайн без лишних шагов.
          </p>
          <div class="d-flex flex-wrap gap-2">
            <router-link class="btn btn-warning btn-lg" to="/movies">Смотреть афишу</router-link>
            <router-link class="btn btn-outline-light btn-lg" to="/search">Найти фильм</router-link>
          </div>
        </div>
      </div>

      <div class="col-lg-5">
        <div v-if="featuredMovie" class="card bg-dark-subtle border-0 shadow-sm h-100 overflow-hidden">
          <img :src="featuredPoster" :alt="featuredMovie.title" class="hero-poster">
          <div class="card-body p-4">
            <span class="badge rounded-pill text-bg-dark mb-3">Сегодня в центре внимания</span>
            <h2 class="h3 text-white">{{ featuredMovie.title }}</h2>
            <p class="text-secondary mb-2">{{ featuredDescription }}</p>
            <button
              type="button"
              class="btn btn-outline-secondary btn-sm mb-3"
              @click="toggleFeaturedDescription"
            >
              {{ isFeaturedDescriptionVisible ? 'Скрыть описание' : 'Показать описание' }}
            </button>
            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge rounded-pill text-bg-warning">{{ featuredMovie.genre }}</span>
              <span class="badge rounded-pill text-bg-secondary">{{ featuredDuration }}</span>
              <span class="badge rounded-pill text-bg-secondary">Рейтинг {{ featuredMovie.rating ?? '—' }}</span>
            </div>
            <router-link class="btn btn-outline-warning" :to="`/movies/${featuredMovie.id}`">
              Открыть страницу фильма
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger mt-4">{{ error }}</div>
    <div v-else-if="loading" class="text-secondary mt-4">Загружаем афишу...</div>

    <section class="mt-5">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3 mb-4">
        <div>
          <span class="text-uppercase text-warning small fw-semibold">Новинки</span>
          <h2 class="text-white mb-1">Горячие релизы</h2>
          <p class="text-secondary mb-0">Выбрали несколько фильмов, с которых удобно начать знакомство с каталогом.</p>
        </div>
        <router-link class="btn btn-outline-light" to="/movies">Открыть весь каталог</router-link>
      </div>

      <div class="row g-4">
        <div v-for="movie in newReleases" :key="movie.id" class="col-md-6 col-xl-4">
          <MovieCard
            :movie="movie"
            :favorite-enabled="true"
            :is-favorite="isFavorite(movie.id)"
            :favorite-loading="favoriteLoadingId === movie.id"
            @toggle-favorite="toggleFavorite"
          />
        </div>
      </div>
    </section>
  </section>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'
import { api } from '@/services/api'
import { sessionState } from '@/store/session'
import { formatDuration, getPosterUrl } from '@/utils/formatters'

export default {
  name: 'HomeView',
  components: {
    MovieCard
  },
  data() {
    return {
      sessionState,
      movies: [],
      favoriteMovies: [],
      favoriteLoadingId: null,
      loading: false,
      error: '',
      isFeaturedDescriptionVisible: false
    }
  },
  computed: {
    currentUser() {
      return this.sessionState.user
    },
    featuredMovie() {
      return this.movies[0] || null
    },
    newReleases() {
      return this.movies.slice(0, 3)
    },
    featuredPoster() {
      return getPosterUrl(this.featuredMovie)
    },
    featuredDuration() {
      return this.featuredMovie ? formatDuration(this.featuredMovie.duration_minutes) : ''
    },
    featuredDescription() {
      const fallback = 'Описание фильма пока не добавлено.'
      if (this.isFeaturedDescriptionVisible) {
        return this.featuredMovie?.description || fallback
      }

      return 'Описание скрыто антиспойлер-режимом.'
    }
  },
  async mounted() {
    await this.loadMovies()
  },
  methods: {
    async loadMovies() {
      this.loading = true
      this.error = ''
      this.isFeaturedDescriptionVisible = false

      try {
        const response = await api.getMovies({ limit: 6, offset: 0 })
        this.movies = response.items
        await this.loadFavorites()
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async loadFavorites() {
      if (!this.currentUser) {
        this.favoriteMovies = []
        return
      }

      try {
        this.favoriteMovies = await api.getFavorites(this.currentUser.id)
      } catch (error) {
        this.favoriteMovies = []
      }
    },
    isFavorite(movieId) {
      return this.favoriteMovies.some((movie) => movie.movie_id === movieId)
    },
    async toggleFavorite(movie) {
      if (!this.currentUser) {
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
            user_id: this.currentUser.id,
            movie_id: movie.id
          })
        } else {
          await api.addFavorite({
            user_id: this.currentUser.id,
            movie_id: movie.id
          })
        }

        await this.loadFavorites()
      } catch (error) {
        this.error = error.message
      } finally {
        this.favoriteLoadingId = null
      }
    },
    toggleFeaturedDescription() {
      this.isFeaturedDescriptionVisible = !this.isFeaturedDescriptionVisible
    }
  }
}
</script>
