<template>
  <section class="container">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3 mb-4">
      <div>
        <span class="text-uppercase text-warning small fw-semibold">Избранное</span>
        <h1 class="text-white mb-1">Сохраненные фильмы</h1>
        <p class="text-secondary mb-0">Подборка для быстрого возврата к интересующим премьерам.</p>
      </div>
      <span class="badge text-bg-dark px-3 py-2">{{ favoriteMovies.length }} фильмов</span>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="loading" class="text-secondary">Загружаем избранное...</div>

    <div v-else class="row g-4">
      <div v-for="movie in favoriteMovies" :key="movie.movie_id" class="col-md-6 col-xl-4">
        <MovieCard
          :movie="mapFavoriteMovie(movie)"
          :favorite-enabled="true"
          :is-favorite="true"
          :favorite-loading="favoriteLoadingId === movie.movie_id"
          @toggle-favorite="toggleFavorite"
        />
      </div>
      <div v-if="!favoriteMovies.length" class="col-12">
        <div class="alert alert-secondary mb-0">Избранное пока пустое.</div>
      </div>
    </div>
  </section>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'
import { api } from '@/services/api'
import { sessionState } from '@/store/session'

export default {
  name: 'FavoritesView',
  components: {
    MovieCard
  },
  data() {
    return {
      sessionState,
      favoriteMovies: [],
      favoriteLoadingId: null,
      loading: false,
      error: ''
    }
  },
  async mounted() {
    await this.loadFavorites()
  },
  methods: {
    async loadFavorites() {
      this.loading = true
      this.error = ''

      try {
        this.favoriteMovies = await api.getFavorites(this.sessionState.user.id)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    mapFavoriteMovie(movie) {
      return {
        id: movie.movie_id,
        title: movie.title,
        description: movie.description,
        genre: movie.genre,
        duration_minutes: movie.duration_minutes,
        rating: movie.rating,
        poster_url: movie.poster_url,
        release_date: movie.release_date
      }
    },
    async toggleFavorite(movie) {
      this.favoriteLoadingId = movie.id

      try {
        await api.removeFavorite({
          user_id: this.sessionState.user.id,
          movie_id: movie.id
        })
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
