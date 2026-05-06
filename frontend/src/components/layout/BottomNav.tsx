import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/', label: '学习', labelEn: 'Learn', icon: '📚' },
  { path: '/diagnose', label: '诊断', labelEn: 'Diagnose', icon: '🔍' },
  { path: '/sprite', label: '精灵', labelEn: 'Sprite', icon: '⭐' },
  { path: '/profile', label: '我的', labelEn: 'Profile', icon: '👤' },
]

export function BottomNav() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <nav className="sticky bottom-0 bg-slate-900 border-t border-slate-800 px-2 pt-2 pb-safe">
      <div className="flex justify-around">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center py-1 px-3 min-w-[64px] min-h-[44px] rounded-lg transition-colors ${
                isActive
                  ? 'text-primary-400'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <span className="text-xl leading-none">{item.icon}</span>
              <span className="text-xs mt-1">{item.label}</span>
            </button>
          )
        })}
      </div>
      <div className="h-[env(safe-area-inset-bottom)]" />
    </nav>
  )
}
