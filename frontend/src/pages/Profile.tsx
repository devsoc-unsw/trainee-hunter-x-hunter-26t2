import { useAuth } from '../auth/AuthContext'
import ProgressBar from '../components/ProgressBar';
import Keyboard from '../components/Keyboard';

// =============================================================================
// !!! HARDCODED DUMMY DATA !!! replace with listInventory() from ../api/shop
// once the backend is wired up
// =============================================================================
const DUMMY_INVENTORY = [
  { id: 's-1', name: 'Blue Keycaps', emoji: '🟦' },
  { id: 's-4', name: 'Cat Sticker', emoji: ':3' },
]

export default function Profile() {
  const { me } = useAuth()


  // TODO: show stats (coins, solved count, keys unlocked), the inventory
  // (listInventory), and an edit-username form that calls updateUsername
  // then refresh()
  return (
    
    //   {me && <p>{me.username}</p>}
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

        <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border-2 border-amber-200/80 rounded-2xl font-black text-yellow-700 text-base">
          <span>🪙</span>
          <span>{me?.coins ?? 0} Coins</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <div className="flex flex-col gap-6">
          <div>
            <ProgressBar />
          </div>

          <div className="w-full bg-slate-50 p-4 rounded-xl border-2 border-slate-200">
            <Keyboard unlockedCount={17}/>
          </div>
        </div>

        {/* inventory */}
        <div className="bg-white p-6 rounded-2xl border-2 border-slate-200 flex flex-col gap-4 mt-0">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="text-lg font-black text-slate-900">Inventory</h2>
            <span className="text-xs font-semibold text-slate-400">Items owned</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {DUMMY_INVENTORY.map((item) => (
              <div key={item.id} className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex flex-col items-center justify-center gap-1.5 text-center">
                {/* emoji is just temporary, should be a drawn image instead */}
                <span className="text-2xl">{item.emoji}</span>
                <span className="text-xs font-bold text-slate-700">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
