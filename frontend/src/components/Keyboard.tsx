// the star of the show. draws the keyboard with however many keys the
// user has unlocked.
import { useEffect, useState } from 'react'
import Key from './Key'
import KeyPicker from './KeyPicker'
import { KEY_LAYOUT, keyState } from '../lib/keyboard'
import { SHOP_ITEM_IMAGES } from '../lib/shopImages'
import { getDecor, setSkin, setAccessory } from '../api/keyboard'
import { listInventory } from '../api/shop'
import type { KeyDecor, ShopItem } from '../types'


import grassKeyImg from '../assets/keys/grass_key.png'
import woodKeyImg from '../assets/keys/wood_key.png'

interface KeyboardProps {
  unlockedCount?: number
  activeKey?: string | null
  pressCounts?: Record<string, number>
  editable?: boolean
}

export default function Keyboard({ unlockedCount=0, activeKey=null, pressCounts={}, editable=false }: KeyboardProps) {
  const [decor, setDecor] = useState<KeyDecor[]>([])
  const [inventory, setInventory] = useState<ShopItem[]>([])
  const [openKey, setOpenKey] = useState<string | null>(null)

  useEffect(() => {
    getDecor().then(setDecor).catch((err) => console.error('Failed to load decor:', err))
  }, [])

  useEffect(() => {
    if (!editable) return
    listInventory().then(setInventory).catch((err) => console.error('Failed to load inventory:', err))
  }, [editable])

  function findDecor(key: string): KeyDecor | undefined {
    return decor.find((d) => d.key_char === key)
  }

  async function refreshDecor() {
    const updated = await getDecor()
    setDecor(updated)
  }

  async function handleSetSkin(key: string, slug: string | null) {
    await setSkin(key, slug)
    await refreshDecor()
  }

  async function handleSetAccessory(key: string, slug: string | null) {
    await setAccessory(key, slug)
    await refreshDecor()
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex flex-col items-center">
        {KEY_LAYOUT.map((row, rowIndex) => (
          <div key={rowIndex}
          className="flex -mb-3">
            {row.map((keyLabel) => {
              const key = keyLabel.toLowerCase()
              const state = keyState(keyLabel, unlockedCount)
              const keyDecor = findDecor(key)

              let keyImage = state === 'unlocked' ? grassKeyImg : woodKeyImg
              if (state === 'unlocked' && keyDecor?.skin_slug) {
                keyImage = SHOP_ITEM_IMAGES[keyDecor.skin_slug] ?? keyImage
              }
              const accessoryImage = state === 'unlocked' && keyDecor?.accessory_slug
                ? SHOP_ITEM_IMAGES[keyDecor.accessory_slug]
                : undefined
              
              const isPressed = activeKey === key
              const count = pressCounts[keyLabel.toLowerCase()] || 0

              return (
                  <Key
                    key={keyLabel}
                    label={keyLabel}
                    state={state}
                    image={keyImage}
                    accessoryImage={accessoryImage}
                    isPressed={isPressed}
                    count={count}
                    onClick={editable ? () => setOpenKey(key) : undefined}
                  />
                )
            })}
          </div>
        ))}
      </div>
      {editable && openKey && (
        <KeyPicker
          keyChar={openKey}
          decor={findDecor(openKey)}
          inventory={inventory}
          onSetSkin={(slug) => handleSetSkin(openKey, slug)}
          onSetAccessory={(slug) => handleSetAccessory(openKey, slug)}
          onClose={() => setOpenKey(null)}
        />
      )}

    </div>

  )
}