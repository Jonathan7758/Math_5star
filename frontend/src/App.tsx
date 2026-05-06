import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { MobileShell } from './components/layout/MobileShell'
import { HomePage } from './pages/HomePage'
import { DiagnosePage } from './pages/DiagnosePage'
import { DiagnoseReportPage } from './pages/DiagnoseReportPage'
import { LearningPathPage } from './pages/LearningPathPage'
import { QuizPage } from './pages/QuizPage'
import { ParentDashboardPage } from './pages/ParentDashboardPage'
import { DailySummaryPage } from './pages/DailySummaryPage'
import { AchievementsPage } from './pages/AchievementsPage'
import { SpriteShop } from './pages/SpriteShop'
import { Onboarding } from './components/onboarding/Onboarding'

export default function App() {
  const [showOnboarding, setShowOnboarding] = useState(false)

  useEffect(() => {
    const done = localStorage.getItem('onboarding_done')
    if (!done) {
      setShowOnboarding(true)
    }
  }, [])

  if (showOnboarding) {
    return <Onboarding onComplete={() => setShowOnboarding(false)} />
  }

  return (
    <MobileShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/diagnose" element={<DiagnosePage />} />
        <Route path="/diagnose-report" element={<DiagnoseReportPage />} />
        <Route path="/learning-path" element={<LearningPathPage />} />
        <Route path="/quiz" element={<QuizPage />} />
        <Route path="/parent" element={<ParentDashboardPage />} />
        <Route path="/daily-summary" element={<DailySummaryPage />} />
        <Route path="/achievements" element={<AchievementsPage />} />
        <Route path="/shop" element={<SpriteShop />} />
      </Routes>
    </MobileShell>
  )
}
