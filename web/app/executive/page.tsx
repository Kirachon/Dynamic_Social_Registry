import SectionCard from '../components/SectionCard'
import StatTile from '../components/StatTile'

export default function ExecutivePage(){
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">DSRS Executive Dashboard</h2>
        <div className="text-sm text-gov-muted">Period: Q4 2024</div>
      </div>

      <SectionCard title="KEY PERFORMANCE INDICATORS">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatTile label="BENEFICIARIES" value="18.5M / 20M" delta="▲ 1.2M" trend="up" />
          <StatTile label="PROGRAMS ACTIVE" value="12 / 15" delta="▲ 2" trend="up" />
          <StatTile label="DISBURSEMENTS" value="₱4.2B / ₱5B" delta="▲ ₱500M" trend="up" />
          <StatTile label="COST/TRANSACTION" value="₱42 / ₱50" delta="▼ ₱3" trend="down" />
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="STRATEGIC OBJECTIVES STATUS">
          <ul className="text-sm space-y-2">
            {[
              ['Digital Transformation', '78%'],
              ['Coverage Expansion', '92%'],
              ['Cost Optimization', '85%'],
              ['Service Excellence', '71%'],
              ['Partnership Development', '66%'],
            ].map(([k,v])=> (
              <li key={k} className="flex items-center justify-between"><span>{k}</span><span>████ {v}</span></li>
            ))}
          </ul>
        </SectionCard>
        <SectionCard title="QUARTERLY TRENDS">
          <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Trend charts placeholder</div>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="REGIONAL PERFORMANCE MATRIX">
          <table className="w-full text-sm">
            <thead className="text-left text-gov-muted">
              <tr><th>Region</th><th>Coverage</th><th>Accuracy</th></tr>
            </thead>
            <tbody>
              {[
                ['NCR','95.2%','98.1%'],
                ['Region III','93.8%','97.5%'],
                ['Region VII','91.4%','96.9%'],
              ].map(([r,c,a]) => (
                <tr key={r} className="border-t border-gov-border">
                  <td className="py-2">{r}</td>
                  <td>{c}</td>
                  <td>{a}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
        <SectionCard title="BUDGET UTILIZATION">
          <div className="text-sm space-y-2">
            <div>Development ████████████ ₱1.2B/1.5B</div>
            <div>Operations ████████ ₱800M/1B</div>
            <div>Infrastructure █████████ ₱450M/500M</div>
            <div>Training ███████ ₱180M/200M</div>
            <div>Contingency ██ ₱20M/100M</div>
            <div className="font-semibold">Total: ₱2.65B / ₱3.3B (80.3%)</div>
          </div>
        </SectionCard>
      </div>

      <SectionCard title="EXECUTIVE ACTIONS REQUIRED">
        <ul className="text-sm space-y-2">
          <li>⚠ Budget approval needed for Q1 2025 infrastructure expansion</li>
          <li>⚠ Partnership agreement with DOH pending signature</li>
          <li>✓ Monthly steering committee meeting scheduled for Dec 25</li>
        </ul>
      </SectionCard>
    </div>
  )
}

