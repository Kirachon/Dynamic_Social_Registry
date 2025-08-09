'use client'

import { useEffect, useState } from 'react'
import Loading from '@/components/Loading'
import ErrorState from '@/components/ErrorState'

// Placeholder: Surface gateway/service errors via future endpoint
export default function SecurityMetrics() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string|null>(null)
  const [data, setData] = useState({ blocked: 0, detected: 0, incidents: 0, vulns: 0, compliance: 0 })

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      setError(null)
      try {
        setData({ blocked: 0, detected: 0, incidents: 0, vulns: 0, compliance: 0 })
      } catch (e:any) {
        setError(e?.message || 'Failed to load security metrics')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    const id = setInterval(load, 30000)
    return () => { mounted = false; clearInterval(id) }
  }, [])

  if (loading) return <Loading label="Loading security metrics..." />
  if (error) return <ErrorState label={error} />

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
      <div className="p-2 border rounded">Blocked Attacks<br/><span className="font-semibold">{data.blocked}</span></div>
      <div className="p-2 border rounded">Threats Detected<br/><span className="font-semibold">{data.detected}</span></div>
      <div className="p-2 border rounded">Incidents Active<br/><span className="font-semibold">{data.incidents}</span></div>
      <div className="p-2 border rounded">Vulnerabilities<br/><span className="font-semibold">{data.vulns}</span></div>
      <div className="p-2 border rounded">Compliance Score<br/><span className="font-semibold">{data.compliance}%</span></div>
    </div>
  )
}

