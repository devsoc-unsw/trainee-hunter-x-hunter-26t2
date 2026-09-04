// the star of the show. draws the keyboard with however many keys the
// user has unlocked.

import Key from './Key'
import { KEY_LAYOUT, keyState } from '../lib/keyboard'

import grassKeyImg from '../assets/keys/grass_key.png'
import woodKeyImg from '../assets/keys/wood_key.png'

interface KeyboardProps {
  unlockedCount?: number
  activeKey?: string | null
  pressCounts?: Record<string, number>
}

export default function Keyboard({ unlockedCount=0, activeKey=null, pressCounts={} }: KeyboardProps) {
  return (
    <div className="flex flex-col items-center">
      
      {KEY_LAYOUT.map((row, rowIndex) => (
        <div key={rowIndex}
        className="flex -mb-3">
          {row.map((keyLabel) => {
            const state = keyState(keyLabel, unlockedCount)
            const keyImage = state === 'unlocked' ? grassKeyImg : woodKeyImg

            const isPressed = activeKey === keyLabel.toLowerCase()
            const count = pressCounts[keyLabel.toLowerCase()] || 0

            return (
                <Key
                  key={keyLabel}
                  label={keyLabel}
                  state={state}
                  image={keyImage}
                  isPressed={isPressed}
                  count={count}
                />
              )
          })}
        </div>
      ))}
    </div>
  )
}