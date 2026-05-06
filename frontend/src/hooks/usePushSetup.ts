import { subscribeToPush, getPushSubscription } from '../utils/pushNotifications'
import { useAppStore } from '../store/appStore'

export async function registerPushIfNew() {
  const sid = useAppStore.getState().activeStudentId

  const existing = await getPushSubscription()
  if (!existing) {
    const sub = await subscribeToPush()
    if (!sub) return

    try {
      await fetch(`/api/push/register?student_id=${sid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          endpoint: sub.endpoint,
          keys: sub.toJSON().keys,
        }),
      })
    } catch {
      // Silent fail
    }
  }
}
