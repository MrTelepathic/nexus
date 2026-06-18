/**
 * ThemeProvider — Live Telegram Theme Sync
 *
 * Maps Telegram's theme variables to CSS custom properties.
 * Updates in real-time when the user changes their Telegram theme.
 *
 * Telegram provides these CSS variables:
 * --tg-theme-bg-color
 * --tg-theme-text-color
 * --tg-theme-hint-color
 * --tg-theme-link-color
 * --tg-theme-button-color
 * --tg-theme-button-text-color
 * --tg-theme-secondary-bg-color
 * --tg-theme-header-bg-color
 * --tg-theme-accent-text-color
 * --tg-theme-section-bg-color
 * --tg-theme-section-header-text-color
 * --tg-theme-section-separator-color
 * --tg-theme-subtitle-text-color
 * --tg-theme-destructive-text-color
 * --tg-theme-secondary-button-color
 * --tg-theme-secondary-button-text-color
 */

import { createContext, useContext, useEffect, ReactNode } from 'react'
import WebApp from '@twa-dev/sdk'

interface ThemeContextType {
  isDark: boolean
  accentColor: string
}

const ThemeContext = createContext<ThemeContextType>({
  isDark: false,
  accentColor: '#2481cc',
})

export const useTheme = () => useContext(ThemeContext)

interface Props {
  children: ReactNode
}

export function ThemeProvider({ children }: Props) {
  useEffect(() => {
    // Apply theme on mount
    applyTheme()

    // Listen for theme changes (Bot API 8.0 feature)
    WebApp.onEvent('themeChanged', applyTheme)

    return () => {
      WebApp.offEvent('themeChanged', applyTheme)
    }
  }, [])

  const isDark = WebApp.colorScheme === 'dark'

  return (
    <ThemeContext.Provider
      value={{
        isDark,
        accentColor: '#2481cc', // Will be read from CSS var
      }}
    >
      {children}
    </ThemeContext.Provider>
  )
}

function applyTheme() {
  // Telegram automatically injects CSS variables into :root
  // We just need to update the <meta theme-color> for the status bar
  const bgColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--tg-theme-bg-color')
    .trim()

  if (bgColor) {
    const meta = document.querySelector('meta[name="theme-color"]')
    if (meta) {
      meta.setAttribute('content', bgColor)
    }
  }
}
