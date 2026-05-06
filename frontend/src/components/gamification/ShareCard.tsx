import { useRef } from 'react'

interface ShareCardProps {
  data: {
    questionsAnswered: number
    correctCount: number
    totalXp: number
    level: number
    streakDays: number
    combo: number
  }
  onClose: () => void
}

export function ShareCard({ data, onClose }: ShareCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)

  const accuracy = data.questionsAnswered > 0
    ? Math.round((data.correctCount / data.questionsAnswered) * 100)
    : 0

  const today = new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div className="space-y-4 max-w-xs w-full mx-4" onClick={(e) => e.stopPropagation()}>
        <div
          ref={cardRef}
          className="card bg-gradient-to-br from-slate-800 via-slate-800 to-primary-900/30 border border-primary-500/30 shadow-xl shadow-primary-500/10 space-y-4"
        >
          <div className="text-center">
            <div className="text-4xl mb-1">⭐</div>
            <h2 className="text-xl font-bold text-white">数学启明星</h2>
            <p className="text-slate-400 text-xs">{today}</p>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div className="text-center bg-slate-900/50 rounded-lg py-2">
              <div className="text-xl font-black text-white">{data.questionsAnswered}</div>
              <div className="text-[10px] text-slate-500">答题数</div>
            </div>
            <div className="text-center bg-slate-900/50 rounded-lg py-2">
              <div className="text-xl font-black text-green-400">{accuracy}%</div>
              <div className="text-[10px] text-slate-500">正确率</div>
            </div>
            <div className="text-center bg-slate-900/50 rounded-lg py-2">
              <div className="text-xl font-black text-primary-400">{data.totalXp}</div>
              <div className="text-[10px] text-slate-500">获得XP</div>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 px-2">
            <span>🔥 连胜 {data.streakDays}天</span>
            <span>🏆 最高 {data.combo}连击</span>
            <span>⭐ Lv.{data.level}</span>
          </div>

          <div className="text-center pt-1">
            <p className="text-primary-300 text-xs">
              每天10分钟 · 点亮知识的星空
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <button onClick={onClose} className="btn-secondary flex-1 text-sm">
            关闭
          </button>
        </div>
      </div>
    </div>
  )
}
