'use client'

import { useEffect, useState } from 'react'
import { Api } from '@/lib/http'
import Loading from '@/components/Loading'
import ErrorState from '@/components/ErrorState'

export default function QualityMetrics() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string|null>(null)
  const [elig, setElig] = useState({ approved:0, pending:0, rejected:0 })
  const [payments, setPayments] = useState<number>(0)

  async function load() {
    setError(null)
    try {
      const [e,p] = await Promise.all([
        Api.eligibility.summary().catch(()=>({approved:0,pending:0,rejected:0})),
        Api.payment.payments().catch(()=>[]),
      ])
      setElig(e as any)
      setPayments((p as any)?.length ?? 0)
    } catch (e:any) {
      setError(e?.message || 'Failed to load quality metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 20000)
    return () => clearInterval(id)
  }, [])

  if (loading) return <Loading label="Loading quality metrics..." />
  if (error) return <ErrorState label={error} />

  const total = elig.approved + elig.pending + elig.rejected
  const rejectionRate = total ? (elig.rejected/total)*100 : 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
      <div className="p-3 border rounded">Assessments<br/><span className="text-2xl font-semibold">{total.toLocaleString()}</span></div>
      <div className="p-3 border rounded">Rejection Rate<br/><span className="text-2xl font-semibold">{rejectionRate.toFixed(1)}%</span></div>
      <div className="p-3 border rounded">Payments<br/><span className="text-2xl font-semibold">{payments.toLocaleString()}</span></div>
    </div>
  )
}

