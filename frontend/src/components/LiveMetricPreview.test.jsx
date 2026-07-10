import { render, screen, cleanup } from '@testing-library/react'
import { describe, it, expect, afterEach } from 'vitest'
import LiveMetricPreview from './LiveMetricPreview.jsx'

describe('LiveMetricPreview', () => {
  afterEach(cleanup)

  it('renders the threshold', () => {
    render(<LiveMetricPreview threshold={80} data={[10, 20, 30]} />)
    expect(screen.getByText('Threshold: 80')).toBeInTheDocument()
  })

  it('flags the current value as over threshold in red', () => {
    render(<LiveMetricPreview threshold={80} data={[10, 90]} />)
    expect(screen.getByTestId('current-value')).toHaveClass('text-red-600')
    expect(screen.getByTestId('gauge-bar')).toHaveClass('bg-red-500')
  })

  it('shows green styling when under threshold', () => {
    render(<LiveMetricPreview threshold={80} data={[10, 50]} />)
    expect(screen.getByTestId('current-value')).toHaveClass('text-green-600')
    expect(screen.getByTestId('gauge-bar')).toHaveClass('bg-green-500')
  })

  it('falls back to its own mock data when none is provided', () => {
    render(<LiveMetricPreview threshold={80} />)
    expect(screen.getByTestId('current-value')).toBeInTheDocument()
  })
})
