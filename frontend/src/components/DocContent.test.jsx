import { render, screen, cleanup } from '@testing-library/react'
import { describe, it, expect, vi, afterEach } from 'vitest'
import DocContent from './DocContent.jsx'

describe('DocContent', () => {
  afterEach(() => cleanup())

  it('compiles and renders fetched MDX content', async () => {
    const fetchContentFn = vi.fn().mockResolvedValue('# Hello\n\nSome **bold** text.\n')
    render(<DocContent path="hello.mdx" fetchContentFn={fetchContentFn} />)

    expect(await screen.findByRole('heading', { name: 'Hello' })).toBeInTheDocument()
    expect(screen.getByText('bold')).toBeInTheDocument()
    expect(fetchContentFn).toHaveBeenCalledWith('hello.mdx')
  })

  it('renders a mapped custom component embedded in the MDX', async () => {
    const fetchContentFn = vi
      .fn()
      .mockResolvedValue('# Title\n\n<Callout type="warning">Careful</Callout>\n')
    render(<DocContent path="callout.mdx" fetchContentFn={fetchContentFn} />)

    expect(await screen.findByText('Careful')).toBeInTheDocument()
    expect(screen.getByRole('note')).toHaveAttribute('data-callout-type', 'warning')
  })

  it('shows an error message when fetching content fails', async () => {
    const fetchContentFn = vi.fn().mockRejectedValue(new Error('doc not found: missing.mdx'))
    render(<DocContent path="missing.mdx" fetchContentFn={fetchContentFn} />)

    expect(await screen.findByText(/doc not found: missing\.mdx/)).toBeInTheDocument()
  })
})
