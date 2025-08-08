import StatTile from '../components/StatTile'
import SectionCard from '../components/SectionCard'

export default function OperationsPage() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">DSRS Operations Center</h2>
        <div className="text-sm text-gov-muted">Last Update: 2024-12-20 14:23:45</div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatTile label="SYSTEM AVAILABILITY" value="99.97%" delta="0.02%" trend="up" />
        <StatTile label="ACTIVE USERS" value="245,892" delta="12.3%" trend="up" />
        <StatTile label="TRANSACTIONS/MIN" value="8,456" delta="5.2%" trend="up" />
        <StatTile label="ERROR RATE" value="0.03%" delta="0.01%" trend="down" />
      </div>

      <SectionCard title="SYSTEM HEALTH MAP">
        <div className="text-sm text-gov-muted">Philippines Regional Status (mock)</div>
        <div className="mt-2 grid grid-cols-4 sm:grid-cols-8 gap-2">
          {['NCR','CAR','I','II','III','IVA','IVB','V','VI','VII','VIII','IX','X','XI','XII','XIII','BARMM'].map((r, i) => (
            <div key={r} className="flex items-center gap-2 text-xs">
              <span className={`inline-block w-2 h-2 rounded-full ${i % 7 === 0 ? 'bg-red-600' : i % 5 === 0 ? 'bg-yellow-500' : 'bg-green-600'}`} aria-hidden />
              <span>{r}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 text-xs">Coverage: <span className="font-semibold">94.5%</span></div>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="SERVICE STATUS">
          <ul className="text-sm space-y-2">
            {['Identity','Registry','Eligibility','Payment','Analytics','Notification','Document','Audit'].map((s, i) => (
              <li key={s} className="flex items-center justify-between">
                <span>{s} Service</span>
                <span className="text-gov-success">[████████●]</span>
              </li>
            ))}
          </ul>
        </SectionCard>
        <SectionCard title="RESPONSE TIME TREND (Last 24 Hours)">
          <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">
            Line chart placeholder
          </div>
        </SectionCard>
      </div>

      <SectionCard title="ALERTS & INCIDENTS" actions={<button className="text-sm px-3 py-1 border rounded">View All</button>}>
        <ul className="text-sm space-y-2">
          <li>⚠ HIGH | 14:15 | Database connection pool reaching limit (Region VII)</li>
          <li>● MEDIUM | 14:02 | Elevated response time in Payment Service</li>
          <li>● LOW | 13:45 | Scheduled maintenance reminder - Region X (Tomorrow 02:00)</li>
        </ul>
      </SectionCard>
    </div>
  )
}

