import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MasteryHeatmap } from '../components/parent/MasteryHeatmap'
import { StatsChart } from '../components/parent/StatsChart'
import { KnowledgeGraph } from '../components/parent/KnowledgeGraph'
import { useAppStore } from '../store/appStore'

export function ParentDashboardPage() {
  const navigate = useNavigate()
  const sid = useAppStore(s => s.activeStudentId)
  const [pin, setPin] = useState('')
  const [authenticated, setAuthenticated] = useState(false)
  const [dashboard, setDashboard] = useState<any>(null)
  const [graphData, setGraphData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedKp, setSelectedKp] = useState<string | null>(null)
  const [detailModal, setDetailModal] = useState<any>(null)

  const login = async () => {
    setLoading(true)
    setError('')
    try {
      const [dashRes, graphRes] = await Promise.all([
        fetch(`/api/parent/dashboard?student_id=${sid}`, { headers: { 'x-parent-pin': pin } }),
        fetch(`/api/parent/graph?student_id=${sid}`, { headers: { 'x-parent-pin': pin } }),
      ])
      if (dashRes.ok && graphRes.ok) {
        const dashData = await dashRes.json()
        const graphJson = await graphRes.json()
        setDashboard(dashData)
        setGraphData(graphJson)
        setAuthenticated(true)
      } else {
        setError('PIN错误，请重试')
      }
    } catch {
      setError('连接失败')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/parent/approve-path?student_id=${sid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-parent-pin': pin },
        body: JSON.stringify({}),
      })
      if (res.ok) {
        setDashboard((prev: any) => ({ ...prev, suggestions: [...prev.suggestions, '✅ 学习路径已确认'] }))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleHeatmapClick = (item: any) => {
    setSelectedKp(item.kp_id)
    setDetailModal(item)
  }

  const handleGraphNodeClick = (node: any) => {
    const item = dashboard?.mastery_heatmap?.find((h: any) => h.kp_id === node.kp_id)
    setSelectedKp(node.kp_id)
    setDetailModal(item || node)
  }

  if (!authenticated) {
    return (
      <div className="space-y-6 animate-slide-up pt-8">
        <header className="text-center">
          <h1 className="text-2xl font-bold">家长看板</h1>
          <p className="text-slate-400 text-sm mt-1">输入PIN码查看学习数据</p>
        </header>

        <div className="card space-y-4">
          <input
            type="password"
            inputMode="numeric"
            maxLength={6}
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && login()}
            placeholder="输入PIN码"
            className="w-full p-3 rounded-xl border bg-slate-900 min-h-[48px] text-white text-lg text-center border-slate-700 focus:border-primary-500"
          />
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}
          <button onClick={login} disabled={loading || !pin} className="btn-primary w-full">
            {loading ? '验证中...' : '进入看板'}
          </button>
        </div>

        <button onClick={() => navigate('/')} className="btn-secondary w-full">
          返回首页
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-5 animate-slide-up pb-8">
      <header className="pt-2 flex items-center justify-between">
        <button onClick={() => { setAuthenticated(false); setPin('') }} className="text-slate-400 text-sm min-h-[44px] px-2">
          ← 退出
        </button>
        <h1 className="text-lg font-bold">家长看板</h1>
        <div className="w-8" />
      </header>

      {dashboard && (
        <>
          <div className="grid grid-cols-3 gap-3">
            <div className="card text-center py-3">
              <div className="text-2xl font-bold text-primary-400">{dashboard.mastery_heatmap?.filter((h: any) => h.score >= 0.6).length ?? 0}</div>
              <div className="text-xs text-slate-500">已掌握</div>
            </div>
            <div className="card text-center py-3">
              <div className="text-2xl font-bold text-yellow-400">{dashboard.streak_days}</div>
              <div className="text-xs text-slate-500">连胜天</div>
            </div>
            <div className="card text-center py-3">
              <div className="text-2xl font-bold text-green-400">{dashboard.total_xp}</div>
              <div className="text-xs text-slate-500">总XP</div>
            </div>
          </div>

          <div className="card">
            <h2 className="font-semibold text-white mb-3">知识掌握度</h2>
            <MasteryHeatmap
              data={dashboard.mastery_heatmap ?? []}
              onItemClick={handleHeatmapClick}
              selectedKp={selectedKp}
            />
          </div>

          {graphData && (
            <div className="card">
              <h2 className="font-semibold text-white mb-3">知识图谱</h2>
              <p className="text-xs text-slate-500 mb-2">点击节点查看详情 · 箭头表示前置依赖关系</p>
              <KnowledgeGraph data={graphData} onNodeClick={handleGraphNodeClick} />
            </div>
          )}

          <div className="card">
            <h2 className="font-semibold text-white mb-3">每周统计</h2>
            <StatsChart data={dashboard.weekly_stats ?? []} />
          </div>

          {dashboard.current_path && dashboard.current_path.length > 0 && (
            <div className="card">
              <h2 className="font-semibold text-white mb-3">当前学习路径</h2>
              <div className="space-y-2">
                {dashboard.current_path.map((pn: any) => (
                  <div key={pn.kp_id} className="flex items-center gap-2 text-sm">
                    <span className="text-primary-400 font-bold min-w-[24px]">{pn.order}.</span>
                    <span className="text-white">{pn.kp_name}</span>
                    <span className="text-slate-500 text-xs ml-auto">{pn.reason}</span>
                  </div>
                ))}
              </div>
              <button onClick={handleApprove} disabled={loading} className="btn-primary w-full mt-3 text-sm">
                {loading ? '处理中...' : '确认路径'}
              </button>
            </div>
          )}

          {dashboard.suggestions && dashboard.suggestions.length > 0 && (
            <div className="card">
              <h2 className="font-semibold text-white mb-3">建议</h2>
              <div className="space-y-2">
                {dashboard.suggestions.map((s: string, i: number) => (
                  <p key={i} className="text-sm text-slate-400">• {s}</p>
                ))}
              </div>
            </div>
          )}

          <button onClick={() => navigate('/')} className="btn-secondary w-full">
            返回首页
          </button>
        </>
      )}

      {detailModal && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => { setDetailModal(null); setSelectedKp(null) }}>
          <div className="card w-full max-w-sm mx-4 mb-8 sm:mb-0 space-y-3 animate-slide-up" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500 px-2 py-0.5 rounded-full bg-slate-700">{detailModal.grade || 'Y7'}</span>
              <button onClick={() => { setDetailModal(null); setSelectedKp(null) }} className="text-slate-400 text-lg min-h-[44px] min-w-[44px] flex items-center justify-center">✕</button>
            </div>
            <h3 className="text-lg font-bold text-white">{detailModal.kp_name}</h3>
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center">
                <div className="text-2xl font-black text-white">{Math.round((detailModal.score ?? 0) * 100)}%</div>
                <div className="text-xs text-slate-500">掌握度</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-black text-white">{detailModal.total_attempts ?? 0}</div>
                <div className="text-xs text-slate-500">总答题</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-black text-white">{detailModal.correct_attempts ?? 0}</div>
                <div className="text-xs text-slate-500">答对</div>
              </div>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-orange-500 via-yellow-500 to-green-500 transition-all" style={{ width: `${Math.round((detailModal.score ?? 0) * 100)}%` }} />
            </div>
            <button onClick={() => { setDetailModal(null); setSelectedKp(null) }} className="btn-secondary w-full text-sm">
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
