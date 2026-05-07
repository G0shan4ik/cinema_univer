const DATE_FORMATTER = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'long',
  hour: '2-digit',
  minute: '2-digit'
})

const SHORT_DATE_FORMATTER = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'short',
  year: 'numeric'
})

export function formatDuration(minutes) {
  if (!minutes) {
    return 'Не указано'
  }

  return `${minutes} мин`
}

export function formatDateTime(value) {
  if (!value) {
    return 'Дата не указана'
  }

  return DATE_FORMATTER.format(new Date(value))
}

export function formatDate(value) {
  if (!value) {
    return 'Дата не указана'
  }

  return SHORT_DATE_FORMATTER.format(new Date(value))
}

export function getPosterUrl(movie) {
  return movie?.poster_url || 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=1200&q=80'
}

export function getTicketStatusLabel(status) {
  const map = {
    booked: 'Забронирован',
    paid: 'Оплачен',
    cancelled: 'Отменен'
  }

  return map[status] || status
}

export function getTicketStatusVariant(status) {
  const map = {
    booked: 'warning',
    paid: 'success',
    cancelled: 'secondary'
  }

  return map[status] || 'secondary'
}
