import { ReactNode } from 'react'
import { BottomNav } from './BottomNav'

interface MobileShellProps {
  children: ReactNode
}

export function MobileShell({ children }: MobileShellProps) {
  return (
    <div className="min-h-dvh flex flex-col mx-auto max-w-md">
      <main className="flex-1 overflow-y-auto px-4 py-6">
        {children}
      </main>
      <BottomNav />
    </div>
  )
}
