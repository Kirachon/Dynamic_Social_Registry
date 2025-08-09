'use client'

import { useEffect, useState } from 'react'
import ErrorState from '@/components/ErrorState'
import Loading from '@/components/Loading'

export default function UserSummary() {
  // Placeholder for Keycloak Admin API integration (OSS); for now, show session-derived counts or static until backend endpoint exists.
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string|null>(null)
  const [data, setData] = useState({ totalUsers: 0, activeSessions: 0, locked: 0, pending: 0 })

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      setError(null)
      try {
        // TODO: Integrate Keycloak Admin API (open source) with service account if desired
        setData({ totalUsers: 0, activeSessions: 0, locked: 0, pending: 0 })
      } catch (e:any) {
        setError(e?.message || 'Failed to load users')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    const id = setInterval(load, 30000)
    return () => { mounted = false; clearInterval(id) }
  }, [])

  if (loading) return <Loading label="Loading users..." />
  if (error) return <ErrorState label={error} />

  return (
    <ul className="text-sm space-y-1">
      <li>Total Users: {data.totalUsers} | Active Sessions: {data.activeSessions} | Locked: {data.locked} | Pending: {data.pending}</li>
    </ul>
  )
}

