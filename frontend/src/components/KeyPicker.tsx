import type { ShopItem, KeyDecor } from '../types'
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

export default function KeyPicker({ keyChar, decor, inventory, onSetSkin, onSetAccessory, onClose }: KeyPickerProps) {
    const skins = inventory.filter((i) => i.kind === 'key_skin')
    const accessories = inventory.filter((i) => i.kind === 'accessory')

    const currentSkinItem = inventory.find((i) => i.slug === decor?.skin_slug)
    const currentHabitat = currentSkinItem?.habitat ?? 'land'
    const matchingAccessories = accessories.filter((a) => a.habitat === currentHabitat)

    return (
        <div className="bg-white border-2 border-slate-200 rounded-xl p-4 flex flex-col gap-4">
            <div className="flex items-center justify-between">
                <h3 className="font-black text-slate-900">Customise "{keyChar.toUpperCase()}"</h3>
                <button onClick={onClose} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <div>
                <p className="text-xs font-bold text-slate-500 mb-2">Key skin</p>
                <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => onSetSkin(null)}
                    className={`p-2 rounded-lg border-2 ${decor?.skin_slug == null ? 'border-lime-500' : 'border-slate-200'}`}
                >
                    <img src={grassKeyImg} alt="Grass (default)" className="w-10 h-10 object-contain" />
                </button>
                {skins.map((item) => (
                    <button
                    key={item.id}
                    onClick={() => onSetSkin(item.slug)}
                    className={`p-2 rounded-lg border-2 ${decor?.skin_slug === item.slug ? 'border-lime-500' : 'border-slate-200'}`}
                    >
                    <img src={SHOP_ITEM_IMAGES[item.slug]} alt={item.name} className="w-10 h-10 object-contain" />
                    </button>
                ))}
                </div>
            </div>

            <div>
                <p className="text-xs font-bold text-slate-500 mb-2">Accessory</p>
                <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => onSetAccessory(null)}
                    className={`p-2 rounded-lg border-2 text-xs font-bold text-slate-500 ${decor?.accessory_slug == null ? 'border-lime-500' : 'border-slate-200'}`}
                >
                    None
                </button>
                {matchingAccessories.map((item) => (
                    <button
                    key={item.id}
                    onClick={() => onSetAccessory(item.slug)}
                    className={`p-2 rounded-lg border-2 ${decor?.accessory_slug === item.slug ? 'border-lime-500' : 'border-slate-200'}`}
                    >
                    <img src={SHOP_ITEM_IMAGES[item.slug]} alt={item.name} className="w-10 h-10 object-contain" />
                    </button>
                ))}
                {matchingAccessories.length === 0 && (
                    <p className="text-xs text-slate-400 italic">No matching accessories owned for this key's habitat.</p>
                )}
                </div>
            </div>
        </div>
    )
}