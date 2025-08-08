import { fetchJSON } from '@/lib/api'

type EligibilityOverview = {
  approved: number
  pending: number
  rejected: number
  under_review: number
}

export default async function EligibilitySummary() {
  // For now, stub from eligibility service or derive from registry later
  let data: EligibilityOverview = { approved: 89456, pending: 15234, rejected: 10234, under_review: 10508 }
  return (
    <div className="text-sm space-y-1">
      <div>Total Applications: { (data.approved + data.pending + data.rejected + data.under_review).toLocaleString() }</div>
      <div>Approved {data.approved.toLocaleString()}</div>
      <div>Pending {data.pending.toLocaleString()}</div>
      <div>Rejected {data.rejected.toLocaleString()}</div>
      <div>Under Review {data.under_review.toLocaleString()}</div>
    </div>
  )
}

