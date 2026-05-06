export function hapticTap(pattern: 'light' | 'medium' | 'heavy' | 'success' | 'error' = 'light') {
  if (!('vibrate' in navigator)) return

  const patterns: Record<string, number | number[]> = {
    light: 10,
    medium: 30,
    heavy: 50,
    success: [10, 50, 10],
    error: [50, 100, 50, 100, 50],
  }

  try {
    navigator.vibrate(patterns[pattern] || 10)
  } catch {
    // Silent fail on unsupported devices
  }
}

export function hapticCorrect() {
  hapticTap('success')
}

export function hapticWrong() {
  hapticTap('error')
}

export function hapticCombo(combo: number) {
  if (combo >= 5) {
    hapticTap('heavy')
  } else if (combo >= 3) {
    hapticTap('medium')
  } else {
    hapticTap('light')
  }
}
