import { render, screen, cleanup } from '@testing-library/react'
import { describe, it, expect, afterEach } from 'vitest'
import Callout from './Callout.jsx'

describe('Callout', () => {
  afterEach(() => cleanup())
  it('renders its children', () => {
    render(<Callout type="warning">Breaking change</Callout>)
    expect(screen.getByText('Breaking change')).toBeInTheDocument()
  })

  it('exposes the callout type for styling', () => {
    render(<Callout type="error">Danger</Callout>)
    expect(screen.getByRole('note')).toHaveAttribute('data-callout-type', 'error')
  })

  it('defaults to the info type when none is provided', () => {
    render(<Callout>Neutral</Callout>)
    expect(screen.getByRole('note')).toHaveAttribute('data-callout-type', 'info')
  })
})
