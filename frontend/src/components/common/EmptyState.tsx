interface EmptyStateProps {
  icon?: string
  message?: string
}

export function EmptyState({ icon = '📊', message = '暂无数据' }: EmptyStateProps) {
  return (
    <div className="card text-center py-8">
      <div className="text-4xl mb-2">{icon}</div>
      <div className="text-slate-400 text-sm">{message}</div>
    </div>
  )
}
