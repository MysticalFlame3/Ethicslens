'use client'

interface Props {
  score: number
  tier: string
}

const TIER_COLORS: Record<string, { stroke: string; text: string; bg: string }> = {
  'High Quality':     { stroke: '#10b981', text: 'text-green-600',  bg: 'bg-green-50' },
  'Moderate Quality': { stroke: '#6366f1', text: 'text-indigo-600', bg: 'bg-indigo-50' },
  'Low Quality':      { stroke: '#ef4444', text: 'text-red-600',    bg: 'bg-red-50' },
}

export default function ScoreGauge({ score, tier }: Props) {
  const colors = TIER_COLORS[tier] || TIER_COLORS['Moderate Quality']
  const radius = 80
  const circumference = 2 * Math.PI * radius
  const progress = (score / 100) * circumference
  const dashOffset = circumference - progress

  return (
    <div className={`flex flex-col items-center justify-center rounded-2xl p-8 ${colors.bg}`}>
      <svg width={200} height={200} viewBox="0 0 200 200">
        {/* Track */}
        <circle cx="100" cy="100" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="14" />
        {/* Progress */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke={colors.stroke}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          transform="rotate(-90 100 100)"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
        <text x="100" y="95" textAnchor="middle" fontSize="40" fontWeight="bold" fill="#1e293b">{score.toFixed(1)}</text>
        <text x="100" y="118" textAnchor="middle" fontSize="14" fill="#64748b">/ 100</text>
      </svg>
      <p className={`text-lg font-bold mt-2 ${colors.text}`}>{tier}</p>
      <p className="text-sm text-gray-500 mt-1">Composite Quality Score</p>
    </div>
  )
}
