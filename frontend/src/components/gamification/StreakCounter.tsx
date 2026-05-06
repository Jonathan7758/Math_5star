interface StreakCounterProps {
  days: number
  isActive?: boolean
}

export function StreakCounter({ days, isActive = true }: StreakCounterProps) {
  return (
    <div className="flex items-center gap-2">
      <span className={`text-lg ${days >= 3 ? 'text-orange-400' : 'text-slate-500'}`}>
        {days >= 3 ? '🔥' : '🔥'}
      </span>
      <span className="text-white font-bold">{days}</span>
      <span className="text-xs text-slate-400">天连胜</span>
      {!isActive && (
        <span className="text-xs text-slate-600">(今日未学习)</span>
      )}
    </div>
  )
}
