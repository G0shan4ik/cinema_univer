<template>
  <section class="container">
    <div v-if="loading" class="text-secondary">Загружаем страницу фильма...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <template v-else-if="movie">
      <div class="row g-4 mb-4">
        <div class="col-lg-4">
          <img :src="posterUrl" :alt="movie.title" class="img-fluid rounded-4 shadow-sm detail-poster">
        </div>

        <div class="col-lg-8">
          <div class="card bg-dark-subtle border-0 shadow-sm h-100">
            <div class="card-body p-4 p-lg-5">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span class="badge rounded-pill text-bg-warning">{{ movie.genre }}</span>
                <span class="badge rounded-pill text-bg-secondary">{{ durationLabel }}</span>
                <span class="badge rounded-pill text-bg-secondary">Рейтинг {{ movie.rating ?? '—' }}</span>
              </div>

              <h1 class="display-6 text-white">{{ movie.title }}</h1>
              <p class="text-secondary mb-2">{{ movieDescription }}</p>
              <button
                class="btn btn-outline-secondary btn-sm mb-4"
                type="button"
                @click="toggleDescription"
              >
                {{ isDescriptionVisible ? 'Скрыть описание' : 'Показать описание' }}
              </button>

              <div class="row g-3 mb-4">
                <div class="col-md-4">
                  <div class="rounded-4 border border-light-subtle p-3 h-100">
                    <div class="text-secondary small mb-1">Дата релиза</div>
                    <div class="text-white fw-semibold">{{ releaseDateLabel }}</div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="rounded-4 border border-light-subtle p-3 h-100">
                    <div class="text-secondary small mb-1">Ближайший сеанс</div>
                    <div class="text-white fw-semibold">{{ nearestSessionLabel }}</div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="rounded-4 border border-light-subtle p-3 h-100">
                    <div class="text-secondary small mb-1">Статус</div>
                    <div class="text-white fw-semibold">{{ currentUser ? 'Можно бронировать' : 'Нужен вход' }}</div>
                  </div>
                </div>
              </div>

              <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-warning" type="button" @click="scrollToSessions">Выбрать сеанс</button>
                <button class="btn btn-outline-light" type="button" @click="toggleFavorite">
                  {{ isFavorite ? 'Убрать из избранного' : 'Добавить в избранное' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div id="sessions" class="row g-4">
        <div class="col-xl-7">
          <div class="card bg-dark-subtle border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-start gap-3 mb-4">
                <div>
                  <h2 class="h4 text-white mb-1">Сеансы</h2>
                  <p class="text-secondary mb-0">Выбери подходящее время и зал.</p>
                </div>
                <span class="badge text-bg-dark">{{ sessions.length }} сеансов</span>
              </div>

              <div v-if="!sessions.length" class="alert alert-secondary mb-0">
                Для этого фильма пока нет доступных сеансов.
              </div>

              <div v-else class="d-grid gap-3">
                <button
                  v-for="session in sessions"
                  :key="session.id"
                  type="button"
                  class="btn text-start session-button"
                  :class="selectedSessionId === session.id ? 'btn-warning' : 'btn-outline-light'"
                  @click="selectSession(session.id)"
                >
                  <div class="d-flex flex-column flex-md-row justify-content-between gap-2">
                    <div>
                      <div class="fw-semibold">{{ formatDateTime(session.start_time) }}</div>
                      <div class="small" :class="selectedSessionId === session.id ? 'text-dark' : 'text-secondary'">
                        {{ session.hall_name }}
                      </div>
                    </div>
                    <div class="fw-semibold">{{ session.price }} BYN</div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-5">
          <div class="card bg-dark-subtle border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <h2 class="h4 text-white mb-1">Бронирование</h2>
              <p class="text-secondary mb-4">Укажи ряд и место для выбранного сеанса.</p>

              <div v-if="bookingMessage" class="alert alert-success">{{ bookingMessage }}</div>
              <div v-if="bookingError" class="alert alert-danger">{{ bookingError }}</div>

              <div v-if="selectedSession" class="rounded-4 border border-light-subtle p-3 mb-4">
                <div class="small text-secondary">Текущий сеанс</div>
                <div class="text-white fw-semibold">{{ formatDateTime(selectedSession.start_time) }}</div>
                <div class="text-secondary">{{ selectedSession.hall_name }} · {{ selectedSession.price }} BYN</div>
              </div>

              <form class="row g-3" @submit.prevent="bookTicket">
                <div class="col-6">
                  <label class="form-label text-secondary">Ряд</label>
                  <input v-model.number="bookingForm.seat_row" type="number" min="1" class="form-control" required>
                </div>
                <div class="col-6">
                  <label class="form-label text-secondary">Место</label>
                  <input v-model.number="bookingForm.seat_number" type="number" min="1" class="form-control" required>
                </div>
                <div class="col-12 d-grid">
                  <button class="btn btn-warning" type="submit" :disabled="!selectedSessionId || bookingLoading">
                    {{ bookingLoading ? 'Бронируем...' : 'Забронировать билет' }}
                  </button>
                </div>
              </form>

              <hr class="border-secondary-subtle my-4">

              <h3 class="h6 text-white">Занятые места</h3>
              <div v-if="seatsLoading" class="text-secondary">Загружаем занятые места...</div>
              <div v-else-if="seatBadges.length" class="d-flex flex-wrap gap-2">
                <span v-for="seat in seatBadges" :key="seat" class="badge text-bg-secondary">{{ seat }}</span>
              </div>
              <div v-else class="text-secondary">Пока все места свободны.</div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="alert alert-secondary">
      Фильм не найден. <router-link to="/movies" class="alert-link">Вернуться к каталогу</router-link>
    </div>
  </section>
</template>

<script>
import { api } from '@/services/api'
import { sessionState } from '@/store/session'
import { formatDate, formatDateTime, formatDuration, getPosterUrl } from '@/utils/formatters'

export default {
  name: 'MovieDetailView',
  props: {
    id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      sessionState,
      movie: null,
      sessions: [],
      favorites: [],
      selectedSessionId: null,
      seatsInfo: null,
      loading: false,
      seatsLoading: false,
      bookingLoading: false,
      error: '',
      bookingError: '',
      bookingMessage: '',
      isDescriptionVisible: false,
      bookingForm: {
        seat_row: 1,
        seat_number: 1
      }
    }
  },
  computed: {
    currentUser() {
      return this.sessionState.user
    },
    selectedSession() {
      return this.sessions.find((session) => session.id === this.selectedSessionId) || null
    },
    nearestSessionLabel() {
      return this.sessions.length ? formatDateTime(this.sessions[0].start_time) : 'Сеансов пока нет'
    },
    durationLabel() {
      return formatDuration(this.movie?.duration_minutes)
    },
    releaseDateLabel() {
      return this.movie?.release_date ? formatDate(this.movie.release_date) : 'Скоро'
    },
    movieDescription() {
      const fallback = 'Описание фильма пока не добавлено.'
      if (this.isDescriptionVisible) {
        return this.movie?.description || fallback
      }

      return 'Описание скрыто антиспойлер-режимом.'
    },
    posterUrl() {
      return getPosterUrl(this.movie)
    },
    isFavorite() {
      return this.favorites.some((movie) => movie.movie_id === this.movie?.id)
    },
    seatBadges() {
      if (!this.seatsInfo?.occupied_seats?.length) {
        return []
      }

      return this.seatsInfo.occupied_seats.map((seat) => `Ряд ${seat.seat_row}, место ${seat.seat_number}`)
    }
  },
  async mounted() {
    await this.loadPage()
  },
  watch: {
    async id() {
      await this.loadPage()
    }
  },
  methods: {
    formatDateTime,
    async loadPage() {
      this.loading = true
      this.error = ''
      this.bookingError = ''
      this.bookingMessage = ''
      this.selectedSessionId = null
      this.seatsInfo = null
      this.isDescriptionVisible = false

      try {
        const [movie, sessions] = await Promise.all([
          api.getMovie(this.id),
          api.getMovieSessions(this.id)
        ])

        this.movie = movie
        this.sessions = sessions

        if (this.currentUser) {
          this.favorites = await api.getFavorites(this.currentUser.id)
        } else {
          this.favorites = []
        }

        if (this.sessions.length) {
          await this.selectSession(this.sessions[0].id)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async selectSession(sessionId) {
      this.selectedSessionId = sessionId
      this.seatsLoading = true
      this.bookingError = ''
      this.bookingMessage = ''

      try {
        this.seatsInfo = await api.getSessionSeats(sessionId)
      } catch (error) {
        this.bookingError = error.message
      } finally {
        this.seatsLoading = false
      }
    },
    async toggleFavorite() {
      if (!this.currentUser) {
        this.$router.push({
          name: 'auth',
          query: {
            redirect: this.$route.fullPath
          }
        })
        return
      }

      try {
        if (this.isFavorite) {
          await api.removeFavorite({
            user_id: this.currentUser.id,
            movie_id: this.movie.id
          })
        } else {
          await api.addFavorite({
            user_id: this.currentUser.id,
            movie_id: this.movie.id
          })
        }

        this.favorites = await api.getFavorites(this.currentUser.id)
      } catch (error) {
        this.bookingError = error.message
      }
    },
    async bookTicket() {
      if (!this.currentUser) {
        this.$router.push({
          name: 'auth',
          query: {
            redirect: this.$route.fullPath
          }
        })
        return
      }

      if (!this.selectedSessionId) {
        this.bookingError = 'Сначала выбери сеанс.'
        return
      }

      this.bookingLoading = true
      this.bookingError = ''
      this.bookingMessage = ''

      try {
        await api.bookTicket({
          user_id: this.currentUser.id,
          session_id: this.selectedSessionId,
          seat_row: this.bookingForm.seat_row,
          seat_number: this.bookingForm.seat_number
        })
        this.bookingMessage = 'Билет успешно забронирован.'
        await this.selectSession(this.selectedSessionId)
      } catch (error) {
        this.bookingError = error.message
      } finally {
        this.bookingLoading = false
      }
    },
    scrollToSessions() {
      const target = document.getElementById('sessions')
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    },
    toggleDescription() {
      this.isDescriptionVisible = !this.isDescriptionVisible
    }
  }
}
</script>
