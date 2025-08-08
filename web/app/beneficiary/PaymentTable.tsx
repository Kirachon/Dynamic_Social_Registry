import { fetchJSON } from '@/lib/api'

type Payment = { id: string; beneficiary_id: string; amount: number; status: string }

export default async function PaymentTable() {
  const base = process.env.NEXT_PUBLIC_PAYMENT_API || 'http://localhost:8004'
  let rows: Payment[] = []
  try {
    rows = await fetchJSON<Payment[]>(`${base}/api/v1/payments`)
  } catch (e) {
    // Fallback to demo data if backend unavailable
    rows = [
      { id: 'P1', beneficiary_id: 'B1', amount: 3000, status: 'Completed' },
      { id: 'P2', beneficiary_id: 'B1', amount: 3000, status: 'Completed' },
    ]
  }
  return (
    <table className="w-full text-sm">
      <thead className="text-left text-gov-muted"><tr><th>ID</th><th>Amount</th><th>Status</th></tr></thead>
      <tbody>
        {rows.map(r => (
          <tr key={r.id} className="border-t border-gov-border"><td className="py-1">{r.id}</td><td>₱{r.amount.toLocaleString()}</td><td>{r.status}</td></tr>
        ))}
      </tbody>
    </table>
  )
}

