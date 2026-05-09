import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DiagnoseReportPage } from '../../src/pages/DiagnoseReportPage'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function renderAt(path: string, state?: any) {
  window.history.pushState(state, '', path)
  return render(
    <MemoryRouter initialEntries={[{ pathname: path, state }]}>
      <Routes>
        <Route path="/diagnose-report" element={<DiagnoseReportPage />} />
        <Route path="/diagnose" element={<div>Diagnose Page</div>} />
        <Route path="/" element={<div>Home</div>} />
      </Routes>
    </MemoryRouter>
  )
}

const sampleReport = {
  success: true,
  root_causes: [
    {
      kp_id: 'K01',
      kp_name: 'Integer Operations',
      priority: 0.85,
      error_count: 5,
      impacted_nodes: ['K03', 'K04'],
      reason: 'Integer Operations(K01) appeared in 5 related errors, affecting 2 downstream topics',
    },
    {
      kp_id: 'K02',
      kp_name: 'Fractions Basics',
      priority: 0.42,
      error_count: 2,
      impacted_nodes: ['K03'],
      reason: 'Fractions Basics(K02) appeared in 2 related errors',
    },
  ],
  total_records: 10,
  incorrect_count: 4,
}

describe('DiagnoseReportPage', () => {
  it('shows empty state when no report', () => {
    renderAt('/diagnose-report')
    expect(screen.getByText('暂无诊断报告')).toBeInTheDocument()
  })

  it('renders root causes', () => {
    renderAt('/diagnose-report', { report: sampleReport })
    expect(screen.getByText('Integer Operations')).toBeInTheDocument()
    expect(screen.getByText('Fractions Basics')).toBeInTheDocument()
  })

  it('shows total and incorrect counts', () => {
    renderAt('/diagnose-report', { report: sampleReport })
    expect(screen.getByText(/共.*10.*题/)).toBeInTheDocument()
    expect(screen.getAllByText(/4.*题错误/).length).toBeGreaterThanOrEqual(1)
  })

  it('renders priority badges', () => {
    renderAt('/diagnose-report', { report: sampleReport })
    expect(screen.getByText('高优先级')).toBeInTheDocument()
    expect(screen.getByText('中优先级')).toBeInTheDocument()
  })

  it('shows "no issues" when root_causes empty', () => {
    renderAt('/diagnose-report', { report: { ...sampleReport, root_causes: [] } })
    expect(screen.getByText('没有发现明显断点！')).toBeInTheDocument()
  })
})
