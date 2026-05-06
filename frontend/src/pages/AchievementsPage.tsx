import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/appStore'

interface AchievementInfo {
  key: string
  name: string
  desc: string
  category: string
  icon: string
  xp_bonus: number
}

const CATEGORY_LABELS: Record<string, string> = {
  streak: '🔥 连胜坚持',
  combo: '🎯 连击达人',
  speed: '⚡ 竞速达人',
  milestone: '📝 题量里程碑',
  knowledge: '🎓 知识掌握',
  special: '✨ 特殊成就',
}

export function AchievementsPage() {
  const navigate = useNavigate()
  const sid = useAppStore(s => s.activeStudentId)
  const [achievements, setAchievements] = useState<AchievementInfo[]>([])
  const [unlocked, setUnlocked] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/api/health/achievements').then(r => r.json()),
      fetch(`/api/rewards/status?student_id=${sid}`).then(r => r.json()),
    ]).then(([allAch, _]) => {
      const all = allAch.achievements || []
      setAchievements(all)
      fetch(`/api/rewards/status?student_id=${sid}`)
        .then(r => r.json())
        .then(status => {
          setUnlocked(new Set(status.unlocked_achievements || []))
        })
    }).finally(() => setLoading(false))
  }, [sid])

  const grouped: Record<string, AchievementInfo[]> = {}
  for (const a of achievements) {
    const cat = a.category || 'special'
    if (!grouped[cat]) grouped[cat] = []
    grouped[cat].push(a)
  }

  return (
    <div className="space-y-5 animate-slide-up pb-8">
      <header className="flex items-center justify-between pt-2">
        <button onClick={() => navigate(-1)} className="text-slate-400 text-sm min-h-[44px] px-2">← 返回</button>
        <h1 className="text-lg font-bold">成就徽章</h1>
        <div className="w-8" />
      </header>

      {loading ? (
        <div className="card text-center py-8">
          <p className="text-slate-400 text-sm">加载中...</p>
        </div>
      ) : (
        <div className="space-y-5">
          <div className="text-center py-2">
            <div className="text-3xl font-black text-yellow-400">{unlocked.size}</div>
            <div className="text-xs text-slate-500">已解锁 / {achievements.length} 总成就</div>
          </div>

          {Object.entries(grouped).map(([cat, items]) => (
            <div key={cat} className="card space-y-3">
              <h2 className="text-sm font-semibold text-slate-300">{CATEGORY_LABELS[cat] || cat}</h2>
              <div className="grid grid-cols-2 gap-2">
                {items.map(a => {
                  const isUnlocked = unlocked.has(a.key)
                  return (
                    <div
                      key={a.key}
                      className={`rounded-lg p-3 flex items-start gap-2 ${
                        isUnlocked ? 'bg-primary-500/10 border border-primary-500/30' : 'bg-slate-700/30 border border-slate-700 opacity-50'
                      }`}
                    >
                      <div className="text-2xl">{a.icon}</div>
                      <div className="min-w-0">
                        <p className={`text-sm font-semibold truncate ${isUnlocked ? 'text-white' : 'text-slate-500'}`}>
                          {a.name}
                        </p>
                        <p className="text-xs text-slate-500 truncate">{a.desc}</p>
                        <p className="text-xs text-slate-600 mt-0.5">+{a.xp_bonus} XP</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}

          {Object.keys(grouped).length === 0 && (
            <div className="card text-center py-8">
              <p className="text-slate-400 text-sm">暂无成就数据</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
