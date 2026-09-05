// the star of the show. draws the keyboard: the keys the user has unlocked,
// plus the locked ones they can spend an unlock credit on.
import { useCallback, useEffect, useState } from 'react'
import Key from './Key'
import KeyPicker from './KeyPicker'
import { KEY_LAYOUT, keyState } from '../lib/keyboard'
import { SHOP_ITEM_IMAGES } from '../lib/shopImages'
import { getDecor, setSkin, setAccessory, unlockKey } from '../api/keyboard'
import { listInventory } from '../api/shop'
import { getToken, ApiError } from '../api/client'
import type { KeyDecor, ShopItem } from '../types'


import grassKeyImg from '../assets/keys/grass_key.png'
import woodKeyImg from '../assets/keys/wood_key.png'

interface KeyboardProps {
  // which keys are unlocked. comes straight off /users/me
  unlockedKeys?: string[]
  // unlocks earned but not yet placed. > 0 makes locked keys clickable.
  unlockCredits?: number
  activeKey?: string | null
  pressCounts?: Record<string, number>
  editable?: boolean
  // called after a key is unlocked or decorated, so the page can refresh
  // /users/me (coins, credits) alongside our own local state
  onChange?: () => void | Promise<void>
}

export default function Keyboard({
  unlockedKeys = [],
  unlockCredits = 0,
  activeKey = null,
  pressCounts = {},
  editable = false,
  onChange,
}: KeyboardProps) {
  const [decor, setDecor] = useState<KeyDecor[]>([])
  const [inventory, setInventory] = useState<ShopItem[]>([])
  const [openKey, setOpenKey] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    // Landing.tsx renders a demo keyboard while logged out - don't ask the
    // api for decor we can't be authorised to read
    if (!getToken()) return
    getDecor().then(setDecor).catch((err) => console.error('Failed to load decor:', err))
  }, [])

  const refreshInventory = useCallback(async () => {
    if (!editable) return
    setInventory(await listInventory())
  }, [editable])

  useEffect(() => {
    if (!editable) return
    listInventory()
      .then(setInventory)
      .catch((err) => console.error('Failed to load inventory:', err))
  }, [editable])

  function findDecor(key: string): KeyDecor | undefined {
    return decor.find((d) => d.key_char === key)
  }

  // placing an item uses one up and removing one frees it, so the picker's
  // remaining counts go stale on every write - inventory has to come back too,
  // not just decor
  async function refreshAll() {
    setDecor(await getDecor())
    await refreshInventory()
    await onChange?.()
  }

  async function run(action: () => Promise<unknown>) {
    setError('')
    try {
      await action()
      await refreshAll()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'something went wrong')
    }
  }

  async function handleKeyClick(key: string, state: string) {
    if (state === 'unlockable') {
      // spending a credit is the click itself - no picker, the key just
      // becomes yours and lands on the default grass
      await run(() => unlockKey(key))
      return
    }
    setOpenKey(key)
  }

  return (
    <div className="flex flex-col items-center gap-4">
      {editable && unlockCredits > 0 && (
        <p className="text-sm font-bold text-lime-700 bg-lime-50 border-2 border-lime-200 rounded-xl px-4 py-2">
          🔓 {unlockCredits} key{unlockCredits === 1 ? '' : 's'} to place — click any locked key
        </p>
      )}

      <div className="flex flex-col items-center">
        {KEY_LAYOUT.map((row, rowIndex) => (
          <div key={rowIndex}
          className="flex -mb-3">
            {row.map((keyLabel) => {
              const key = keyLabel.toLowerCase()
              const state = keyState(key, unlockedKeys, editable ? unlockCredits : 0)
              const keyDecor = findDecor(key)

              let keyImage = state === 'unlocked' ? grassKeyImg : woodKeyImg
              if (state === 'unlocked' && keyDecor?.skin_slug) {
                keyImage = SHOP_ITEM_IMAGES[keyDecor.skin_slug] ?? keyImage
              }
              const accessoryImage = state === 'unlocked' && keyDecor?.accessory_slug
                ? SHOP_ITEM_IMAGES[keyDecor.accessory_slug]
                : undefined

              const isPressed = activeKey === key
              const count = pressCounts[key] || 0

              return (
                  <Key
                    key={keyLabel}
                    label={keyLabel}
                    state={state}
                    image={keyImage}
                    accessoryImage={accessoryImage}
                    isPressed={isPressed}
                    count={count}
                    onClick={editable ? () => handleKeyClick(key, state) : undefined}
                  />
                )
            })}
          </div>
        ))}
      </div>

      {error && <p className="text-sm font-bold text-red-600">{error}</p>}

      {editable && openKey && (
        <KeyPicker
          keyChar={openKey}
          decor={findDecor(openKey)}
          inventory={inventory}
          onSetSkin={(slug) => run(() => setSkin(openKey, slug))}
          onSetAccessory={(slug) => run(() => setAccessory(openKey, slug))}
          onClose={() => setOpenKey(null)}
        />
      )}

    </div>

  )
}
