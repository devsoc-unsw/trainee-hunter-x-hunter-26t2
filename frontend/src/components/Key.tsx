import type { KeyState } from '../lib/keyboard'

interface KeyProps {
  label: string
  state: KeyState
  // when the handdrawn key images are ready, drop them in src/assets/keys/
  // and pass the right one in here
  // did in keyboard! :3
  image?: string
  isPressed?: boolean
  count?: number
}

export default function Key({ label, state, image, isPressed=false, count=0}: KeyProps) {
  const isUnlocked = state === 'unlocked'

  return (
    <div className="relative flex items-center justify-center w-12 h-12 select-none group">
      {image && (
        <img
          src={image}
          alt={label}

          className={`w-full h-full object-contain cursor-pointer transition-all duration-75 
            ${isPressed ? 'brightness-50 scale-95' : 'hover:brightness-75'}
          `}
        />
      )}

      <span className="absolute font-mono font-bold text-white text-lg drop-shadow-md pointer-events-none">
        {isUnlocked ? label.toUpperCase() : ''}
      </span>

      {count > 0 && (
        <span className="absolute -top-1 -right-1 bg-lime-500 text-white text-[10px] font-bold px-2 py-1 rounded-full shadow-sm border border-white">
          {count}
        </span>
      )}
    </div>
  )
}
