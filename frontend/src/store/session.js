import { reactive } from 'vue'

const STORAGE_KEY = 'cinema-space-user'

function isExpired(value) {
  if (!value) {
    return true
  }

  const expiresAt = new Date(value).getTime()
  return Number.isNaN(expiresAt) || expiresAt <= Date.now()
}

function normalizeSession(user) {
  if (!user || isExpired(user.refresh_expires_at)) {
    return null
  }

  return user
}

function readStoredUser() {
  if (typeof window === 'undefined') {
    return null
  }

  const raw = window.localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return null
  }

  try {
    const parsed = JSON.parse(raw)
    const normalized = normalizeSession(parsed)

    if (!normalized) {
      window.localStorage.removeItem(STORAGE_KEY)
      return null
    }

    return normalized
  } catch (error) {
    window.localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

export const sessionState = reactive({
  user: readStoredUser()
})

export function setStoredUser(user) {
  const normalized = normalizeSession(user)
  sessionState.user = normalized

  if (typeof window === 'undefined') {
    return
  }

  if (normalized) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(normalized))
  } else {
    window.localStorage.removeItem(STORAGE_KEY)
  }
}

export function clearStoredUser() {
  sessionState.user = null
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(STORAGE_KEY)
  }
}

export function getStoredUser() {
  const user = readStoredUser()
  if (sessionState.user !== user) {
    sessionState.user = user
  }
  return user
}

export function updateStoredTokens(payload) {
  const currentUser = getStoredUser()
  if (!currentUser) {
    return null
  }

  const updatedUser = {
    ...currentUser,
    ...payload,
  }
  setStoredUser(updatedUser)
  return updatedUser
}

export function isAccessTokenExpired(user = getStoredUser()) {
  if (!user?.access_expires_at) {
    return true
  }

  return isExpired(user.access_expires_at)
}

export function isRefreshTokenExpired(user = getStoredUser()) {
  if (!user?.refresh_expires_at) {
    return true
  }

  return isExpired(user.refresh_expires_at)
}
