import { MultipleChoiceOptions } from './MultipleChoiceOptions'
import { AnswerInput } from './AnswerInput'
import { FeedbackPanel } from './FeedbackPanel'

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
    }`} aria-live="polite">
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
        <MultipleChoiceOptions
          options={question.options}
          selectedAnswer={selectedAnswer}
          onSelect={onSelect}
          disabled={disabled}
          feedback={feedback}
          highlightCorrect
        />
      ) : (
        <AnswerInput
          value={selectedAnswer ?? ''}
          onChange={onSelect}
          disabled={disabled}
          placeholder="Type your answer..."
          ariaLabel="Type your answer"
          isCorrect={isCorrect}
        />
      )}

      <FeedbackPanel
        isCorrect={isCorrect}
        hint={hint}
        explanation={feedback?.is_correct === false ? feedback.explanation : null}
        successText="Correct!"
      />
    </div>
  )
}
