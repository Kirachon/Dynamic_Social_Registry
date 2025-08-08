import SectionCard from '../components/SectionCard'

export default function QualityPage(){
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Quality Assurance Dashboard</h2>

      <SectionCard title="KEY QUALITY METRICS">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
          <div className="p-2 border rounded">Code Coverage<br/><span className="font-semibold">84%</span></div>
          <div className="p-2 border rounded">Build Status<br/><span className="font-semibold">✓ Passing</span></div>
          <div className="p-2 border rounded">Test Pass Rate<br/><span className="font-semibold">98.2%</span></div>
          <div className="p-2 border rounded">Bugs Found<br/><span className="font-semibold">23 Open</span></div>
          <div className="p-2 border rounded">Tech Debt<br/><span className="font-semibold">4.2%</span></div>
        </div>
      </SectionCard>

      <SectionCard title="TEST EXECUTION MATRIX">
        <table className="w-full text-sm">
          <thead className="text-left text-gov-muted"><tr><th>Test Suite</th><th>Total</th><th>Passed</th><th>Failed</th><th>Skipped</th><th>Duration</th><th>Trend</th></tr></thead>
          <tbody>
            {[
              ['Unit Tests','1,234','1,230','4','0','2m 34s','Improving'],
              ['Integration Tests','456','445','8','3','8m 12s','Stable'],
              ['API Tests','234','232','2','0','5m 45s','Improving'],
              ['UI Tests','189','185','3','1','12m 23s','Degrading'],
              ['Performance Tests','67','65','2','0','15m 10s','Stable'],
              ['Security Tests','45','45','0','0','6m 30s','Improving'],
            ].map(([s,t,p,f,sk,d,tr]) => (
              <tr key={s} className="border-t border-gov-border"><td className="py-1">{s}</td><td>{t}</td><td>{p}</td><td>{f}</td><td>{sk}</td><td>{d}</td><td>{tr}</td></tr>
            ))}
          </tbody>
        </table>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="CODE QUALITY METRICS">
          <ul className="text-sm space-y-1">
            <li>Maintainability: A</li>
            <li>Reliability: B+</li>
            <li>Security: A</li>
            <li>Duplications: 2.3%</li>
            <li>Complexity: Low</li>
          </ul>
        </SectionCard>
        <SectionCard title="PERFORMANCE BENCHMARKS">
          <ul className="text-sm space-y-1">
            <li>Response Time P95: 423ms</li>
            <li>Throughput: 8,234 TPS</li>
            <li>CPU Usage: 45%</li>
            <li>Memory Usage: 62%</li>
            <li>DB Queries: 234/sec | Cache Hit Rate: 92%</li>
          </ul>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="BUG TRACKING">
          <table className="w-full text-sm">
            <thead className="text-left text-gov-muted"><tr><th>ID</th><th>Priority</th><th>Description</th><th>Component</th><th>Status</th></tr></thead>
            <tbody>
              {[
                ['BUG-234','Critical','Payment fails for amounts > 10K','Payment','In Progress'],
                ['BUG-235','High','Search timeout on large datasets','Registry','Open'],
                ['BUG-236','Medium','UI alignment issue on mobile','Frontend','In Review'],
              ].map(([id,p,desc,c,st]) => (
                <tr key={id} className="border-t border-gov-border"><td className="py-1">{id}</td><td>{p}</td><td>{desc}</td><td>{c}</td><td>{st}</td></tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
        <SectionCard title="AUTOMATION COVERAGE">
          <ul className="text-sm space-y-1">
            <li>Automated: 78%</li>
            <li>Manual: 15%</li>
            <li>In Progress: 7%</li>
            <li>Target: 85% automation by Q1 2025</li>
          </ul>
        </SectionCard>
      </div>
    </div>
  )
}

