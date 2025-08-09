import { Api } from '@/lib/http'

type EligibilityOverview = {
  approved: number
  pending: number
  rejected: number
}

export default async function EligibilitySummary() {
  let data: EligibilityOverview = { approved: 0, pending: 0, rejected: 0 }
  try {
    data = await Api.eligibility.summary()
  } catch {
    // keep defaults
  }
  return (
    <div className="text-sm space-y-1">
      <div>Total Assessments: { (data.approved + data.pending + data.rejected).toLocaleString() }</div>
      <div>Approved {data.approved.toLocaleString()}</div>
      <div>Pending {data.pending.toLocaleString()}</div>
      <div>Rejected {data.rejected.toLocaleString()}</div>
    </div>
  )
}

