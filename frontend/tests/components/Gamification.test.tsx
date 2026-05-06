import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { XPBar } from '../../src/components/gamification/XPBar'
import { StreakCounter } from '../../src/components/gamification/StreakCounter'
import { DailyGoalRing } from '../../src/components/gamification/DailyGoalRing'

describe('XPBar', () => {
  it('renders level and progress', () => {
    render(<XPBar currentXp={45} nextLevelXp={100} level={3} />)
    expect(screen.getByText('Lv.3')).toBeInTheDocument()
    expect(screen.getByText('45/100')).toBeInTheDocument()
  })

  it('has progressbar role', () => {
    render(<XPBar currentXp={50} nextLevelXp={100} level={1} />)
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })
})

describe('StreakCounter', () => {
  it('renders streak days', () => {
    render(<StreakCounter days={5} />)
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('天连胜')).toBeInTheDocument()
  })
})

describe('DailyGoalRing', () => {
  it('renders progress percentage', () => {
    render(<DailyGoalRing progress={0.75} minutes={10} />)
    expect(screen.getByText('75%')).toBeInTheDocument()
    expect(screen.getByText('每日 10分钟')).toBeInTheDocument()
  })

  it('shows checkmark when complete', () => {
    render(<DailyGoalRing progress={1.0} minutes={15} />)
    expect(screen.getByText('100%')).toBeInTheDocument()
  })
})
