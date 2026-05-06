import { useState, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { SpriteDisplay } from '../components/sprite/SpriteDisplay'
import { AchievementToast } from '../components/gamification/AchievementToast'
import { LevelUpModal } from '../components/gamification/LevelUpModal'
import { playSound } from '../utils/sound'
import { hapticCorrect, hapticWrong, hapticCombo } from '../utils/haptic'
import { useAppStore } from '../store/appStore'

const MAX_HEARTS = 3

export function QuizPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const kpId = location.state?.kp_id
  const kpName = location.state?.kp_name
  const sid = useAppStore(s => s.activeStudentId)

  const [question, setQuestion] = useState<any>(null)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [feedback, setFeedback] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [hintLevel, setHintLevel] = useState(0)
  const [questionCount, setQuestionCount] = useState(0)
  const [correctCount, setCorrectCount] = useState(0)
  const [spriteReaction, setSpriteReaction] = useState<string>('idle')
  const [combo, setCombo] = useState(0)
  const [maxCombo, setMaxCombo] = useState(0)
  const [totalXp, setTotalXp] = useState(0)
  const [level, setLevel] = useState(1)
  const [spriteStage, setSpriteStage] = useState(0)
  const [prevSpriteStage, setPrevSpriteStage] = useState(0)
  const [spriteName, setSpriteName] = useState('星尘')
  const [streakDays, setStreakDays] = useState(0)

  const [hearts, setHearts] = useState(MAX_HEARTS)
  const [wrongOnQuestion, setWrongOnQuestion] = useState(0)

  const [achievement, setAchievement] = useState<string | null>(null)
  const [showLevelUp, setShowLevelUp] = useState(false)
  const [newLevel, setNewLevel] = useState(0)

  const [xpFlyText, setXpFlyText] = useState<string | null>(null)
  const [xpFlyKey, setXpFlyKey] = useState(0)
  const feedbackRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (xpFlyText) {
      const timer = setTimeout(() => setXpFlyText(null), 1500)
      return () => clearTimeout(timer)
    }
  }, [xpFlyText])

  const fetchQuestion = async () => {
    setLoading(true)
    try {
      const url = kpId ? `/api/exercise/next?student_id=${sid}&kp_id=${kpId}` : `/api/exercise/next?student_id=${sid}`
      const res = await fetch(url)
      const data = await res.json()
      setQuestion(data)
      setSelectedAnswer(null)
      setFeedback(null)
      setHintLevel(0)
      setWrongOnQuestion(0)
    } finally {
      setLoading(false)
    }
  }

  const submit = async () => {
    if (!selectedAnswer || !question || loading) return
    setLoading(true)
    try {
      const res = await fetch('/api/exercise/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: sid,
          question_id: question.question_id,
          answer: selectedAnswer,
          hint_level_used: hintLevel,
        }),
      })
      const data = await res.json()
      setFeedback(data)

      const newCombo = data.is_correct ? combo + 1 : 0
      setCombo(newCombo)
      if (newCombo > maxCombo) setMaxCombo(newCombo)

      const rewardRes = await fetch(`/api/rewards/process?student_id=${sid}&is_correct=${data.is_correct}&combo=${newCombo}`)
      const rewardData = await rewardRes.json()
      setSpriteReaction(rewardData.sprite_reaction || 'idle')
      if (rewardData.xp_earned > 0) {
        setTotalXp(rewardData.total_xp)
        if (data.is_correct) {
          setXpFlyKey(k => k + 1)
          setXpFlyText(`+${rewardData.xp_earned} XP`)
        }
      }
      if (rewardData.sprite_stage !== undefined && rewardData.sprite_stage !== spriteStage) {
        setPrevSpriteStage(spriteStage)
        setSpriteStage(rewardData.sprite_stage)
      }
      if (rewardData.sprite_name) setSpriteName(rewardData.sprite_name)
      if (rewardData.level) setLevel(rewardData.level)
      if (rewardData.streak_days != null) setStreakDays(rewardData.streak_days)

      if (rewardData.achievement_unlocked) {
        setAchievement(rewardData.achievement_unlocked)
      }

      if (rewardData.level_up) {
        setNewLevel(rewardData.level)
        setShowLevelUp(true)
      }

      if (data.is_correct) {
        playSound(newCombo >= 5 ? 'combo' : 'correct')
        hapticCombo(newCombo)
        setCorrectCount(c => c + 1)
        setQuestionCount((c) => c + 1)
        setHintLevel(0)
      } else {
        playSound('incorrect')
        hapticWrong()
        setHintLevel(data.hint_level)
        setWrongOnQuestion((w) => w + 1)
      }

      setTimeout(() => setSpriteReaction('idle'), 2000)
    } finally {
      setLoading(false)
    }
  }

  const handleContinue = () => {
    if (!feedback) return

    if (feedback.is_correct || (!feedback.should_retry)) {
      const remainingHearts = feedback.is_correct ? hearts : hearts - 1
      if (!feedback.is_correct) {
        setHearts(remainingHearts)
        setQuestionCount(c => c + 1)
      }
      setWrongOnQuestion(0)

      if (remainingHearts <= 0) {
        navigate('/daily-summary', {
          state: {
            questionsAnswered: questionCount + (feedback.is_correct ? 1 : 0),
            correctCount: correctCount + (feedback.is_correct ? 1 : 0),
            totalXp,
            level,
            streakDays,
            combo: maxCombo,
            heartsLeft: 0,
            spriteStage,
            spriteName,
          },
        })
      } else {
        fetchQuestion()
      }
    } else {
      setFeedback(null)
      setSelectedAnswer(null)
    }
  }

  if (loading && !question) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-pulse text-slate-400">加载题目中...</div>
      </div>
    )
  }

  if (!question) {
    return (
      <div className="space-y-6 animate-slide-up">
        <header className="pt-4">
          <h1 className="text-xl font-bold">{kpName || '练习模式'}</h1>
          {kpName && <p className="text-slate-400 text-sm mt-1">巩固知识点</p>}
        </header>
        <div className="card text-center py-8 space-y-4">
          <div className="text-5xl">✏️</div>
          <p className="text-slate-300">{kpName ? `开始练习 ${kpName}` : '准备开始答题'}</p>
          <button onClick={fetchQuestion} className="btn-primary w-full">
            开始
          </button>
        </div>
        <button onClick={() => navigate(-1)} className="btn-secondary w-full">
          返回
        </button>
      </div>
    )
  }

  const isCorrect = feedback?.is_correct

  return (
    <div className="space-y-4 animate-slide-up">
      <AchievementToast
        achievementKey={achievement}
        onClose={() => setAchievement(null)}
      />
      {showLevelUp && (
        <LevelUpModal
          level={newLevel}
          onClose={() => setShowLevelUp(false)}
        />
      )}

      <header className="flex items-center justify-between pt-2">
        <button onClick={() => {
          if (questionCount > 0) {
            navigate('/daily-summary', {
              state: {
                questionsAnswered: questionCount,
                correctCount,
                totalXp,
                level,
                streakDays,
                combo: maxCombo,
                heartsLeft: hearts,
                spriteStage,
                spriteName,
              },
            })
          } else {
            navigate(-1)
          }
        }} className="text-slate-400 text-sm min-h-[44px] px-2">
          ← 返回
        </button>

        <SpriteDisplay stage={spriteStage} stageName={spriteName} reaction={spriteReaction as any} size="sm" prevStage={prevSpriteStage} />

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-0.5">
            {Array.from({ length: MAX_HEARTS }).map((_, i) => (
              <span key={i} className={`text-sm ${i < hearts ? 'text-red-400' : 'text-slate-600'}`}>
                {i < hearts ? '❤️' : '🖤'}
              </span>
            ))}
          </div>
        </div>
      </header>

      <div className="flex items-center justify-between text-sm px-1">
        <span className="text-slate-400">第 {questionCount + 1} 题 · {question.kp_name || kpName}</span>
        {combo >= 3 && (
          <span className={`font-bold ${combo >= 10 ? 'text-yellow-400 text-lg' : combo >= 5 ? 'text-purple-400' : 'text-blue-400'}`}>
            {combo}连击🔥
          </span>
        )}
      </div>

      <div ref={feedbackRef} className={`card space-y-4 transition-all relative ${
        isCorrect === true ? 'ring-2 ring-green-500' :
        isCorrect === false ? 'ring-2 ring-orange-500 animate-wrong-shake' : ''
      }`}>
        {xpFlyText && (
          <div key={xpFlyKey} className="absolute top-4 right-4 z-10 animate-xp-fly text-green-400 font-bold text-lg">
            {xpFlyText}
          </div>
        )}

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded-full">
            Lv.{question.level}
          </span>
          <span>提示 {hintLevel}/3</span>
        </div>

        <p className="text-lg font-medium text-white leading-relaxed">
          {question.question}
        </p>

        {question.question_type === 'multiple_choice' && question.options ? (
          <div className="space-y-2">
            {question.options.map((opt: string, i: number) => {
              const isSelected = selectedAnswer === opt
              let cls = 'w-full text-left p-3 rounded-xl border border-slate-700 min-h-[44px] transition-colors '
              if (isSelected && !feedback) cls += 'bg-primary-500/20 border-primary-500 text-primary-300 '
              else if (isSelected && isCorrect) cls += 'bg-green-500/20 border-green-500 text-green-300 '
              else if (isSelected && !isCorrect) cls += 'bg-red-500/20 border-red-500 text-red-300 '
              else if (feedback) cls += 'text-slate-600 '
              else cls += 'hover:border-slate-500 hover:bg-slate-700/50 text-slate-300 '

              return (
                <button
                  key={i}
                  onClick={() => !feedback && setSelectedAnswer(opt)}
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
            onChange={(e) => setSelectedAnswer(e.target.value)}
            disabled={!!feedback}
            placeholder="输入答案..."
            className="w-full p-3 rounded-xl border bg-slate-900 min-h-[48px] text-white text-lg text-center border-slate-700 focus:border-primary-500"
          />
        )}

        {isCorrect && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 text-green-400 text-sm">
            正确！+{feedback.xp_earned} XP {combo >= 3 && `· ${combo}连击`}
          </div>
        )}

        {feedback?.hint && !isCorrect && (
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-3 text-orange-400 text-sm">
            {wrongOnQuestion <= 1 ? `💡 提示: ${feedback.hint}` : `📖 ${feedback.hint}`}
          </div>
        )}

        {feedback && !isCorrect && feedback.explanation && (
          <div className="bg-slate-700/50 rounded-xl p-3 text-slate-300 text-sm">
            {feedback.explanation}
          </div>
        )}

        {!feedback && hearts <= 1 && (
          <div className="text-center text-red-400 text-xs animate-pulse">
            ⚠️ 最后一次机会，小心作答！
          </div>
        )}
      </div>

      {!feedback ? (
        <button
          onClick={submit}
          disabled={!selectedAnswer || loading}
          className="btn-primary w-full"
        >
          {loading ? '检查中...' : '提交答案'}
        </button>
      ) : (
        <div className="space-y-3">
          <button onClick={handleContinue} disabled={loading} className="btn-primary w-full">
            {feedback.is_correct || !feedback.should_retry
              ? feedback.is_correct ? '下一题' : (hearts <= 1 ? '查看总结' : '下一题')
              : '再试一次'}
          </button>
          {hearts > 1 && feedback.should_retry && (
            <button onClick={() => {
              navigate('/daily-summary', {
                state: {
                  questionsAnswered: questionCount,
                  correctCount,
                  totalXp,
                  level,
                  streakDays,
                  combo: maxCombo,
                  heartsLeft: hearts,
                  spriteStage,
                  spriteName,
                },
              })
            }} className="btn-secondary w-full">
              结束练习
            </button>
          )}
          {!feedback.should_retry && hearts > 0 && (
            <button onClick={() => {
              navigate('/daily-summary', {
                state: {
                  questionsAnswered: questionCount + 1,
                  correctCount: correctCount + (isCorrect ? 1 : 0),
                  totalXp,
                  level,
                  streakDays,
                  combo: maxCombo,
                  heartsLeft: hearts,
                  spriteStage,
                  spriteName,
                },
              })
            }} className="btn-secondary w-full">
              查看总结
            </button>
          )}
        </div>
      )}
    </div>
  )
}
