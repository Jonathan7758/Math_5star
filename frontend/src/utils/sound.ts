type SoundType = 'correct' | 'incorrect' | 'combo' | 'levelup' | 'achievement'

let audioCtx: AudioContext | null = null

function getCtx(): AudioContext {
  if (!audioCtx) {
    audioCtx = new AudioContext()
  }
  return audioCtx
}

function playTone(freq: number, duration: number, type: OscillatorType = 'sine', gain = 0.3) {
  try {
    const ctx = getCtx()
    const osc = ctx.createOscillator()
    const vol = ctx.createGain()
    osc.type = type
    osc.frequency.setValueAtTime(freq, ctx.currentTime)
    vol.gain.setValueAtTime(gain, ctx.currentTime)
    vol.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration)
    osc.connect(vol); vol.connect(ctx.destination)
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + duration)
  } catch {}
}

export function playSound(sound: SoundType) {
  switch (sound) {
    case 'correct':
      playTone(523, 0.15, 'sine')
      setTimeout(() => playTone(659, 0.15, 'sine'), 80)
      break
    case 'incorrect':
      playTone(200, 0.3, 'triangle', 0.2)
      break
    case 'combo':
      playTone(440, 0.08, 'square', 0.15)
      setTimeout(() => playTone(554, 0.08, 'square', 0.15), 60)
      setTimeout(() => playTone(659, 0.08, 'square', 0.15), 120)
      setTimeout(() => playTone(880, 0.15, 'square', 0.15), 180)
      break
    case 'levelup':
      playTone(262, 0.12, 'sine', 0.2)
      setTimeout(() => playTone(330, 0.12, 'sine', 0.2), 100)
      setTimeout(() => playTone(392, 0.12, 'sine', 0.2), 200)
      setTimeout(() => playTone(523, 0.3, 'sine', 0.2), 300)
      break
    case 'achievement':
      for (let i = 0; i < 5; i++) {
        setTimeout(() => playTone(440 + i * 110, 0.1, 'sine', 0.15), i * 70)
      }
      break
  }
}
