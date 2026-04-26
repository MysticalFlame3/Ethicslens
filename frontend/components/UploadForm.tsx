'use client'

import { useState, useRef, DragEvent } from 'react'
import { Upload, FileText, Loader2, AlertCircle } from 'lucide-react'
import { uploadDataset } from '@/lib/api'
import { useRouter } from 'next/navigation'

export default function UploadForm() {
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  const ACCEPTED = ['.csv', '.json', '.jsonl']

  function validateFile(f: File) {
    const ext = '.' + f.name.split('.').pop()?.toLowerCase()
    if (!ACCEPTED.includes(ext)) {
      setError(`Unsupported file type. Please upload CSV, JSON, or JSONL.`)
      return false
    }
    if (f.size > 100 * 1024 * 1024) {
      setError('File exceeds 100MB limit.')
      return false
    }
    return true
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f && validateFile(f)) {
      setFile(f)
      setError(null)
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (f && validateFile(f)) {
      setFile(f)
      setError(null)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const { id } = await uploadDataset(file)
      router.push(`/results/${id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Audit failed. Please try again.')
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all
          ${dragging ? 'border-indigo-400 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50/50'}
          ${file ? 'border-green-400 bg-green-50/50' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.json,.jsonl"
          onChange={handleChange}
          className="hidden"
        />

        {file ? (
          <div className="flex flex-col items-center gap-3">
            <FileText className="w-12 h-12 text-green-500" />
            <div>
              <p className="font-semibold text-gray-800">{file.name}</p>
              <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
            <p className="text-sm text-gray-500">Click to change file</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <Upload className="w-12 h-12 text-gray-400" />
            <div>
              <p className="font-semibold text-gray-700">Drop your dataset here</p>
              <p className="text-sm text-gray-500 mt-1">or click to browse</p>
            </div>
            <p className="text-xs text-gray-400">Supports CSV, JSON, JSONL &mdash; up to 100MB</p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-3 flex items-start gap-2 text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button
        type="submit"
        disabled={!file || loading}
        className="mt-4 w-full py-3 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Running 8 Audit Tests&hellip;
          </>
        ) : (
          <>
            <Upload className="w-5 h-5" />
            Run Quality Audit
          </>
        )}
      </button>
    </form>
  )
}
