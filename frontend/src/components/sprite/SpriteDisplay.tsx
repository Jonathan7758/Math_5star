import { useEffect, useState } from 'react'

interface SpriteDisplayProps {
  stage: number
  stageName: string
  reaction: 'idle' | 'happy' | 'encourage' | 'celebrate' | 'excited' | 'thinking'
  skin?: string
  size?: 'sm' | 'md' | 'lg'
  animateIn?: boolean
  prevStage?: number
}

const STAGE_SIZE: Record<string, string> = { sm: 'w-12 h-12 text-2xl', md: 'w-20 h-20 text-4xl', lg: 'w-32 h-32 text-6xl' }

const STAGE_NAMES = ['星尘', '星芽', '星苗', '星光', '启明星']

function SpriteSVG({ stage, reaction, animateIn, transitioning }: { stage: number; reaction: string; animateIn?: boolean; transitioning?: boolean }) {
  const animClass = reaction === 'celebrate' ? 'animate-bounce' :
    reaction === 'happy' || reaction === 'excited' ? 'animate-bounce-slow' :
    reaction === 'encourage' ? 'animate-pulse' :
    reaction === 'thinking' ? 'animate-wiggle' :
    'animate-float'

  const entranceClass = animateIn ? 'animate-slide-down-in' : ''
  const transitionClass = transitioning ? 'animate-scale-in' : ''

  const stars = reaction === 'celebrate' ? (
    <>
      <circle cx="15" cy="15" r="3" fill="#fbbf24" className="animate-ping" />
      <circle cx="85" cy="15" r="3" fill="#fbbf24" className="animate-ping" />
      <circle cx="50" cy="90" r="3" fill="#fbbf24" className="animate-ping" />
    </>
  ) : null

  const thinkingBubble = reaction === 'thinking' ? (
    <>
      <circle cx="5" cy="5" r="4" fill="#475569" opacity="0.5" className="animate-ping" />
      <circle cx="-2" cy="-10" r="3" fill="#475569" opacity="0.4" className="animate-ping" />
    </>
  ) : null

  const wrapperClass = `${animClass} ${entranceClass} ${transitionClass} relative`

  switch (stage) {
    case 0: return (
      <div className={wrapperClass}>
        <svg viewBox="0 0 80 80" className="w-full h-full">
          <defs><radialGradient id="gs0" cx="50%" cy="50%"><stop offset="0%" stopColor="#fbbf24"/><stop offset="100%" stopColor="#d97706"/></radialGradient></defs>
          <circle cx="40" cy="40" r="25" fill="url(#gs0)" opacity="0.9"/>
          <circle cx="40" cy="40" r="18" fill="#fef3c7" opacity="0.6"/>
          <circle cx="40" cy="40" r="10" fill="#fbbf24" opacity="0.8"/>
          {stars}
          {thinkingBubble}
        </svg>
      </div>
    )
    case 1: return (
      <div className={wrapperClass}>
        <svg viewBox="0 0 100 120" className="w-full h-full">
          <defs><radialGradient id="gs1" cx="50%" cy="40%"><stop offset="0%" stopColor="#fbbf24"/><stop offset="100%" stopColor="#ea580c"/></radialGradient></defs>
          <ellipse cx="50" cy="60" rx="20" ry="26" fill="url(#gs1)" opacity="0.9"/>
          <polygon points="50,18 37,48 63,48" fill="#22c55e" opacity="0.85"/>
          <polygon points="28,40 15,62 41,62" fill="#22c55e" opacity="0.7"/>
          <polygon points="72,40 59,62 85,62" fill="#22c55e" opacity="0.7"/>
          {stars}
          {thinkingBubble}
        </svg>
      </div>
    )
    case 2: return (
      <div className={wrapperClass}>
        <svg viewBox="0 0 120 150" className="w-full h-full">
          <defs><radialGradient id="gs2" cx="50%" cy="40%"><stop offset="0%" stopColor="#a78bfa"/><stop offset="100%" stopColor="#7c3aed"/></radialGradient></defs>
          <rect x="50" y="20" width="14" height="60" rx="5" fill="#78350f" opacity="0.8"/>
          <polygon points="35,40 57,35 79,40 70,65 57,75 44,65" fill="#22c55e" opacity="0.85"/>
          <circle cx="57" cy="42" r="8" fill="#a855f7" opacity="0.9"/>
          <circle cx="44" cy="50" r="6" fill="#eab308" opacity="0.8"/>
          <circle cx="68" cy="52" r="6" fill="#eab308" opacity="0.8"/>
          <polygon points="57,20 52,10 62,10" fill="#eab308"/>
          {stars}
          {thinkingBubble}
        </svg>
      </div>
    )
    case 3: return (
      <div className={wrapperClass}>
        <svg viewBox="0 0 140 160" className="w-full h-full">
          <defs><radialGradient id="gs3" cx="50%" cy="35%"><stop offset="0%" stopColor="#38bdf8"/><stop offset="100%" stopColor="#0ea5e9"/></radialGradient></defs>
          <rect x="58" y="15" width="24" height="24" rx="6" fill="url(#gs3)" opacity="0.9" transform="rotate(20 70 27)"/>
          <ellipse cx="70" cy="55" rx="30" ry="40" fill="url(#gs3)" opacity="0.4"/>
          <polygon points="70,65 70,90" stroke="#38bdf8" strokeWidth="2" opacity="0.5"/>
          <text x="70" y="48" textAnchor="middle" fontSize="14" fill="white" fontStyle="italic">π</text>
          <text x="45" y="63" textAnchor="middle" fontSize="12" fill="#eab308">∑</text>
          <text x="95" y="60" textAnchor="middle" fontSize="12" fill="#eab308">√</text>
          <text x="55" y="78" textAnchor="middle" fontSize="10" fill="#a855f7">Δ</text>
          <text x="88" y="78" textAnchor="middle" fontSize="10" fill="#a855f7">∞</text>
          {stars}
          {thinkingBubble}
        </svg>
      </div>
    )
    case 4: return (
      <div className={wrapperClass}>
        <svg viewBox="0 0 160 180" className="w-full h-full">
          <defs>
            <radialGradient id="gs4" cx="50%" cy="40%"><stop offset="0%" stopColor="#fbbf24"/><stop offset="60%" stopColor="#f59e0b"/><stop offset="100%" stopColor="#ea580c"/></radialGradient>
          </defs>
          <polygon points="80,15 95,55 140,55 105,80 118,120 80,95 42,120 55,80 20,55 65,55" fill="url(#gs4)" opacity="0.95" stroke="#fcd34d" strokeWidth="2"/>
          <circle cx="80" cy="68" r="20" fill="#fef3c7" opacity="0.7"/>
          <polygon points="80,50 85,62 98,62 88,70 92,82 80,75 68,82 72,70 62,62 75,62" fill="#fbbf24" opacity="0.8"/>
          {stars}
          {thinkingBubble}
        </svg>
      </div>
    )
    default: return null
  }
}

export function SpriteDisplay({ stage, stageName, reaction = 'idle', size = 'md', animateIn = false, prevStage }: SpriteDisplayProps) {
  const [showTransition, setShowTransition] = useState(false)

  useEffect(() => {
    if (prevStage !== undefined && prevStage !== stage) {
      setShowTransition(true)
      const timer = setTimeout(() => setShowTransition(false), 600)
      return () => clearTimeout(timer)
    }
  }, [stage, prevStage])

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`${STAGE_SIZE[size]} relative`} aria-label={`Sprite: ${stageName}`}>
        <SpriteSVG stage={stage} reaction={reaction} animateIn={animateIn} transitioning={showTransition} />
      </div>
      <span className="text-xs text-slate-400">{stageName}</span>
    </div>
  )
}

export { STAGE_NAMES }
