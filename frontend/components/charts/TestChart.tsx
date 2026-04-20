'use client'

import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts'
import type { ChartData } from '@/types/audit'

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']

interface Props {
  chart: ChartData
}

export default function TestChart({ chart }: Props) {
  if (chart.type === 'pie' && chart.labels && chart.data) {
    const pieData = chart.labels.map((label, i) => ({
      name: label,
      value: chart.data![i],
    }))
    return (
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={pieData} dataKey="value" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
            {pieData.map((_, i) => (
              <Cell key={i} fill={chart.colors?.[i] || COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: number) => v.toLocaleString()} />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  if (chart.type === 'bar') {
    if (chart.datasets && chart.labels) {
      const barData = chart.labels.map((label, i) => {
        const entry: Record<string, string | number> = { name: label }
        chart.datasets!.forEach(ds => { entry[ds.label] = ds.data[i] })
        return entry
      })
      return (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={barData} margin={{ top: 5, right: 10, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            {chart.datasets.map((ds, i) => (
              <Bar key={ds.label} dataKey={ds.label} fill={Array.isArray(ds.backgroundColor) ? ds.backgroundColor[0] : (ds.backgroundColor || COLORS[i % COLORS.length])} radius={[3, 3, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      )
    }

    if (chart.labels && chart.data) {
      const barData = chart.labels.map((label, i) => ({ name: label, value: chart.data![i] }))
      return (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={barData} margin={{ top: 5, right: 10, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="value" radius={[3, 3, 0, 0]}>
              {barData.map((_, i) => (
                <Cell key={i} fill={chart.colors?.[i] || COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )
    }
  }

  if (chart.type === 'heatmap' && chart.matrix && chart.labels) {
    return <HeatmapChart matrix={chart.matrix} labels={chart.labels} />
  }

  return null
}

function HeatmapChart({ matrix, labels }: { matrix: number[][], labels: string[] }) {
  const max = Math.max(...matrix.flat().filter(v => v < 1))
  const getColor = (v: number) => {
    if (v >= 0.8) return '#ef4444'
    if (v >= 0.6) return '#f97316'
    if (v >= 0.4) return '#f59e0b'
    if (v >= 0.2) return '#86efac'
    return '#e0f2fe'
  }

  const truncate = (s: string, n = 12) => s.length > n ? s.slice(0, n) + '…' : s

  return (
    <div className="overflow-auto">
      <table className="text-xs border-collapse">
        <thead>
          <tr>
            <th className="w-20" />
            {labels.map(l => (
              <th key={l} className="p-0.5 font-normal text-gray-500" style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)', height: 80, width: 20 }}>
                {truncate(l)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, ri) => (
            <tr key={ri}>
              <td className="pr-2 text-right text-gray-500 text-xs whitespace-nowrap">{truncate(labels[ri])}</td>
              {row.map((v, ci) => (
                <td
                  key={ci}
                  style={{ backgroundColor: getColor(v), width: 20, height: 20 }}
                  title={`${labels[ri]} × ${labels[ci]}: ${v.toFixed(2)}`}
                />
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
