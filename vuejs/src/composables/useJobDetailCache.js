import axios from 'axios';

const cache = new Map();
const inflight = new Map();

export function getCachedJob(jobId) {
  const id = Number(jobId);
  if (!Number.isFinite(id) || id <= 0) return null;
  return cache.get(id) ?? null;
}

export function invalidateJobCache(jobId) {
  const id = Number(jobId);
  if (Number.isFinite(id) && id > 0) {
    cache.delete(id);
    inflight.delete(id);
  }
}

/** Fetch job detail; dedupes concurrent requests and caches results. */
export async function fetchJobDetail(jobId, { force = false } = {}) {
  const id = Number(jobId);
  if (!Number.isFinite(id) || id <= 0) return null;

  if (!force && cache.has(id)) {
    return cache.get(id);
  }

  if (!force && inflight.has(id)) {
    return inflight.get(id);
  }

  const request = axios
    .get(`/api/job-market/jobs/${id}`)
    .then(({ data }) => {
      cache.set(id, data);
      inflight.delete(id);
      return data;
    })
    .catch((err) => {
      inflight.delete(id);
      throw err;
    });

  inflight.set(id, request);
  return request;
}

/** Warm cache on list hover without blocking UI. */
export function prefetchJobDetail(jobId) {
  const id = Number(jobId);
  if (!Number.isFinite(id) || id <= 0) return;
  if (cache.has(id) || inflight.has(id)) return;
  fetchJobDetail(id).catch(() => {});
}
