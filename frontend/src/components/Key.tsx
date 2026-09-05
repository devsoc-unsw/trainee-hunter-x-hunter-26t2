import type { KeyState } from '../lib/keyboard'

interface KeyProps {
  label: string
  state: KeyState
  // when the handdrawn key images are ready, drop them in src/assets/keys/
  // and pass the right one in here
  // did in keyboard! :3
  image?: string
  accessoryImage?: string
  isPressed?: boolean
  count?: number
  onClick?: () => void
}

export default function Key({ label, state, image, accessoryImage, isPressed=false, count=0, onClick}: KeyProps) {
  const isUnlocked = state === 'unlocked'

  return (
    <div
      onClick={isUnlocked ? onClick : undefined}
      className={`relative flex items-center justify-center w-12 h-12 select-none group ${isUnlocked && onClick ? 'cursor-pointer' : ''}`}>
      {image && (
        <img
          src={image}
          alt={label}

          className={`w-full h-full object-contain transition-all duration-75 
            ${isPressed ? 'brightness-50 scale-95' : 'hover:brightness-75'}
          `}
        />
      )}

      {accessoryImage && (
        <img
          src={accessoryImage}
          alt=""
          className="absolute w-6 h-6 object-contain pointer-events-none"
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
