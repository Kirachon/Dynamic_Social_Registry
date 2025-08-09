'use client'

import { useEffect, useState } from 'react'
import LineChart from '@/components/LineChart'

export default function LiveSagaChart() {
  const [labels, setLabels] = useState<string[]>([])
  const [values, setValues] = useState<number[]>([])

  useEffect(() => {
    let mounted = true
    const base = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
    async function tick() {
      try {
        const res = await fetch(`${base}/analytics/api/v1/analytics/summary`, { cache: 'no-store' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        const now = new Date()
        if (!mounted) return
        setLabels(prev => [...prev.slice(-29), now.toLocaleTimeString()])
        setValues(prev => [...prev.slice(-29), json.beneficiaries_total ?? 0])
      } catch (e) {
        // swallow errors during polling
      }
    }
    const id = setInterval(tick, 15000)
    tick()
    return () => { mounted = false; clearInterval(id) }
  }, [])

  return <LineChart labels={labels} seriesLabel="Beneficiaries (total)" data={values} />
}

