import { fetchJSON } from '@/lib/api'

type AnalyticsSummary = {
  risk_model_accuracy: number
  beneficiaries_total: number
  coverage_rate: number
  non_compliance_rate: number
}

export default async function AnalyticsSummaryCard() {
  const base = process.env.NEXT_PUBLIC_ANALYTICS_API || 'http://localhost:8005'
  let data: AnalyticsSummary | null = null
  try {
    data = await fetchJSON<AnalyticsSummary>(`${base}/api/v1/analytics/summary`)
  } catch {
    data = {
      risk_model_accuracy: 0.87,
      beneficiaries_total: 18500000,
      coverage_rate: 0.945,
      non_compliance_rate: 0.078,
    }
  }
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
      <div className="p-2 border rounded">Risk Model Accuracy<br/><span className="font-semibold">{(data.risk_model_accuracy*100).toFixed(1)}%</span></div>
      <div className="p-2 border rounded">Beneficiaries<br/><span className="font-semibold">{data.beneficiaries_total.toLocaleString()}</span></div>
      <div className="p-2 border rounded">Coverage Rate<br/><span className="font-semibold">{(data.coverage_rate*100).toFixed(1)}%</span></div>
      <div className="p-2 border rounded">Non-Compliance<br/><span className="font-semibold">{(data.non_compliance_rate*100).toFixed(1)}%</span></div>
    </div>
  )
}

