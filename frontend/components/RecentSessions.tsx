'use client'

import { useEffect, useState } from 'react'
import { Clock, FileText, ArrowRight, Loader2 } from 'lucide-react'
import { listSessions } from '@/lib/api'
import type { SessionListItem } from '@/types/audit'

const TIER_BADGE: Record<string, string> = {
  'High Quality':     'bg-green-100 text-green-700',
  'Moderate Quality': 'bg-indigo-100 text-indigo-700',
  'Low Quality':      'bg-red-100 text-red-700',
}

export default function RecentSessions() {
  const [sessions, setSessions] = useState<SessionListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listSessions()
      .then(setSessions)
      .catch(() => setSessions([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-400 text-sm py-6">
        <Loader2 className="w-4 h-4 animate-spin" />
        Loading recent audits&hellip;
      </div>
    )
  }

  if (sessions.length === 0) {
    return (
      <p className="text-gray-400 text-sm py-6">No audits yet. Upload a dataset above to get started.</p>
    )
  }

  return (
    <div className="space-y-3">
      {sessions.map(s => (
        <a
          key={s.id}
          href={`/results/${s.id}`}
          className="flex items-center gap-4 bg-white border border-gray-200 rounded-xl px-5 py-4 hover:shadow-md transition-shadow group"
        >
          <FileText className="w-5 h-5 text-gray-400 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 truncate">{s.filename}</p>
            <p className="text-sm text-gray-500 flex items-center gap-3 mt-0.5">
              <span>{s.total_rows.toLocaleString()} rows</span>
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{new Date(s.created_at).toLocaleDateString()}</span>
            </p>
          </div>
          {s.composite_score !== null && (
            <div className="text-right flex-shrink-0">
              <p className="text-xl font-bold text-gray-900 tabular-nums">{s.composite_score.toFixed(1)}</p>
              {s.quality_tier && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TIER_BADGE[s.quality_tier] || 'bg-gray-100 text-gray-600'}`}>
                  {s.quality_tier}
                </span>
              )}
            </div>
          )}
          <ArrowRight className="w-5 h-5 text-gray-300 group-hover:text-indigo-500 transition-colors" />
        </a>
      ))}
    </div>
  )
}
