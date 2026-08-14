/**
 * Shared in-memory cache for pin preview blob URLs.
 * Kept across card remounts so scroll-back does not re-download.
 */
import axios from 'axios'

const urlByPinId = new Map()
const inflight = new Map()

export function getCachedPinMediaUrl(pinId) {
  const id = Number(pinId)
  if (!Number.isFinite(id) || id <= 0) return null
  return urlByPinId.get(id) ?? null
}

export async function fetchPinMediaUrl(pinId) {
  const id = Number(pinId)
  if (!Number.isFinite(id) || id <= 0) return null

  if (urlByPinId.has(id)) return urlByPinId.get(id)
  if (inflight.has(id)) return inflight.get(id)

  const request = axios
    .get(`/api/pins/upload/${id}`, { responseType: 'blob' })
    .then((res) => {
      const url = URL.createObjectURL(res.data)
      urlByPinId.set(id, url)
      inflight.delete(id)
      return url
    })
    .catch((err) => {
      inflight.delete(id)
      throw err
    })

  inflight.set(id, request)
  return request
}
