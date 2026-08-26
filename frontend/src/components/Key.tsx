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
  return (
    <div className={`key key-${state}`} title={image ? label : undefined}>
      {state === 'unlocked' ? label : ''}
    </div>
  )
}
