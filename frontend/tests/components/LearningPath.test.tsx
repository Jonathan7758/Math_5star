import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { LearningPathPage } from '../../src/pages/LearningPathPage'

const samplePath = [
  { order: 1, kp_id: 'K01', kp_name: 'Integer Operations', reason: '前置知识' },
  { order: 2, kp_id: 'K02', kp_name: 'Fractions Basics', reason: '薄弱环节' },
]

function renderAt(path: string, state?: any) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: path, state }]}>
      <Routes>
        <Route path="/learning-path" element={<LearningPathPage />} />
        <Route path="/quiz" element={<div>Quiz Page</div>} />
        <Route path="/" element={<div>Home</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('LearningPathPage', () => {
  it('shows empty state when no path', () => {
    renderAt('/learning-path')
    expect(screen.getByText('没有学习路径数据')).toBeInTheDocument()
  })

  it('renders path nodes', () => {
    renderAt('/learning-path', { path: samplePath, summary: 'Test summary' })
    expect(screen.getByText('Integer Operations')).toBeInTheDocument()
    expect(screen.getByText('Fractions Basics')).toBeInTheDocument()
    expect(screen.getByText('Test summary')).toBeInTheDocument()
  })

  it('shows step numbers', () => {
    renderAt('/learning-path', { path: samplePath, summary: '' })
    expect(screen.getByText('步骤 1')).toBeInTheDocument()
    expect(screen.getByText('步骤 2')).toBeInTheDocument()
  })

  it('renders start buttons for each node', () => {
    renderAt('/learning-path', { path: samplePath, summary: '' })
    const buttons = screen.getAllByText('开始练习')
    expect(buttons).toHaveLength(2)
  })

  it('has back to home button', () => {
    renderAt('/learning-path', { path: samplePath, summary: '' })
    expect(screen.getByText('返回首页')).toBeInTheDocument()
  })
})
