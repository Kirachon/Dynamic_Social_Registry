import SectionCard from '../components/SectionCard'

export default function ProgramsPage(){
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Program Management Dashboard</h2>
      <SectionCard title="PROGRAM PORTFOLIO OVERVIEW">
        <table className="w-full text-sm">
          <thead className="text-left text-gov-muted"><tr><th>Program</th><th>Beneficiaries</th><th>Budget</th><th>Disbursed</th><th>Efficiency</th></tr></thead>
          <tbody>
            {[
              ['4Ps','4.4M','₱2.5B','₱2.1B (84%)','████████ 92%'],
              ['UCT','2.8M','₱1.2B','₱980M (82%)','███████ 88%'],
              ['KALAHI-CIDSS','1.5M','₱800M','₱650M (81%)','███████ 85%'],
            ].map(([p,b,bu,d,e]) => (
              <tr key={p} className="border-t border-gov-border"><td className="py-2">{p}</td><td>{b}</td><td>{bu}</td><td>{d}</td><td>{e}</td></tr>
            ))}
          </tbody>
        </table>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="ELIGIBILITY PROCESSING">
          <div className="text-sm space-y-1">
            <div>Total Applications: 125,432</div>
            <div>████████████ Approved 89,456</div>
            <div>████ Pending 15,234</div>
            <div>██ Rejected 10,234</div>
            <div>█ Under Review 10,508</div>
            <div>Avg Processing Time: 3.2 days (▼ 1.5 days)</div>
          </div>
        </SectionCard>
        <SectionCard title="GEOGRAPHIC DISTRIBUTION">
          <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Heat map placeholder</div>
          <div className="text-xs mt-2">Legend: High ▉ Medium ▓ Low ░</div>
        </SectionCard>
      </div>

      <SectionCard title="COMPLIANCE & CONDITIONALITIES TRACKING">
        <ul className="text-sm space-y-2">
          <li>Health Check-ups ████████████████████ 95.2% ✓ Above Target (90%)</li>
          <li>School Attendance ███████████████████ 93.8% ✓ Above Target (85%)</li>
          <li>Family Dev Sessions ████████████ 78.4% ⚠ Below Target (85%)</li>
        </ul>
        <div className="mt-2 text-sm">Non-Compliance Cases: 8,234 <button className="ml-2 px-2 py-1 border rounded text-sm">View Details</button> <button className="px-2 py-1 border rounded text-sm">Generate Report</button></div>
      </SectionCard>

      <SectionCard title="CROSS-PROGRAM ANALYTICS">
        <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Charts placeholder</div>
      </SectionCard>
    </div>
  )
}

