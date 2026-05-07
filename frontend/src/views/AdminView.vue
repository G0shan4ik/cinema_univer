<template>
  <section class="container">
    <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-end gap-3 mb-4">
      <div>
        <span class="text-uppercase text-warning small fw-semibold">Панель управления</span>
        <h1 class="text-white mb-1">Админка кинотеатра</h1>
        <p class="text-secondary mb-0">Управление фильмами, залами, сеансами, пользователями и билетами.</p>
      </div>
      <button class="btn btn-outline-light" type="button" @click="loadAdminData">
        Обновить данные
      </button>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row g-4 mb-4">
      <div class="col-sm-6 col-xl-3" v-for="stat in stats" :key="stat.label">
        <div class="card bg-dark-subtle border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="text-secondary small">{{ stat.label }}</div>
            <div class="display-6 text-white fw-bold">{{ stat.value }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-12">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex flex-wrap gap-2">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                type="button"
                class="btn"
                :class="activeTab === tab.id ? 'btn-warning' : 'btn-outline-light'"
                @click="activeTab = tab.id"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'movies'" class="col-12">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4">
            <div class="row g-4">
              <div class="col-xl-4">
                <h2 class="h5 text-white mb-3">Добавить фильм</h2>
                <form class="row g-3" @submit.prevent="createMovie">
                  <div class="col-12">
                    <input v-model="movieForm.title" class="form-control" placeholder="Название" required>
                  </div>
                  <div class="col-12">
                    <textarea v-model="movieForm.description" class="form-control" rows="4" placeholder="Описание"></textarea>
                  </div>
                  <div class="col-md-6">
                    <input v-model="movieForm.genre" class="form-control" placeholder="Жанр" required>
                  </div>
                  <div class="col-md-6">
                    <input v-model.number="movieForm.duration_minutes" type="number" min="1" class="form-control" placeholder="Минуты" required>
                  </div>
                  <div class="col-md-6">
                    <input v-model.number="movieForm.rating" type="number" min="0" max="10" step="0.1" class="form-control" placeholder="Рейтинг">
                  </div>
                  <div class="col-md-6">
                    <input v-model="movieForm.release_date" type="date" class="form-control">
                  </div>
                  <div class="col-12">
                    <input v-model="movieForm.poster_url" class="form-control" placeholder="Ссылка на постер">
                  </div>
                  <div class="col-12 d-grid">
                    <button class="btn btn-warning" type="submit">Создать фильм</button>
                  </div>
                </form>
              </div>

              <div class="col-xl-8">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h2 class="h5 text-white mb-0">Список фильмов</h2>
                  <span class="badge text-bg-dark">{{ movies.length }}</span>
                </div>

                <div class="table-responsive">
                  <table class="table table-dark table-hover align-middle">
                    <thead>
                      <tr>
                        <th>Название</th>
                        <th>Жанр</th>
                        <th>Длительность</th>
                        <th>Рейтинг</th>
                        <th>Дата</th>
                        <th class="text-end">Действия</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="movie in movies" :key="movie.id">
                        <td v-if="editingMovieId === movie.id">
                          <input v-model="movieEditForm.title" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ movie.title }}</td>

                        <td v-if="editingMovieId === movie.id">
                          <input v-model="movieEditForm.genre" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ movie.genre }}</td>

                        <td v-if="editingMovieId === movie.id">
                          <input v-model.number="movieEditForm.duration_minutes" type="number" min="1" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ movie.duration_minutes }} мин</td>

                        <td v-if="editingMovieId === movie.id">
                          <input v-model.number="movieEditForm.rating" type="number" min="0" max="10" step="0.1" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ movie.rating ?? '—' }}</td>

                        <td v-if="editingMovieId === movie.id">
                          <input v-model="movieEditForm.release_date" type="date" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ formatDate(movie.release_date) }}</td>

                        <td class="text-end">
                          <div class="d-flex flex-wrap justify-content-end gap-2">
                            <template v-if="editingMovieId === movie.id">
                              <button class="btn btn-sm btn-warning" type="button" @click="saveMovie(movie.id)">Сохранить</button>
                              <button class="btn btn-sm btn-outline-light" type="button" @click="cancelMovieEdit">Отмена</button>
                            </template>
                            <template v-else>
                              <button class="btn btn-sm btn-outline-warning" type="button" @click="startMovieEdit(movie)">Редактировать</button>
                              <button class="btn btn-sm btn-outline-danger" type="button" @click="deleteMovie(movie.id)">Удалить</button>
                            </template>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="!movies.length">
                        <td colspan="6" class="text-center text-secondary">Фильмов пока нет.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'halls'" class="col-12">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4">
            <div class="row g-4">
              <div class="col-xl-4">
                <h2 class="h5 text-white mb-3">Добавить зал</h2>
                <form class="row g-3" @submit.prevent="createHall">
                  <div class="col-12">
                    <input v-model="hallForm.name" class="form-control" placeholder="Название зала" required>
                  </div>
                  <div class="col-6">
                    <input v-model.number="hallForm.total_rows" type="number" min="1" class="form-control" placeholder="Рядов" required>
                  </div>
                  <div class="col-6">
                    <input v-model.number="hallForm.seats_per_row" type="number" min="1" class="form-control" placeholder="Мест в ряду" required>
                  </div>
                  <div class="col-12 d-grid">
                    <button class="btn btn-warning" type="submit">Создать зал</button>
                  </div>
                </form>
              </div>

              <div class="col-xl-8">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h2 class="h5 text-white mb-0">Список залов</h2>
                  <span class="badge text-bg-dark">{{ halls.length }}</span>
                </div>

                <div class="table-responsive">
                  <table class="table table-dark table-hover align-middle">
                    <thead>
                      <tr>
                        <th>Название</th>
                        <th>Рядов</th>
                        <th>Мест в ряду</th>
                        <th class="text-end">Действия</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="hall in halls" :key="hall.id">
                        <td v-if="editingHallId === hall.id">
                          <input v-model="hallEditForm.name" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ hall.name }}</td>

                        <td v-if="editingHallId === hall.id">
                          <input v-model.number="hallEditForm.total_rows" type="number" min="1" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ hall.total_rows }}</td>

                        <td v-if="editingHallId === hall.id">
                          <input v-model.number="hallEditForm.seats_per_row" type="number" min="1" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ hall.seats_per_row }}</td>

                        <td class="text-end">
                          <div class="d-flex flex-wrap justify-content-end gap-2">
                            <template v-if="editingHallId === hall.id">
                              <button class="btn btn-sm btn-warning" type="button" @click="saveHall(hall.id)">Сохранить</button>
                              <button class="btn btn-sm btn-outline-light" type="button" @click="cancelHallEdit">Отмена</button>
                            </template>
                            <template v-else>
                              <button class="btn btn-sm btn-outline-warning" type="button" @click="startHallEdit(hall)">Редактировать</button>
                              <button class="btn btn-sm btn-outline-danger" type="button" @click="deleteHall(hall.id)">Удалить</button>
                            </template>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="!halls.length">
                        <td colspan="4" class="text-center text-secondary">Залов пока нет.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'sessions'" class="col-12">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4">
            <div class="row g-4">
              <div class="col-xl-4">
                <h2 class="h5 text-white mb-3">Добавить сеанс</h2>
                <form class="row g-3" @submit.prevent="createSession">
                  <div class="col-12">
                    <select v-model.number="sessionForm.movie_id" class="form-select" required>
                      <option disabled value="">Выбери фильм</option>
                      <option v-for="movie in movies" :key="movie.id" :value="movie.id">{{ movie.title }}</option>
                    </select>
                  </div>
                  <div class="col-12">
                    <select v-model.number="sessionForm.hall_id" class="form-select" required>
                      <option disabled value="">Выбери зал</option>
                      <option v-for="hall in halls" :key="hall.id" :value="hall.id">{{ hall.name }}</option>
                    </select>
                  </div>
                  <div class="col-12">
                    <input v-model="sessionForm.start_time" type="datetime-local" class="form-control" required>
                  </div>
                  <div class="col-12">
                    <input v-model.number="sessionForm.price" type="number" min="1" step="0.5" class="form-control" placeholder="Цена" required>
                  </div>
                  <div class="col-12 d-grid">
                    <button class="btn btn-warning" type="submit">Создать сеанс</button>
                  </div>
                </form>
              </div>

              <div class="col-xl-8">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h2 class="h5 text-white mb-0">Список сеансов</h2>
                  <span class="badge text-bg-dark">{{ sessions.length }}</span>
                </div>

                <div class="table-responsive">
                  <table class="table table-dark table-hover align-middle">
                    <thead>
                      <tr>
                        <th>Фильм</th>
                        <th>Зал</th>
                        <th>Начало</th>
                        <th>Цена</th>
                        <th class="text-end">Действия</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="session in sessions" :key="session.id">
                        <td v-if="editingSessionId === session.id">
                          <select v-model.number="sessionEditForm.movie_id" class="form-select form-select-sm">
                            <option v-for="movie in movies" :key="movie.id" :value="movie.id">{{ movie.title }}</option>
                          </select>
                        </td>
                        <td v-else>{{ session.movie_title }}</td>

                        <td v-if="editingSessionId === session.id">
                          <select v-model.number="sessionEditForm.hall_id" class="form-select form-select-sm">
                            <option v-for="hall in halls" :key="hall.id" :value="hall.id">{{ hall.name }}</option>
                          </select>
                        </td>
                        <td v-else>{{ session.hall_name }}</td>

                        <td v-if="editingSessionId === session.id">
                          <input v-model="sessionEditForm.start_time" type="datetime-local" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ formatDateTime(session.start_time) }}</td>

                        <td v-if="editingSessionId === session.id">
                          <input v-model.number="sessionEditForm.price" type="number" min="1" step="0.5" class="form-control form-control-sm">
                        </td>
                        <td v-else>{{ session.price }} BYN</td>

                        <td class="text-end">
                          <div class="d-flex flex-wrap justify-content-end gap-2">
                            <template v-if="editingSessionId === session.id">
                              <button class="btn btn-sm btn-warning" type="button" @click="saveSession(session.id)">Сохранить</button>
                              <button class="btn btn-sm btn-outline-light" type="button" @click="cancelSessionEdit">Отмена</button>
                            </template>
                            <template v-else>
                              <button class="btn btn-sm btn-outline-warning" type="button" @click="startSessionEdit(session)">Редактировать</button>
                              <button class="btn btn-sm btn-outline-danger" type="button" @click="deleteSession(session.id)">Удалить</button>
                            </template>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="!sessions.length">
                        <td colspan="5" class="text-center text-secondary">Сеансов пока нет.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'users'" class="col-12">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h2 class="h5 text-white mb-0">Пользователи</h2>
              <span class="badge text-bg-dark">{{ users.length }}</span>
            </div>

            <div class="table-responsive">
              <table class="table table-dark table-hover align-middle">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Имя</th>
                    <th>Роль</th>
                    <th>Статус</th>
                    <th class="text-end">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.name }}</td>
                    <td>{{ user.role === 'admin' ? 'Админ' : 'Пользователь' }}</td>
                    <td>
                      <span class="badge" :class="user.is_active ? 'text-bg-success' : 'text-bg-secondary'">
                        {{ user.is_active ? 'Активен' : 'Отключен' }}
                      </span>
                    </td>
                    <td class="text-end">
                      <button
                        class="btn btn-sm btn-outline-danger"
                        type="button"
                        :disabled="!user.is_active || user.role === 'admin'"
                        @click="deactivateUser(user.id)"
                      >
                        Деактивировать
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!users.length">
                    <td colspan="6" class="text-center text-secondary">Пользователей пока нет.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'tickets'" class="col-12">
        <div class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h2 class="h5 text-white mb-0">Билеты</h2>
              <span class="badge text-bg-dark">{{ tickets.length }}</span>
            </div>

            <div class="table-responsive">
              <table class="table table-dark table-hover align-middle">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Фильм</th>
                    <th>Пользователь</th>
                    <th>Место</th>
                    <th>Сеанс</th>
                    <th>Статус</th>
                    <th class="text-end">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="ticket in tickets" :key="ticket.id">
                    <td>{{ ticket.id }}</td>
                    <td>{{ ticket.movie_title }}</td>
                    <td>#{{ ticket.user_id }}</td>
                    <td>Ряд {{ ticket.seat_row }}, место {{ ticket.seat_number }}</td>
                    <td>{{ formatDateTime(ticket.start_time) }}</td>
                    <td>
                      <select
                        :value="ticketStatusDrafts[ticket.id] || ticket.status"
                        class="form-select form-select-sm"
                        @change="ticketStatusDrafts[ticket.id] = $event.target.value"
                      >
                        <option value="booked">Забронирован</option>
                        <option value="paid">Оплачен</option>
                        <option value="cancelled">Отменен</option>
                      </select>
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-warning" type="button" @click="saveTicketStatus(ticket)">
                        Сохранить статус
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!tickets.length">
                    <td colspan="7" class="text-center text-secondary">Билетов пока нет.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { api } from '@/services/api'
import { formatDate, formatDateTime } from '@/utils/formatters'

function createMovieForm() {
  return {
    title: '',
    description: '',
    genre: '',
    duration_minutes: 120,
    rating: '',
    poster_url: '',
    release_date: ''
  }
}

function createHallForm() {
  return {
    name: '',
    total_rows: 8,
    seats_per_row: 10
  }
}

function createSessionForm() {
  return {
    movie_id: '',
    hall_id: '',
    start_time: '',
    price: 15
  }
}

export default {
  name: 'AdminView',
  data() {
    return {
      loading: false,
      error: '',
      message: '',
      activeTab: 'movies',
      tabs: [
        { id: 'movies', label: 'Фильмы' },
        { id: 'halls', label: 'Залы' },
        { id: 'sessions', label: 'Сеансы' },
        { id: 'users', label: 'Пользователи' },
        { id: 'tickets', label: 'Билеты' }
      ],
      movies: [],
      halls: [],
      sessions: [],
      users: [],
      tickets: [],
      ticketStatusDrafts: {},
      movieForm: createMovieForm(),
      hallForm: createHallForm(),
      sessionForm: createSessionForm(),
      editingMovieId: null,
      editingHallId: null,
      editingSessionId: null,
      movieEditForm: createMovieForm(),
      hallEditForm: createHallForm(),
      sessionEditForm: createSessionForm()
    }
  },
  computed: {
    stats() {
      return [
        { label: 'Фильмы', value: this.movies.length },
        { label: 'Залы', value: this.halls.length },
        { label: 'Сеансы', value: this.sessions.length },
        { label: 'Пользователи', value: this.users.length }
      ]
    }
  },
  async mounted() {
    await this.loadAdminData()
  },
  methods: {
    formatDate,
    formatDateTime,
    resetAlerts() {
      this.error = ''
      this.message = ''
    },
    buildMoviePayload(form) {
      return {
        title: form.title,
        description: form.description || null,
        genre: form.genre,
        duration_minutes: Number(form.duration_minutes),
        rating: form.rating === '' || form.rating === null ? null : Number(form.rating),
        poster_url: form.poster_url || null,
        release_date: form.release_date || null
      }
    },
    buildHallPayload(form) {
      return {
        name: form.name,
        total_rows: Number(form.total_rows),
        seats_per_row: Number(form.seats_per_row)
      }
    },
    buildSessionPayload(form) {
      return {
        movie_id: Number(form.movie_id),
        hall_id: Number(form.hall_id),
        start_time: form.start_time,
        price: Number(form.price)
      }
    },
    toDateInput(value) {
      if (!value) {
        return ''
      }
      return new Date(value).toISOString().slice(0, 10)
    },
    toDateTimeLocal(value) {
      if (!value) {
        return ''
      }
      const date = new Date(value)
      const offset = date.getTimezoneOffset()
      const normalized = new Date(date.getTime() - offset * 60000)
      return normalized.toISOString().slice(0, 16)
    },
    async loadAdminData() {
      this.loading = true
      this.resetAlerts()

      try {
        const [moviesResponse, halls, sessions, users, tickets] = await Promise.all([
          api.getMovies({ limit: 100, offset: 0 }),
          api.getHalls(),
          api.getSessions({ per_page: 100 }),
          api.getUsers({ per_page: 100 }),
          api.getTickets({ per_page: 100 })
        ])

        this.movies = moviesResponse.items
        this.halls = halls
        this.sessions = sessions
        this.users = users
        this.tickets = tickets
        this.ticketStatusDrafts = tickets.reduce((acc, ticket) => {
          acc[ticket.id] = ticket.status
          return acc
        }, {})
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async createMovie() {
      this.resetAlerts()

      try {
        await api.createMovie(this.buildMoviePayload(this.movieForm))
        this.movieForm = createMovieForm()
        this.message = 'Фильм создан.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    startMovieEdit(movie) {
      this.editingMovieId = movie.id
      this.movieEditForm = {
        title: movie.title,
        description: movie.description || '',
        genre: movie.genre,
        duration_minutes: movie.duration_minutes,
        rating: movie.rating ?? '',
        poster_url: movie.poster_url || '',
        release_date: this.toDateInput(movie.release_date)
      }
    },
    cancelMovieEdit() {
      this.editingMovieId = null
      this.movieEditForm = createMovieForm()
    },
    async saveMovie(movieId) {
      this.resetAlerts()

      try {
        await api.updateMovie(movieId, this.buildMoviePayload(this.movieEditForm))
        this.message = 'Фильм обновлен.'
        this.cancelMovieEdit()
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    async deleteMovie(movieId) {
      this.resetAlerts()

      try {
        await api.deleteMovie(movieId)
        this.message = 'Фильм удален.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    async createHall() {
      this.resetAlerts()

      try {
        await api.createHall(this.buildHallPayload(this.hallForm))
        this.hallForm = createHallForm()
        this.message = 'Зал создан.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    startHallEdit(hall) {
      this.editingHallId = hall.id
      this.hallEditForm = {
        name: hall.name,
        total_rows: hall.total_rows,
        seats_per_row: hall.seats_per_row
      }
    },
    cancelHallEdit() {
      this.editingHallId = null
      this.hallEditForm = createHallForm()
    },
    async saveHall(hallId) {
      this.resetAlerts()

      try {
        await api.updateHall(hallId, this.buildHallPayload(this.hallEditForm))
        this.message = 'Зал обновлен.'
        this.cancelHallEdit()
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    async deleteHall(hallId) {
      this.resetAlerts()

      try {
        await api.deleteHall(hallId)
        this.message = 'Зал удален.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    async createSession() {
      this.resetAlerts()

      try {
        await api.createSession(this.buildSessionPayload(this.sessionForm))
        this.sessionForm = createSessionForm()
        this.message = 'Сеанс создан.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    startSessionEdit(session) {
      this.editingSessionId = session.id
      this.sessionEditForm = {
        movie_id: session.movie_id,
        hall_id: session.hall_id,
        start_time: this.toDateTimeLocal(session.start_time),
        price: session.price
      }
    },
    cancelSessionEdit() {
      this.editingSessionId = null
      this.sessionEditForm = createSessionForm()
    },
    async saveSession(sessionId) {
      this.resetAlerts()

      try {
        await api.updateSession(sessionId, this.buildSessionPayload(this.sessionEditForm))
        this.message = 'Сеанс обновлен.'
        this.cancelSessionEdit()
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    async deleteSession(sessionId) {
      this.resetAlerts()

      try {
        await api.deleteSession(sessionId)
        this.message = 'Сеанс удален.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    async deactivateUser(userId) {
      this.resetAlerts()

      try {
        await api.deactivateUser(userId)
        this.message = 'Пользователь деактивирован.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    },
    async saveTicketStatus(ticket) {
      this.resetAlerts()

      try {
        await api.updateTicketStatus(ticket.id, {
          status: this.ticketStatusDrafts[ticket.id] || ticket.status
        })
        this.message = 'Статус билета обновлен.'
        await this.loadAdminData()
      } catch (error) {
        this.error = error.message
      }
    }
  }
}
</script>
