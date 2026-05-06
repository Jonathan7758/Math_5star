import { useEffect, useState } from 'react'
import { playSound } from '../../utils/sound'

interface AchievementToastProps {
  achievementKey: string | null
  achievementName?: string
  achievementDesc?: string
  onClose: () => void
}

const ACHIEVEMENT_INFO: Record<string, { name: string; desc: string; icon: string }> = {
  first_correct: { name: '初试锋芒', desc: '答对第一道题', icon: '⭐' },
  perfect_10: { name: '十全十美', desc: '连续答对10题', icon: '💎' },
  streak_3_days: { name: '三天打鱼', desc: '连续学习3天', icon: '🔥' },
  streak_7_days: { name: '七日之约', desc: '连续学习7天', icon: '🏆' },
  speed_demon: { name: '闪电侠', desc: '5秒内答对', icon: '⚡' },
}

export function AchievementToast({ achievementKey, achievementName, achievementDesc, onClose }: AchievementToastProps) {
  const [visible, setVisible] = useState(false)
  const [hiding, setHiding] = useState(false)

  useEffect(() => {
    if (achievementKey) {
      playSound('achievement')
      setVisible(true)
      const hideTimer = setTimeout(() => {
        setHiding(true)
        setTimeout(() => {
          setVisible(false)
          setHiding(false)
          onClose()
        }, 500)
      }, 3000)
      return () => clearTimeout(hideTimer)
    }
  }, [achievementKey])

  if (!visible) return null

  const info = achievementKey ? ACHIEVEMENT_INFO[achievementKey] : null
  const name = achievementName || info?.name || '成就解锁'
  const desc = achievementDesc || info?.desc || ''
  const icon = info?.icon || '🎖️'

  return (
    <div
      className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-sm ${
        hiding ? 'animate-slide-up-out opacity-0' : 'animate-slide-down-in'
      }`}
    >
      <div className="card bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/40 shadow-lg shadow-yellow-500/10">
        <div className="flex items-center gap-3">
          <div className="text-4xl animate-bounce-slow">{icon}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-yellow-400 font-semibold">成就解锁！</p>
            <p className="text-white font-bold text-lg">{name}</p>
            <p className="text-slate-400 text-xs mt-0.5">{desc}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
