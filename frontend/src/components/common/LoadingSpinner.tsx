interface LoadingSpinnerProps {
  text?: string
}

export function LoadingSpinner({ text = '加载中...' }: LoadingSpinnerProps) {
  return (
    <div className="flex justify-center items-center min-h-[200px]">
      <div className="text-slate-400 text-sm animate-pulse">{text}</div>
    </div>
  )
}
