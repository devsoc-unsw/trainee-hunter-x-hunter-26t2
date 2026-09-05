import { useEffect, useState } from 'react'
import type { ShopItem } from '../types'
import { unplaced } from '../types'
import { listShop, buyItem } from '../api/shop'
import { useAuth } from '../auth/AuthContext'
import { ApiError } from '../api/client'
import { SHOP_ITEM_IMAGES } from '../lib/shopImages'

export default function Shop() {
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
      // /users/me carries coins AND unlock credits, and the shop rows carry
      // the new quantity - both change on a purchase
      await refresh()
      setItems(await listShop())
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        setError("you can't afford that :(")
      } else if (err instanceof ApiError) {
        // 409 is no longer "already owned" - items stack. it's the keyboard
        // being full, so show what the api actually said.
        setError(err.message)
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
        <div>
          <h1 className="text-2xl font-black text-slate-900">Shop</h1>
          <p className="text-xs font-semibold text-slate-400 mt-1">
            One copy dresses one key — buy as many as you need
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border-2 border-amber-200/80 rounded-2xl font-black text-yellow-700 text-base">
          <span>🪙</span>
          <span>{me?.coins ?? 0} Coins</span>
        </div>
      </div>

      {error && <p className="text-red-600 font-bold">{error}</p>}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {items.map((item) => {
          const isKeyUnlock = item.kind === 'key_unlock'
          const available = unplaced(item)
          const tooPoor = (me?.coins ?? 0) < item.price

          return (
            <div key={item.id}
            className="p-4 bg-white border-2 border-slate-200 rounded-xl flex flex-col items-center gap-2 text-center">
              <img src={SHOP_ITEM_IMAGES[item.slug]} alt={item.name} className="w-12 h-12 object-contain" />
              <span className="text-sm font-bold text-slate-800">{item.name}</span>

              {/* a key unlock isn't stocked - it becomes a credit, and the
                  credit count lives on /users/me */}
              {isKeyUnlock ? (
                <span className="text-xs font-semibold text-slate-400">
                  {me?.unlock_credits ? `${me.unlock_credits} to place` : 'Choose any locked key'}
                </span>
              ) : item.quantity > 0 ? (
                <span className="text-xs font-bold text-lime-600">
                  Owned {item.quantity}
                  {item.placed > 0 && (
                    <span className="text-slate-400 font-semibold"> · {available} free</span>
                  )}
                </span>
              ) : (
                <span className="text-xs font-semibold text-slate-300">Not owned</span>
              )}

              <button type="button"
              onClick={() => handleBuy(item.id)}
              disabled={buyingId === item.id || tooPoor}
              className="px-4 py-1.5 text-xs font-bold text-white bg-lime-600 hover:bg-lime-700 rounded-full
                disabled:bg-slate-300 disabled:cursor-not-allowed cursor-pointer transition-colors">
                {buyingId === item.id ? '…' : `🪙 ${item.price}`}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
