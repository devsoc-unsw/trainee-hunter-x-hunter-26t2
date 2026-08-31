// a plain textarea for now. when someone takes on the editor task, swap this
// for codemirror (@uiw/react-codemirror + @codemirror/lang-python) - the
// props can stay the same so nothing else changes.

interface CodeEditorProps {
  value: string
  onChange: (code: string) => void
}

export default function CodeEditor({ value, onChange }: CodeEditorProps) {
  return (
    <textarea
      className="code-editor w-full h-full p-4 font-mono text-sm text-slate-900 focus:outline-none resize-y"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      spellCheck={false}
      rows={16}
    />
  )
}