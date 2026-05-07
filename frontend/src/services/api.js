import {
  clearStoredUser,
  getStoredUser,
  isAccessTokenExpired,
  isRefreshTokenExpired,
  updateStoredTokens,
} from '@/store/session'

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000'
export const MOVIES_PAGE_SIZE = Number(process.env.VUE_APP_MOVIES_PAGE_SIZE || 5)

let refreshPromise = null

async function parseResponse(response) {
  const rawText = await response.text()

  if (!rawText) {
    return null
  }

  try {
    return JSON.parse(rawText)
  } catch (error) {
    return rawText
  }
}

async function refreshAccessToken() {
  if (refreshPromise) {
    return refreshPromise
  }

  const user = getStoredUser()
  if (!user?.refresh_token || isRefreshTokenExpired(user)) {
    clearStoredUser()
    throw new Error('Сессия истекла. Выполните вход заново.')
  }

  refreshPromise = fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      refresh_token: user.refresh_token
    })
  })
    .then(async (response) => {
      const payload = await parseResponse(response)
      if (!response.ok) {
        clearStoredUser()
        throw new Error(payload?.detail || 'Не удалось обновить сессию')
      }

      updateStoredTokens(payload)
      return payload
    })
    .finally(() => {
      refreshPromise = null
    })

  return refreshPromise
}

async function request(path, options = {}) {
  const user = getStoredUser()
  const shouldUseAuth = options.auth !== false

  if (shouldUseAuth && user?.refresh_token && isAccessTokenExpired(user) && !isRefreshTokenExpired(user)) {
    await refreshAccessToken()
  }

  const currentUser = getStoredUser()
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  }

  if (shouldUseAuth && currentUser?.access_token) {
    headers.Authorization = `Bearer ${currentUser.access_token}`
  }

  const config = {
    method: options.method || 'GET',
    headers
  }

  if (options.body !== undefined) {
    config.body = typeof options.body === 'string'
      ? options.body
      : JSON.stringify(options.body)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, config)
  const payload = await parseResponse(response)

  if (response.status === 401 && shouldUseAuth && currentUser?.refresh_token && !options._retry) {
    await refreshAccessToken()
    return request(path, { ...options, _retry: true })
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearStoredUser()
    }
    throw new Error(payload?.detail || 'Не удалось выполнить запрос к серверу')
  }

  return payload
}

function buildQuery(params = {}) {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.set(key, value)
    }
  })

  const suffix = searchParams.toString()
  return suffix ? `?${suffix}` : ''
}

export const api = {
  getMovies(params = {}) {
    return request(`/movies${buildQuery(params)}`, { auth: false })
  },

  getMovie(movieId) {
    return request(`/movie/${movieId}`, { auth: false })
  },

  getMovieSessions(movieId) {
    return request(`/movie/${movieId}/sessions`, { auth: false })
  },

  getSessionSeats(sessionId) {
    return request(`/session/${sessionId}/seats`, { auth: false })
  },

  registerUser(payload) {
    return request('/auth/register', {
      method: 'POST',
      body: payload,
      auth: false
    })
  },

  loginUser(payload) {
    return request('/auth/login', {
      method: 'POST',
      body: payload,
      auth: false
    })
  },

  refreshSession(payload) {
    return request('/auth/refresh', {
      method: 'POST',
      body: payload,
      auth: false
    })
  },

  logoutUser(payload) {
    return request('/auth/logout', {
      method: 'POST',
      body: payload
    })
  },

  getCurrentUser() {
    return request('/auth/me')
  },

  getUser(userId) {
    return request(`/user/${userId}`)
  },

  getUsers(params = {}) {
    return request(`/users${buildQuery(params)}`)
  },

  deactivateUser(userId) {
    return request(`/user/deactivate/${userId}`, {
      method: 'POST'
    })
  },

  updateUser(userId, payload) {
    return request(`/user/update/${userId}`, {
      method: 'POST',
      body: payload
    })
  },

  setKeyword(payload) {
    return request('/user/set_keyword', {
      method: 'POST',
      body: payload
    })
  },

  recoverPassword(payload) {
    return request('/user/recover_password', {
      method: 'POST',
      body: payload,
      auth: false
    })
  },

  getUserTickets(userId, params = {}) {
    return request(`/tickets/user/${userId}${buildQuery(params)}`)
  },

  getTickets(params = {}) {
    return request(`/tickets${buildQuery(params)}`)
  },

  bookTicket(payload) {
    return request('/ticket', {
      method: 'POST',
      body: payload
    })
  },

  cancelTicket(ticketId) {
    return request(`/ticket/${ticketId}/cancel`, {
      method: 'POST'
    })
  },

  updateTicketStatus(ticketId, payload) {
    return request(`/ticket/${ticketId}/status`, {
      method: 'PATCH',
      body: payload
    })
  },

  getFavorites(userId) {
    return request(`/favorites/${userId}`)
  },

  addFavorite(payload) {
    return request('/favorite', {
      method: 'POST',
      body: payload
    })
  },

  removeFavorite(payload) {
    return request('/favorite/remove', {
      method: 'POST',
      body: payload
    })
  },

  getHalls() {
    return request('/halls', { auth: false })
  },

  createHall(payload) {
    return request('/hall', {
      method: 'POST',
      body: payload
    })
  },

  updateHall(hallId, payload) {
    return request(`/hall/${hallId}`, {
      method: 'PATCH',
      body: payload
    })
  },

  deleteHall(hallId) {
    return request(`/hall/${hallId}`, {
      method: 'DELETE'
    })
  },

  getSessions(params = {}) {
    return request(`/sessions${buildQuery(params)}`, { auth: false })
  },

  createMovie(payload) {
    return request('/movie', {
      method: 'POST',
      body: payload
    })
  },

  updateMovie(movieId, payload) {
    return request(`/movie/${movieId}`, {
      method: 'PATCH',
      body: payload
    })
  },

  deleteMovie(movieId) {
    return request(`/movie/${movieId}`, {
      method: 'DELETE'
    })
  },

  createSession(payload) {
    return request('/session', {
      method: 'POST',
      body: payload
    })
  },

  updateSession(sessionId, payload) {
    return request(`/session/${sessionId}`, {
      method: 'PATCH',
      body: payload
    })
  },

  deleteSession(sessionId) {
    return request(`/session/${sessionId}`, {
      method: 'DELETE'
    })
  }
}
