import Link from 'next/link'

export default function Home() {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Welcome to DSRS Prototype</h2>
      <p>Choose a dashboard to view:</p>
      <ul className="list-disc ml-6">
        {[
          ['Operations','/operations'],
          ['Executive','/executive'],
          ['Beneficiary','/beneficiary'],
          ['Field','/field'],
          ['Programs','/programs'],
          ['Payments','/payments'],
          ['SOC','/soc'],
          ['Analytics','/analytics'],
          ['Admin','/admin'],
          ['Quality','/quality'],
          ['Mobile Registration','/mobile/registration'],
        ].map(([label, href]) => (
          <li key={href}><Link className="text-gov-primary underline" href={href}>{label}</Link></li>
        ))}
      </ul>
    </div>
  )
}

