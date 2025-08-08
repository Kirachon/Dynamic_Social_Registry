import SectionCard from '../components/SectionCard'

export default function PaymentsPage(){
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Payment Operations Center</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="TODAY'S PAYMENT SUMMARY">
          <ul className="text-sm space-y-1">
            <li>Total Transactions: 45,892</li>
            <li>Total Amount: ₱142.5M</li>
            <li>Success Rate: 99.2%</li>
            <li>Failed: 367 | Pending: 1,245 | Average Time: 2.3s</li>
          </ul>
        </SectionCard>
        <SectionCard title="PAYMENT CHANNELS">
          <ul className="text-sm space-y-1">
            <li>LandBank ████████ 35,234</li>
            <li>GCash ██████ 28,456</li>
            <li>PayMaya ████ 15,234</li>
            <li>Cash Pickup ██ 8,123</li>
            <li>Bank Transfer █ 3,456</li>
          </ul>
        </SectionCard>
      </div>

      <SectionCard title="REAL-TIME TRANSACTION FLOW">
        <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Area chart placeholder (current: 584 TPS)</div>
        <div className="mt-2 text-sm">[⚡ Live] [1H] [6H] [1D] [1W]</div>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="RECONCILIATION STATUS">
          <ul className="text-sm space-y-1">
            <li>Matched: 42,345 (98.2%)</li>
            <li>Unmatched: 623 (1.4%)</li>
            <li>Under Review: 156 (0.4%)</li>
          </ul>
          <div className="mt-2 flex gap-2"><button className="px-2 py-1 border rounded text-sm">Resolve Unmatched</button><button className="px-2 py-1 border rounded text-sm">Export</button></div>
        </SectionCard>
        <SectionCard title="FRAUD DETECTION ALERTS">
          <ul className="text-sm space-y-1">
            <li>🔴 Duplicate payment attempt - ID: TXN789012</li>
            <li>🔴 Unusual pattern detected - Batch: B456</li>
            <li>🟡 Location anomaly - 3 transactions</li>
            <li>🟡 Velocity check warning - 2 beneficiaries</li>
          </ul>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="SETTLEMENT SUMMARY">
          <ul className="text-sm space-y-1">
            <li>Ready for Settlement: ₱125.8M</li>
            <li>Settled Today: ₱118.2M</li>
            <li>Pending Settlement: ₱7.6M</li>
            <li>Hold for Review: ₱2.1M</li>
          </ul>
        </SectionCard>
        <SectionCard title="PAYMENT BATCH QUEUE">
          <table className="w-full text-sm">
            <thead className="text-left text-gov-muted"><tr><th>Batch ID</th><th>Recipients</th><th>Amount</th><th>Status</th></tr></thead>
            <tbody>
              {[
                ['B2024-1220','5,234','₱15.7M','⏳ Queue'],
                ['B2024-1219','8,456','₱25.4M','▶ Active'],
                ['B2024-1218','12,345','₱37.1M','✓ Done'],
              ].map(([id,rec,amount,status]) => (
                <tr key={id} className="border-t border-gov-border"><td className="py-1">{id}</td><td>{rec}</td><td>{amount}</td><td>{status}</td></tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
      </div>
    </div>
  )
}

