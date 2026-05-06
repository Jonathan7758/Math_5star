import { useEffect, useState } from 'react'
import { playSound } from '../../utils/sound'
import { hapticTap } from '../../utils/haptic'

interface LevelUpModalProps {
  level: number
  onClose: () => void
}

export function LevelUpModal({ level, onClose }: LevelUpModalProps) {
  const [show, setShow] = useState(false)

  useEffect(() => {
    if (level > 0) {
      playSound('levelup')
      hapticTap('heavy')
      setShow(true)
      const timer = setTimeout(() => {
        setShow(false)
        onClose()
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [level])

  if (!show) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="card text-center space-y-4 animate-scale-in max-w-xs w-full mx-4">
        <div className="text-6xl animate-bounce">🎉</div>
        <div>
          <p className="text-yellow-400 text-sm font-semibold">升级！</p>
          <p className="text-4xl font-black text-white mt-1">
            Lv.{level}
          </p>
          <p className="text-slate-400 text-sm mt-2">
            获得 {20 * level} 星币奖励
          </p>
        </div>
        <div className="flex flex-wrap gap-1 justify-center">
          {Array.from({ length: 6 }).map((_, i) => (
            <span key={i} className="text-lg animate-bounce" style={{ animationDelay: `${i * 0.15}s` }}>
              ✨
            </span>
          ))}
        </div>
        <p className="text-slate-500 text-xs">点击任意处关闭</p>
      </div>
    </div>
  )
}
