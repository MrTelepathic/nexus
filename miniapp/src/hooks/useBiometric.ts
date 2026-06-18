/**
 * useBiometric — Biometric Authentication
 *
 * Fingerprint/Face ID for securing the financial section.
 * Only available on supported devices.
 */

import { useState, useEffect, useCallback } from 'react'
import WebApp from '@twa-dev/sdk'

export function useBiometric() {
  const [isAvailable, setIsAvailable] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const biometric = WebApp.BiometricManager
    setIsAvailable(biometric.isBiometricAvailable)

    if (biometric.isBiometricAvailable) {
      setIsAuthenticated(biometric.isBiometricAuthenticated)
    }
  }, [])

  const authenticate = useCallback(async (): Promise<boolean> => {
    const biometric = WebApp.BiometricManager
    if (!biometric.isBiometricAvailable) {
      return false
    }

    return new Promise((resolve) => {
      biometric.authenticate(
        (success) => {
          setIsAuthenticated(success)
          resolve(success)
        },
        {
          title: 'Verify Identity',
          subtitle: 'Confirm your identity to access financial features',
          reason: 'Biometric verification required for payment operations',
        },
      )
    })
  }, [])

  const openSettings = useCallback(() => {
    WebApp.BiometricManager.openSettings()
  }, [])

  return {
    isAvailable,
    isAuthenticated,
    authenticate,
    openSettings,
  }
}
