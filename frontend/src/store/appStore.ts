import { create } from 'zustand'

interface Student {
  id: number
  name: string
  level: number
  star_coins: number
  total_xp: number
  current_streak_days: number
  daily_goal_minutes: number
  locale: string
}

interface AppState {
  student: Student | null
  healthStatus: string | null
  setStudent: (s: Student) => void
  setHealthStatus: (s: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  student: null,
  healthStatus: null,
  setStudent: (student) => set({ student }),
  setHealthStatus: (healthStatus) => set({ healthStatus }),
}))
