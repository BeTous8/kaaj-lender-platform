import { useState, useEffect } from 'react'
import { getLenders, updateRule, deleteRule, addRule } from '../api'
import type { Lender, Program, PolicyRule } from '../types'
import type { RulePayload } from '../api'

const OPERATORS = ['gte', 'lte', 'gt', 'lt', 'equals', 'not_in', 'in'] as const

const inputClass =
  'bg-[#0f1117] border border-[#2a2d3e] rounded-md px-2 py-1 text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors'

export default function PoliciesPage() {
  const [lenders, setLenders] = useState<Lender[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getLenders()
      .then(data => {
        setLenders(data)
        if (data.length > 0) setSelectedId(data[0].id)
      })
      .catch(() => setError('Failed to load lenders.'))
      .finally(() => setLoading(false))
  }, [])

  const selected = lenders.find(l => l.id === selectedId) ?? null

  function updateLenderLocally(updated: Lender) {
    setLenders(ls => ls.map(l => (l.id === updated.id ? updated : l)))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32 text-slate-400">
        <svg className="animate-spin h-6 w-6 mr-3" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Loading lenders…
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <p className="text-red-400">{error}</p>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-61px)]">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 border-r border-[#2a2d3e] bg-[#1a1d2e] overflow-y-auto">
        <div className="p-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3">Lenders</p>
          <ul className="space-y-1">
            {lenders.map(lender => (
              <li key={lender.id}>
                <button
                  onClick={() => setSelectedId(lender.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    lender.id === selectedId
                      ? 'bg-indigo-600 text-white font-medium'
                      : 'text-slate-300 hover:bg-[#2a2d3e] hover:text-white'
                  }`}
                >
                  {lender.name}
                  <span
                    className={`ml-2 text-xs ${lender.id === selectedId ? 'text-indigo-200' : 'text-slate-500'}`}
                  >
                    {lender.programs.length}p
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto p-6">
        {selected ? (
          <LenderDetail lender={selected} onUpdate={updateLenderLocally} />
        ) : (
          <p className="text-slate-500 mt-20 text-center">Select a lender</p>
        )}
      </main>
    </div>
  )
}

function LenderDetail({
  lender,
  onUpdate,
}: {
  lender: Lender
  onUpdate: (updated: Lender) => void
}) {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">{lender.name}</h1>
        {lender.notes && <p className="text-slate-400 text-sm mt-1">{lender.notes}</p>}
        <div className="flex items-center gap-2 mt-2">
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              lender.is_active ? 'bg-emerald-900/40 text-emerald-400' : 'bg-slate-700 text-slate-400'
            }`}
          >
            {lender.is_active ? 'Active' : 'Inactive'}
          </span>
          <span className="text-xs text-slate-600">{lender.slug}</span>
        </div>
      </div>

      <div className="space-y-6">
        {lender.programs.map(program => (
          <ProgramSection
            key={program.id}
            program={program}
            lender={lender}
            onUpdate={onUpdate}
          />
        ))}
      </div>
    </div>
  )
}

function ProgramSection({
  program,
  lender,
  onUpdate,
}: {
  program: Program
  lender: Lender
  onUpdate: (updated: Lender) => void
}) {
  const [addingRule, setAddingRule] = useState(false)
  const [addForm, setAddForm] = useState<RulePayload>({
    field_name: '',
    operator: 'gte',
    value: '',
    is_hard_stop: false,
    description: '',
  })
  const [addError, setAddError] = useState<string | null>(null)
  const [addLoading, setAddLoading] = useState(false)

  function setAddField<K extends keyof RulePayload>(key: K, value: RulePayload[K]) {
    setAddForm(f => ({ ...f, [key]: value }))
  }

  async function handleAddRule() {
    if (!addForm.field_name || !addForm.value) {
      setAddError('Field name and value are required.')
      return
    }
    setAddError(null)
    setAddLoading(true)
    try {
      const newRule = await addRule(program.id, addForm)
      const updatedLender: Lender = {
        ...lender,
        programs: lender.programs.map(p =>
          p.id === program.id ? { ...p, policy_rules: [...p.policy_rules, newRule] } : p
        ),
      }
      onUpdate(updatedLender)
      setAddForm({ field_name: '', operator: 'gte', value: '', is_hard_stop: false, description: '' })
      setAddingRule(false)
    } catch {
      setAddError('Failed to add rule.')
    } finally {
      setAddLoading(false)
    }
  }

  async function handleDeleteRule(ruleId: number) {
    try {
      await deleteRule(ruleId)
      const updatedLender: Lender = {
        ...lender,
        programs: lender.programs.map(p =>
          p.id === program.id
            ? { ...p, policy_rules: p.policy_rules.filter(r => r.id !== ruleId) }
            : p
        ),
      }
      onUpdate(updatedLender)
    } catch {
      // silently ignore for now
    }
  }

  function handleUpdateRule(updatedRule: PolicyRule) {
    const updatedLender: Lender = {
      ...lender,
      programs: lender.programs.map(p =>
        p.id === program.id
          ? { ...p, policy_rules: p.policy_rules.map(r => (r.id === updatedRule.id ? updatedRule : r)) }
          : p
      ),
    }
    onUpdate(updatedLender)
  }

  return (
    <div className="bg-[#1a1d2e] rounded-xl border border-[#2a2d3e]">
      {/* Program header */}
      <div className="px-5 py-4 border-b border-[#2a2d3e] flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white">{program.name}</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Priority {program.priority} ·{' '}
            <span className={program.is_active ? 'text-emerald-500' : 'text-slate-500'}>
              {program.is_active ? 'Active' : 'Inactive'}
            </span>
          </p>
        </div>
        <button
          onClick={() => { setAddingRule(a => !a); setAddError(null) }}
          className="text-xs bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-600/30 px-3 py-1.5 rounded-lg transition-colors"
        >
          + Add Rule
        </button>
      </div>

      {/* Rules table */}
      <div className="divide-y divide-[#2a2d3e]">
        {program.policy_rules.length === 0 && !addingRule && (
          <p className="text-slate-600 text-sm px-5 py-4">No rules configured.</p>
        )}
        {program.policy_rules.map(rule => (
          <RuleRow
            key={rule.id}
            rule={rule}
            onUpdate={handleUpdateRule}
            onDelete={() => handleDeleteRule(rule.id)}
          />
        ))}

        {/* Add rule form */}
        {addingRule && (
          <div className="px-5 py-4 bg-indigo-950/20">
            <p className="text-xs font-semibold text-indigo-300 mb-3 uppercase tracking-wider">New Rule</p>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <input
                className={inputClass}
                placeholder="field_name (e.g. fico_score)"
                value={addForm.field_name ?? ''}
                onChange={e => setAddField('field_name', e.target.value)}
              />
              <select
                className={inputClass}
                value={addForm.operator ?? 'gte'}
                onChange={e => setAddField('operator', e.target.value)}
              >
                {OPERATORS.map(op => (
                  <option key={op} value={op}>{op}</option>
                ))}
              </select>
              <input
                className={inputClass}
                placeholder="value"
                value={addForm.value ?? ''}
                onChange={e => setAddField('value', e.target.value)}
              />
              <input
                className={`${inputClass} col-span-1`}
                placeholder="description (optional)"
                value={addForm.description ?? ''}
                onChange={e => setAddField('description', e.target.value)}
              />
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  className="accent-red-500 w-3.5 h-3.5"
                  checked={addForm.is_hard_stop ?? false}
                  onChange={e => setAddField('is_hard_stop', e.target.checked)}
                />
                Hard Stop
              </label>
              <button
                onClick={handleAddRule}
                disabled={addLoading}
                className="text-xs bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-3 py-1.5 rounded-md transition-colors"
              >
                {addLoading ? 'Saving…' : 'Save Rule'}
              </button>
              <button
                onClick={() => { setAddingRule(false); setAddError(null) }}
                className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
              >
                Cancel
              </button>
            </div>
            {addError && <p className="text-red-400 text-xs mt-2">{addError}</p>}
          </div>
        )}
      </div>
    </div>
  )
}

function RuleRow({
  rule,
  onUpdate,
  onDelete,
}: {
  rule: PolicyRule
  onUpdate: (updated: PolicyRule) => void
  onDelete: () => void
}) {
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    value: rule.value,
    is_hard_stop: rule.is_hard_stop,
    description: rule.description ?? '',
  })
  const [saving, setSaving] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  function setEditField<K extends keyof typeof editForm>(key: K, value: (typeof editForm)[K]) {
    setEditForm(f => ({ ...f, [key]: value }))
  }

  async function handleSave() {
    setSaving(true)
    setEditError(null)
    try {
      const updated = await updateRule(rule.id, {
        value: editForm.value,
        is_hard_stop: editForm.is_hard_stop,
        description: editForm.description || null,
      })
      onUpdate(updated)
      setEditing(false)
    } catch {
      setEditError('Failed to save.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!confirm(`Delete rule "${rule.field_name} ${rule.operator} ${rule.value}"?`)) return
    setDeleting(true)
    try {
      await onDelete()
    } finally {
      setDeleting(false)
    }
  }

  if (editing) {
    return (
      <div className="px-5 py-3 bg-slate-900/40">
        <div className="flex items-start gap-2 mb-2">
          <span className="text-sm text-slate-400 font-mono pt-1.5 shrink-0">
            {rule.field_name} <span className="text-slate-600">{rule.operator}</span>
          </span>
          <input
            className={`${inputClass} flex-1`}
            value={editForm.value}
            onChange={e => setEditField('value', e.target.value)}
          />
          <input
            className={`${inputClass} flex-1`}
            placeholder="description"
            value={editForm.description}
            onChange={e => setEditField('description', e.target.value)}
          />
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              className="accent-red-500 w-3.5 h-3.5"
              checked={editForm.is_hard_stop}
              onChange={e => setEditField('is_hard_stop', e.target.checked)}
            />
            Hard Stop
          </label>
          <button
            onClick={handleSave}
            disabled={saving}
            className="text-xs bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-white px-3 py-1.5 rounded-md transition-colors"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button
            onClick={() => { setEditing(false); setEditError(null) }}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            Cancel
          </button>
        </div>
        {editError && <p className="text-red-400 text-xs mt-1">{editError}</p>}
      </div>
    )
  }

  return (
    <div className="px-5 py-3 flex items-center gap-3 group hover:bg-[#0f1117]/40 transition-colors">
      <span className="text-sm font-mono text-slate-300 shrink-0">{rule.field_name}</span>
      <span className="text-xs text-slate-600 shrink-0">{rule.operator}</span>
      <span className="text-sm text-indigo-300 font-medium shrink-0">{rule.value}</span>

      {rule.is_hard_stop && (
        <span className="text-xs bg-red-900/40 text-red-400 border border-red-700/40 px-1.5 py-0.5 rounded font-semibold shrink-0">
          ⛔ HARD STOP
        </span>
      )}

      {rule.description && (
        <span className="text-xs text-slate-500 truncate flex-1">{rule.description}</span>
      )}

      <div className="ml-auto flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
        <button
          onClick={() => setEditing(true)}
          className="text-xs text-slate-400 hover:text-white border border-[#2a2d3e] hover:border-slate-500 px-2 py-1 rounded transition-colors"
        >
          Edit
        </button>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="text-xs text-red-500 hover:text-red-400 border border-red-900/40 hover:border-red-700/50 px-2 py-1 rounded transition-colors disabled:opacity-50"
        >
          {deleting ? '…' : 'Delete'}
        </button>
      </div>
    </div>
  )
}
