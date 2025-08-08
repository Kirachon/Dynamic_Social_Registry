import { fetchJSON } from '@/lib/api'

type ServiceStatus = { name: string; status: 'up'|'degraded'|'down' }

export default async function ServicesStatus() {
  async function probe(name: string, base: string): Promise<ServiceStatus> {
    try {
      const r = await fetch(`${base}/health`, { cache: 'no-store' })
      if (r.ok) return { name, status: 'up' }
      return { name, status: 'degraded' }
    } catch {
      return { name, status: 'down' }
    }
  }
  const bases: [string, string][] = [
    ['Identity','http://localhost:8001'],
    ['Registry','http://localhost:8002'],
    ['Eligibility','http://localhost:8003'],
    ['Payment','http://localhost:8004'],
    ['Analytics','http://localhost:8005'],
  ]
  const statuses = await Promise.all(bases.map(([n,b]) => probe(n,b)))
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

