import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/appStore'

interface SkinInfo {
  key: string
  name: string
  desc: string
  cost: number
  color: string
}

export function SpriteShop() {
  const navigate = useNavigate()
  const sid = useAppStore(s => s.activeStudentId)
  const [skins, setSkins] = useState<SkinInfo[]>([])
  const [owned, setOwned] = useState<string[]>([])
  const [coins, setCoins] = useState(0)
  const [currentSkin, setCurrentSkin] = useState('classic_gold')
  const [freezeCount, setFreezeCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  const fetchData = async () => {
    const [skinRes, statusRes] = await Promise.all([
      fetch('/api/health/skins').then(r => r.json()),
      fetch(`/api/rewards/status?student_id=${sid}`).then(r => r.json()),
    ])
    setSkins(skinRes.skins || [])
    setCoins(statusRes.star_coins || 0)

    const spriteRes = await fetch(`/api/sprite/state?student_id=${sid}`)
    const spriteData = await spriteRes.json()
    setOwned(spriteData.owned_skins || ['classic_gold'])
    setCurrentSkin(spriteData.skin || 'classic_gold')
    setFreezeCount(spriteData.streak_freeze_count || 0)
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [sid])

  const buySkin = async (key: string) => {
    const res = await fetch(`/api/sprite/buy-skin?student_id=${sid}&skin_key=${key}`, { method: 'POST' })
    const data = await res.json()
    if (res.ok) {
      setMessage(`成功购买！`)
      setCoins(c => c - (skins.find(s => s.key === key)?.cost || 0))
      setOwned([...owned, key])
    } else {
      setMessage(data.detail || '购买失败')
    }
    setTimeout(() => setMessage(''), 3000)
  }

  const useSkin = async (key: string) => {
    await fetch(`/api/sprite/customize?student_id=${sid}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skin: key }),
    })
    setCurrentSkin(key)
    setMessage('皮肤已切换！')
    setTimeout(() => setMessage(''), 2000)
  }

  const buyFreeze = async () => {
    const res = await fetch(`/api/sprite/buy-streak-freeze?student_id=${sid}`, { method: 'POST' })
    const data = await res.json()
    if (res.ok) {
      setCoins(c => c - 50)
      setFreezeCount(c => c + 1)
      setMessage('连胜保护盾已购买！')
    } else {
      setMessage(data.detail || '购买失败')
    }
    setTimeout(() => setMessage(''), 3000)
  }

  if (loading) return <div className="card text-center py-8"><p className="text-slate-400 text-sm">加载中...</p></div>

  return (
    <div className="space-y-5 animate-slide-up pb-8">
      <header className="flex items-center justify-between pt-2">
        <button onClick={() => navigate(-1)} className="text-slate-400 text-sm min-h-[44px] px-2">← 返回</button>
        <h1 className="text-lg font-bold">精灵商店</h1>
        <span className="text-yellow-400 text-sm">⭐{coins}</span>
      </header>

      {message && <div className="card bg-primary-500/10 border border-primary-500/30 text-center py-2 text-sm text-primary-300">{message}</div>}

      <div className="card space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">🛡️ 连胜保护盾</h2>
          <span className="text-xs text-slate-400">拥有: {freezeCount}</span>
        </div>
        <p className="text-xs text-slate-400">保护你的连胜不被中断。使用后自动消耗。</p>
        <button onClick={buyFreeze} disabled={coins < 50} className="btn-secondary w-full text-sm">
          购买 (50 ⭐) {coins < 50 ? '- 星币不足' : ''}
        </button>
      </div>

      <div className="card">
        <h2 className="text-sm font-semibold text-white mb-3">🎨 精灵皮肤</h2>
        <div className="space-y-2">
          {skins.map(s => {
            const isOwned = owned.includes(s.key)
            const isActive = currentSkin === s.key
            return (
              <div key={s.key} className={`flex items-center gap-3 p-2 rounded-lg border ${isActive ? 'border-primary-500 bg-primary-500/10' : 'border-slate-700'}`}>
                <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg" style={{ backgroundColor: s.color + '30', color: s.color }}>
                  ✦
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium">{s.name}</p>
                  <p className="text-xs text-slate-500">{s.desc}</p>
                </div>
                {isActive ? (
                  <span className="text-xs text-primary-400 px-2">使用中</span>
                ) : isOwned ? (
                  <button onClick={() => useSkin(s.key)} className="text-xs text-primary-300 hover:text-primary-200 min-h-[36px] px-2">装备</button>
                ) : (
                  <button onClick={() => buySkin(s.key)} disabled={coins < s.cost} className="text-xs bg-slate-700 hover:bg-slate-600 rounded px-2 py-1 min-h-[36px] text-yellow-400">
                    {s.cost} ⭐
                  </button>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
