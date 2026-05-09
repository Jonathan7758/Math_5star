import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SpriteDisplay } from '../../src/components/sprite/SpriteDisplay'

describe('SpriteDisplay', () => {
  it('renders stage 0 star dust', () => {
    render(<SpriteDisplay stage={0} stageName="星尘" reaction="idle" size="sm" />)
    expect(screen.getByLabelText('精灵: 星尘，点击互动')).toBeInTheDocument()
    expect(screen.getByText('星尘')).toBeInTheDocument()
  })

  it('renders stage 1 star sprout', () => {
    render(<SpriteDisplay stage={1} stageName="星芽" reaction="happy" />)
    expect(screen.getByText('星芽')).toBeInTheDocument()
  })

  it('renders in different sizes', () => {
    const { rerender } = render(<SpriteDisplay stage={0} stageName="星尘" reaction="idle" size="sm" />)
    const el = screen.getByLabelText('精灵: 星尘，点击互动')
    expect(el.closest('.w-12')).toBeTruthy()

    rerender(<SpriteDisplay stage={0} stageName="星尘" reaction="idle" size="lg" />)
    expect(screen.getByLabelText('精灵: 星尘，点击互动').closest('.w-32')).toBeTruthy()
  })
})
