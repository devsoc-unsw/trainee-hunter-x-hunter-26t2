// codemirror 6, python. the props are the same ones the old textarea took,
// so Problem.tsx didn't have to change.

import React from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { indentUnit } from '@codemirror/language'
import { indentWithTab } from '@codemirror/commands'
import { EditorView, keymap } from '@codemirror/view'
import { logKeyPress } from '../api/keylogger'

interface CodeEditorProps {
  value: string
  onChange: (code: string) => void
  // which keys are unlocked - typing anything else earns nothing
  unlockedKeys: string[]
  onKeyLogged: (key: string) => void
  // how many coins the SERVER says that press just paid out. 0 most of the
  // time, 1 on every tenth press of an unlocked key.
  onCoinsEarned?: (coins: number) => void
}

// python is 4 spaces, and Tab should indent rather than tab out of the editor
// (the default browser behaviour, and the single most annoying thing a code
// box can do). keymap.of goes before the language so it wins.
const EXTENSIONS = [
  keymap.of([indentWithTab]),
  python(),
  indentUnit.of('    '),
  EditorView.lineWrapping,
]

// matches the slate palette the rest of the app uses
const THEME = EditorView.theme({
  '&': { fontSize: '13px', backgroundColor: 'transparent' },
  '.cm-content': { fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace' },
  '.cm-gutters': {
    backgroundColor: 'transparent',
    border: 'none',
    color: '#94a3b8',
  },
  '.cm-activeLine': { backgroundColor: '#f8fafc' },
  '.cm-activeLineGutter': { backgroundColor: 'transparent', color: '#475569' },
  '&.cm-focused': { outline: 'none' },
})

export default function CodeEditor({ value, onChange, unlockedKeys = [], onKeyLogged, onCoinsEarned }: CodeEditorProps) {
  // unchanged from the textarea version. codemirror has no onKeyDown prop, so
  // the wrapper div below catches the event on the way out instead - which is
  // why the keylogger keeps paying coins for typing in here.
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const key = e.key.toLowerCase()

    if (e.key.length > 1) {
      return
    }

    if (unlockedKeys.includes(key)) {
      // the response carries coins_earned - 1 on every tenth press. this used
      // to be discarded, which is why the navbar's coin count sat still until
      // something else happened to refetch /users/me. no extra request is
      // needed to notice a payout: we already made one, and it answered.
      logKeyPress(key)
        .then((result) => onCoinsEarned?.(result.coins_earned))
        .catch(() => {
          // a dropped press just doesn't pay - the server is the record
        })

      // fired straight away rather than off the response, so the press-count
      // badge keeps up with fast typing
      if (onKeyLogged) {
        onKeyLogged(key)
      }
    }
  }

  return (
    <div className="code-editor overflow-hidden rounded-xl" onKeyDown={handleKeyDown}>
      <CodeMirror
        value={value}
        onChange={onChange}
        height="420px"
        extensions={[...EXTENSIONS, THEME]}
        basicSetup={{
          lineNumbers: true,
          foldGutter: false,
          // off on purpose: this is a typing game, and a popup completing
          // your identifiers means fewer keypresses and fewer coins
          autocompletion: false,
          highlightActiveLine: true,
        }}
      />
    </div>
  )
}
