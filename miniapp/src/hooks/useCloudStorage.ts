/**
 * useCloudStorage — Telegram CloudStorage API
 *
 * Persist key-value data synced across devices via Telegram.
 * Storage is per-user, per-bot (512KB total limit).
 */

import { useState, useCallback } from 'react'
import WebApp from '@twa-dev/sdk'

export function useCloudStorage() {
  const [error, setError] = useState<string | null>(null)

  const setItem = useCallback(async (key: string, value: string): Promise<boolean> => {
    return new Promise((resolve) => {
      WebApp.CloudStorage.setItem(key, value, (success, err) => {
        if (err) setError(err)
        else setError(null)
        resolve(success)
      })
    })
  }, [])

  const getItem = useCallback(async (key: string): Promise<string | null> => {
    return new Promise((resolve) => {
      WebApp.CloudStorage.getItem(key, (value, err) => {
        if (err) {
          setError(err)
          resolve(null)
        } else {
          setError(null)
          resolve(value)
        }
      })
    })
  }, [])

  const getItems = useCallback(async (keys: string[]): Promise<Record<string, string>> => {
    return new Promise((resolve) => {
      WebApp.CloudStorage.getItems(keys, (values, err) => {
        if (err) {
          setError(err)
          resolve({})
        } else {
          setError(null)
          resolve(values)
        }
      })
    })
  }, [])

  const removeItem = useCallback(async (key: string): Promise<boolean> => {
    return new Promise((resolve) => {
      WebApp.CloudStorage.removeItem(key, (success, err) => {
        if (err) setError(err)
        else setError(null)
        resolve(success)
      })
    })
  }, [])

  return { setItem, getItem, getItems, removeItem, error }
}
