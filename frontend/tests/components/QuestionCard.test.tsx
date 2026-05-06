import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { QuestionCard } from '../../src/components/exercise/QuestionCard'

const baseQuestion = {
  question_id: 'Q1',
  knowledge_point_id: 'K01',
  level: 1,
  question: 'What is 2 + 2?',
  options: ['3', '4', '5', '6'],
  question_type: 'multiple_choice' as const,
  kp_name: 'Addition',
}

describe('QuestionCard', () => {
  it('renders question text', () => {
    render(
      <QuestionCard question={baseQuestion} selectedAnswer={null} onSelect={vi.fn()} disabled={false} feedback={null} hint={null} explanation={null} />
    )
    expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument()
  })

  it('renders all options', () => {
    render(
      <QuestionCard question={baseQuestion} selectedAnswer={null} onSelect={vi.fn()} disabled={false} feedback={null} hint={null} explanation={null} />
    )
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('6')).toBeInTheDocument()
  })

  it('calls onSelect when option clicked', () => {
    const onSelect = vi.fn()
    render(
      <QuestionCard question={baseQuestion} selectedAnswer={null} onSelect={onSelect} disabled={false} feedback={null} hint={null} explanation={null} />
    )
    fireEvent.click(screen.getByText('4'))
    expect(onSelect).toHaveBeenCalledWith('4')
  })

  it('disables options when disabled', () => {
    const onSelect = vi.fn()
    render(
      <QuestionCard question={baseQuestion} selectedAnswer={null} onSelect={onSelect} disabled={true} feedback={null} hint={null} explanation={null} />
    )
    const buttons = screen.getAllByRole('button')
    buttons.forEach((btn) => expect(btn).toBeDisabled())
  })

  it('shows correct feedback', () => {
    render(
      <QuestionCard
        question={baseQuestion}
        selectedAnswer="4"
        onSelect={vi.fn()}
        disabled={true}
        feedback={{ is_correct: true } as any}
        hint={null}
        explanation={null}
      />
    )
    expect(screen.getByText('Correct!')).toBeInTheDocument()
  })

  it('shows hint when wrong', () => {
    render(
      <QuestionCard
        question={baseQuestion}
        selectedAnswer="3"
        onSelect={vi.fn()}
        disabled={true}
        feedback={{ is_correct: false } as any}
        hint="Try adding the numbers"
        explanation={null}
      />
    )
    expect(screen.getByText('Try adding the numbers')).toBeInTheDocument()
  })

  it('renders text input for numeric type', () => {
    const numericQ = { ...baseQuestion, question_type: 'numeric', options: null }
    render(
      <QuestionCard question={numericQ} selectedAnswer={null} onSelect={vi.fn()} disabled={false} feedback={null} hint={null} explanation={null} />
    )
    expect(screen.getByPlaceholderText('Type your answer...')).toBeInTheDocument()
  })
})
