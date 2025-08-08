import SectionCard from '../components/SectionCard'

export default function SocPage(){
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Security Operations Center (SOC)</h2>

      <SectionCard title="KEY SECURITY METRICS">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
          <div className="p-2 border rounded">Blocked Attacks<br/><span className="font-semibold">1,245</span></div>
          <div className="p-2 border rounded">Threats Detected<br/><span className="font-semibold">89</span></div>
          <div className="p-2 border rounded">Incidents Active<br/><span className="font-semibold">3</span></div>
          <div className="p-2 border rounded">Vulnerabilities<br/><span className="font-semibold">12</span></div>
          <div className="p-2 border rounded">Compliance Score<br/><span className="font-semibold">94%</span></div>
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="THREAT MAP - REAL-TIME ATTACK ORIGINS">
          <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Threat map placeholder</div>
        </SectionCard>
        <SectionCard title="SECURITY EVENTS TIMELINE">
          <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Activity chart placeholder</div>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="ACTIVE INCIDENTS">
          <table className="w-full text-sm">
            <thead className="text-left text-gov-muted"><tr><th>ID</th><th>Priority</th><th>Description</th><th>Assigned To</th><th>Status</th></tr></thead>
            <tbody>
              {[
                ['INC-123','HIGH','Suspicious API access pattern','Team Alpha','Investigating'],
                ['INC-124','MEDIUM','Failed login spike from Region V','Team Beta','Monitoring'],
                ['INC-125','LOW','Certificate expiry warning','DevOps','Scheduled'],
              ].map(([id,p,desc,ass,st]) => (
                <tr key={id} className="border-t border-gov-border"><td className="py-1">{id}</td><td>{p}</td><td>{desc}</td><td>{ass}</td><td>{st}</td></tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
        <SectionCard title="COMPLIANCE & AUDIT">
          <ul className="text-sm space-y-1">
            <li>PCI DSS: 98% Compliant</li>
            <li>ISO 27001: 95% Compliant</li>
            <li>Data Privacy: 96% Compliant</li>
            <li>NIST Framework: 92% Compliant</li>
            <li>Next Audit: January 15, 2025</li>
          </ul>
        </SectionCard>
      </div>
    </div>
  )
}

