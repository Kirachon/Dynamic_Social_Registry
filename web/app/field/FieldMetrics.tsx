'use client'

import { useEffect, useState } from 'react'
import { Api } from '@/lib/http'
import Loading from '@/components/Loading'
import ErrorState from '@/components/ErrorState'

export default function FieldMetrics() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string|null>(null)
  const [households, setHouseholds] = useState<number>(0)
  const [eligibility, setEligibility] = useState<{approved:number; pending:number; rejected:number}>({approved:0,pending:0,rejected:0})
  const [payments, setPayments] = useState<number>(0)

  async function load() {
    setError(null)
    try {
      const [reg, elig, pay] = await Promise.all([
        Api.registry.householdsSummary().catch(()=>({ total:0 })),
        Api.eligibility.summary().catch(()=>({ approved:0,pending:0,rejected:0 })),
        Api.payment.payments().catch(()=>[]),
      ])
      setHouseholds((reg as any)?.total ?? 0)
      setEligibility(elig as any)
      setPayments((pay as any)?.length ?? 0)
    } catch (e:any) {
      setError(e?.message || 'Failed to load field metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 15000)
    return () => clearInterval(id)
  }, [])

  if (loading) return <Loading label="Loading field metrics..." />
  if (error) return <ErrorState label={error} />

  const totalAssessments = eligibility.approved + eligibility.pending + eligibility.rejected
  const approvalRate = totalAssessments ? (eligibility.approved/totalAssessments)*100 : 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
      <div className="p-3 border rounded">Households Registered<br/><span className="text-2xl font-semibold">{households.toLocaleString()}</span></div>
      <div className="p-3 border rounded">Approval Rate<br/><span className="text-2xl font-semibold">{approvalRate.toFixed(1)}%</span></div>
      <div className="p-3 border rounded">Payments (All)<br/><span className="text-2xl font-semibold">{payments.toLocaleString()}</span></div>
    </div>
  )
}

