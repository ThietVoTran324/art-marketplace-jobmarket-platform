import axios from 'axios'

let refreshPromise = null
let sessionExpiredNotified = false
const listeners = new Set()

export function onSessionExpired(fn) {
  listeners.add(fn)
  return () => listeners.delete(fn)
}

export function resetSessionExpiredFlag() {
  sessionExpiredNotified = false
}

function notifySessionExpired() {
  if (sessionExpiredNotified) return
  sessionExpiredNotified = true
  listeners.forEach((fn) => {
    try {
      fn()
    } catch (e) {
      console.error(e)
    }
  })
}

function isExpiredTokenError(error) {
  const status = error?.response?.status
  const detail = error?.response?.data?.detail
  return status === 403 && typeof detail === 'string' && /token has expired/i.test(detail)
}

function shouldSkipRefresh(config) {
  const url = config?.url || ''
  return (
    url.includes('/users/refresh_token') ||
    url.includes('/users/login') ||
    url.includes('/users/signup') ||
    url.includes('/users/register') ||
    url.includes('/users/csrf')
  )
}

function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = axios
      .get('/api/users/refresh_token', { withCredentials: true })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

export function installAuthRefreshInterceptor(client) {
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const config = error.config
      const status = error?.response?.status
      const detail = error?.response?.data?.detail
      const canRefresh =
        config && !config._retry && !shouldSkipRefresh(config) && isExpiredTokenError(error)

      if (canRefresh) {
        try {
          await refreshAccessToken()
          config._retry = true
          return client(config)
        } catch (refreshErr) {
          notifySessionExpired()
          const refreshStatus = refreshErr?.response?.status
          const refreshDetail = refreshErr?.response?.data?.detail
          console.error('[API]', refreshStatus, refreshDetail ?? refreshErr.message, config?.url)
          return Promise.reject(refreshErr)
        }
      }

      if (status >= 400) {
        console.error('[API]', status, detail ?? error.message, config?.url)
      }
      return Promise.reject(error)
    }
  )
}
