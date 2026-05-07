<template>
  <section class="container">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3 mb-4">
      <div>
        <span class="text-uppercase text-warning small fw-semibold">Мои билеты</span>
        <h1 class="text-white mb-1">Предстоящие сеансы</h1>
        <p class="text-secondary mb-0">Все бронирования и покупки, привязанные к текущему аккаунту.</p>
      </div>
      <router-link class="btn btn-outline-light" to="/profile">Назад в профиль</router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="loading" class="text-secondary">Загружаем билеты...</div>

    <div v-else class="row g-4">
      <div v-for="ticket in tickets" :key="ticket.id" class="col-12">
        <article class="card bg-dark-subtle border-0 shadow-sm">
          <div class="card-body p-4 d-flex flex-column flex-lg-row justify-content-between gap-3">
            <div>
              <h2 class="h4 text-white mb-2">{{ ticket.movie_title }}</h2>
              <div class="text-secondary">{{ formatDateTime(ticket.start_time) }}</div>
              <div class="text-secondary">{{ ticket.hall_name }} · {{ ticket.price }} BYN</div>
            </div>
            <div class="d-flex flex-column align-items-lg-end gap-2">
              <span class="badge" :class="`text-bg-${getTicketStatusVariant(ticket.status)}`">
                {{ getTicketStatusLabel(ticket.status) }}
              </span>
              <div class="text-secondary">Ряд {{ ticket.seat_row }}, место {{ ticket.seat_number }}</div>
            </div>
          </div>
        </article>
      </div>
      <div v-if="!tickets.length" class="col-12">
        <div class="alert alert-secondary mb-0">У этого пользователя пока нет билетов.</div>
      </div>
    </div>
  </section>
</template>

<script>
import { api } from '@/services/api'
import { sessionState } from '@/store/session'
import { formatDateTime, getTicketStatusLabel, getTicketStatusVariant } from '@/utils/formatters'

export default {
  name: 'ProfileTicketsView',
  data() {
    return {
      sessionState,
      tickets: [],
      loading: false,
      error: ''
    }
  },
  async mounted() {
    await this.loadTickets()
  },
  methods: {
    formatDateTime,
    getTicketStatusLabel,
    getTicketStatusVariant,
    async loadTickets() {
      this.loading = true
      this.error = ''

      try {
        this.tickets = await api.getUserTickets(this.sessionState.user.id)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
