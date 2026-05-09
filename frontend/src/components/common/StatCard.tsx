interface StatCardProps {
  value: string | number
  label: string
}

export function StatCard({ value, label }: StatCardProps) {
  return (
    <div className="card text-center py-3">
      <div className="text-2xl font-black">{value}</div>
      <div className="text-xs text-slate-500 mt-1">{label}</div>
    </div>
  )
}
