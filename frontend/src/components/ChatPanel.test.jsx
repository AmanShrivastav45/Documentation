import { render, screen, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, afterEach } from 'vitest'
import ChatPanel from './ChatPanel.jsx'

describe('ChatPanel', () => {
  afterEach(() => cleanup())

  it('submits a question and renders the markdown answer with source citations', async () => {
    const queryFn = vi.fn().mockResolvedValue({
      answer: 'The answer is **42**.',
      sources: [
        {
          file_path: 'getting-started.mdx',
          heading: 'Installation',
          git_commit_hash: 'abc123',
          last_updated: '2026-01-01T00:00:00Z',
        },
      ],
    })
    render(<ChatPanel queryFn={queryFn} />)

    await userEvent.click(screen.getByRole('button', { name: 'Ask the docs' }))
    await userEvent.type(
      screen.getByPlaceholderText('Ask a question about the docs'),
      'How do I install it?',
    )
    await userEvent.click(screen.getByRole('button', { name: 'Ask' }))

    expect(queryFn).toHaveBeenCalledWith('How do I install it?')
    expect(await screen.findByText('42')).toBeInTheDocument()
    const link = screen.getByRole('link', { name: /getting-started\.mdx/ })
    expect(link).toHaveAttribute('href', '/docs/getting-started')
  })

  it('shows an error message when the query fails', async () => {
    const queryFn = vi.fn().mockRejectedValue(new Error('Query failed with status 500'))
    render(<ChatPanel queryFn={queryFn} />)

    await userEvent.click(screen.getByRole('button', { name: 'Ask the docs' }))
    await userEvent.type(
      screen.getByPlaceholderText('Ask a question about the docs'),
      'Anything?',
    )
    await userEvent.click(screen.getByRole('button', { name: 'Ask' }))

    expect(await screen.findByText('Query failed with status 500')).toBeInTheDocument()
  })
})
