import { PropsWithChildren } from 'react'

type SectionCardProps = PropsWithChildren<{ title: string; actions?: React.ReactNode }>

export default function SectionCard({ title, actions, children }: SectionCardProps) {
  return (
    <section className="bg-gov-surface shadow-card border border-gov-border rounded">
      <header className="px-4 py-2 border-b border-gov-border flex items-center justify-between">
        <h3 className="font-semibold text-sm">{title}</h3>
        {actions}
      </header>
      <div className="p-4">
        {children}
      </div>
    </section>
  )
}

