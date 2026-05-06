interface WeeklyStat {
  date: string
  minutes: number
  accuracy: number
  questions: number
}

interface StatsChartProps {
  data: WeeklyStat[]
}

export function StatsChart({ data }: StatsChartProps) {
  if (data.length === 0) {
    return <div className="text-center text-slate-500 py-8">暂无学习记录</div>
  }

  const maxMin = Math.max(...data.map((d) => d.minutes), 1)
  const maxQ = Math.max(...data.map((d) => d.questions), 1)

  return (
    <div className="space-y-4">
      <div>
        <div className="text-xs text-slate-500 mb-2">学习时长 (分钟)</div>
        <div className="flex items-end gap-1 h-20">
          {data.map((d, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-primary-500 rounded-t transition-all"
                style={{ height: `${(d.minutes / maxMin) * 100}%` }}
              />
              <span className="text-[10px] text-slate-500">{d.date.slice(5)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {data.slice().reverse().slice(0, 3).map((d, i) => (
          <div key={i} className="card space-y-1">
            <div className="text-xs text-slate-500">{d.date}</div>
            <div className="text-lg font-bold text-white">{d.minutes}min</div>
            <div className="text-xs text-slate-400">
              {d.questions}题 · 正确率 {Math.round(d.accuracy * 100)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
