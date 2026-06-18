/**
 * User types
 */

export interface User {
  user_id: number
  username: string | null
  first_name: string | null
  last_name: string | null
  language_code: string | null
  is_premium: boolean
  role: string
}
