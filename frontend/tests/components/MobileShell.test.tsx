import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { MobileShell } from '../../src/components/layout/MobileShell'

describe('MobileShell', () => {
  it('renders children', () => {
    render(
      <MemoryRouter>
        <MobileShell>
          <div data-testid="child">Content</div>
        </MobileShell>
      </MemoryRouter>
    )
    expect(screen.getByTestId('child')).toBeInTheDocument()
  })

  it('renders bottom navigation', () => {
    render(
      <MemoryRouter>
        <MobileShell>
          <div>Content</div>
        </MobileShell>
      </MemoryRouter>
    )
    expect(screen.getByText('学习')).toBeInTheDocument()
    expect(screen.getByText('诊断')).toBeInTheDocument()
  })
})
