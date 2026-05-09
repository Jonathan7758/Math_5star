interface BackButtonProps {
  onClick?: () => void
}

export function BackButton({ onClick }: BackButtonProps) {
  const handleClick = onClick || (() => window.history.back())
  return (
    <button onClick={handleClick} className="text-slate-400 text-sm min-h-[44px] px-2">
      ← 返回
    </button>
  )
}

export function BackToHomeButton() {
  const handleClick = () => window.location.href = '/'
  return (
    <button onClick={handleClick} className="btn-secondary w-full">
      返回首页
    </button>
  )
}
