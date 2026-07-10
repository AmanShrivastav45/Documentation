import { useEffect, useState } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import ChatPanel from './components/ChatPanel.jsx'
import DocsSidebar from './components/DocsSidebar.jsx'
import DocContent from './components/DocContent.jsx'
import { fetchDocContent, fetchDocsStructure } from './lib/docsApi.js'
import { findNodeLabel, routeToDocPath } from './lib/docsTree.js'

export default function App({
  fetchStructureFn = fetchDocsStructure,
  fetchContentFn = fetchDocContent,
}) {
  const [tree, setTree] = useState(null)
  const [error, setError] = useState(null)
  const location = useLocation()

  useEffect(() => {
    fetchStructureFn()
      .then((structure) => setTree(structure.tree))
      .catch((err) => setError(err.message))
  }, [fetchStructureFn])

  const activePath = tree ? routeToDocPath(location.pathname) : null

  useEffect(() => {
    if (!tree) return
    const label = activePath ? findNodeLabel(tree, activePath) : null
    document.title = label ? `${label} — Docs Platform` : 'Docs Platform'
  }, [tree, activePath])

  if (error) {
    return <p className="p-8 text-red-600">Failed to load docs: {error}</p>
  }
  if (!tree) {
    return <p className="p-8 text-text-muted">Loading…</p>
  }

  return (
    <div className="flex min-h-screen bg-surface-white font-body text-text-primary">
      <DocsSidebar tree={tree} activePath={activePath} />
      <main className="flex-1 p-8">
        <Routes>
          <Route
            path="/"
            element={<p className="text-text-muted">Docs platform — select a page from the sidebar.</p>}
          />
          <Route
            path="/docs/*"
            element={<DocContent path={activePath} fetchContentFn={fetchContentFn} />}
          />
        </Routes>
      </main>
      <ChatPanel />
    </div>
  )
}
