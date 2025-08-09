'use client'

import { useState } from 'react'
import { setToken, clearToken } from '@/lib/auth'

export default function LoginPage() {
  const [jwt, setJwt] = useState('')
  const [info, setInfo] = useState<string | null>(null)

  function onLogin(e: React.FormEvent) {
    e.preventDefault()
    if (!jwt) return setInfo('Provide a JWT to continue.')
    setToken(jwt)
    setInfo('Token saved. You can now access protected APIs via Kong.')
  }

  function onUseDev() {
    const dev = process.env.NEXT_PUBLIC_DEV_MODE ? (process.env.DEV_JWT || '') : ''
    if (!dev) { setInfo('No DEV_JWT configured.'); return }
    setToken(dev)
    setInfo('Development token saved.')
  }

  return (
    <div className="max-w-lg space-y-4">
      <h2 className="text-xl font-semibold">Login (JWT)</h2>
      <p className="text-sm text-gov-muted">Paste a JWT issued by your IdP (e.g., Keycloak). For local dev, you may use a DEV_JWT if configured.</p>
      <form onSubmit={onLogin} className="space-y-2">
        <textarea className="w-full border rounded p-2 h-40" value={jwt} onChange={e => setJwt(e.target.value)} placeholder="Paste JWT here..." />
        <div className="flex gap-2">
          <button className="px-3 py-2 rounded bg-gov-primary text-white" type="submit">Save Token</button>
          <button className="px-3 py-2 rounded border" type="button" onClick={onUseDev}>Use DEV_JWT</button>
          <button className="px-3 py-2 rounded border" type="button" onClick={() => { clearToken(); setInfo('Token cleared.') }}>Clear</button>
        </div>
      </form>
      {info && <div className="text-sm text-gov-muted">{info}</div>}
    </div>
  )
}

