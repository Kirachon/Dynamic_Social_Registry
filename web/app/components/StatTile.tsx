type StatTileProps = {
  label: string
  value: string
  delta?: string
  trend?: 'up' | 'down' | 'flat'
}

export default function StatTile({ label, value, delta, trend = 'flat' }: StatTileProps) {
  const trendSymbol = trend === 'up' ? '▲' : trend === 'down' ? '▼' : '═'
  const trendColor = trend === 'up' ? 'text-gov-success' : trend === 'down' ? 'text-gov-danger' : 'text-gov-muted'
  return (
    <div className="bg-gov-surface shadow-card border border-gov-border rounded p-4">
      <div className="text-xs text-gov-muted">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
      {delta && (
        <div className={`text-xs ${trendColor}`}>{trendSymbol} {delta}</div>
      )}
    </div>
  )
}

