/**
 * AuthProvider — initData Validation & Session Management
 *
 * On mount:
 * 1. Extract initData from Telegram Web App
 * 2. Send to backend /api/v1/auth/verify for HMAC validation
 * 3. Store validated user info
 * 4. Provide auth state to all components
 */

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import WebApp from '@twa-dev/sdk'
import { api } from '../lib/api'

interface User {
  user_id: number
  username: string | null
  first_name: string | null
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  initData: string
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  initData: '',
})

export const useAuth = () => useContext(AuthContext)

interface Props {
  children: ReactNode
}

export function AuthProvider({ children }: Props) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const initData = WebApp.initData

  useEffect(() => {
    async function authenticate() {
      if (!initData) {
        setIsLoading(false)
        return
      }

      try {
        const response = await api.post('/auth/verify', { init_data: initData })
        setUser(response.data)
      } catch (error) {
        console.error('Auth failed:', error)
        // In development, allow bypass
        if (import.meta.env.DEV) {
          setUser({
            user_id: 123456789,
            username: 'dev_user',
            first_name: 'Dev',
          })
        }
      } finally {
        setIsLoading(false)
      }
    }

    authenticate()
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        initData,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
