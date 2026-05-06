interface HeatmapItem {
  kp_id: string
  kp_name: string
  grade: string
  score: number
  total_attempts: number
  correct_attempts?: number
}

interface MasteryHeatmapProps {
  data: HeatmapItem[]
  onItemClick?: (item: HeatmapItem) => void
  selectedKp?: string | null
}

function scoreColor(score: number): string {
  if (score >= 0.8) return 'bg-green-500 text-white'
  if (score >= 0.6) return 'bg-green-400/80 text-white'
  if (score >= 0.4) return 'bg-yellow-500 text-white'
  if (score > 0) return 'bg-orange-500 text-white'
  return 'bg-slate-700 text-slate-500'
}

export function MasteryHeatmap({ data, onItemClick, selectedKp }: MasteryHeatmapProps) {
  if (data.length === 0) {
    return <div className="text-center text-slate-500 py-8">暂无掌握度数据</div>
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <span>低掌握</span>
        <div className="flex gap-1">
          <div className="w-4 h-4 rounded bg-slate-700" />
          <div className="w-4 h-4 rounded bg-orange-500" />
          <div className="w-4 h-4 rounded bg-yellow-500" />
          <div className="w-4 h-4 rounded bg-green-400" />
          <div className="w-4 h-4 rounded bg-green-500" />
        </div>
        <span>已掌握</span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {data.map((item) => {
          const isSelected = selectedKp === item.kp_id
          return (
            <button
              key={item.kp_id}
              onClick={() => onItemClick?.(item)}
              className={`${scoreColor(item.score)} rounded-lg p-2 text-xs min-h-[56px] flex flex-col justify-between transition-all text-left ${
                onItemClick ? 'cursor-pointer hover:scale-[1.03] hover:shadow-lg' : ''
              } ${isSelected ? 'ring-2 ring-white scale-[1.03] shadow-lg' : ''}`}
            >
              <span className="font-medium truncate">{item.kp_name}</span>
              <div className="flex items-center justify-between opacity-75">
                <span>{item.grade}</span>
                <span>{Math.round(item.score * 100)}%</span>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
