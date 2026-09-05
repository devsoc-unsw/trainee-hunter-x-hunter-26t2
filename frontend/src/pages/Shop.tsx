import { useEffect, useState } from 'react'
import type { ShopItem } from '../types'
import { listShop, buyItem } from '../api/shop'
import { useAuth } from '../auth/AuthContext'
import { ApiError } from '../api/client'
import { SHOP_ITEM_IMAGES } from '../lib/shopImages'

export default function Shop() {
  // TODO: swap for listShop() + buyItem(id) + refresh() when the backend exists.
  // remember buy can fail: 402 = too poor, show the error nicely
  const { me, refresh } = useAuth()
  const [items, setItems] = useState<ShopItem[]>([])
  const [error, setError] = useState('')
  const [buyingId, setBuyingId] = useState<string | null>(null)

  useEffect(() => {
    listShop()
      .then(setItems)
      .catch((err) => console.error('Failed to load shop:', err))
  }, [])

  async function handleBuy(id: string) {
    setError('')
    setBuyingId(id)
    try {
      await buyItem(id)
      await refresh()
      const updated = await listShop()
      setItems(updated)
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        setError("you can't afford that :(")
      } else if (err instanceof ApiError && err.status === 409) {
        setError("you've already purchased this! :(")
      } else {
        setError('something went wrong buying that')
      }
    } finally {
      setBuyingId(null)
    }
  }

  return (
    <div className="page p-6 mx-auto flex flex-col gap-6 text-slate-800">
      <div className="flex items-center justify-between bg-white p-6 rounded-xl border-2 border-slate-200">
        <h1 className="text-2xl font-black text-slate-900">Shop</h1>
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border-2 border-amber-200/80 rounded-2xl font-black text-yellow-700 text-base">
          <span>🪙</span>
          <span>{me?.coins ?? 0} Coins</span>
        </div>
      </div>

      {error && <p className="text-red-600 font-bold">{error}</p>}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {items.map((item) => (
          <div key={item.id}
          className="p-4 bg-white border-2 border-slate-200 rounded-xl flex flex-col items-center gap-2 text-center">
            <img src={SHOP_ITEM_IMAGES[item.slug]} alt={item.name} className="w-12 h-12 object-contain" />
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
