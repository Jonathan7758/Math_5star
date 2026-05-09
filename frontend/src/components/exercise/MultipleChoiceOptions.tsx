interface FeedbackState {
  is_correct?: boolean
  correct_answer?: string
}

interface MultipleChoiceOptionsProps {
  options: string[]
  selectedAnswer: string | null
  onSelect: (opt: string) => void
  disabled: boolean
  feedback?: boolean | FeedbackState | null
  highlightCorrect?: boolean
  className?: string
}

export function MultipleChoiceOptions({
  options,
  selectedAnswer,
  onSelect,
  disabled,
  feedback,
  highlightCorrect,
  className = '',
}: MultipleChoiceOptionsProps) {
  const fbIsCorrect = typeof feedback === 'object' ? feedback?.is_correct : feedback
  const fbCorrect = typeof feedback === 'object' ? feedback?.correct_answer : null

  return (
    <div className={`space-y-2 ${className}`}>
      {options.map((opt, i) => {
        const isSelected = selectedAnswer === opt
        const isCorrectOpt = highlightCorrect && fbCorrect === opt
        const isWrongSelected = isSelected && fbIsCorrect === false

        let cls = 'w-full text-left p-3 rounded-xl border border-slate-700 min-h-[44px] transition-colors '
        if (isWrongSelected) cls += 'bg-red-500/20 border-red-500 text-red-300 '
        else if (isCorrectOpt) cls += 'bg-green-500/20 border-green-500 text-green-300 '
        else if (isSelected && fbIsCorrect === undefined) cls += 'bg-primary-500/20 border-primary-500 text-primary-300 '
        else if (isSelected && fbIsCorrect) cls += 'bg-green-500/20 border-green-500 text-green-300 '
        else if (disabled) cls += 'text-slate-600 '
        else cls += 'hover:border-slate-500 hover:bg-slate-700/50 text-slate-300 '

        return (
          <button
            key={i}
            onClick={() => onSelect(opt)}
            disabled={disabled}
            className={cls}
          >
            {opt}
          </button>
        )
      })}
    </div>
  )
}
