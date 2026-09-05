import { useAuth } from '../auth/AuthContext'
import ProgressBar from '../components/ProgressBar'
import Keyboard from '../components/Keyboard'
import { useNavigate } from 'react-router-dom'
import { logout } from '../api/auth'
import { useCallback, useEffect, useState } from 'react'
import { listInventory } from '../api/shop'
import type { ShopItem } from '../types'
import { unplaced } from '../types'
import { SHOP_ITEM_IMAGES } from '../lib/shopImages'

export default function Profile() {
  const { me, refresh } = useAuth()
  const navigate = useNavigate()
  const [inventory, setInventory] = useState<ShopItem[]>([])

  // decorating a key changes what's free to plant, so this has to be
  // re-readable rather than fetched once on mount
  const loadInventory = useCallback(() => {
    listInventory()
      .then(setInventory)
      .catch((err) => console.error('Failed to load inventory:', err))
  }, [])

  useEffect(loadInventory, [loadInventory])

  const handleLogout = async () => {
    try {
      await logout()
    } catch (err) {
      console.error('Logout failed:', err)
    } finally {
      // Refresh auth context state and redirect to login page
      await refresh()
      navigate('/login')
    }
  }


  return (
    <div className="p-6 mx-auto flex flex-col gap-6 text-slate-800">
      <div className="flex items-center justify-between bg-white p-6 rounded-xl border-2 border-slate-200">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-xl bg-lime-500 text-white font-black text-2xl flex items-center justify-center uppercase">
            <p>{me?.username?.[0] ?? 'u'}</p>
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">
              {me?.username ?? 'not logged in'}
            </h1>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border-2 border-amber-200/80 rounded-2xl font-black text-yellow-700 text-base">
            <span>🪙</span>
            <span>{me?.coins ?? 0} Coins</span>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2
            bg-red-50 border-2 border-red-200/80 rounded-2xl font-black text-red-700 text-base hover:bg-red-100 cursor-pointer transition-colors">
            <span>Logout</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="flex flex-col gap-6">
          <div>
            <ProgressBar />
          </div>

          <div className="w-full bg-slate-50 p-4 rounded-xl border-2 border-slate-200">
            <Keyboard
              unlockedKeys={me?.unlocked_keys ?? []}
              unlockCredits={me?.unlock_credits ?? 0}
              editable
              // a placement or an unlock changes both /users/me (coins,
              // credits) and what's left in the inventory panel
              onChange={async () => {
                await refresh()
                loadInventory()
              }}
            />
          </div>
        </div>

        {/* inventory */}
        <div className="bg-white p-6 rounded-2xl border-2 border-slate-200 flex flex-col gap-4 mt-0">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="text-lg font-black text-slate-900">Inventory</h2>
            <span className="text-xs font-semibold text-slate-400">Free to plant / owned</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {inventory.filter((item) => item.quantity > 0).map((item) => (
              <div key={item.id} className="relative p-3 bg-slate-50 border border-slate-200 rounded-xl flex flex-col items-center justify-center gap-1.5 text-center">
                <span className="absolute top-1.5 right-1.5 text-[10px] font-bold text-slate-500 bg-white border border-slate-200 rounded-full px-1.5 py-0.5">
                  {unplaced(item)}/{item.quantity}
                </span>
                <img src={SHOP_ITEM_IMAGES[item.slug]} alt={item.name} className="w-12 h-12 object-contain" />
                <span className="text-xs font-bold text-slate-700">{item.name}</span>
              </div>
            ))}
            {inventory.every((item) => item.quantity === 0) && (
              <p className="text-xs text-slate-400 italic col-span-full">
                Nothing bought yet — the shop has flowers.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
