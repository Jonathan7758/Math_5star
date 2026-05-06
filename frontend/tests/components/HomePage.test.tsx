import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { HomePage } from '../../src/pages/HomePage'

describe('HomePage', () => {
  it('renders app title', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    )
    expect(screen.getByText('数学启明星')).toBeInTheDocument()
  })

  it('shows buttons for main features', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    )
    expect(screen.getByText('开始诊断')).toBeInTheDocument()
    expect(screen.getByText('自由练习')).toBeInTheDocument()
  })
})
