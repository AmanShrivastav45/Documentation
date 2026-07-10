import { describe, it, expect } from 'vitest'
import { collectAncestorIds, docPathToRoute, findNodeLabel, routeToDocPath } from './docsTree.js'

const tree = [
  { id: 'getting-started', label: 'Getting Started', path: 'getting-started.mdx' },
  {
    id: 'guides',
    label: 'Guides',
    children: [
      { id: 'api-tabs-example', label: 'API Install Options', path: 'guides/api-tabs-example.mdx' },
      { id: 'alerting-live-preview', label: 'Alerting Live Preview', path: 'guides/alerting-live-preview.mdx' },
    ],
  },
]

describe('docPathToRoute', () => {
  it('converts a relative doc path into a /docs route', () => {
    expect(docPathToRoute('guides/api-tabs-example.mdx')).toBe('/docs/guides/api-tabs-example')
  })
})

describe('routeToDocPath', () => {
  it('converts a /docs route back into the relative doc path', () => {
    expect(routeToDocPath('/docs/guides/api-tabs-example')).toBe('guides/api-tabs-example.mdx')
  })

  it('returns null for a route outside /docs', () => {
    expect(routeToDocPath('/')).toBeNull()
  })

  it('round-trips with docPathToRoute', () => {
    const path = 'guides/alerting-live-preview.mdx'
    expect(routeToDocPath(docPathToRoute(path))).toBe(path)
  })
})

describe('collectAncestorIds', () => {
  it('returns an empty list for a top-level doc', () => {
    expect(collectAncestorIds(tree, 'getting-started.mdx')).toEqual([])
  })

  it('returns the parent folder ids for a nested doc', () => {
    expect(collectAncestorIds(tree, 'guides/api-tabs-example.mdx')).toEqual(['guides'])
  })

  it('returns null when the path is not found', () => {
    expect(collectAncestorIds(tree, 'missing.mdx')).toBeNull()
  })
})

describe('findNodeLabel', () => {
  it('finds the label for a top-level doc', () => {
    expect(findNodeLabel(tree, 'getting-started.mdx')).toBe('Getting Started')
  })

  it('finds the label for a nested doc', () => {
    expect(findNodeLabel(tree, 'guides/alerting-live-preview.mdx')).toBe('Alerting Live Preview')
  })

  it('returns null when the path is not found', () => {
    expect(findNodeLabel(tree, 'missing.mdx')).toBeNull()
  })
})
