import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuizStore } from '../store/quizStore'
import { useAppStore } from '../store/appStore'
import { SpriteDisplay } from '../components/sprite/SpriteDisplay'
import { QuestionCardEnhanced } from '../components/exercise/QuestionCardEnhanced'

export function DiagnosePage() {
  const navigate = useNavigate()
  const sid = useAppStore(s => s.activeStudentId)
  const { currentQuestion, selectedAnswer, feedback, isSubmitting, diagnoseRecords, setQuestion, selectAnswer, setFeedback, setSubmitting, addDiagnoseRecord, resetQuiz } = useQuizStore()
  const [spriteReaction, setSpriteReaction] = useState<'idle' | 'happy' | 'thinking' | 'encourage' | 'celebrate' | 'excited'>('idle')

  const fetchNext = async () => {
    setSubmitting(true)
    try {
      const res = await fetch(`/api/exercise/next?student_id=${sid}`)
      const data = await res.json()
      setQuestion(data)
      setSpriteReaction('idle')
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
      setSpriteReaction(data.is_correct ? 'happy' : 'thinking')
      setTimeout(() => setSpriteReaction('idle'), 2500)
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
  const MIN_QUESTIONS = 5

  if (!currentQuestion) {
    return (
      <div className="space-y-6 animate-slide-up">
        <header className="text-center pt-4">
          <div className="flex justify-center mb-3">
            <SpriteDisplay stage={0} stageName="星尘" reaction="idle" size="md" animateIn />
          </div>
          <h1 className="text-2xl font-bold text-white">知识诊断</h1>
          <p className="text-slate-400 text-sm mt-1">
            启小星帮你找出需要加强的知识点
          </p>
        </header>

        <div className="card text-center py-8 space-y-4 border border-slate-700/50 bg-gradient-to-b from-slate-800/80 to-slate-900/80">
          <div className="text-5xl">🔍</div>
          <div>
            <p className="text-white font-semibold text-lg">准备好了吗？</p>
            <p className="text-slate-400 text-sm mt-1">
              系统会根据你的答题情况，找出薄弱环节
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 text-xs text-slate-500">
            <span>📝 覆盖20个知识点</span>
            <span>⏱️ 约5-10分钟</span>
          </div>
          <button onClick={fetchNext} disabled={isSubmitting} className="btn-primary w-full text-base">
            {isSubmitting ? '加载中...' : '开始诊断'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3 animate-slide-up pb-6">
      {/* Header */}
      <header className="flex items-center justify-between pt-3 pb-1">
        <div className="flex items-center gap-2">
          <SpriteDisplay stage={0} stageName="星尘" reaction={spriteReaction} size="sm" />
          <div>
            <h1 className="text-base font-bold text-white">知识诊断</h1>
            <span className="text-xs text-slate-500">已答 {questionCount} 题</span>
          </div>
        </div>
        <button onClick={finishDiagnostic} disabled={isSubmitting || questionCount < MIN_QUESTIONS} className="text-xs text-primary-400 bg-primary-500/10 px-3 py-1.5 rounded-full border border-primary-500/20 disabled:opacity-30 min-h-[36px]">
          {questionCount < MIN_QUESTIONS ? `还需${MIN_QUESTIONS - questionCount}题` : '完成诊断'}
        </button>
      </header>

      {/* Question */}
      <QuestionCardEnhanced
        question={currentQuestion}
        selectedAnswer={selectedAnswer}
        onSelect={(opt) => !feedback && selectAnswer(opt)}
        feedback={feedback}
        hintLevel={0}
        questionIndex={questionCount + 1}
        totalQuestions={Math.max(MIN_QUESTIONS, questionCount + 1)}
        mode="diagnose"
      />

      {/* Action buttons */}
      {!feedback ? (
        <button
          onClick={submit}
          disabled={!selectedAnswer || isSubmitting}
          className="btn-primary w-full text-base"
        >
          {isSubmitting ? '检查中...' : '提交答案'}
        </button>
      ) : (
        <div className="space-y-2.5">
          <button onClick={fetchNext} disabled={isSubmitting} className="btn-primary w-full text-base">
            {isSubmitting ? '加载...' : '下一题'}
          </button>
          {questionCount >= MIN_QUESTIONS && (
            <button onClick={finishDiagnostic} className="btn-secondary w-full">
              完成诊断
            </button>
          )}
        </div>
      )}
    </div>
  )
}
