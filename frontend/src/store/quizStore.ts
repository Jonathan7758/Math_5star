import { create } from 'zustand'

export interface Question {
  question_id: string
  knowledge_point_id: string
  level: number
  question: string
  options: string[] | null
  question_type: string
  kp_name: string
}

export interface Feedback {
  is_correct: boolean
  correct_answer: string
  xp_earned: number
  hint: string | null
  explanation: string | null
}

interface QuizState {
  /* Current state */
  currentQuestion: Question | null
  selectedAnswer: string | null
  feedback: Feedback | null
  hintShown: string | null
  isSubmitting: boolean
  errorCount: number

  /* Session stats */
  sessionXp: number
  questionsAnswered: number
  correctCount: number

  /* Diagnostic records */
  diagnoseRecords: { kp_id: string; is_correct: boolean }[]

  /* Actions */
  setQuestion: (q: Question) => void
  selectAnswer: (answer: string) => void
  setFeedback: (f: Feedback) => void
  setSubmitting: (v: boolean) => void
  resetQuiz: () => void
  addDiagnoseRecord: (r: { kp_id: string; is_correct: boolean }) => void
  clearDiagnoseRecords: () => void
}

export const useQuizStore = create<QuizState>((set) => ({
  currentQuestion: null,
  selectedAnswer: null,
  feedback: null,
  hintShown: null,
  isSubmitting: false,
  errorCount: 0,
  sessionXp: 0,
  questionsAnswered: 0,
  correctCount: 0,
  diagnoseRecords: [],

  setQuestion: (q) => set({
    currentQuestion: q,
    selectedAnswer: null,
    feedback: null,
    hintShown: null,
  }),

  selectAnswer: (answer) => set({ selectedAnswer: answer }),

  setFeedback: (f) => set((s) => ({
    feedback: f,
    hintShown: f.is_correct ? null : f.hint,
    sessionXp: s.sessionXp + f.xp_earned,
    questionsAnswered: s.questionsAnswered + 1,
    correctCount: f.is_correct ? s.correctCount + 1 : s.correctCount,
  })),

  setSubmitting: (v) => set({ isSubmitting: v }),

  resetQuiz: () => set({
    currentQuestion: null,
    selectedAnswer: null,
    feedback: null,
    hintShown: null,
    isSubmitting: false,
    errorCount: 0,
  }),

  addDiagnoseRecord: (r) => set((s) => ({
    diagnoseRecords: [...s.diagnoseRecords, r],
  })),

  clearDiagnoseRecords: () => set({ diagnoseRecords: [] }),
}))
