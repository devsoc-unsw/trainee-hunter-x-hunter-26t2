// the visual layout of the keyboard. WHICH keys are unlocked lives in the
// backend (the key_unlocks table) and arrives via /users/me as a list of
// chars - the frontend used to be told a count and unlock a prefix of a fixed
// order, which stopped being true once the user got to pick.

// rows as they appear on screen
export const KEY_LAYOUT: string[][] = [
  ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
  ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
  ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
  ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
]

// 'unlockable' = still locked, but the user has a credit to spend on it.
// that's the click target for choosing where a new key goes.
export type KeyState = 'unlocked' | 'unlockable' | 'locked'

export function keyState(
  key: string,
  unlockedKeys: string[],
  unlockCredits = 0,
): KeyState {
  if (unlockedKeys.includes(key.toLowerCase())) return 'unlocked'
  return unlockCredits > 0 ? 'unlockable' : 'locked'
}
