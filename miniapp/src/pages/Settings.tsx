/**
 * Settings Page — Bot configuration
 */

import { motion } from 'framer-motion'
import WebApp from '@twa-dev/sdk'
import { useBiometric } from '../hooks/useBiometric'

export default function Settings() {
  const { isAvailable, isAuthenticated, openSettings } = useBiometric()

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      <h1 className="text-2xl font-bold mb-4">Settings</h1>

      <div className="space-y-1">
        <div className="p-4 bg-tg-section-bg rounded-xl">
          <p className="font-medium">Biometric Auth</p>
          <p className="text-sm text-tg-text-secondary mt-1">
            {isAvailable
              ? isAuthenticated
                ? '✅ Enabled'
                : '⚠️ Available but not set up'
              : '❌ Not available on this device'}
          </p>
          {isAvailable && (
            <button
              onClick={openSettings}
              className="text-tg-link text-sm mt-2"
            >
              Configure
            </button>
          )}
        </div>

        <div className="p-4 bg-tg-section-bg rounded-xl">
          <p className="font-medium">Theme</p>
          <p className="text-sm text-tg-text-secondary mt-1">
            Synced with Telegram ({WebApp.colorScheme})
          </p>
        </div>

        <div className="p-4 bg-tg-section-bg rounded-xl">
          <p className="font-medium">Platform</p>
          <p className="text-sm text-tg-text-secondary mt-1">
            {WebApp.platform}
          </p>
        </div>
      </div>
    </motion.div>
  )
}
