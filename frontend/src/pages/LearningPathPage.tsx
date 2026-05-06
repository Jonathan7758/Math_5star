import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useQuizStore } from '../store/quizStore'
import { useAppStore } from '../store/appStore'

interface PathNode {
  order: number
  kp_id: string
  kp_name: string
  reason: string
}

export function LearningPathPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const sid = useAppStore(s => s.activeStudentId)
  const [path, setPath] = useState<PathNode[]>(location.state?.path ?? [])
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState(location.state?.summary ?? '')
  const { resetQuiz } = useQuizStore()

  const fetchPath = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: sid,
          root_causes: location.state?.rootCauses ?? [],
        }),
      })
      const data = await res.json()
      setPath(data.path ?? [])
      setSummary(data.summary ?? '')
    } finally {
      setLoading(false)
    }
  }

  const startTopic = (node: PathNode) => {
    resetQuiz()
    navigate('/quiz', { state: { kp_id: node.kp_id, kp_name: node.kp_name, path } })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-pulse text-slate-400">生成学习路径中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-5 animate-slide-up">
      <header className="pt-2">
        <h1 className="text-xl font-bold">学习路径</h1>
        {summary && <p className="text-slate-400 text-sm mt-1">{summary}</p>}
      </header>

      {path.length === 0 ? (
        <div className="card text-center py-8 space-y-3">
          <div className="text-5xl">🗺️</div>
          <p className="text-slate-300">没有学习路径数据</p>
          <button onClick={fetchPath} className="btn-primary">
            生成路径
          </button>
        </div>
      ) : (
        <div className="relative">
          <div className="absolute left-5 top-8 bottom-4 w-0.5 bg-slate-700" />
          <div className="space-y-4">
            {path.map((node, i) => (
              <div key={node.kp_id} className="relative pl-10">
                <div className={`absolute left-3.5 top-4 w-3 h-3 rounded-full border-2 z-10 ${
                  i === 0 ? 'bg-primary-500 border-primary-500' : 'bg-slate-800 border-slate-600'
                }`} />
                <div className="card space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500">步骤 {node.order}</span>
                    <span className="text-xs text-primary-400 bg-primary-400/10 px-2 py-0.5 rounded-full">
                      {node.kp_id}
                    </span>
                  </div>
                  <h3 className="font-semibold text-white">{node.kp_name}</h3>
                  <p className="text-sm text-slate-400">{node.reason}</p>
                  <button
                    onClick={() => startTopic(node)}
                    className="btn-primary w-full text-sm"
                  >
                    开始练习
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <button onClick={() => navigate('/')} className="btn-secondary w-full">
        返回首页
      </button>
    </div>
  )
}
