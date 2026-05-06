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
  activeStudentId: number
  setStudent: (s: Student) => void
  setHealthStatus: (s: string) => void
  setActiveStudentId: (id: number) => void
}

function getStudentIdFromStorage(): number {
  try {
    const raw = localStorage.getItem('active_student_id')
    if (raw) return parseInt(raw, 10)
  } catch {}
  return 1
}

export const useAppStore = create<AppState>((set) => ({
  student: null,
  healthStatus: null,
  activeStudentId: getStudentIdFromStorage(),
  setStudent: (student) => set({ student }),
  setHealthStatus: (healthStatus) => set({ healthStatus }),
  setActiveStudentId: (id) => {
    localStorage.setItem('active_student_id', String(id))
    set({ activeStudentId: id })
  },
}))
