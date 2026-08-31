// the visual layout of the keyboard. the ORDER keys unlock in lives in the
// backend (backend/keyboard.py) - the frontend just gets told how many keys
// are unlocked via /users/me and draws them.

// this must stay in sync with backend/keyboard.py KEY_UNLOCK_ORDER
export const KEY_UNLOCK_ORDER = [
  'f', 'j', 'd', 'k', 's', 'l', 'a', ';',
  'g', 'h', 'r', 'u', 'e', 'i', 'w', 'o', 'q', 'p',
  't', 'y', 'v', 'm', 'c', 'n', 'x', 'b', 'z', ',', '.', '/',
  '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
]

// rows as they appear on screen
export const KEY_LAYOUT: string[][] = [
  ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
  ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
  ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
  ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
]

export type KeyState = 'unlocked' | 'locked' | 'next'

export function keyState(_key: string, _unlockedCount: number): KeyState {
  // 'unlocked' if the key's position in KEY_UNLOCK_ORDER is < unlockedCount,
  // 'next' if it's the very next one to unlock (nice for a little glow),
  // 'locked' otherwise
  // throw new Error('not implemented')
  const index = KEY_UNLOCK_ORDER.indexOf(_key)

  // Key is not in unlock order array
  if (index === -1) return 'locked'

  if (index < _unlockedCount) {
    return 'unlocked'
  } else if (index === _unlockedCount) {
    return 'next'
  } else {
    return 'locked'
  }
}
