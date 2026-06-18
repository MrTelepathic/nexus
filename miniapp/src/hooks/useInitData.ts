/**
 * useInitData — Access validated Telegram initData
 */

import WebApp from '@twa-dev/sdk'

export function useInitData() {
  return WebApp.initData || null
}
