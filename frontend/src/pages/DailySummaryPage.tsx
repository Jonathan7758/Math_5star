import { useNavigate, useLocation } from 'react-router-dom'
import { SpriteDisplay } from '../components/sprite/SpriteDisplay'

interface SummaryData {
  questionsAnswered: number
  correctCount: number
  totalXp: number
  level: number
  streakDays: number
  combo: number
  heartsLeft: number
  spriteStage: number
  spriteName: string
}

export function DailySummaryPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const summary: SummaryData = location.state || {}

  const accuracy = summary.questionsAnswered > 0
    ? Math.round((summary.correctCount / summary.questionsAnswered) * 100)
    : 0

  const getMessage = () => {
    if (summary.heartsLeft === 0) return '休息一下，明天继续加油！'
    if (accuracy === 100) return '全对！！你是天才吗？！'
    if (accuracy >= 80) return '很棒的一天！明天继续加油～'
    if (accuracy >= 50) return '不错的练习，多做几题会更好！'
    return '每一次错误都让你离正确更近一步！'
  }

  const getEncouragement = () => {
    if (summary.heartsLeft === 0) return '今天的心用完了，好好休息，知识会在睡梦中巩固哦～'
    return '明天见，连胜等你守护！'
  }

  return (
    <div className="space-y-6 animate-slide-up pb-8">
      <header className="text-center pt-6">
        <SpriteDisplay
          stage={summary.spriteStage ?? 0}
          stageName={summary.spriteName ?? '星尘'}
          reaction="celebrate"
          size="lg"
        />
        <h1 className="text-2xl font-bold text-white mt-3">今日学习总结</h1>
        <p className="text-slate-400 text-sm mt-2">{getMessage()}</p>
      </header>

      <div className="grid grid-cols-2 gap-3">
        <div className="card text-center py-4">
          <div className="text-3xl font-black text-white">{summary.questionsAnswered ?? 0}</div>
          <div className="text-xs text-slate-500 mt-1">今日答题</div>
        </div>
        <div className="card text-center py-4">
          <div className="text-3xl font-black text-green-400">{accuracy}%</div>
          <div className="text-xs text-slate-500 mt-1">正确率</div>
        </div>
        <div className="card text-center py-4">
          <div className="text-3xl font-black text-primary-400">{summary.totalXp ?? 0}</div>
          <div className="text-xs text-slate-500 mt-1">总XP</div>
        </div>
        <div className="card text-center py-4">
          <div className="text-3xl font-black text-yellow-400">{summary.level ?? 1}</div>
          <div className="text-xs text-slate-500 mt-1">等级</div>
        </div>
      </div>

      <div className="card space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">🔥 连胜</span>
          <span className="text-white font-semibold">{summary.streakDays ?? 0} 天</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">最高连击</span>
          <span className="text-white font-semibold">{summary.combo ?? 0} 连击</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">❤️ 剩余爱心</span>
          <span className="text-white font-semibold">{summary.heartsLeft ?? 0} 心</span>
        </div>
      </div>

      <p className="text-center text-slate-500 text-sm italic">
        "{getEncouragement()}"
      </p>

      <div className="space-y-3">
        <button onClick={() => navigate('/quiz')} className="btn-primary w-full">
          继续练习
        </button>
        <button onClick={() => navigate('/')} className="btn-secondary w-full">
          返回首页
        </button>
      </div>
    </div>
  )
}
