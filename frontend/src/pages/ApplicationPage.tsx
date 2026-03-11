import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createApplication, triggerUnderwrite } from '../api'
import type { ApplicationFormData } from '../types'

const initial: ApplicationFormData = {
  business_name: '',
  industry: '',
  state: '',
  years_in_business: '',
  annual_revenue: '',
  is_startup: false,
  fico_score: '',
  paynet_score: '',
  transunion_score: '',
  loan_amount: '',
  equipment_type: '',
  equipment_year: '',
  equipment_mileage: '',
  has_bankruptcy: false,
  has_judgments: false,
  has_repossessions: false,
  has_tax_liens: false,
  is_us_citizen: true,
}

const inputClass =
  'w-full bg-[#0f1117] border border-[#2a2d3e] rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors'
const labelClass = 'block text-sm font-medium text-slate-300 mb-1'

export default function ApplicationPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<ApplicationFormData>(initial)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function setField<K extends keyof ApplicationFormData>(key: K, value: ApplicationFormData[K]) {
    setForm(f => ({ ...f, [key]: value }))
  }

  function numField(key: keyof ApplicationFormData) {
    return {
      type: 'number' as const,
      value: form[key] as number | '',
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setField(key, e.target.value === '' ? '' : Number(e.target.value)),
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Strip empty string fields → undefined for optional numbers
      const payload = {
        business_name: form.business_name,
        industry: form.industry || undefined,
        state: form.state || undefined,
        years_in_business: form.years_in_business !== '' ? Number(form.years_in_business) : undefined,
        annual_revenue: form.annual_revenue !== '' ? Number(form.annual_revenue) : undefined,
        is_startup: form.is_startup,
        fico_score: form.fico_score !== '' ? Number(form.fico_score) : undefined,
        paynet_score: form.paynet_score !== '' ? Number(form.paynet_score) : undefined,
        transunion_score: form.transunion_score !== '' ? Number(form.transunion_score) : undefined,
        loan_amount: form.loan_amount !== '' ? Number(form.loan_amount) : undefined,
        equipment_type: form.equipment_type || undefined,
        equipment_year: form.equipment_year !== '' ? Number(form.equipment_year) : undefined,
        equipment_mileage: form.equipment_mileage !== '' ? Number(form.equipment_mileage) : undefined,
        has_bankruptcy: form.has_bankruptcy,
        has_judgments: form.has_judgments,
        has_repossessions: form.has_repossessions,
        has_tax_liens: form.has_tax_liens,
        is_us_citizen: form.is_us_citizen,
      }

      const app = await createApplication(payload)
      const results = await triggerUnderwrite(app.id)
      navigate('/results', { state: { results, businessName: form.business_name } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">New Loan Application</h1>
        <p className="text-slate-400 mt-1">Submit an application to match against lender credit policies.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Business Info */}
        <section className="bg-[#1a1d2e] rounded-xl border border-[#2a2d3e] p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Business Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className={labelClass}>Business Name <span className="text-red-400">*</span></label>
              <input
                required
                className={inputClass}
                placeholder="Acme Equipment LLC"
                value={form.business_name}
                onChange={e => setField('business_name', e.target.value)}
              />
            </div>
            <div>
              <label className={labelClass}>Industry <span className="text-red-400">*</span></label>
              <input
                required
                className={inputClass}
                placeholder="Construction"
                value={form.industry}
                onChange={e => setField('industry', e.target.value)}
              />
            </div>
            <div>
              <label className={labelClass}>State <span className="text-red-400">*</span></label>
              <input
                required
                maxLength={2}
                className={inputClass}
                placeholder="TX"
                value={form.state}
                onChange={e => setField('state', e.target.value.toUpperCase())}
              />
            </div>
            <div>
              <label className={labelClass}>Years in Business <span className="text-red-400">*</span></label>
              <input required className={inputClass} placeholder="5" {...numField('years_in_business')} />
            </div>
            <div>
              <label className={labelClass}>Annual Revenue ($) <span className="text-red-400">*</span></label>
              <input required className={inputClass} placeholder="500000" {...numField('annual_revenue')} />
            </div>
            <div className="col-span-2 flex items-center gap-3 mt-1">
              <input
                type="checkbox"
                id="is_startup"
                className="w-4 h-4 accent-indigo-500"
                checked={form.is_startup}
                onChange={e => setField('is_startup', e.target.checked)}
              />
              <label htmlFor="is_startup" className="text-sm text-slate-300">This is a startup (less than 2 years)</label>
            </div>
          </div>
        </section>

        {/* Credit Scores */}
        <section className="bg-[#1a1d2e] rounded-xl border border-[#2a2d3e] p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Credit Scores</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className={labelClass}>FICO Score <span className="text-red-400">*</span></label>
              <input required className={inputClass} placeholder="720" {...numField('fico_score')} />
            </div>
            <div>
              <label className={labelClass}>PayNet Score <span className="text-slate-500">(optional)</span></label>
              <input className={inputClass} placeholder="—" {...numField('paynet_score')} />
            </div>
            <div>
              <label className={labelClass}>TransUnion Score <span className="text-slate-500">(optional)</span></label>
              <input className={inputClass} placeholder="—" {...numField('transunion_score')} />
            </div>
          </div>
        </section>

        {/* Loan Details */}
        <section className="bg-[#1a1d2e] rounded-xl border border-[#2a2d3e] p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Loan Details</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Loan Amount ($) <span className="text-red-400">*</span></label>
              <input required className={inputClass} placeholder="75000" {...numField('loan_amount')} />
            </div>
            <div>
              <label className={labelClass}>Equipment Type <span className="text-red-400">*</span></label>
              <input
                required
                className={inputClass}
                placeholder="Semi Truck"
                value={form.equipment_type}
                onChange={e => setField('equipment_type', e.target.value)}
              />
            </div>
            <div>
              <label className={labelClass}>Equipment Year <span className="text-red-400">*</span></label>
              <input required className={inputClass} placeholder="2020" {...numField('equipment_year')} />
            </div>
            <div>
              <label className={labelClass}>Equipment Mileage <span className="text-slate-500">(optional)</span></label>
              <input className={inputClass} placeholder="—" {...numField('equipment_mileage')} />
            </div>
          </div>
        </section>

        {/* Background Flags */}
        <section className="bg-[#1a1d2e] rounded-xl border border-[#2a2d3e] p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Background</h2>
          <div className="grid grid-cols-2 gap-3">
            {(
              [
                ['has_bankruptcy', 'Bankruptcy history'],
                ['has_judgments', 'Judgments'],
                ['has_repossessions', 'Repossessions'],
                ['has_tax_liens', 'Tax liens'],
              ] as const
            ).map(([key, label]) => (
              <div key={key} className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id={key}
                  className="w-4 h-4 accent-indigo-500"
                  checked={form[key]}
                  onChange={e => setField(key, e.target.checked)}
                />
                <label htmlFor={key} className="text-sm text-slate-300">{label}</label>
              </div>
            ))}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="is_us_citizen"
                className="w-4 h-4 accent-indigo-500"
                checked={form.is_us_citizen}
                onChange={e => setField('is_us_citizen', e.target.checked)}
              />
              <label htmlFor="is_us_citizen" className="text-sm text-slate-300">US Citizen / Permanent Resident</label>
            </div>
          </div>
        </section>

        {error && (
          <div className="bg-red-900/30 border border-red-500/50 text-red-300 rounded-lg px-4 py-3 text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Spinner />
              Running Underwrite...
            </>
          ) : (
            'Submit Application'
          )}
        </button>
      </form>
    </div>
  )
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  )
}
