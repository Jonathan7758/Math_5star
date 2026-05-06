interface XPBarProps {
  currentXp: number
  nextLevelXp: number
  level: number
}

export function XPBar({ currentXp, nextLevelXp, level }: XPBarProps) {
  const pct = Math.min((currentXp / nextLevelXp) * 100, 100)

  return (
    <div className="flex items-center gap-2" role="progressbar" aria-valuenow={currentXp} aria-valuemax={nextLevelXp}>
      <span className="text-xs font-bold text-primary-400 min-w-[32px]">Lv.{level}</span>
      <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary-500 to-primary-300 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-slate-500 min-w-[48px] text-right">{currentXp}/{nextLevelXp}</span>
    </div>
  )
}
