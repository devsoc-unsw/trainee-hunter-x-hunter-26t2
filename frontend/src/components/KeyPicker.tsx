import type { ShopItem, KeyDecor } from '../types'
import { unplaced } from '../types'
import { SHOP_ITEM_IMAGES } from '../lib/shopImages'
import grassKeyImg from '../assets/keys/grass_key.png'

interface KeyPickerProps {
  keyChar: string
  decor: KeyDecor | undefined
  inventory: ShopItem[]
  onSetSkin: (slug: string | null) => void
  onSetAccessory: (slug: string | null) => void
  onClose: () => void
}

// one item button. greyed out when every copy is already on another key -
// except the one this key is currently wearing, which is always re-selectable.
function ItemButton({ item, selected, onPick }: {
  item: ShopItem
  selected: boolean
  onPick: () => void
}) {
  const available = unplaced(item)
  const disabled = !selected && available < 1

  return (
    <button
      onClick={disabled ? undefined : onPick}
      disabled={disabled}
      title={disabled ? `All ${item.quantity} are on other keys` : item.name}
      className={`relative p-2 rounded-lg border-2 transition
        ${selected ? 'border-lime-500' : 'border-slate-200'}
        ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer hover:border-slate-400'}`}
    >
      <img src={SHOP_ITEM_IMAGES[item.slug]} alt={item.name} className="w-10 h-10 object-contain" />
      <span className={`absolute -top-1.5 -right-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full border border-white shadow-sm
        ${available > 0 ? 'bg-lime-500 text-white' : 'bg-slate-400 text-white'}`}>
        {available}
      </span>
    </button>
  )
}

export default function KeyPicker({ keyChar, decor, inventory, onSetSkin, onSetAccessory, onClose }: KeyPickerProps) {
    // quantity 0 rows stick around forever (key_decor's foreign key cascades
    // off them, so nothing deletes them), so filter on what's actually held
    const held = inventory.filter((i) => i.quantity > 0)
    const skins = held.filter((i) => i.kind === 'key_skin')
    const accessories = held.filter((i) => i.kind === 'accessory')

    const currentSkinItem = inventory.find((i) => i.slug === decor?.skin_slug)
    const currentHabitat = currentSkinItem?.habitat ?? 'land'
    const matchingAccessories = accessories.filter((a) => a.habitat === currentHabitat)

    return (
        <div className="bg-white border-2 border-slate-200 rounded-xl p-4 flex flex-col gap-4 w-full">
            <div className="flex items-center justify-between">
                <h3 className="font-black text-slate-900">Customise "{keyChar.toUpperCase()}"</h3>
                <button onClick={onClose} className="text-slate-400 hover:text-slate-600 font-bold cursor-pointer">✕</button>
            </div>

            <p className="text-xs text-slate-400 -mt-2">
                The badge is how many you have left to plant. Taking one off a key gives it back.
            </p>

            <div>
                <p className="text-xs font-bold text-slate-500 mb-2">Key skin</p>
                <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => onSetSkin(null)}
                    title="Grass (default, free)"
                    className={`p-2 rounded-lg border-2 cursor-pointer ${decor?.skin_slug == null ? 'border-lime-500' : 'border-slate-200'}`}
                >
                    <img src={grassKeyImg} alt="Grass (default)" className="w-10 h-10 object-contain" />
                </button>
                {skins.map((item) => (
                    <ItemButton
                      key={item.id}
                      item={item}
                      selected={decor?.skin_slug === item.slug}
                      onPick={() => onSetSkin(item.slug)}
                    />
                ))}
                {skins.length === 0 && (
                    <p className="text-xs text-slate-400 italic self-center">No skins owned yet — buy some in the shop.</p>
                )}
                </div>
            </div>

            <div>
                <p className="text-xs font-bold text-slate-500 mb-2">Accessory</p>
                <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => onSetAccessory(null)}
                    className={`p-2 rounded-lg border-2 text-xs font-bold text-slate-500 cursor-pointer ${decor?.accessory_slug == null ? 'border-lime-500' : 'border-slate-200'}`}
                >
                    None
                </button>
                {matchingAccessories.map((item) => (
                    <ItemButton
                      key={item.id}
                      item={item}
                      selected={decor?.accessory_slug === item.slug}
                      onPick={() => onSetAccessory(item.slug)}
                    />
                ))}
                {matchingAccessories.length === 0 && (
                    <p className="text-xs text-slate-400 italic self-center">No matching accessories owned for this key's habitat.</p>
                )}
                </div>
            </div>
        </div>
    )
}
