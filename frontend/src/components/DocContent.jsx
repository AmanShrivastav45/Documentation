import { useEffect, useState } from 'react'
import * as runtime from 'react/jsx-runtime'
import { evaluate } from '@mdx-js/mdx'
import Callout from './Callout.jsx'
import CodeTabs from './CodeTabs.jsx'
import LiveMetricPreview from './LiveMetricPreview.jsx'
import { fetchDocContent } from '../lib/docsApi.js'

const MDX_COMPONENTS = { Callout, CodeTabs, LiveMetricPreview }

export default function DocContent({ path, fetchContentFn = fetchDocContent }) {
  const [Content, setContent] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setContent(null)
    setError(null)
    fetchContentFn(path)
      .then((source) => evaluate(source, runtime))
      .then((compiled) => {
        if (!cancelled) setContent(() => compiled.default)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [path, fetchContentFn])

  if (error) {
    return <p className="text-red-600">Failed to load doc: {error}</p>
  }
  if (!Content) {
    return <p className="text-text-muted">Loading…</p>
  }

  return (
    <article className="prose max-w-none">
      <Content components={MDX_COMPONENTS} />
    </article>
  )
}
