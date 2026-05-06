const VAPID_PUBLIC_KEY = 'BNxJUzV2Fw5DnLJ5hXJGcS_cR3ZH8KJIqK4jPSyFJ2z5SYH4kj8L6mWTRkHfLPO0BKVQ5n-T9KAlXTqI-axLlkk'

function urlBase64ToUint8Array(base64String: string): ArrayBuffer {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; i++) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray.buffer
}

export async function subscribeToPush(): Promise<PushSubscription | null> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    return null
  }

  try {
    const permission = await Notification.requestPermission()
    if (permission !== 'granted') return null

    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
    })

    return subscription
  } catch {
    return null
  }
}

export async function unsubscribeFromPush(): Promise<void> {
  try {
    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.getSubscription()
    if (subscription) {
      await subscription.unsubscribe()
    }
  } catch {
    // Silent
  }
}

export async function getPushSubscription(): Promise<PushSubscription | null> {
  try {
    const registration = await navigator.serviceWorker.ready
    return await registration.pushManager.getSubscription()
  } catch {
    return null
  }
}
