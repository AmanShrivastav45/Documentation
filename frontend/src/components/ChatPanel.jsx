import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { docPathToRoute } from '../lib/docsTree.js'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function defaultQueryFn(question) {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!res.ok) {
    throw new Error(`Query failed with status ${res.status}`)
  }
  return res.json()
}

export default function ChatPanel({ queryFn = defaultQueryFn }) {
  const [open, setOpen] = useState(false)
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    if (!question.trim()) return
    setIsLoading(true)
    setError(null)
    try {
      const response = await queryFn(question)
      setResult(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 font-body">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="rounded-lg bg-link-blue px-4 py-2 text-sm font-medium text-surface-white shadow"
      >
        {open ? 'Close chat' : 'Ask the docs'}
      </button>
      {open && (
        <div className="mt-2 rounded-lg border border-border-subtle bg-surface-white p-4 shadow-lg">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question about the docs"
              className="flex-1 rounded-md border border-border-light px-2 py-1 text-sm"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="rounded-md bg-link-blue px-3 py-1 text-sm text-surface-white disabled:opacity-50"
            >
              {isLoading ? 'Asking…' : 'Ask'}
            </button>
          </form>
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          {result && (
            <div className="mt-4 text-sm">
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{result.answer}</ReactMarkdown>
              </div>
              {result.sources?.length > 0 && (
                <ul className="mt-2 space-y-1 border-t border-border-light pt-2">
                  {result.sources.map((source) => (
                    <li key={`${source.file_path}-${source.heading}`}>
                      <a
                        href={docPathToRoute(source.file_path)}
                        className="text-xs text-link-blue hover:underline"
                      >
                        {source.file_path}
                        {source.heading ? ` — ${source.heading}` : ''}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
