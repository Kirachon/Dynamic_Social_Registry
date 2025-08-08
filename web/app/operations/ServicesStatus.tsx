import { fetchJSON } from '@/lib/api'

type ServiceStatus = { name: string; status: 'up'|'degraded'|'down' }

export default async function ServicesStatus() {
  // Derive from registry/analytics later; stub request failure fallback
  let statuses: ServiceStatus[] = [
    { name: 'Identity', status: 'up' },
    { name: 'Registry', status: 'up' },
    { name: 'Eligibility', status: 'up' },
    { name: 'Payment', status: 'degraded' },
    { name: 'Analytics', status: 'up' },
  ]
  return (
    <ul className="text-sm space-y-2">
      {statuses.map(s => (
        <li key={s.name} className="flex items-center justify-between">
          <span>{s.name} Service</span>
          <span className={s.status==='up'?'text-gov-success':s.status==='degraded'?'text-yellow-600':'text-gov-danger'}>
            {s.status==='up'?'[████████●]': s.status==='degraded'?'[███●    ]':'[●       ]'}
          </span>
        </li>
      ))}
    </ul>
  )
}

