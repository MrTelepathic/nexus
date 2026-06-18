/**
 * TWAProvider — Telegram Web App SDK Context
 *
 * Wraps the app with @twa-dev/sdk context and provides
 * the TWA instance to all child components.
 */

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import WebApp from '@twa-dev/sdk'

interface TWAContextType {
  webapp: typeof WebApp
  isReady: boolean
  platform: string
  colorScheme: 'light' | 'dark'
}

const TWAContext = createContext<TWAContextType>({
  webapp: WebApp,
  isReady: false,
  platform: 'unknown',
  colorScheme: 'light',
})

export const useTWA = () => useContext(TWAContext)

interface Props {
  children: ReactNode
}

export function TWAProvider({ children }: Props) {
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Signal to Telegram that the Mini App is ready
    WebApp.ready()
    WebApp.expand()

    setIsReady(true)
  }, [])

  return (
    <TWAContext.Provider
      value={{
        webapp: WebApp,
        isReady,
        platform: WebApp.platform,
        colorScheme: WebApp.colorScheme,
      }}
    >
      {children}
    </TWAContext.Provider>
  )
}
