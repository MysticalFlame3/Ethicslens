'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, CheckCircle, AlertTriangle, XCircle, Info, SkipForward } from 'lucide-react'
import type { TestResult } from '@/types/audit'
import TestChart from './charts/TestChart'

const STATUS_CONFIG = {
  excellent: { color: 'text-green-600', bg: 'bg-green-50 border-green-200', icon: CheckCircle, label: 'Excellent', badge: 'bg-green-100 text-green-700' },
  good:      { color: 'text-blue-600',  bg: 'bg-blue-50 border-blue-200',   icon: Info,        label: 'Good',      badge: 'bg-blue-100 text-blue-700' },
  warning:   { color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200', icon: AlertTriangle,label: 'Warning',  badge: 'bg-amber-100 text-amber-700' },
  critical:  { color: 'text-red-600',   bg: 'bg-red-50 border-red-200',     icon: XCircle,     label: 'Critical',  badge: 'bg-red-100 text-red-700' },
  skipped:   { color: 'text-gray-400',  bg: 'bg-gray-50 border-gray-200',   icon: SkipForward, label: 'Skipped',   badge: 'bg-gray-100 text-gray-500' },
}

const SCORE_COLOR = (s: number | null) => {
  if (s === null) return 'text-gray-400'
  if (s >= 80) return 'text-green-600'
  if (s >= 60) return 'text-blue-600'
  if (s >= 40) return 'text-amber-600'
  return 'text-red-600'
}

interface Props {
  result: TestResult
  index: number
}

export default function TestResultCard({ result, index }: Props) {
  const [open, setOpen] = useState(false)
  const cfg = STATUS_CONFIG[result.status]
  const Icon = cfg.icon

  const metrics = result.metrics as Record<string, unknown>

  return (
    <div className={`border rounded-xl overflow-hidden transition-shadow hover:shadow-md ${cfg.bg}`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full text-left px-5 py-4 flex items-center gap-4"
      >
        <span className="text-gray-400 font-mono text-sm w-5 text-right flex-shrink-0">{index + 1}</span>

        <Icon className={`w-5 h-5 flex-shrink-0 ${cfg.color}`} />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-gray-900">{result.test_name}</h3>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cfg.badge}`}>{cfg.label}</span>
          </div>
          <p className="text-sm text-gray-500 mt-0.5 line-clamp-1">{result.description}</p>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          {result.score !== null && (
            <span className={`text-2xl font-bold tabular-nums ${SCORE_COLOR(result.score)}`}>
              {result.score}
              <span className="text-sm font-normal text-gray-400">/100</span>
            </span>
          )}
          {open ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
        </div>
      </button>

      {open && (
        <div className="px-5 pb-5 border-t border-inherit space-y-5 bg-white/60">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-5">
            {/* Metrics */}
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Metrics</h4>
              <dl className="space-y-2">
                {Object.entries(metrics).map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-4 text-sm">
                    <dt className="text-gray-500 capitalize">{k.replace(/_/g, ' ')}</dt>
                    <dd className="font-medium text-gray-800 text-right">
                      {typeof v === 'number' ? v.toLocaleString(undefined, { maximumFractionDigits: 4 }) : String(v)}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>

            {/* Chart */}
            {result.chart_data && (
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Visualization</h4>
                <TestChart chart={result.chart_data} />
              </div>
            )}
          </div>

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Recommendations</h4>
              <ul className="space-y-2">
                {result.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="mt-1 w-4 h-4 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold flex-shrink-0">{i + 1}</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
