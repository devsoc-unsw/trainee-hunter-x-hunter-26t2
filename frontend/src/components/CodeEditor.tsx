// codemirror 6, python. the props are the same ones the old textarea took,
// so Problem.tsx didn't have to change.

import React from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { indentUnit } from '@codemirror/language'
import { indentWithTab } from '@codemirror/commands'
import { EditorView, keymap } from '@codemirror/view'
import { keyState } from '../lib/keyboard'
import { logKeyPress } from '../api/keylogger'

interface CodeEditorProps {
  value: string
  onChange: (code: string) => void
  unlockedCount: number
  onKeyLogged: (key: string) => void
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

export default function CodeEditor({ value, onChange, unlockedCount = 0, onKeyLogged }: CodeEditorProps) {
  // unchanged from the textarea version. codemirror has no onKeyDown prop, so
  // the wrapper div below catches the event on the way out instead - which is
  // why the keylogger keeps paying coins for typing in here.
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const key = e.key.toLowerCase()

    if (e.key.length > 1) {
      return
    }

    const state = keyState(key, unlockedCount)

    if (state === 'unlocked') {
      logKeyPress(key).catch(() => {
        // do nothing
      })

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
