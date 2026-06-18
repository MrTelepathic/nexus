/**
 * useMainButton — Control Telegram's MainButton
 *
 * The MainButton is the primary action button at the bottom
 * of the Mini App (like "Pay", "Submit", etc.)
 */

import { useCallback } from 'react'
import WebApp from '@twa-dev/sdk'

export function useMainButton() {
  const setText = useCallback((text: string) => {
    WebApp.MainButton.setText(text)
  }, [])

  const show = useCallback(() => {
    WebApp.MainButton.show()
  }, [])

  const hide = useCallback(() => {
    WebApp.MainButton.hide()
  }, [])

  const enable = useCallback(() => {
    WebApp.MainButton.enable()
  }, [])

  const disable = useCallback(() => {
    WebApp.MainButton.disable()
  }, [])

  const showProgress = useCallback((leaveProgress?: boolean) => {
    WebApp.MainButton.showProgress(leaveProgress)
  }, [])

  const hideProgress = useCallback(() => {
    WebApp.MainButton.hideProgress()
  }, [])

  const onClick = useCallback((callback: () => void) => {
    WebApp.MainButton.onClick(callback)
    return () => {
      WebApp.MainButton.offClick(callback)
    }
  }, [])

  return {
    setText,
    show,
    hide,
    enable,
    disable,
    showProgress,
    hideProgress,
    onClick,
    color: WebApp.MainButton.color,
    textColor: WebApp.MainButton.textColor,
    isActive: WebApp.MainButton.isActive,
    isVisible: WebApp.MainButton.isVisible,
  }
}
