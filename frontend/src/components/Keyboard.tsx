// the star of the show. draws the keyboard with however many keys the
// user has unlocked.

import Key from './Key'
import { KEY_LAYOUT } from '../lib/keyboard'

interface KeyboardProps {
  unlockedCount: number
}

export default function Keyboard({ unlockedCount }: KeyboardProps) {
  // TODO: for each row in KEY_LAYOUT, render a row of <Key>s using
  // keyState(key, unlockedCount) from lib/keyboard
  void unlockedCount
  return (
    <div className="keyboard">
      <p>keyboard goes here ({KEY_LAYOUT.flat().length} keys total)</p>
      <Key label="f" state="unlocked" />
    </div>
  )
}
