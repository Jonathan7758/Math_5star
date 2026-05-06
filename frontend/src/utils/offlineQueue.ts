interface OfflineAnswer {
  questionId: string
  answer: string
  hintLevel: number
  studentId: number
  timestamp: number
}

const STORAGE_KEY = 'offline_answer_queue'

export function getOfflineQueue(): OfflineAnswer[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveQueue(queue: OfflineAnswer[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(queue))
}

export function enqueueOfflineAnswer(answer: Omit<OfflineAnswer, 'timestamp'>) {
  const queue = getOfflineQueue()
  queue.push({ ...answer, timestamp: Date.now() })
  saveQueue(queue)
}

export async function syncOfflineQueue(): Promise<{ synced: number; failed: number }> {
  const queue = getOfflineQueue()
  if (queue.length === 0) return { synced: 0, failed: 0 }

  let synced = 0
  let failed = 0

  for (const item of queue) {
    try {
      const res = await fetch('/api/exercise/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: item.studentId,
          question_id: item.questionId,
          answer: item.answer,
          hint_level_used: item.hintLevel,
        }),
      })
      if (res.ok) {
        synced++
      } else {
        failed++
      }
    } catch {
      failed++
    }
  }

  const remaining = queue.slice(synced)
  saveQueue(remaining)

  return { synced, failed }
}

export function clearOfflineQueue() {
  localStorage.removeItem(STORAGE_KEY)
}
