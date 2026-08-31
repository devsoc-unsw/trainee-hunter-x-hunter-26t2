import type { KeyState } from '../lib/keyboard'

interface KeyProps {
  label: string
  state: KeyState
  // when the handdrawn key images are ready, drop them in src/assets/keys/
  // and pass the right one in here
  image?: string
}

export default function Key({ label, state, image }: KeyProps) {
  // TODO: locked keys should look greyed out / missing, 'next' should hint
  // at what's coming. swap the div for an <img> once image is passed

  const isUnlocked = state === 'unlocked'

  return (
    <div className="relative flex items-center justify-center w-12 h-12 select-none group">
      {image && (
        <img
          src={image}
          alt={label}
          className="scale-105 w-full h-full object-contain cursor-pointer transition-all duration-100
          hover:brightness-75 hover:scale-105 active:brightness-50"
        />
      )}

      <span className="absolute font-mono font-bold text-white text-lg drop-shadow-md pointer-events-none">
        {isUnlocked ? label.toUpperCase() : ''}
      </span>
    </div>
  )
}
