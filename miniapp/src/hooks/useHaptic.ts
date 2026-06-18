/**
 * useHaptic — Telegram Haptic Feedback
 *
 * Provides haptic feedback on user interactions.
 * Types:
 * - impact: Physical impact (button press, collision)
 *   - light: Light tap
 *   - medium: Medium tap
 *   - heavy: Heavy tap
 *   - rigid: Rigid feedback
 *   - soft: Soft feedback
 * - notification: System notification
 *   - success: Success action
 *   - warning: Warning action
 *   - error: Error action
 * - selection: UI selection change
 */

import { useCallback } from 'react'
import WebApp from '@twa-dev/sdk'

type ImpactStyle = 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'
type NotificationType = 'success' | 'warning' | 'error'

export function useHaptic() {
  const impactOccurred = useCallback((style: ImpactStyle = 'medium') => {
    if (WebApp.HapticFeedback) {
      WebApp.HapticFeedback.impactOccurred(style)
    }
  }, [])

  const notificationOccurred = useCallback((type: NotificationType) => {
    if (WebApp.HapticFeedback) {
      WebApp.HapticFeedback.notificationOccurred(type)
    }
  }, [])

  const selectionChanged = useCallback(() => {
    if (WebApp.HapticFeedback) {
      WebApp.HapticFeedback.selectionChanged()
    }
  }, [])

  return {
    impactOccurred,
    notificationOccurred,
    selectionChanged,
  }
}
