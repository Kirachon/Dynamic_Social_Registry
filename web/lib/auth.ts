import { cookies } from 'next/headers'

// Simple token store utilizing next/headers cookies API
export function getToken() {
  const jar = cookies()
  const t = jar.get('dsrs_token')?.value
  return t || process.env.DEV_JWT || null
}

export function setToken(token: string) {
  // In Next server actions you can set cookies; for client, we use localStorage fallback
  if (typeof document !== 'undefined') {
    localStorage.setItem('dsrs_token', token)
    document.cookie = `dsrs_token=${token}; path=/; SameSite=Lax`
  }
}

export function clearToken() {
  if (typeof document !== 'undefined') {
    localStorage.removeItem('dsrs_token')
    document.cookie = 'dsrs_token=; Max-Age=0; path=/;'
  }
}

export function getClientToken(): string | null {
  if (typeof document === 'undefined') return null
  const ls = localStorage.getItem('dsrs_token')
  return ls || null
}

