<template>
  <article class="card h-100 border-0 shadow-sm overflow-hidden bg-dark-subtle movie-card">
    <div class="position-relative">
      <img
        :src="posterUrl"
        :alt="movie.title"
        class="card-img-top movie-card__poster"
      >
      <button
        v-if="favoriteEnabled"
        type="button"
        class="btn btn-dark btn-sm rounded-circle position-absolute top-0 end-0 m-3 movie-card__favorite"
        :disabled="favoriteLoading"
        :title="isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'"
        @click="$emit('toggle-favorite', movie)"
      >
        <i :class="isFavorite ? 'bi bi-heart-fill text-danger' : 'bi bi-heart text-white'"></i>
      </button>
    </div>
    <div class="card-body d-flex flex-column">
      <div class="d-flex flex-wrap gap-2 mb-3">
        <span class="badge rounded-pill text-bg-warning">{{ movie.genre }}</span>
        <span class="badge rounded-pill text-bg-dark">{{ durationLabel }}</span>
      </div>
      <h3 class="h5 text-white">{{ movie.title }}</h3>
      <p class="text-secondary flex-grow-1 movie-description">
        {{ descriptionText }}
      </p>
      <button
        type="button"
        class="btn btn-outline-secondary btn-sm align-self-start mb-3"
        @click="toggleDescription"
      >
        {{ isDescriptionVisible ? 'Скрыть описание' : 'Показать описание' }}
      </button>
      <div class="d-flex justify-content-between align-items-center text-secondary small mb-3">
        <span><i class="bi bi-star-fill text-warning me-1"></i>{{ movie.rating ?? '—' }}</span>
        <span>{{ releaseDateLabel }}</span>
      </div>
      <div class="d-flex gap-2 mt-auto">
        <router-link class="btn btn-warning w-100" :to="`/movies/${movie.id}`">
          Подробнее
        </router-link>
      </div>
    </div>
  </article>
</template>

<script>
import { formatDate, formatDuration, getPosterUrl } from '@/utils/formatters'

export default {
  name: 'MovieCard',
  props: {
    movie: {
      type: Object,
      required: true
    },
    favoriteEnabled: {
      type: Boolean,
      default: false
    },
    isFavorite: {
      type: Boolean,
      default: false
    },
    favoriteLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-favorite'],
  data() {
    return {
      isDescriptionVisible: false
    }
  },
  computed: {
    descriptionText() {
      const fallback = 'Описание фильма пока не добавлено.'
      if (this.isDescriptionVisible) {
        return this.movie.description || fallback
      }

      return 'Описание скрыто антиспойлер-режимом.'
    },
    durationLabel() {
      return formatDuration(this.movie.duration_minutes)
    },
    releaseDateLabel() {
      return this.movie.release_date ? formatDate(this.movie.release_date) : 'Скоро в прокате'
    },
    posterUrl() {
      return getPosterUrl(this.movie)
    }
  },
  methods: {
    toggleDescription() {
      this.isDescriptionVisible = !this.isDescriptionVisible
    }
  }
}
</script>
