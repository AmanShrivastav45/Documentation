const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function fetchDocsStructure() {
  const res = await fetch(`${API_BASE}/api/docs/structure`)
  if (!res.ok) {
    throw new Error(`Failed to load docs structure (status ${res.status})`)
  }
  return res.json()
}

export async function fetchDocContent(path) {
  const res = await fetch(`${API_BASE}/api/docs/content?path=${encodeURIComponent(path)}`)
  if (!res.ok) {
    throw new Error(`Failed to load doc content for "${path}" (status ${res.status})`)
  }
  return res.text()
}
