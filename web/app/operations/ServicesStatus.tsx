type ServiceStatus = { name: string; status: 'up'|'degraded'|'down' }

export default async function ServicesStatus() {
  async function probe(name: string, path: string): Promise<ServiceStatus> {
    try {
      const base = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
      const r = await fetch(`${base}${path}`, { cache: 'no-store' })
      if (r.ok) return { name, status: 'up' }
      return { name, status: 'degraded' }
    } catch {
      return { name, status: 'down' }
    }
  }
  const paths: [string, string][] = [
    ['Identity','/identity/health'],
    ['Registry','/registry/health'],
    ['Eligibility','/eligibility/health'],
    ['Payment','/payment/health'],
    ['Analytics','/analytics/health'],
  ]
  const statuses = await Promise.all(paths.map(([n,p]) => probe(n,p)))
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

