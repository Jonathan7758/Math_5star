import { useState, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { SpriteDisplay } from '../components/sprite/SpriteDisplay'
import { AchievementToast } from '../components/gamification/AchievementToast'
import { LevelUpModal } from '../components/gamification/LevelUpModal'
import { QuestionCardEnhanced } from '../components/exercise/QuestionCardEnhanced'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { BackButton } from '../components/common/BackButton'
import { playSound } from '../utils/sound'
import { hapticCorrect, hapticWrong, hapticCombo } from '../utils/haptic'
import { useAppStore } from '../store/appStore'

const MAX_HEARTS = 3

function buildSummaryState(
  questionsAnswered: number, correctCount: number, totalXp: number, level: number,
  streakDays: number, combo: number, heartsLeft: number, spriteStage: number, spriteName: string,
) {
  return { questionsAnswered, correctCount, totalXp, level, streakDays, combo, heartsLeft, spriteStage, spriteName }
}

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
  const [spriteReaction, setSpriteReaction] = useState<'idle' | 'happy' | 'thinking' | 'encourage' | 'celebrate' | 'excited'>('idle')
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

  // Storyteller state
  const [storyText, setStoryText] = useState<string | null>(null)
  const [storyTheme, setStoryTheme] = useState<string | null>(null)
  const [storyThemeName, setStoryThemeName] = useState<string | null>(null)
  const [storyThemeIcon, setStoryThemeIcon] = useState<string | null>(null)
  const [availableThemes, setAvailableThemes] = useState<{ key: string; name: string; icon: string }[]>([])
  const [currentTheme, setCurrentTheme] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/exercise/themes')
      .then(r => r.json())
      .then(d => {
        if (d.themes) setAvailableThemes(d.themes)
      })
      .catch(() => {})
  }, [])

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

      // Fetch story version of the question
      if (data.question) {
        fetch('/api/exercise/story', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question_id: data.question_id, question_text: data.question, theme: currentTheme }),
        })
          .then(r => r.json())
          .then(s => {
            if (s.story_question) {
              setStoryText(s.story_question)
              setStoryTheme(s.theme)
              setStoryThemeName(s.theme_name)
              setStoryThemeIcon(s.theme_icon)
            }
          })
          .catch(() => {})
      }
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
        body: JSON.stringify({ student_id: sid, question_id: question.question_id, answer: selectedAnswer, hint_level_used: hintLevel }),
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
      if (rewardData.achievement_unlocked) setAchievement(rewardData.achievement_unlocked)
      if (rewardData.level_up) { setNewLevel(rewardData.level); setShowLevelUp(true) }

      if (data.is_correct) {
        playSound(newCombo >= 5 ? 'combo' : 'correct')
        hapticCombo(newCombo)
        setCorrectCount(c => c + 1)
        setQuestionCount(c => c + 1)
        setHintLevel(0)
      } else {
        playSound('incorrect')
        hapticWrong()
        setHintLevel(data.hint_level)
        setWrongOnQuestion(w => w + 1)
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
      if (!feedback.is_correct) { setHearts(remainingHearts); setQuestionCount(c => c + 1) }
      setWrongOnQuestion(0)
      if (remainingHearts <= 0) {
        navigate('/daily-summary', {
          state: buildSummaryState(questionCount + (feedback.is_correct ? 1 : 0), correctCount + (feedback.is_correct ? 1 : 0), totalXp, level, streakDays, maxCombo, 0, spriteStage, spriteName),
        })
      } else {
        fetchQuestion()
      }
    } else {
      setFeedback(null)
      setSelectedAnswer(null)
    }
  }

  if (loading && !question) return <LoadingSpinner text="加载题目中..." />

  if (!question) {
    return (
      <div className="space-y-6 animate-slide-up">
        <header className="pt-4 flex items-center gap-3">
          <SpriteDisplay stage={0} stageName="星尘" reaction="happy" size="md" animateIn />
          <div>
            <h1 className="text-xl font-bold text-white">{kpName || '自由练习'}</h1>
            {kpName && <p className="text-slate-400 text-sm mt-0.5">巩固知识点</p>}
          </div>
        </header>
        <div className="card text-center py-8 space-y-4 border border-slate-700/50 bg-gradient-to-b from-slate-800/80 to-slate-900/80">
          <div className="text-5xl">{kpName ? '🎯' : '✏️'}</div>
          <div>
            <p className="text-white font-semibold">{kpName ? `专攻: ${kpName}` : '准备好了吗？'}</p>
            <p className="text-slate-400 text-sm mt-1">答对获得XP和星币，让启小星成长！</p>
          </div>
          <button onClick={fetchQuestion} className="btn-primary w-full text-base">开始</button>
        </div>
        <button onClick={() => navigate(-1)} className="btn-secondary w-full">返回</button>
      </div>
    )
  }

  const isCorrect = feedback?.is_correct

  return (
    <div className="space-y-3 animate-slide-up pb-6">
      <AchievementToast achievementKey={achievement} onClose={() => setAchievement(null)} />
      {showLevelUp && <LevelUpModal level={newLevel} onClose={() => setShowLevelUp(false)} />}

      {/* Header bar */}
      <header className="flex items-center justify-between pt-3 pb-1">
        <BackButton onClick={() => {
          if (questionCount > 0) {
            navigate('/daily-summary', { state: buildSummaryState(questionCount, correctCount, totalXp, level, streakDays, maxCombo, hearts, spriteStage, spriteName) })
          } else { window.history.back() }
        }} />

        <div className="flex items-center gap-3">
          <SpriteDisplay stage={spriteStage} stageName={spriteName} reaction={spriteReaction} size="sm" prevStage={prevSpriteStage} />
          <div className="flex items-center gap-0.5">
            {Array.from({ length: MAX_HEARTS }).map((_, i) => (
              <span key={i} className={`text-sm transition-all ${i < hearts ? 'text-red-400 scale-110' : 'text-slate-600 opacity-50'}`}>
                {i < hearts ? '❤️' : '🖤'}
              </span>
            ))}
          </div>
        </div>
      </header>

      {/* Combo + KP info */}
      <div className="flex items-center justify-between px-1">
        <span className="text-xs text-slate-500">{question.kp_name || kpName}</span>
        {combo >= 3 && (
          <span className={`font-bold animate-bounce-slow ${combo >= 10 ? 'text-yellow-400 text-lg' : combo >= 5 ? 'text-purple-400' : 'text-blue-400'}`}>
            🔥 {combo}连击
          </span>
        )}
      </div>

      {/* Theme selector chips */}
      {availableThemes.length > 0 && (
        <div className="flex items-center gap-1 px-1 overflow-x-auto no-scrollbar">
          <button
            onClick={() => {
              setCurrentTheme(null)
              if (question) {
                fetch('/api/exercise/story', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ question_id: question.question_id, question_text: question.question, theme: null }),
                }).then(r => r.json()).then(s => {
                  if (s.story_question) { setStoryText(s.story_question); setStoryTheme(s.theme); setStoryThemeName(s.theme_name); setStoryThemeIcon(s.theme_icon) }
                }).catch(() => {})
              }
            }}
            className={`shrink-0 text-xs px-2.5 py-1 rounded-full border transition-colors ${
              !currentTheme ? 'bg-primary-500/20 border-primary-500/40 text-primary-300' : 'bg-slate-800 border-slate-700 text-slate-500'
            }`}
          >
            随机
          </button>
          {availableThemes.map(t => (
            <button
              key={t.key}
              onClick={() => {
                setCurrentTheme(t.key)
                if (question) {
                  fetch('/api/exercise/story', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question_id: question.question_id, question_text: question.question, theme: t.key }),
                  }).then(r => r.json()).then(s => {
                    if (s.story_question) { setStoryText(s.story_question); setStoryTheme(s.theme); setStoryThemeName(s.theme_name); setStoryThemeIcon(s.theme_icon) }
                  }).catch(() => {})
                }
              }}
              className={`shrink-0 text-xs px-2.5 py-1 rounded-full border transition-colors ${
                currentTheme === t.key ? 'bg-primary-500/20 border-primary-500/40 text-primary-300' : 'bg-slate-800 border-slate-700 text-slate-500'
              }`}
            >
              {t.icon} {t.name}
            </button>
          ))}
        </div>
      )}

      {/* Enhanced question card */}
      <QuestionCardEnhanced
        question={question}
        selectedAnswer={selectedAnswer}
        onSelect={(opt) => !feedback && setSelectedAnswer(opt)}
        feedback={feedback}
        hintLevel={wrongOnQuestion}
        combo={combo}
        questionIndex={questionCount + 1}
        mode="quiz"
        lowHearts={!feedback && hearts <= 1}
        xpFlyText={xpFlyText}
        xpFlyKey={xpFlyKey}
        storyText={storyText || undefined}
        themeName={storyThemeName || undefined}
        themeIcon={storyThemeIcon || undefined}
        themeKey={storyTheme || undefined}
      />

      {/* Action buttons */}
      {!feedback ? (
        <button onClick={submit} disabled={!selectedAnswer || loading} className="btn-primary w-full text-base">
          {loading ? '检查中...' : '提交答案'}
        </button>
      ) : (
        <div className="space-y-2.5">
          <button onClick={handleContinue} disabled={loading} className="btn-primary w-full text-base">
            {feedback.is_correct || !feedback.should_retry
              ? feedback.is_correct ? '下一题 ✨' : (hearts <= 1 ? '查看总结 📊' : '下一题')
              : '再试一次 🔄'}
          </button>
          {hearts > 1 && feedback.should_retry && (
            <button onClick={() => {
              navigate('/daily-summary', { state: buildSummaryState(questionCount, correctCount, totalXp, level, streakDays, maxCombo, hearts, spriteStage, spriteName) })
            }} className="btn-secondary w-full">结束练习</button>
          )}
          {!feedback.should_retry && hearts > 0 && (
            <button onClick={() => {
              navigate('/daily-summary', { state: buildSummaryState(questionCount + 1, correctCount + (isCorrect ? 1 : 0), totalXp, level, streakDays, maxCombo, hearts, spriteStage, spriteName) })
            }} className="btn-secondary w-full">查看总结</button>
          )}
        </div>
      )}
    </div>
  )
}
