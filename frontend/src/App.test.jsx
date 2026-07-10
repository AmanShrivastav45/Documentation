import { render, screen, cleanup } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, afterEach } from 'vitest'
import App from './App.jsx'

const tree = [
  { id: 'getting-started', label: 'Getting Started', path: 'getting-started.mdx' },
  {
    id: 'guides',
    label: 'Guides',
    children: [
      { id: 'api-tabs-example', label: 'API Install Options', path: 'guides/api-tabs-example.mdx' },
    ],
  },
]

describe('App', () => {
  afterEach(() => cleanup())

  it('renders the sidebar and chat toggle once the doc structure loads', async () => {
    const fetchStructureFn = vi.fn().mockResolvedValue({ tree })
    render(
      <MemoryRouter>
        <App fetchStructureFn={fetchStructureFn} />
      </MemoryRouter>,
    )

    expect(await screen.findByRole('link', { name: 'Getting Started' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Guides/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ask the docs' })).toBeInTheDocument()
  })

  it('renders a doc page at its /docs/* route with its sidebar folder auto-expanded', async () => {
    const fetchStructureFn = vi.fn().mockResolvedValue({ tree })
    const fetchContentFn = vi.fn().mockResolvedValue('# API Install Options\n\nContent.\n')
    render(
      <MemoryRouter initialEntries={['/docs/guides/api-tabs-example']}>
        <App fetchStructureFn={fetchStructureFn} fetchContentFn={fetchContentFn} />
      </MemoryRouter>,
    )

    expect(await screen.findByRole('link', { name: 'API Install Options' })).toBeInTheDocument()
    expect(await screen.findByRole('heading', { name: 'API Install Options' })).toBeInTheDocument()
  })

  it('shows an error message when the docs structure fails to load', async () => {
    const fetchStructureFn = vi.fn().mockRejectedValue(new Error('structure fetch failed'))
    render(
      <MemoryRouter>
        <App fetchStructureFn={fetchStructureFn} />
      </MemoryRouter>,
    )

    expect(await screen.findByText(/structure fetch failed/)).toBeInTheDocument()
  })
})
