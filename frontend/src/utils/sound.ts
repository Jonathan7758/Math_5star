/**
 * Web Audio API sound system for Math-5star
 * Uses synthesized tones - no external audio files needed.
 */
export type SoundName = 'correct' | 'incorrect' | 'combo' | 'achievement' | 'levelup' | 'click';

let audioCtx: AudioContext | null = null; let bgmOsc: OscillatorNode | null = null; let bgmGain: GainNode | null = null; let bgmPlaying = false;

function getCtx(): AudioContext {
  if (!audioCtx) audioCtx = new AudioContext();
  return audioCtx;
}

function playTone(freq: number, duration: number, type: OscillatorType = 'sine', volume = 0.15) {
  const ctx = getCtx();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(volume, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + duration);
}

function playMelody(notes: [number, number, number][], type: OscillatorType = 'sine') {
  const ctx = getCtx();
  let t = ctx.currentTime;
  notes.forEach(([freq, dur, vol]) => {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(vol || 0.12, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + dur);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(t);
    osc.stop(t + dur);
    t += dur;
  });
}

const SOUNDS: Record<SoundName, () => void> = {
  correct: () => playMelody([
    [523, 0.08, 0.15], [659, 0.08, 0.15], [784, 0.15, 0.2],
  ], 'triangle'),
  incorrect: () => playTone(200, 0.3, 'square', 0.1),
  combo: () => playMelody([
    [784, 0.06, 0.15], [988, 0.06, 0.15], [1175, 0.12, 0.2],
  ], 'triangle'),
  achievement: () => playMelody([
    [523, 0.1, 0.15], [659, 0.1, 0.15], [784, 0.1, 0.15], [1047, 0.3, 0.25],
  ], 'sine'),
  levelup: () => playMelody([
    [392, 0.08, 0.12], [523, 0.08, 0.12], [659, 0.08, 0.12],
    [784, 0.08, 0.12], [1047, 0.2, 0.2],
  ], 'sine'),
  click: () => playTone(800, 0.05, 'sine', 0.08),
};

export function playSound(name: SoundName) {
  try {
    SOUNDS[name]?.();
  } catch {
    // Audio not available (e.g., WebView without user gesture)
  }
}

export function playBGM() {
  if (bgmPlaying) return;
  try {
    const ctx = getCtx();
    bgmGain = ctx.createGain();
    bgmGain.gain.value = 0.03;
    bgmGain.connect(ctx.destination);

    bgmOsc = ctx.createOscillator();
    bgmOsc.type = 'sine';
    bgmOsc.frequency.value = 220;
    bgmOsc.connect(bgmGain);
    bgmOsc.start();
    bgmPlaying = true;

    // Gentle frequency modulation
    const lfo = ctx.createOscillator();
    lfo.type = 'sine';
    lfo.frequency.value = 0.5;
    const lfoGain = ctx.createGain();
    lfoGain.gain.value = 5;
    lfo.connect(lfoGain);
    lfoGain.connect(bgmOsc.frequency);
    lfo.start();
  } catch {}
}

export function stopBGM() {
  bgmOsc?.stop();
  bgmOsc = null;
  bgmGain = null;
  bgmPlaying = false;
}

export function isBGMPlaying() { return bgmPlaying; }
