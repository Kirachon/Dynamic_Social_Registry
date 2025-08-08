import SectionCard from '../components/SectionCard'

export default function FieldPage(){
  return (
    <div className="space-y-4 max-w-md">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">📱 DSRS Field Worker</h2>
        <div className="text-sm text-gov-muted">Region VII - Cebu</div>
      </div>

      <SectionCard title="TODAY'S OVERVIEW (2024-12-20)">
        <ul className="text-sm space-y-1">
          <li>📊 Visits Completed: 8/12</li>
          <li>📊 Registrations: 5</li>
          <li>📊 Verifications: 3</li>
          <li>📊 Distance Traveled: 15.2km</li>
        </ul>
      </SectionCard>

      <SectionCard title="SCHEDULED VISITS">
        <ul className="text-sm space-y-2">
          {[
            ['09:00','Santos Family','Brgy Lahug | New Registration'],
            ['10:30','Reyes Household','Brgy Apas | Verification'],
            ['14:00','Garcia Family','Brgy Kamputhaw | Update'],
          ].map(([t,f,desc]) => (
            <li key={t} className="border rounded p-2">
              <div className="font-medium">⏰ {t} | {f}</div>
              <div className="text-gov-muted">📍 {desc}</div>
              <div className="mt-1 flex gap-2">
                <button className="px-2 py-1 border rounded text-sm">Navigate</button>
                <button className="px-2 py-1 border rounded text-sm">Start Visit</button>
              </div>
            </li>
          ))}
        </ul>
      </SectionCard>

      <SectionCard title="QUICK ACTIONS">
        <div className="grid grid-cols-2 gap-2">
          {['New Registration','Verify Household','Document Upload','Search Beneficiary'].map(a => (
            <button key={a} className="px-3 py-2 border rounded text-sm">{a}</button>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="MAP VIEW">
        <div className="h-48 bg-gov-bg border border-dashed border-gov-border rounded flex items-center justify-center text-gov-muted">Map placeholder</div>
        <div className="mt-2 flex gap-2">
          <button className="px-2 py-1 border rounded text-sm">Full Screen</button>
          <button className="px-2 py-1 border rounded text-sm">List View</button>
        </div>
      </SectionCard>

      <div className="text-sm">OFFLINE MODE: ● Enabled | Last Sync: 2 hours ago <button className="ml-2 px-2 py-1 border rounded text-sm">Sync Now</button></div>

      <nav className="flex justify-between text-sm border-t pt-2">
        <button>Home</button><button>Schedule</button><button>Cases</button><button>Profile</button>
      </nav>
    </div>
  )
}

