interface Question {
  question_id: string
  knowledge_point_id: string
  level: number
  question: string
  options: string[] | null
  question_type: string
  kp_name: string
}

interface FeedbackFull {
  is_correct: boolean
  correct_answer: string
  xp_earned: number
  hint: string | null
  explanation: string | null
}

interface Props {
  question: Question
  selectedAnswer: string | null
  onSelect: (answer: string) => void
  disabled: boolean
  feedback: FeedbackFull | null
  hint: string | null
  explanation: string | null
}

export function QuestionCard({ question, selectedAnswer, onSelect, disabled, feedback, hint }: Props) {
  const isCorrect = feedback?.is_correct ?? null

  return (
    <div className={`card space-y-4 transition-all ${
      isCorrect === true ? 'ring-2 ring-green-500 animate-correct-flash' :
      isCorrect === false ? 'ring-2 ring-orange-500 animate-wrong-shake' : ''
    }`}>
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <span className="bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded-full">
          Lv.{question.level}
        </span>
        <span>{question.kp_name || question.knowledge_point_id}</span>
      </div>

      <p className="text-lg font-medium text-white leading-relaxed">
        {question.question}
      </p>

      {question.question_type === 'multiple_choice' && question.options ? (
        <div className="space-y-2">
          {question.options.map((opt, i) => {
            const isSelected = selectedAnswer === opt
            const isCorrectOpt = feedback && opt === feedback.correct_answer
            const isWrongSelected = feedback && isSelected && !feedback.is_correct

            let btnClass = 'w-full text-left p-3 rounded-xl border border-slate-700 min-h-[44px] transition-colors '
            if (isWrongSelected) btnClass += 'bg-red-500/20 border-red-500 text-red-300 '
            else if (isCorrectOpt) btnClass += 'bg-green-500/20 border-green-500 text-green-300 '
            else if (isSelected) btnClass += 'bg-primary-500/20 border-primary-500 text-primary-300 '
            else if (disabled) btnClass += 'text-slate-600 '
            else btnClass += 'hover:border-slate-500 hover:bg-slate-700/50 text-slate-300 '

            return (
              <button
                key={i}
                onClick={() => onSelect(opt)}
                disabled={disabled}
                className={btnClass}
              >
                {opt}
              </button>
            )
          })}
        </div>
      ) : (
        <div className="space-y-2">
          <input
            type="text"
            inputMode="decimal"
            value={selectedAnswer ?? ''}
            onChange={(e) => onSelect(e.target.value)}
            disabled={disabled}
            placeholder="Type your answer..."
            className={`w-full p-3 rounded-xl border bg-slate-900 min-h-[48px] text-white text-lg text-center transition-colors ${
              isCorrect === true ? 'border-green-500 bg-green-500/10' :
              isCorrect === false ? 'border-orange-500 bg-orange-500/10' :
              'border-slate-700 focus:border-primary-500'
            }`}
          />
        </div>
      )}

      {feedback && feedback.is_correct && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 text-green-400 text-sm">
          Correct!
        </div>
      )}

      {hint && !feedback?.is_correct && (
        <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-3 text-orange-400 text-sm">
          {hint}
        </div>
      )}

      {feedback?.is_correct === false && feedback?.explanation && (
        <div className="bg-slate-700/50 rounded-xl p-3 text-slate-300 text-sm">
          {feedback.explanation}
        </div>
      )}
    </div>
  )
}
