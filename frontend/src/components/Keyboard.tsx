// the star of the show. draws the keyboard with however many keys the
// user has unlocked.

import Key from './Key'
// import { KEY_LAYOUT } from '../lib/keyboard'
import { KEY_LAYOUT, keyState } from '../lib/keyboard'

import grassKeyImg from '../assets/keys/grass_key.png'
import woodKeyImg from '../assets/keys/wood_key.png'

interface KeyboardProps {
  unlockedCount: number
}

// ! FIX!! when actually doing it, change unlockedcount to actually how many are unlocked :3
export default function Keyboard({ unlockedCount = 0 }: KeyboardProps) {
  // Select active image texture
  // TODO: for each row in KEY_LAYOUT, render a row of <Key>s using
  // keyState(key, unlockedCount) from lib/keyboard
  void unlockedCount
  return (

    <div className="flex flex-col items-center">
      {KEY_LAYOUT.map((row, rowIndex) => (
        <div key={rowIndex}
        className="flex -mb-3">
          {row.map((keyLabel) => {
            const state = keyState ? keyState(keyLabel, unlockedCount) : 'unlocked'
            const keyImage = state === 'unlocked' ? grassKeyImg : woodKeyImg

            return (
              <Key
                key={keyLabel}
                label={keyLabel}
                state={state}
                image={keyImage}
              />
            )
          })}
        </div>
      ))}
    </div>
  )
}