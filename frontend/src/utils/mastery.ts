export function masteryScoreColor(score: number): string {
  if (score >= 0.8) return 'bg-green-500 text-white'
  if (score >= 0.6) return 'bg-green-400/80 text-white'
  if (score >= 0.4) return 'bg-yellow-500 text-white'
  if (score > 0) return 'bg-orange-500 text-white'
  return 'bg-slate-700 text-slate-500'
}

export function masteryScoreHex(score: number): string {
  if (score >= 0.8) return '#22c55e'
  if (score >= 0.6) return '#4ade80'
  if (score >= 0.4) return '#eab308'
  if (score > 0) return '#f97316'
  return '#475569'
}
