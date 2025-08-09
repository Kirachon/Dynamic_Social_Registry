import { getToken, getClientToken } from './auth'

export type HttpError = {
  status: number
  message: string
}

const DEFAULT_TIMEOUT = 10000

export async function apiFetch<T>(path: string, init: RequestInit = {}, throughKong = true): Promise<T> {
  const base = throughKong
    ? process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
    : ''
  const url = throughKong ? `${base}${path}` : path

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT)

  // Token resolution (client vs server)
  const token = typeof window === 'undefined' ? getToken() : getClientToken() || getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  try {
    const res = await fetch(url, { ...init, headers, signal: controller.signal, cache: 'no-store' })
    clearTimeout(timeout)

    if (!res.ok) {
      let msg = `HTTP ${res.status}`
      try {
        const body = await res.json()
        msg = body?.detail || body?.message || msg
      } catch {}
      const err: HttpError = { status: res.status, message: msg }
      throw err
    }

    if (res.status === 204) return undefined as unknown as T
    return res.json() as Promise<T>
  } catch (e: any) {
    if (e?.name === 'AbortError') {
      const err: HttpError = { status: 0, message: 'Request timed out' }
      throw err
    }
    if (e?.status) throw e
    const err: HttpError = { status: 0, message: e?.message || 'Network error' }
    throw err
  }
}

export const Api = {
  registry: {
    householdsSummary() { return apiFetch('/registry/api/v1/households/summary') },
    householdsList() { return apiFetch('/registry/api/v1/households') },
    createHousehold(payload: any) { return apiFetch('/registry/api/v1/households', { method: 'POST', body: JSON.stringify(payload) }) },
  },
  eligibility: {
    summary() { return apiFetch('/eligibility/api/v1/summary') },
  },
  payment: {
    payments() { return apiFetch('/payment/api/v1/payments') },
  },
  analytics: {
    summary() { return apiFetch('/analytics/api/v1/analytics/summary') },
  },
}

export function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)) }

export async function poll<T>(fn: () => Promise<T>, intervalMs = 15000, retries = 20, onError?: (e: any) => void): Promise<T> {
  let lastErr: any
  for (let i = 0; i < retries; i++) {
    try {
      const v = await fn()
      return v
    } catch (e) {
      lastErr = e
      if (onError) onError(e)
      await sleep(intervalMs)
    }
  }
  throw lastErr
}

