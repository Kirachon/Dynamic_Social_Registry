import SectionCard from '../components/SectionCard'
import AnalyticsSummaryCard from './AnalyticsSummary'
import LiveSagaChart from './LiveSagaChart'

export default function AnalyticsPage(){
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Analytics & Business Intelligence</h2>

      <SectionCard title="ANALYTICS SUMMARY">
        {/* @ts-expect-error Async Server Component */}
        <AnalyticsSummaryCard />
      </SectionCard>

      <SectionCard title="REAL-TIME SAGA INDICATOR">
        <div className="text-sm">Live metric from Analytics API (via Kong). Refreshes every 15s.</div>
        {/* @ts-expect-error Client Component */}
        <div className="mt-2"><LiveSagaChart /></div>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="DEMOGRAPHIC INSIGHTS">
          <ul className="text-sm space-y-1">
            <li>Age Distribution — 0-17: 35%, 18-35: 28%, 36-50: 22%, 51-65: 10%, 65+: 5%</li>
            <li>Gender Split — Female: 52%, Male: 48%</li>
          </ul>
        </SectionCard>
        <SectionCard title="PROGRAM EFFECTIVENESS MATRIX">
          <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Matrix chart placeholder</div>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="REGIONAL PERFORMANCE SCORECARD">
          <ul className="text-sm space-y-1">
            <li>NCR — Coverage: ████████, Accuracy: ████████, Efficiency: █████████</li>
            <li>III — Coverage: ████████, Accuracy: ████████, Efficiency: ████████</li>
            <li>VII — Coverage: ███████, Accuracy: ████████, Efficiency: ████████</li>
          </ul>
        </SectionCard>
        <SectionCard title="CUSTOM REPORT BUILDER">
          <div className="text-sm space-y-2">
            <div>Select Metrics: [✓] Beneficiaries [✓] Disbursements [ ] Compliance [ ] Efficiency</div>
            <div>Date Range: [Jan 1, 2024] to [Dec 31, 2024]</div>
            <div>Grouping: [By Region ▼] Visualization: [Bar Chart ▼]</div>
            <div><button className="px-3 py-1 border rounded text-sm">Generate Report</button> <button className="px-3 py-1 border rounded text-sm">Save Template</button> <button className="px-3 py-1 border rounded text-sm">Schedule Delivery</button></div>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}

