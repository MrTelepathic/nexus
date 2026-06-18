/**
 * useBackButton — Control Telegram's BackButton
 *
 * The BackButton appears in the top-left corner when shown.
 * Use it for navigation within the Mini App.
 */

import { useCallback } from 'react'
import WebApp from '@twa-dev/sdk'

export function useBackButton() {
  const show = useCallback(() => {
    WebApp.BackButton.show()
  }, [])

  const hide = useCallback(() => {
    WebApp.BackButton.hide()
  }, [])

  const onClick = useCallback((callback: () => void) => {
    WebApp.BackButton.onClick(callback)
    return () => {
      WebApp.BackButton.offClick(callback)
    }
  }, [])

  return {
    show,
    hide,
    onClick,
    isVisible: WebApp.BackButton.isVisible,
  }
}
