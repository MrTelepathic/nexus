/**
 * WebSocketProvider — Real-time Dashboard Connection
 *
 * Manages a persistent WebSocket connection to the backend
 * for live updates: sales feed, analytics, leaderboard.
 *
 * Protocol:
 * 1. Connect to /ws/dashboard
 * 2. Send auth message with initData
 * 3. Subscribe to rooms (dashboard, leaderboard)
 * 4. Receive real-time updates
 */

import { createContext, useContext, useEffect, useState, useRef, ReactNode, useCallback } from 'react'
import WebApp from '@twa-dev/sdk'

interface WSMessage {
  type: string
  [key: string]: unknown
}

interface WebSocketContextType {
  isConnected: boolean
  subscribe: (room: string) => void
  unsubscribe: (room: string) => void
  onMessage: (type: string, handler: (data: WSMessage) => void) => () => void
}

const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  subscribe: () => {},
  unsubscribe: () => {},
  onMessage: () => () => {},
})

export const useWebSocket = () => useContext(WebSocketContext)

interface Props {
  children: ReactNode
}

export function WebSocketProvider({ children }: Props) {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const listenersRef = useRef<Map<string, Set<(data: WSMessage) => void>>>(new Map())
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    const initData = WebApp.initData
    if (!initData) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`

    const ws = new WebSocket(`${host}/ws/dashboard`)

    ws.onopen = () => {
      // Send auth message
      ws.send(JSON.stringify({
        type: 'auth',
        init_data: initData,
      }))
    }

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data)

        if (msg.type === 'auth_ok') {
          setIsConnected(true)
          return
        }

        if (msg.type === 'auth_error') {
          console.error('WS auth failed:', msg.detail)
          return
        }

        // Dispatch to listeners
        const handlers = listenersRef.current.get(msg.type)
        if (handlers) {
          handlers.forEach((handler) => handler(msg))
        }
      } catch (e) {
        console.error('WS parse error:', e)
      }
    }

    ws.onclose = () => {
      setIsConnected(false)
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(connect, 3000)
    }

    ws.onerror = (error) => {
      console.error('WS error:', error)
    }

    wsRef.current = ws
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      wsRef.current?.close()
    }
  }, [connect])

  const subscribe = useCallback((room: string) => {
    wsRef.current?.send(JSON.stringify({ type: 'subscribe', room }))
  }, [])

  const unsubscribe = useCallback((room: string) => {
    wsRef.current?.send(JSON.stringify({ type: 'unsubscribe', room }))
  }, [])

  const onMessage = useCallback((type: string, handler: (data: WSMessage) => void) => {
    if (!listenersRef.current.has(type)) {
      listenersRef.current.set(type, new Set())
    }
    listenersRef.current.get(type)!.add(handler)

    return () => {
      listenersRef.current.get(type)?.delete(handler)
    }
  }, [])

  return (
    <WebSocketContext.Provider value={{ isConnected, subscribe, unsubscribe, onMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}
