export default function Loading({ label = 'Loading...' }: { label?: string }) {
  return (
    <div role="status" aria-live="polite" className="text-sm text-gov-muted animate-pulse">
      {label}
    </div>
  )
}

