import { render, screen, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, afterEach } from 'vitest'
import DocsSidebar from './DocsSidebar.jsx'

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

describe('DocsSidebar', () => {
  afterEach(() => cleanup())

  it('renders a link for a top-level doc and a toggle button for a folder', () => {
    render(
      <MemoryRouter>
        <DocsSidebar tree={tree} activePath={null} />
      </MemoryRouter>,
    )
    expect(screen.getByRole('link', { name: 'Getting Started' })).toHaveAttribute(
      'href',
      '/docs/getting-started',
    )
    expect(screen.getByRole('button', { name: /Guides/ })).toBeInTheDocument()
  })

  it('keeps a folder collapsed by default when its children are not active', () => {
    render(
      <MemoryRouter>
        <DocsSidebar tree={tree} activePath={null} />
      </MemoryRouter>,
    )
    expect(screen.queryByRole('link', { name: 'API Install Options' })).not.toBeInTheDocument()
  })

  it('auto-expands the parent folder of the active doc', () => {
    render(
      <MemoryRouter>
        <DocsSidebar tree={tree} activePath="guides/api-tabs-example.mdx" />
      </MemoryRouter>,
    )
    expect(screen.getByRole('link', { name: 'API Install Options' })).toBeInTheDocument()
  })

  it('toggles a folder open and closed when its button is clicked', async () => {
    render(
      <MemoryRouter>
        <DocsSidebar tree={tree} activePath={null} />
      </MemoryRouter>,
    )
    await userEvent.click(screen.getByRole('button', { name: /Guides/ }))
    expect(screen.getByRole('link', { name: 'Alerting Live Preview' })).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /Guides/ }))
    expect(screen.queryByRole('link', { name: 'Alerting Live Preview' })).not.toBeInTheDocument()
  })
})
