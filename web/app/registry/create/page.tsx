'use client'

import { useState } from 'react'
import { Api } from '@/lib/http'

const initial = {
  head_of_household_name: '',
  address: '',
  phone_number: '',
  email: '',
  household_size: 1,
  monthly_income: '' as unknown as number | ''
}

type Form = typeof initial

export default function CreateHouseholdPage() {
  const [form, setForm] = useState<Form>(initial)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  function update<K extends keyof Form>(key: K, value: Form[K]) {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  function validate(): string | null {
    if (!form.head_of_household_name.trim()) return 'Head of household name is required.'
    if (!form.address.trim()) return 'Address is required.'
    if (form.household_size && (form.household_size as number) < 1) return 'Household size must be at least 1.'
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return 'Email is invalid.'
    if (form.phone_number && form.phone_number.length > 20) return 'Phone number is too long.'
    return null
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null); setSuccess(null)
    const err = validate()
    if (err) { setError(err); return }
    setSubmitting(true)
    try {
      const payload = {
        head_of_household_name: form.head_of_household_name,
        address: form.address,
        phone_number: form.phone_number || undefined,
        email: form.email || undefined,
        household_size: Number(form.household_size) || 1,
        monthly_income: form.monthly_income === '' ? undefined : Number(form.monthly_income)
      }
      await Api.registry.createHousehold(payload)
      setSuccess('Household created successfully! The saga will process it shortly.')
      setForm(initial)
    } catch (e: any) {
      setError(e?.message || 'Failed to create household.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-4">
      <h2 className="text-xl font-semibold">Register a Household</h2>
      <form onSubmit={onSubmit} className="bg-gov-surface border border-gov-border rounded p-4 space-y-3">
        <div>
          <label className="block text-sm mb-1">Head of Household Name *</label>
          <input className="w-full border rounded p-2" value={form.head_of_household_name} onChange={e => update('head_of_household_name', e.target.value)} required />
        </div>
        <div>
          <label className="block text-sm mb-1">Address *</label>
          <textarea className="w-full border rounded p-2" value={form.address} onChange={e => update('address', e.target.value)} required />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm mb-1">Phone Number</label>
            <input className="w-full border rounded p-2" value={form.phone_number} onChange={e => update('phone_number', e.target.value)} maxLength={20} />
          </div>
          <div>
            <label className="block text-sm mb-1">Email</label>
            <input type="email" className="w-full border rounded p-2" value={form.email} onChange={e => update('email', e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm mb-1">Household Size</label>
            <input type="number" min={1} className="w-full border rounded p-2" value={form.household_size} onChange={e => update('household_size', Number(e.target.value))} />
          </div>
          <div>
            <label className="block text-sm mb-1">Monthly Income (₱)</label>
            <input type="number" min={0} className="w-full border rounded p-2" value={form.monthly_income as any} onChange={e => update('monthly_income', e.target.value === '' ? '' : Number(e.target.value))} />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button disabled={submitting} className="px-4 py-2 rounded bg-gov-primary text-white disabled:opacity-50" type="submit">{submitting ? 'Submitting...' : 'Create Household'}</button>
          {error && <span className="text-sm text-red-600">{error}</span>}
          {success && <span className="text-sm text-gov-success">{success}</span>}
        </div>
      </form>
      <div className="text-sm text-gov-muted">After submission, the Registry service emits an event which triggers Eligibility and Payment. Check the Analytics dashboard for counters.</div>
    </div>
  )
}

