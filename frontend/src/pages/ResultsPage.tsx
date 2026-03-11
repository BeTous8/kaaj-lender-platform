import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import type { MatchResult, UnderwriteResponse } from '../types'

interface LocationState {
  results: UnderwriteResponse
  businessName: string
}

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null

  if (!state?.results) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <p className="text-slate-400 text-lg">No results to display.</p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 text-indigo-400 hover:text-indigo-300 underline text-sm"
        >
          Submit an application
        </button>
      </div>
    )
  }

  const { results, businessName } = state
  const sorted = [...results.results].sort((a, b) => {
    if (a.is_eligible !== b.is_eligible) return a.is_eligible ? -1 : 1
    return b.fit_score - a.fit_score
  })
  const approvedCount = results.results.filter(r => r.is_eligible).length

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white">
          Results for <span className="text-indigo-400">{businessName}</span>
        </h1>

        {/* Summary bar */}
        <div className="mt-4 flex items-center gap-4">
          <div className="bg-[#1a1d2e] border border-[#2a2d3e] rounded-xl px-6 py-3 flex items-center gap-3">
            <span
              className={`text-3xl font-extrabold ${approvedCount > 0 ? 'text-emerald-400' : 'text-red-400'}`}
            >
              {approvedCount}
            </span>
            <div className="text-slate-400 text-sm leading-tight">
              <div>of {results.results.length}</div>
              <div>lenders approved</div>
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            className="text-sm text-slate-400 hover:text-white border border-[#2a2d3e] rounded-lg px-4 py-2 transition-colors hover:border-slate-500"
          >
            ← New Application
          </button>
        </div>
      </div>

      {/* Cards */}
      <div className="space-y-4">
        {sorted.map((result, i) => (
          <ResultCard key={`${result.lender_name}-${result.program_name}-${i}`} result={result} />
        ))}
      </div>
    </div>
  )
}

function ResultCard({ result }: { result: MatchResult }) {
  const [expanded, setExpanded] = useState(false)
  const [scoreVisible, setScoreVisible] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setScoreVisible(true), 100)
    return () => clearTimeout(t)
  }, [])

  const score = result.fit_score
  const scoreColor = score >= 70 ? 'bg-emerald-500' : score >= 40 ? 'bg-amber-500' : 'bg-red-500'
  const scoreText = score >= 70 ? 'text-emerald-400' : score >= 40 ? 'text-amber-400' : 'text-red-400'

  const hardStopFailures = result.rule_evaluations.filter(r => !r.passed)
  const totalRules = result.rule_evaluations.length
  const passedRules = result.rule_evaluations.filter(r => r.passed).length

  return (
    <div
      className={`bg-[#1a1d2e] rounded-xl border transition-colors ${
        result.is_eligible ? 'border-emerald-500/30' : 'border-[#2a2d3e]'
      }`}
    >
      {/* Top section */}
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">
              {result.lender_name}
            </p>
            <h3 className="text-xl font-bold text-white truncate">{result.program_name}</h3>

            {/* Fit score bar */}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-500">Fit Score</span>
                <span className={`text-sm font-bold ${scoreText}`}>{score}/100</span>
              </div>
              <div className="h-2 bg-[#0f1117] rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ease-out ${scoreColor}`}
                  style={{ width: scoreVisible ? `${score}%` : '0%' }}
                />
              </div>
            </div>

            {/* Rule summary */}
            <p className="mt-3 text-xs text-slate-500">
              {passedRules}/{totalRules} rules passed
              {hardStopFailures.length > 0 && (
                <span className="ml-2 text-red-400">
                  · {hardStopFailures.length} failed
                </span>
              )}
            </p>
          </div>

          {/* Badge */}
          <div className="shrink-0">
            {result.is_eligible ? (
              <div className="bg-emerald-500/10 border-2 border-emerald-500 rounded-xl px-5 py-3 text-center">
                <span className="text-emerald-400 text-xl font-extrabold tracking-widest">APPROVED</span>
              </div>
            ) : (
              <div className="bg-red-500/10 border-2 border-red-500 rounded-xl px-5 py-3 text-center">
                <span className="text-red-400 text-xl font-extrabold tracking-widest">DECLINED</span>
              </div>
            )}
          </div>
        </div>

        {/* Expand toggle */}
        <button
          onClick={() => setExpanded(e => !e)}
          className="mt-4 text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1 transition-colors"
        >
          <svg
            className={`w-3 h-3 transition-transform ${expanded ? 'rotate-90' : ''}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M6 6l8 4-8 4V6z" />
          </svg>
          {expanded ? 'Hide' : 'Show'} rule evaluations
        </button>
      </div>

      {/* Expandable rule evaluations */}
      {expanded && (
        <div className="border-t border-[#2a2d3e] divide-y divide-[#2a2d3e]">
          {result.rule_evaluations.map((rule, i) => (
            <RuleRow key={`${rule.rule_id}-${i}`} evaluation={rule} />
          ))}
        </div>
      )}
    </div>
  )
}

function RuleRow({
  evaluation,
}: {
  evaluation: MatchResult['rule_evaluations'][number]
}) {
  const passed = evaluation.passed

  return (
    <div
      className={`px-6 py-3 flex items-start gap-3 text-sm ${
        passed ? 'bg-emerald-950/20' : 'bg-red-950/20'
      }`}
    >
      <span className={`mt-0.5 shrink-0 text-base ${passed ? 'text-emerald-400' : 'text-red-400'}`}>
        {passed ? '✓' : '✗'}
      </span>
      <div className="flex-1 min-w-0">
        <p className={`${passed ? 'text-slate-300' : 'text-slate-200 font-medium'}`}>
          {evaluation.explanation}
        </p>
        {!passed && (
          <p className="text-xs text-slate-500 mt-0.5">
            Got: <span className="text-red-300">{evaluation.actual_value ?? 'N/A'}</span>
            {' '}· Required: <span className="text-slate-400">{evaluation.required_value}</span>
          </p>
        )}
      </div>
    </div>
  )
}
