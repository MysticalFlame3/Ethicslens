export interface TestResult {
  id: number
  session_id: string
  test_name: string
  score: number | null
  status: 'excellent' | 'good' | 'warning' | 'critical' | 'skipped'
  metrics: Record<string, unknown>
  chart_data: ChartData | null
  description: string
  recommendations: string[]
}

export interface ChartData {
  type: 'pie' | 'bar' | 'heatmap'
  labels?: string[]
  data?: number[]
  colors?: string[]
  datasets?: {
    label: string
    data: number[]
    backgroundColor?: string | string[]
  }[]
  matrix?: number[][]
}

export interface AuditSession {
  id: string
  filename: string
  total_rows: number
  detected_columns: Record<string, string>
  composite_score: number | null
  quality_tier: string | null
  created_at: string
  results: TestResult[]
}

export interface SessionListItem {
  id: string
  filename: string
  total_rows: number
  composite_score: number | null
  quality_tier: string | null
  created_at: string
}
