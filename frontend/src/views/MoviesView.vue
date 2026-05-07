<template>
  <section class="container">
    <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-end gap-3 mb-4">
      <div>
        <span class="text-uppercase text-warning small fw-semibold">Каталог</span>
        <h1 class="text-white mb-1">Все фильмы</h1>
        <p class="text-secondary mb-0">Фильтруй каталог по жанру и поисковому запросу.</p>
      </div>
      <span class="badge text-bg-dark px-3 py-2">{{ total }} фильмов</span>
    </div>

    <form class="card bg-dark-subtle border-0 shadow-sm p-3 p-lg-4 mb-4" @submit.prevent="applyFilters">
      <div class="row g-3 align-items-end">
        <div class="col-md-6 col-lg-5">
          <label class="form-label text-secondary">Поиск</label>
          <input v-model="filters.search" type="search" class="form-control" placeholder="Например, Дюна">
        </div>
        <div class="col-md-4 col-lg-3">
          <label class="form-label text-secondary">Жанр</label>
          <select v-model="filters.genre" class="form-select">
            <option value="">Все жанры</option>
            <option v-for="genre in genres" :key="genre" :value="genre">{{ genre }}</option>
          </select>
        </div>
        <div class="col-md-2 col-lg-2">
          <label class="form-label text-secondary">От рейтинга</label>
          <input v-model.number="filters.min_rating" type="number" min="0" max="10" step="0.1" class="form-control">
        </div>
        <div class="col-lg-2 d-grid">
          <button class="btn btn-warning" type="submit">Обновить</button>
        </div>
      </div>
    </form>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row g-4">
      <div v-for="movie in movies" :key="movie.id" class="col-md-6 col-xl-4">
        <MovieCard
          :movie="movie"
          :favorite-enabled="true"
          :is-favorite="isFavorite(movie.id)"
          :favorite-loading="favoriteLoadingId === movie.id"
          @toggle-favorite="toggleFavorite"
        />
      </div>
      <div v-if="!movies.length && !loading" class="col-12">
        <div class="alert alert-secondary mb-0">По текущим фильтрам фильмы не найдены.</div>
      </div>
    </div>

    <div v-if="loading && !movies.length" class="text-secondary mt-4">Загружаем фильмы...</div>

    <div v-if="movies.length" ref="sentinel" class="py-4 d-flex justify-content-center">
      <div v-if="loadingMore" class="spinner-border text-warning" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <div v-else-if="!hasMore" class="text-secondary small">Все фильмы загружены.</div>
    </div>
  </section>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'
import { api, MOVIES_PAGE_SIZE } from '@/services/api'
import { sessionState } from '@/store/session'

export default {
  name: 'MoviesView',
  components: {
    MovieCard
  },
  data() {
    return {
      sessionState,
      movies: [],
      favoriteMovies: [],
      total: 0,
      loading: false,
      loadingMore: false,
      error: '',
      hasMore: true,
      nextOffset: 0,
      pageSize: MOVIES_PAGE_SIZE,
      observer: null,
      favoriteLoadingId: null,
      filters: {
        search: this.$route.query.search || '',
        genre: '',
        min_rating: ''
      }
    }
  },
  computed: {
    currentUser() {
      return this.sessionState.user
    },
    genres() {
      return [...new Set(this.movies.map((movie) => movie.genre).filter(Boolean))].sort()
    }
  },
  async mounted() {
    await this.loadMovies({ reset: true })
    this.initObserver()
  },
  beforeUnmount() {
    if (this.observer) {
      this.observer.disconnect()
    }
  },
  methods: {
    initObserver() {
      this.observer = new IntersectionObserver((entries) => {
        const [entry] = entries
        if (entry?.isIntersecting) {
          this.loadMoreMovies()
        }
      }, { rootMargin: '200px 0px' })

      if (this.$refs.sentinel) {
        this.observer.observe(this.$refs.sentinel)
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
    async applyFilters() {
      await this.loadMovies({ reset: true })
    },
    async loadMovies({ reset = false } = {}) {
      if (reset) {
        this.loading = true
      } else {
        this.loadingMore = true
      }
      this.error = ''

      try {
        if (reset) {
          this.nextOffset = 0
          this.hasMore = true
          await this.loadFavorites()
        }

        const response = await api.getMovies({
          ...this.filters,
          limit: this.pageSize,
          offset: this.nextOffset
        })

        this.total = response.total
        this.hasMore = response.has_more
        this.nextOffset = response.offset + response.items.length
        this.movies = reset ? response.items : [...this.movies, ...response.items]
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
        this.loadingMore = false
        this.$nextTick(() => {
          if (this.observer && this.$refs.sentinel) {
            this.observer.disconnect()
            this.observer.observe(this.$refs.sentinel)
          }
        })
      }
    },
    async loadMoreMovies() {
      if (this.loading || this.loadingMore || !this.hasMore) {
        return
      }

      await this.loadMovies()
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
    }
  }
}
</script>
