import SectionCard from '../components/SectionCard'
import UserSummary from './UserSummary'

export default function AdminPage(){
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">System Administration Console</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="SYSTEM CONFIGURATION">
          <ul className="text-sm space-y-1">
            <li>Environment: PRODUCTION</li>
            <li>Version: 2.5.1</li>
            <li>Database: Primary (Manila)</li>
            <li>Cache: Enabled (Redis)</li>
            <li>Queue: Active (15,234 jobs)</li>
          </ul>
          <div className="mt-2 flex gap-2"><button className="px-2 py-1 border rounded text-sm">Edit Config</button><button className="px-2 py-1 border rounded text-sm">View Logs</button></div>
        </SectionCard>
        <SectionCard title="USER MANAGEMENT">
          {/* @ts-expect-error Client component */}
          <UserSummary />
          <div className="mt-2 flex gap-2"><button className="px-2 py-1 border rounded text-sm">Add User</button><button className="px-2 py-1 border rounded text-sm">Bulk Import</button><button className="px-2 py-1 border rounded text-sm">Export List</button></div>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="DATABASE MANAGEMENT">
          <ul className="text-sm space-y-1">
            <li>Connections: 234/500</li>
            <li>Queries/sec: 1,234 | Slow Queries: 12 | Cache Hit: 94%</li>
            <li>Replication: In Sync</li>
          </ul>
          <div className="mt-2 flex gap-2"><button className="px-2 py-1 border rounded text-sm">Optimize</button><button className="px-2 py-1 border rounded text-sm">Backup</button><button className="px-2 py-1 border rounded text-sm">Restore</button></div>
        </SectionCard>
        <SectionCard title="ROLE PERMISSIONS MATRIX">
          <table className="w-full text-sm">
            <thead className="text-left text-gov-muted"><tr><th>Role</th><th>Users</th><th>Read</th><th>Write</th><th>Admin</th></tr></thead>
            <tbody>
              {[
                ['Super Admin','5','✓','✓','✓'],
                ['Admin','25','✓','✓','✗'],
                ['Manager','150','✓','✓','✗'],
                ['Field Worker','8,234','✓','✓','✗'],
                ['Viewer','4,042','✓','✗','✗'],
              ].map(([role,users,r,w,a]) => (
                <tr key={role} className="border-t border-gov-border"><td className="py-1">{role}</td><td>{users}</td><td>{r}</td><td>{w}</td><td>{a}</td></tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
      </div>

      <SectionCard title="API CONFIGURATION & MONITORING">
        <table className="w-full text-sm">
          <thead className="text-left text-gov-muted"><tr><th>Endpoint</th><th>Status</th><th>Rate Limit</th><th>Calls Today</th><th>Avg Response</th></tr></thead>
          <tbody>
            {[
              ['/api/v1/households','✓','1000/min','456,234','234ms'],
              ['/api/v1/eligibility','✓','500/min','234,567','456ms'],
              ['/api/v1/payments','✓','2000/min','678,901','123ms'],
              ['/api/v1/auth','✓','100/min','123,456','89ms'],
              ['/api/v1/documents','⚠','500/min','45,678','1,234ms'],
            ].map(([ep,st,rl,ct,rt]) => (
              <tr key={ep} className="border-t border-gov-border"><td className="py-1">{ep}</td><td>{st}</td><td>{rl}</td><td>{ct}</td><td>{rt}</td></tr>
            ))}
          </tbody>
        </table>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SectionCard title="SCHEDULED JOBS">
          <table className="w-full text-sm">
            <thead className="text-left text-gov-muted"><tr><th>Job Name</th><th>Next Run</th></tr></thead>
            <tbody>
              {[
                ['Daily Backup','02:00 AM'],['Report Gen','06:00 AM'],['Data Sync','Every 15 min'],['Health Check','Every 5 min'],['Cleanup','03:00 AM']
              ].map(([n,t]) => (
                <tr key={n} className="border-t border-gov-border"><td className="py-1">{n}</td><td>{t}</td></tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
        <SectionCard title="SYSTEM LOGS">
          <div className="text-sm space-y-1">
            <div>2024-12-20 14:23:45 [INFO] User login...</div>
            <div>2024-12-20 14:23:44 [WARN] Slow query...</div>
            <div>2024-12-20 14:23:42 [ERROR] API timeout...</div>
          </div>
          <div className="mt-2 flex gap-2"><button className="px-2 py-1 border rounded text-sm">Filter</button><button className="px-2 py-1 border rounded text-sm">Export</button><button className="px-2 py-1 border rounded text-sm">Clear</button></div>
        </SectionCard>
      </div>
    </div>
  )
}

