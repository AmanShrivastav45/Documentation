import { render, screen, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, afterEach } from 'vitest'
import CodeTabs from './CodeTabs.jsx'

const tabs = [
  { label: 'Docker', language: 'bash', code: 'docker run app' },
  { label: 'Helm', language: 'bash', code: 'helm install app' },
]

describe('CodeTabs', () => {
  afterEach(() => cleanup())

  it('shows the first tab content by default', () => {
    render(<CodeTabs tabs={tabs} />)
    expect(screen.getByText('docker run app')).toBeInTheDocument()
  })

  it('switches content when a different tab is clicked', async () => {
    render(<CodeTabs tabs={tabs} />)
    await userEvent.click(screen.getByRole('tab', { name: 'Helm' }))
    expect(screen.getByText('helm install app')).toBeInTheDocument()
    expect(screen.queryByText('docker run app')).not.toBeInTheDocument()
  })
})
