import { useEffect, useRef } from 'react'

interface FireworksProps {
  show: boolean
  onEnd?: () => void
}

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
  color: string
  size: number
  gravity: number
}

const COLORS = ['#fbbf24', '#f87171', '#34d399', '#60a5fa', '#c084fc', '#f472b6', '#fb923c']

export function Fireworks({ show, onEnd }: FireworksProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animFrameRef = useRef<number>(0)

  useEffect(() => {
    if (!show) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1
    const rect = canvas.parentElement?.getBoundingClientRect()
    const w = rect?.width || 320
    const h = rect?.height || 200
    canvas.width = w * dpr
    canvas.height = h * dpr
    canvas.style.width = `${w}px`
    canvas.style.height = `${h}px`
    ctx.scale(dpr, dpr)

    const particles: Particle[] = []
    const burstCount = 5
    let frameCount = 0
    let done = false

    const createBurst = (cx: number, cy: number) => {
      const color = COLORS[Math.floor(Math.random() * COLORS.length)]
      const count = 30 + Math.floor(Math.random() * 20)
      for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.5
        const speed = 1.5 + Math.random() * 3
        particles.push({
          x: cx,
          y: cy,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          life: 0,
          maxLife: 40 + Math.random() * 30,
          color,
          size: 1.5 + Math.random() * 2,
          gravity: 0.04,
        })
      }
    }

    const animate = () => {
      if (!ctx || !canvas) return
      ctx.globalCompositeOperation = 'destination-out'
      ctx.fillStyle = 'rgba(0, 0, 0, 0.15)'
      ctx.fillRect(0, 0, w, h)
      ctx.globalCompositeOperation = 'lighter'

      if (frameCount % 25 === 0 && frameCount < 120) {
        const bx = Math.random() * w * 0.7 + w * 0.15
        const by = Math.random() * h * 0.5 + h * 0.1
        createBurst(bx, by)
      }

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i]
        p.x += p.vx
        p.y += p.vy
        p.vy += p.gravity
        p.vx *= 0.99
        p.life++

        const alpha = 1 - p.life / p.maxLife
        ctx.fillStyle = p.color
        ctx.globalAlpha = alpha
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()

        if (p.life >= p.maxLife) {
          particles.splice(i, 1)
        }
      }

      if (frameCount > 200 && particles.length < 5) {
        done = true
      }

      if (!done) {
        frameCount++
        animFrameRef.current = requestAnimationFrame(animate)
      } else {
        ctx.clearRect(0, 0, w, h)
        onEnd?.()
      }
    }

    animFrameRef.current = requestAnimationFrame(animate)

    return () => {
      cancelAnimationFrame(animFrameRef.current)
    }
  }, [show])

  if (!show) return null

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 z-20 pointer-events-none"
      style={{ width: '100%', height: '100%' }}
    />
  )
}
