interface WeeklyStat {
  date: string
  minutes: number
  accuracy: number
  questions: number
}

interface StatsChartProps {
  data: WeeklyStat[]
}

function formatDate(d: string): string {
  const parts = d.split('-')
  if (parts.length === 3) return `${parts[1]}/${parts[2]}`
  return d
}

export function StatsChart({ data }: StatsChartProps) {
  if (data.length === 0) {
    return <div className="text-center text-slate-500 py-8">暂无学习记录</div>
  }

  const maxMin = Math.max(...data.map((d) => d.minutes), 1)
  const maxQ = Math.max(...data.map((d) => d.questions), 1)

  const chartW = 320
  const chartH = 80
  const padding = { top: 4, right: 8, bottom: 20, left: 0 }
  const plotW = chartW - padding.left - padding.right
  const plotH = chartH - padding.top - padding.bottom

  const n = data.length
  const xStep = n > 1 ? plotW / (n - 1) : plotW / 2

  const renderTrendLine = (
    getVal: (d: WeeklyStat) => number,
    maxVal: number,
    color: string,
    label: string,
  ) => {
    const points: { x: number; y: number }[] = data.map((d, i) => ({
      x: padding.left + i * xStep,
      y: padding.top + plotH - (getVal(d) / maxVal) * plotH,
    }))
    const maxY = Math.max(...points.map(p => p.y))

    return (
      <div key={label} className="space-y-1">
        <div className="text-xs text-slate-500">{label}</div>
        <svg viewBox={`0 0 ${chartW} ${chartH}`} className="w-full" style={{ maxWidth: chartW }}>
          {points.map((p, i) => (
            <line
              key={`grid-${i}`}
              x1={p.x} y1={padding.top} x2={p.x} y2={padding.top + plotH}
              stroke="#334155" strokeWidth={0.5} strokeDasharray="3,3"
            />
          ))}

          <polyline
            points={points.map((p) => `${p.x},${p.y}`).join(' ')}
            fill="none"
            stroke={color}
            strokeWidth={2.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          <polyline
            points={points.map((p) => `${p.x},${maxY + 20}`).join(' ')}
            fill="none"
            stroke="none"
          />

          {points.map((p, i) => (
            <g key={i}>
              <circle cx={p.x} cy={p.y} r={3.5} fill={color} stroke="#1e293b" strokeWidth={1.5} />
              <text x={p.x} y={padding.top + plotH + 14} textAnchor="middle" fill="#64748b" fontSize={9}>
                {formatDate(data[i].date)}
              </text>
            </g>
          ))}
        </svg>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div>
        <div className="text-xs text-slate-500 mb-2">学习时长 (分钟)</div>
        <div className="flex items-end gap-1 h-20">
          {data.map((d, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-primary-500 rounded-t transition-all"
                style={{ height: `${(d.minutes / maxMin) * 100}%` }}
              />
              <span className="text-[10px] text-slate-500">{formatDate(d.date)}</span>
            </div>
          ))}
        </div>
      </div>

      {data.length >= 2 && (
        <>
          {renderTrendLine((d) => d.minutes, maxMin, '#38bdf8', '时长趋势')}
          {renderTrendLine((d) => d.accuracy * 100, 100, '#22c55e', '正确率趋势 (%)')}
        </>
      )}

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
