import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { ParentDashboardPage } from '../../src/pages/ParentDashboardPage'
import { MasteryHeatmap } from '../../src/components/parent/MasteryHeatmap'
import { StatsChart } from '../../src/components/parent/StatsChart'

describe('MasteryHeatmap', () => {
  it('shows empty state', () => {
    render(<MasteryHeatmap data={[]} />)
    expect(screen.getByText('暂无掌握度数据')).toBeInTheDocument()
  })

  it('renders items with color coding', () => {
    render(<MasteryHeatmap data={[
      { kp_id: 'K01', kp_name: 'Integers', grade: 'Y7', score: 0.9, total_attempts: 10 },
      { kp_id: 'K02', kp_name: 'Fractions', grade: 'Y7', score: 0.3, total_attempts: 5 },
    ]} />)
    expect(screen.getByText('Integers')).toBeInTheDocument()
    expect(screen.getByText('Fractions')).toBeInTheDocument()
  })
})

describe('StatsChart', () => {
  it('shows empty state', () => {
    render(<StatsChart data={[]} />)
    expect(screen.getByText('暂无学习记录')).toBeInTheDocument()
  })

  it('renders weekly data', () => {
    render(<StatsChart data={[
      { date: '2026-05-01', minutes: 15, accuracy: 0.8, questions: 10 },
      { date: '2026-05-02', minutes: 12, accuracy: 0.9, questions: 8 },
    ]} />)
    expect(screen.getByText('15min')).toBeInTheDocument()
  })
})

describe('ParentDashboardPage', () => {
  it('shows PIN login initially', () => {
    render(
      <MemoryRouter initialEntries={['/parent']}>
        <Routes>
          <Route path="/parent" element={<ParentDashboardPage />} />
          <Route path="/" element={<div>Home</div>} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText('家长看板')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('输入PIN码')).toBeInTheDocument()
  })
})
