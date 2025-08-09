'use client'

import { signIn, signOut, useSession } from 'next-auth/react'

export default function AuthButtons() {
  const { data: session } = useSession()
  if (session) {
    return (
      <div className="flex items-center gap-2 text-sm">
        <span className="text-gov-muted">Signed in</span>
        <button className="px-3 py-1 border rounded" onClick={() => signOut({ callbackUrl: '/' })}>Logout</button>
      </div>
    )
  }
  return (
    <div className="flex items-center gap-2 text-sm">
      <button className="px-3 py-1 border rounded" onClick={() => signIn('keycloak')}>Login</button>
    </div>
  )
}

