'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { ArrowLeft, Clock, FileText, Columns, Loader2, AlertCircle } from 'lucide-react'
import { getAuditSession } from '@/lib/api'
import type { AuditSession } from '@/types/audit'
import ScoreGauge from '@/components/ScoreGauge'
import TestResultCard from '@/components/TestResultCard'

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>()
  const [session, setSession] = useState<AuditSession | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getAuditSession(id)
      .then(setSession)
      .catch(() => setError('Audit session not found or still processing.'))
  }, [id])

  if (error) {
    return (
      <div className="max-w-3xl mx-auto py-20 px-4 text-center">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Error</h2>
        <p className="text-gray-500">{error}</p>
        <a href="/" className="mt-6 inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 text-sm">
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </a>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] gap-3 text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Loading audit results&hellip;</span>
      </div>
    )
  }

  const passedCount = session.results.filter(r => r.status === 'excellent' || r.status === 'good').length
  const warningCount = session.results.filter(r => r.status === 'warning').length
  const criticalCount = session.results.filter(r => r.status === 'critical').length

  return (
    <div className="max-w-5xl mx-auto py-10 px-4">
      {/* Back */}
      <a href="/" className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-800 text-sm mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Home
      </a>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Audit Results</h1>
        <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-gray-500">
          <span className="flex items-center gap-1.5"><FileText className="w-4 h-4" />{session.filename}</span>
          <span className="flex items-center gap-1.5"><Columns className="w-4 h-4" />{session.total_rows.toLocaleString()} rows</span>
          <span className="flex items-center gap-1.5"><Clock className="w-4 h-4" />{new Date(session.created_at).toLocaleString()}</span>
        </div>
      </div>

      {/* Overview grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* Score gauge */}
        {session.composite_score !== null && session.quality_tier && (
          <div className="md:col-span-1">
            <ScoreGauge score={session.composite_score} tier={session.quality_tier} />
          </div>
        )}

        {/* Summary stats */}
        <div className="md:col-span-2 grid grid-cols-2 gap-4 content-start">
          <StatCard value={session.results.length} label="Tests Run" color="text-gray-800" />
          <StatCard value={passedCount} label="Passed (Good/Excellent)" color="text-green-600" />
          <StatCard value={warningCount} label="Warnings" color="text-amber-600" />
          <StatCard value={criticalCount} label="Critical Failures" color="text-red-600" />

          {/* Detected columns */}
          <div className="col-span-2 bg-white border border-gray-200 rounded-xl p-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Detected Columns</h3>
            <div className="flex flex-wrap gap-2">
              {Object.entries(session.detected_columns).map(([role, col]) => (
                <span key={role} className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full px-2.5 py-0.5">
                  <span className="font-semibold">{role}:</span> {col}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Test Results */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Diagnostic Test Results</h2>
        <div className="space-y-3">
          {session.results.map((result, i) => (
            <TestResultCard key={result.id} result={result} index={i} />
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
      <p className={`text-3xl font-bold tabular-nums ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  )
}
