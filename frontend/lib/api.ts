const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function uploadDataset(file: File): Promise<{ id: string }> {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/api/audit`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(err.detail || 'Upload failed')
  }

  return res.json()
}

export async function getAuditSession(id: string) {
  const res = await fetch(`${API_BASE}/api/results/${id}`)
  if (!res.ok) throw new Error('Session not found')
  return res.json()
}

export async function listSessions() {
  const res = await fetch(`${API_BASE}/api/sessions`)
  if (!res.ok) throw new Error('Failed to load sessions')
  return res.json()
}
