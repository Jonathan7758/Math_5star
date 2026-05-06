import { useEffect, useState, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/appStore'
import { SpriteDisplay, STAGE_NAMES } from '../components/sprite/SpriteDisplay'
import { XPBar } from '../components/gamification/XPBar'
import { StreakCounter } from '../components/gamification/StreakCounter'
import { DailyGoalRing } from '../components/gamification/DailyGoalRing'
import { Fireworks } from '../components/vfx/Fireworks'
import { playSound } from '../utils/sound'

const TIME_GREETINGS: { start: number; end: number; greeting: string; emoji: string }[] = [
  { start: 6, end: 12, greeting: '早安！今天的数学冒险开始啦～', emoji: '🌅' },
  { start: 12, end: 18, greeting: '下午好！来活动一下大脑吧！', emoji: '☀️' },
  { start: 18, end: 22, greeting: '晚上好！睡前做几题，知识记得牢～', emoji: '🌙' },
  { start: 22, end: 24, greeting: '夜深了，做完题早点休息哦～', emoji: '🌟' },
  { start: 0, end: 6, greeting: '这么晚了还在学习，真厉害！', emoji: '✨' },
]

function getTimeGreeting(): { text: string; emoji: string } {
  const hour = new Date().getHours()
  const match = TIME_GREETINGS.find(g => hour >= g.start && hour < g.end)
  if (match) return { text: match.greeting, emoji: match.emoji }
  return { text: TIME_GREETINGS[0].greeting, emoji: TIME_GREETINGS[0].emoji }
}

export function HomePage() {
  const navigate = useNavigate()
  const { student, healthStatus, activeStudentId: sid, setActiveStudentId } = useAppStore()
  const [rewards, setRewards] = useState<any>(null)
  const [goalCelebrated, setGoalCelebrated] = useState(false)
  const [showFireworks, setShowFireworks] = useState(false)
  const [prevStage, setPrevStage] = useState<number>(0)

  const greeting = useMemo(() => getTimeGreeting(), [])

  const fetchRewards = useCallback(() => {
    fetch(`/api/rewards/status?student_id=${sid}`)
      .then(r => r.json())
      .then(data => {
        const newStage = data.sprite_stage ?? 0
        setRewards((prev: any) => {
          if (prev && prev.sprite_stage !== newStage) {
            setPrevStage(prev.sprite_stage)
          }
          return data
        })
        if (data.daily_goal_progress >= 100 && !goalCelebrated) {
          setGoalCelebrated(true)
          setShowFireworks(true)
          playSound('achievement')
          setTimeout(() => setShowFireworks(false), 4000)
        }
      })
      .catch(() => {})
  }, [goalCelebrated])

  useEffect(() => {
    fetchRewards()
  }, [])

  const isGoalComplete = rewards?.daily_goal_progress >= 100
  const spriteReaction = isGoalComplete && showFireworks ? 'celebrate' : 'idle'

  return (
    <div className="space-y-6 animate-slide-up">
      <header className="text-center pt-4">
        <div className="flex items-center justify-end mb-2">
          <select
            value={sid}
            onChange={(e) => { setActiveStudentId(Number(e.target.value)); fetchRewards() }}
            className="text-xs bg-slate-800 rounded-lg px-2 py-1 border border-slate-700 text-slate-300"
          >
            <option value={1}>学生 1</option>
            <option value={2}>学生 2</option>
            <option value={3}>学生 3</option>
          </select>
        </div>
        <SpriteDisplay
          stage={rewards?.sprite_stage ?? 0}
          stageName={rewards?.sprite_name ?? '星尘'}
          reaction={spriteReaction}
          size="lg"
          animateIn
          prevStage={prevStage}
        />
        <h1 className="text-2xl font-bold text-white mt-2">数学启明星</h1>
        <p className="text-slate-400 text-sm mt-1">点亮知识的星空</p>
        <div className="flex items-center justify-center gap-1.5 mt-2">
          <span>{greeting.emoji}</span>
          <p className="text-primary-300 text-xs">{greeting.text}</p>
        </div>
      </header>

      {isGoalComplete && showFireworks && (
        <div className="card border border-yellow-500/40 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 text-center py-3 space-y-1 relative overflow-hidden">
          <Fireworks show={showFireworks} />
          <div className="flex justify-center gap-1 text-lg relative z-10">
            {Array.from({ length: 5 }).map((_, i) => (
              <span key={i} className="animate-bounce" style={{ animationDelay: `${i * 0.15}s` }}>
                🎉
              </span>
            ))}
          </div>
          <p className="text-yellow-400 font-bold relative z-10">今日目标完成！太棒了！</p>
          <p className="text-slate-400 text-xs relative z-10">明天继续加油，连胜等你守护～</p>
        </div>
      )}

      {rewards && (
        <div className="card space-y-4">
          <XPBar
            currentXp={rewards.xp_current}
            nextLevelXp={rewards.xp_next}
            level={rewards.level}
          />
          <div className="flex items-center justify-between">
            <StreakCounter days={rewards.streak_days} />
            <DailyGoalRing progress={rewards.daily_goal_progress} minutes={rewards.daily_goal_minutes} />
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-yellow-400">⭐ {rewards.star_coins} 星币</span>
          </div>
        </div>
      )}

      {!rewards && (
        <div className="card text-center py-4">
          <p className="text-slate-400 text-sm">加载中...</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <button onClick={() => navigate('/diagnose')} className="card flex flex-col items-center py-6 hover:bg-slate-700 transition-colors">
          <span className="text-3xl mb-2">🔍</span><span className="font-semibold text-sm">开始诊断</span><span className="text-slate-500 text-xs mt-1">Diagnostic</span>
        </button>
        <button onClick={() => navigate('/quiz')} className="card flex flex-col items-center py-6 hover:bg-slate-700 transition-colors">
          <span className="text-3xl mb-2">✏️</span><span className="font-semibold text-sm">自由练习</span><span className="text-slate-500 text-xs mt-1">Practice</span>
        </button>
        <button onClick={() => navigate('/parent')} className="card flex flex-col items-center py-6 hover:bg-slate-700 transition-colors">
          <span className="text-3xl mb-2">📊</span><span className="font-semibold text-sm">家长看板</span><span className="text-slate-500 text-xs mt-1">Dashboard</span>
        </button>
        <button className="card flex flex-col items-center py-6 hover:bg-slate-700 transition-colors">
          <span className="text-3xl mb-2">🏆</span><span className="font-semibold text-sm">成就徽章</span><span className="text-slate-500 text-xs mt-1">Badges</span>
        </button>
      </div>

      <footer className="text-center text-slate-600 text-xs pb-4">
        v0.7.0 · {healthStatus ?? 'connected'}
      </footer>
    </div>
  )
}
