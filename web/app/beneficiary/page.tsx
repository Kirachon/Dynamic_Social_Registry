import SectionCard from '../components/SectionCard'
import PaymentTable from './PaymentTable'

export default function BeneficiaryPage(){
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">My DSRS Portal</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <SectionCard title="MY HOUSEHOLD">
          <dl className="grid grid-cols-2 gap-2 text-sm">
            <dt className="text-gov-muted">Household ID</dt><dd>HH-2024-123456</dd>
            <dt className="text-gov-muted">Members</dt><dd>5</dd>
            <dt className="text-gov-muted">Address</dt><dd>Brgy 123, QC</dd>
            <dt className="text-gov-muted">Status</dt><dd>Active ●</dd>
            <dt className="text-gov-muted">PMT Score</dt><dd>42.5</dd>
            <dt className="text-gov-muted">Last Update</dt><dd>Dec 15, 2024</dd>
          </dl>
        </SectionCard>
        <SectionCard title="QUICK ACTIONS">
          <div className="flex flex-wrap gap-2">
            {['Update Information','View Documents','Payment History','Apply for Program','Contact Support','Download Reports'].map(x=> (
              <button key={x} className="px-3 py-2 border rounded text-sm hover:bg-gov-bg">{x}</button>
            ))}
          </div>
        </SectionCard>
        <SectionCard title="NOTIFICATIONS" actions={<button className="text-sm px-2 py-1 border rounded">Mark Read</button>}>
          <ul className="text-sm space-y-2">
            <li>🔔 Your 4Ps payment has been processed (Dec 20, 2024 - ₱3,000)</li>
            <li>📋 Annual review scheduled for January 2025</li>
            <li>✓ Profile update successfully completed (Dec 10, 2024)</li>
          </ul>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="ENROLLED PROGRAMS">
          <ul className="text-sm space-y-2">
            <li>✓ 4Ps Program — Active | Next Payment: Jan 15 | Amount: ₱3,000</li>
            <li>✓ PhilHealth — Covered | ID: 12-345678901-2</li>
            <li>⏳ UCT Program — Under Review | Decision: By Dec 30</li>
          </ul>
        </SectionCard>
        <SectionCard title="PAYMENT HISTORY">
          {/* Server component fetch to backend API with fallback */}
          {/* @ts-expect-error Async Server Component */}
          <PaymentTable />
          <div className="mt-2 flex gap-2"><button className="px-3 py-1 border rounded text-sm">View All</button><button className="px-3 py-1 border rounded text-sm">Download Statement</button><button className="px-3 py-1 border rounded text-sm">Report Issue</button></div>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="HOUSEHOLD MEMBERS">
          <ul className="text-sm space-y-1">
            {['Juan Dela Cruz (Head)','Maria Dela Cruz (Spouse)','Jose (Child)','Ana (Child)','Rosa Santos (Dependent)'].map(m=> (
              <li key={m}>👤 {m}</li>
            ))}
          </ul>
          <div className="mt-2 flex gap-2"><button className="px-3 py-1 border rounded text-sm">+ Add Member</button><button className="px-3 py-1 border rounded text-sm">Edit</button></div>
        </SectionCard>
        <SectionCard title="COMPLIANCE REQUIREMENTS">
          <ul className="text-sm space-y-2">
            <li>✓ Health Check-up — Completed Oct 2024</li>
            <li>✓ School Attendance — 85% (Meeting requirement)</li>
            <li>⚠ Family Dev Session — Due by Dec 31, 2024</li>
          </ul>
        </SectionCard>
      </div>
    </div>
  )
}

