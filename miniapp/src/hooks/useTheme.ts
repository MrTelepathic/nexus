/**
 * useTheme — Access Telegram theme variables
 */

import { useState, useEffect } from 'react'
import WebApp from '@twa-dev/sdk'

export function useTheme() {
  const [isDark, setIsDark] = useState(WebApp.colorScheme === 'dark')

  useEffect(() => {
    const handler = () => {
      setIsDark(WebApp.colorScheme === 'dark')
    }
    WebApp.onEvent('themeChanged', handler)
    return () => {
      WebApp.offEvent('themeChanged', handler)
    }
  }, [])

  return {
    isDark,
    colorScheme: WebApp.colorScheme,
    themeParams: WebApp.themeParams,
  }
}
