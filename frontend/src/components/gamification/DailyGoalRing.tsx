interface DailyGoalRingProps {
  progress: number
  minutes: number
}

export function DailyGoalRing({ progress, minutes }: DailyGoalRingProps) {
  const pct = Math.round(progress * 100)
  const radius = 18
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (progress * circumference)

  return (
    <div className="flex items-center gap-3">
      <svg width="44" height="44" viewBox="0 0 44 44">
        <circle cx="22" cy="22" r={radius} fill="none" stroke="#1e293b" strokeWidth="4" />
        <circle
          cx="22" cy="22" r={radius} fill="none" stroke={progress >= 1 ? '#22c55e' : '#f59e0b'}
          strokeWidth="4" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 22 22)"
          className="transition-all duration-500"
        />
        {progress >= 1 && (
          <text x="22" y="27" textAnchor="middle" fill="#22c55e" fontSize="16">✓</text>
        )}
      </svg>
      <div>
        <div className="text-sm font-bold text-white">{pct}%</div>
        <div className="text-xs text-slate-400">每日 {minutes}分钟</div>
      </div>
    </div>
  )
}
