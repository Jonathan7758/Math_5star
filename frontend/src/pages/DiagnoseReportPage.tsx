import { useLocation, useNavigate } from 'react-router-dom'
import { BackToHomeButton } from '../components/common/BackButton'

interface RootCause {
  kp_id: string
  kp_name: string
  priority: number
  error_count: number
  impacted_nodes: string[]
  reason: string
}

interface Report {
  success: boolean
  root_causes: RootCause[]
  total_records: number
  incorrect_count: number
}

const PRIORITY_COLORS: Record<string, string> = {
  high: 'text-red-400 bg-red-500/10 border-red-500/30',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  low: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
}

function getPriorityLabel(p: number): { label: string; cls: string } {
  if (p >= 0.7) return { label: '高', cls: PRIORITY_COLORS.high }
  if (p >= 0.4) return { label: '中', cls: PRIORITY_COLORS.medium }
  return { label: '低', cls: PRIORITY_COLORS.low }
}

export function DiagnoseReportPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const report = location.state?.report as Report | undefined

  if (!report) {
    return (
      <div className="space-y-6 animate-slide-up pt-8 text-center">
        <div className="text-5xl mb-4">📋</div>
        <h1 className="text-xl font-bold">暂无诊断报告</h1>
        <p className="text-slate-400 text-sm">请先完成诊断测试</p>
        <button onClick={() => navigate('/diagnose')} className="btn-primary">
          开始诊断
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-5 animate-slide-up">
      <header className="pt-2">
        <h1 className="text-xl font-bold">诊断报告</h1>
        <p className="text-slate-400 text-sm mt-1">
          共 {report.total_records} 题，{report.incorrect_count} 题错误
        </p>
      </header>

      {report.root_causes.length === 0 ? (
        <div className="card text-center py-8 space-y-3 border border-green-500/20 bg-gradient-to-b from-green-500/5 to-slate-900/80">
          <div className="text-5xl">🎉</div>
          <p className="text-lg font-semibold text-green-400">没有发现明显断点！</p>
          <div className="flex items-center justify-center gap-2 text-sm">
            <span className="text-slate-300">正确率</span>
            <span className="text-green-400 font-bold text-lg">
              {Math.round((1 - report.incorrect_count / Math.max(report.total_records, 1)) * 100)}%
            </span>
          </div>
        </div>
      ) : (
        <>
          {/* Score overview */}
          <div className="card flex items-center gap-4 border border-slate-700/50">
            <div className="w-16 h-16 rounded-full border-4 border-primary-500 flex items-center justify-center"
              role="progressbar" aria-valuenow={Math.round((1 - report.incorrect_count / Math.max(report.total_records, 1)) * 100)}
              aria-valuemin={0} aria-valuemax={100}>
              <span className="text-lg font-bold text-primary-400">
                {Math.round((1 - report.incorrect_count / Math.max(report.total_records, 1)) * 100)}%
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-semibold">诊断结果</p>
              <p className="text-slate-400 text-sm">
                发现 <span className="text-orange-400 font-bold">{report.root_causes.length}</span> 个薄弱点
                · {report.total_records}题中{report.incorrect_count}题错误
              </p>
            </div>
          </div>
          <p className="text-sm text-slate-400">
            以下是系统发现的知识薄弱点，按优先级排序：
          </p>

          <div className="space-y-3">
            {report.root_causes.map((rc) => {
              const { label, cls } = getPriorityLabel(rc.priority)
              return (
                <div key={rc.kp_id} className="card space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white truncate">
                        {rc.kp_name}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">{rc.kp_id}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full border shrink-0 ${cls}`}>
                      {label}优先级
                    </span>
                  </div>

                  <div className="w-full bg-slate-700 rounded-full h-1.5">
                    <div
                      className="bg-primary-500 h-1.5 rounded-full transition-all"
                      style={{ width: `${Math.round(rc.priority * 100)}%` }}
                    />
                  </div>

                  <p className="text-sm text-slate-300 leading-relaxed">{rc.reason}</p>

                  {rc.impacted_nodes.length > 0 && (
                    <p className="text-xs text-slate-500">
                      影响知识点: {rc.impacted_nodes.join(', ')}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        </>
      )}

      <div className="space-y-3 pt-4 pb-8">
        {report.root_causes.length > 0 && (
          <button
            onClick={() => navigate('/learning-path', { state: { rootCauses: report.root_causes } })}
            className="btn-primary w-full"
          >
            生成学习路径
          </button>
        )}
        <button onClick={() => navigate('/diagnose')} className="btn-secondary w-full">
          重新诊断
        </button>
        <BackToHomeButton />
      </div>
    </div>
  )
}
