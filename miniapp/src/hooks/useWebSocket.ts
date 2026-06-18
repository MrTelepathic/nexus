/**
 * useWebSocket — Subscribe to real-time data streams
 */

import { useEffect, useCallback } from 'react'
import { useWebSocket as useWSContext } from '../providers/WebSocketProvider'

export function useRoomSubscription(room: string) {
  const { isConnected, subscribe, unsubscribe, onMessage } = useWSContext()

  useEffect(() => {
    if (isConnected) {
      subscribe(room)
      return () => unsubscribe(room)
    }
  }, [isConnected, room])

  return { isConnected }
}

export function useRealtimeData<T>(type: string, initialData: T) {
  const { onMessage, isConnected } = useWSContext()
  const [data, setData] = React.useState<T>(initialData)

  useEffect(() => {
    const unsub = onMessage(type, (msg) => {
      if (msg.data) {
        setData(msg.data as T)
      }
    })
    return unsub
  }, [type])

  return { data, isConnected }
}
