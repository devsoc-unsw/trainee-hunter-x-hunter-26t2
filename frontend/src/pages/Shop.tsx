import { useState } from 'react'
import type { ShopItem } from '../types'

// =============================================================================
// !!! HARDCODED DUMMY DATA !!! replace with listShop() from ../api/shop once
// the backend is wired up. items match backend/seed.sql; emoji stand in for
// image_url for now. DUMMY_COINS + handleBuy are fake local state too.
// =============================================================================
const DUMMY_ITEMS: (ShopItem & { emoji: string })[] = [
  { id: 's-1', name: 'Blue Keycaps', price: 50, image_url: '', owned: true, emoji: '🟦' },
  { id: 's-2', name: 'Pink Keycaps', price: 50, image_url: '', owned: false, emoji: '🌸' },
  { id: 's-3', name: 'Wooden Case', price: 150, image_url: '', owned: false, emoji: '🪵' },
  { id: 's-4', name: 'Cat Sticker', price: 25, image_url: '', owned: true, emoji: ':3' },
]

const DUMMY_COINS = 135

export default function Shop() {
  // TODO: swap for listShop() + buyItem(id) + refresh() when the backend exists.
  // remember buy can fail: 402 = too poor, show the error nicely
  const [items, setItems] = useState(DUMMY_ITEMS)
  const [coins, setCoins] = useState(DUMMY_COINS)
  const [error, setError] = useState('')

  //! HARDCODED DUMMY: just flips local state. real version calls buyItem(id)
  //! then refresh(), and shows the 402 error from the backend
  function handleBuy(id: string) {
    const item = items.find((i) => i.id === id)
    if (!item || item.owned) return
    if (item.price > coins) {
      setError("you can't afford that :(")
      return
    }
    setError('')
    setCoins((c) => c - item.price)
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, owned: true } : i)))
  }

  return (
    <div className="page p-6 mx-auto flex flex-col gap-6 text-slate-800">
      <div className="flex items-center justify-between bg-white p-6 rounded-xl border-2 border-slate-200">
        <h1 className="text-2xl font-black text-slate-900">Shop</h1>
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border-2 border-amber-200/80 rounded-2xl font-black text-yellow-700 text-base">
          <span>🪙</span>
          <span>{coins} Coins</span>
        </div>
      </div>

      {error && <p className="text-red-600 font-bold">{error}</p>}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {items.map((item) => (
          <div key={item.id}
          className="p-4 bg-white border-2 border-slate-200 rounded-xl flex flex-col items-center gap-2 text-center">
            <span className="text-3xl">{item.emoji}</span>
            <span className="text-sm font-bold text-slate-800">{item.name}</span>
            {item.owned ? (
              <span className="text-xs font-bold text-lime-600">Owned</span>
            ) : (
              <button type="button"
              onClick={() => handleBuy(item.id)}
              className="px-4 py-1.5 text-xs font-bold text-white bg-lime-600 hover:bg-lime-700 rounded-full">
                🪙 {item.price}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
