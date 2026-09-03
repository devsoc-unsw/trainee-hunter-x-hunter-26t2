// a plain textarea for now. when someone takes on the editor task, swap this
// for codemirror (@uiw/react-codemirror + @codemirror/lang-python) - the
// props can stay the same so nothing else changes.

import React from 'react'
import { keyState } from '../lib/keyboard'
import { logKeyPress } from '../api/keylogger'

interface CodeEditorProps {
  value: string
  onChange: (code: string) => void
  unlockedCount: number
  onKeyLogged: (key:string) => void
}

export default function CodeEditor({ value, onChange, unlockedCount=0, onKeyLogged }: CodeEditorProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
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
    <textarea
      className="code-editor w-full h-full p-4 font-mono text-sm text-slate-900 focus:outline-none resize-y"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={handleKeyDown}
      spellCheck={false}
      rows={16}
    />
  )
}