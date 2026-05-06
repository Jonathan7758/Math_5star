import { useNavigate } from 'react-router-dom'
import { useQuizStore } from '../store/quizStore'
import { useAppStore } from '../store/appStore'

export function DiagnosePage() {
  const navigate = useNavigate()
  const sid = useAppStore(s => s.activeStudentId)
  const { currentQuestion, selectedAnswer, feedback, isSubmitting, diagnoseRecords, setQuestion, selectAnswer, setFeedback, setSubmitting, addDiagnoseRecord, clearDiagnoseRecords, resetQuiz } = useQuizStore()

  const fetchNext = async () => {
    setSubmitting(true)
    try {
      const res = await fetch(`/api/exercise/next?student_id=${sid}`)
      const data = await res.json()
      setQuestion(data)
    } finally {
      setSubmitting(false)
    }
  }

  const submit = async () => {
    if (!selectedAnswer || !currentQuestion || isSubmitting) return
    setSubmitting(true)
    try {
      const res = await fetch('/api/exercise/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: sid,
          question_id: currentQuestion.question_id,
          answer: selectedAnswer,
        }),
      })
      const data = await res.json()
      setFeedback({
        is_correct: data.is_correct,
        correct_answer: data.correct_answer,
        xp_earned: 0,
        hint: data.hint,
        explanation: data.explanation || null,
      })
      addDiagnoseRecord({
        kp_id: currentQuestion.knowledge_point_id,
        is_correct: data.is_correct,
      })
    } finally {
      setSubmitting(false)
    }
  }

  const finishDiagnostic = async () => {
    setSubmitting(true)
    try {
      const res = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: sid, records: diagnoseRecords }),
      })
      const report = await res.json()
      resetQuiz()
      navigate('/diagnose-report', { state: { report } })
    } catch {
      setSubmitting(false)
    }
  }

  const questionCount = diagnoseRecords.length

  if (!currentQuestion) {
    return (
      <div className="space-y-6 animate-slide-up">
        <header className="text-center pt-4">
          <h1 className="text-2xl font-bold">知识诊断</h1>
          <p className="text-slate-400 text-sm mt-1">
            完成下面的题目，系统将找出你的知识断点
          </p>
        </header>

        <div className="card text-center py-8 space-y-4">
          <div className="text-5xl">🔍</div>
          <p className="text-slate-300">准备开始诊断测试</p>
          <p className="text-slate-500 text-sm">
            包含 {questionCount} 个知识点的代表题目
          </p>
          <button onClick={fetchNext} disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? '加载中...' : '开始诊断'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 animate-slide-up">
      <header className="flex items-center justify-between pt-2">
        <h1 className="text-lg font-bold">知识诊断</h1>
        <span className="text-slate-400 text-sm">
          第 {questionCount} 题
        </span>
      </header>

      <div className="card space-y-4">
        <p className="text-lg text-white leading-relaxed">{currentQuestion.question}</p>

        {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options ? (
          <div className="space-y-2">
            {currentQuestion.options.map((opt: string, i: number) => {
              const isSelected = selectedAnswer === opt
              let cls = 'w-full text-left p-3 rounded-xl border border-slate-700 min-h-[44px] transition-colors '
              if (isSelected && !feedback) cls += 'bg-primary-500/20 border-primary-500 text-primary-300 '
              else if (isSelected && feedback?.is_correct) cls += 'bg-green-500/20 border-green-500 text-green-300 '
              else if (isSelected && feedback && !feedback.is_correct) cls += 'bg-red-500/20 border-red-500 text-red-300 '
              else if (feedback) cls += 'text-slate-600 '
              else cls += 'hover:border-slate-500 hover:bg-slate-700/50 text-slate-300 '

              return (
                <button
                  key={i}
                  onClick={() => !feedback && selectAnswer(opt)}
                  disabled={!!feedback}
                  className={cls}
                >
                  {opt}
                </button>
              )
            })}
          </div>
        ) : (
          <input
            type="text"
            inputMode="decimal"
            value={selectedAnswer ?? ''}
            onChange={(e) => selectAnswer(e.target.value)}
            disabled={!!feedback}
            placeholder="输入答案..."
            aria-label="输入答案"
            className="w-full p-3 rounded-xl border bg-slate-900 min-h-[48px] text-white text-lg text-center border-slate-700 focus:border-primary-500"
          />
        )}

        {feedback?.is_correct && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 text-green-400 text-sm" role="status">
            正确！
          </div>
        )}
        {feedback?.hint && !feedback.is_correct && (
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-3 text-orange-400 text-sm" role="status">
            {feedback.hint}
          </div>
        )}
        {feedback && !feedback.is_correct && feedback.explanation && (
          <div className="bg-slate-700/50 rounded-xl p-3 text-slate-300 text-sm" role="status">
            {feedback.explanation}
          </div>
        )}
      </div>

      {!feedback ? (
        <button
          onClick={submit}
          disabled={!selectedAnswer || isSubmitting}
          className="btn-primary w-full"
        >
          {isSubmitting ? '检查中...' : '提交答案'}
        </button>
      ) : (
        <div className="space-y-3">
          <button onClick={fetchNext} disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? '加载...' : '下一题'}
          </button>
          <button
            onClick={finishDiagnostic}
            className="btn-secondary w-full"
          >
            完成诊断 ({diagnoseRecords.length} 题已答)
          </button>
        </div>
      )}
    </div>
  )
}
