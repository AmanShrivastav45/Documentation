import { describe, it, expect, vi, afterEach } from 'vitest'
import { fetchDocContent, fetchDocsStructure } from './docsApi.js'

describe('fetchDocsStructure', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('fetches and parses the docs structure as JSON', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ tree: [] }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const result = await fetchDocsStructure()

    expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/docs/structure')
    expect(result).toEqual({ tree: [] })
  })

  it('throws when the response is not ok', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500 }))

    await expect(fetchDocsStructure()).rejects.toThrow('500')
  })
})

describe('fetchDocContent', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('fetches raw doc content as text', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      text: () => Promise.resolve('# Hello\n'),
    })
    vi.stubGlobal('fetch', mockFetch)

    const result = await fetchDocContent('guides/api-tabs-example.mdx')

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/docs/content?path=guides%2Fapi-tabs-example.mdx',
    )
    expect(result).toBe('# Hello\n')
  })

  it('throws when the response is not ok', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }))

    await expect(fetchDocContent('missing.mdx')).rejects.toThrow('404')
  })
})
