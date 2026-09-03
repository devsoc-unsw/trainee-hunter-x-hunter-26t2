import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import TestResults from '../components/TestResults'
import { useAuth } from '../auth/AuthContext'
import Keyboard from '../components/Keyboard';
import type { QuestionDetail, SubmitResponse } from '../types'

// =============================================================================
// !!! HARDCODED DUMMY DATA !!! replace with getQuestion(id) from ../api/questions
// once the backend is wired up. the fake handleSubmit below always passes -
// replace it with submitCode(id, code)
// =============================================================================
const DUMMY_DETAILS: Record<string, QuestionDetail> = {
  '1': {
    id: '1', slug: 'two-sum', name: 'Two Sum', difficulty: 'easy', solved: true,
    details: 'Given a list of numbers and a target, return the indices of the two numbers that add up to the target. Each input has exactly one solution, and you may not use the same element twice.',
    function_name: 'two_sum',
    starter_code: 'def two_sum(nums, target):\n    pass\n',
    samples: [
      { input: [[2, 7, 11, 15], 9], expected: [0, 1] },
      { input: [[3, 2, 4], 6], expected: [1, 2] },
    ],
  },
  '2': {
    id: '2', slug: 'reverse-string', name: 'Reverse String', difficulty: 'easy', solved: true,
    details: 'Given a string, return it reversed.',
    function_name: 'reverse_string',
    starter_code: 'def reverse_string(s):\n    pass\n',
    samples: [
      { input: ['hello'], expected: 'olleh' },
      { input: ['ab'], expected: 'ba' },
    ],
  },
}

// generic filler for questions without hand-written details yet
function fallbackDetail(id: string): QuestionDetail {
  return {
    id, slug: `question-${id}`, name: `Question ${id}`, difficulty: 'medium', solved: false,
    details: 'Details for this question have not been written yet. Solve it anyway :3',
    function_name: 'solve',
    starter_code: 'def solve():\n    pass\n',
    samples: [{ input: [1], expected: 1 }],
  }
}

export default function Problem() {
  // the question id from the url, /problems/:id
  const { id } = useParams()
  const { refresh } = useAuth()
  const [code, setCode] = useState('')
  const [result, setResult] = useState<SubmitResponse | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const [activeKey, setActiveKey] = useState<string | null>(null)
  const [pressCounts, setPressCounts] = useState<Record<string, number>>({})

  const unlockedCount = 17

  const handleKeyLogged = (key: string) => {
    setActiveKey(key)
    setPressCounts((prev) => ({
      ...prev,
      [key]: (prev[key] || 0) + 1,
    }))
  }

  const question = DUMMY_DETAILS[id ?? ''] ?? fallbackDetail(id ?? '?')

  useEffect(() => {
    setCode(question.starter_code)
    setResult(null)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  //! HARDCODED DUMMY: fakes a passing submission after 500ms.
  //! real version calls submitCode(id, code) and can fail
  function handleSubmit() {
    setSubmitting(true)
    setResult(null)
    setTimeout(() => {
      setResult({
        passed: true,
        coins_earned: 10,
        first_solve: !question.solved,
        results: question.samples.map((s) => ({
          passed: true, input: s.input, expected: s.expected, got: s.expected, error: null,
        })),
      })
      setSubmitting(false)
      refresh()
    }, 500)
  }

  return (
    <div className="m-4 p-4 page grid grid-cols-2 gap-2 text-slate-900">
      {/* lhs */}
      <div className="flex flex-col gap-4 bg-white p-5 rounded-xl border-2 border-slate-200">
        {/* im gonna put the keyboard here */}
        <div className="w-full p-4">
            <Keyboard 
            unlockedCount={unlockedCount} 
            activeKey={activeKey} 
            pressCounts={pressCounts} 
          />
        </div>
        <div>
          <h1 className="text-2xl font-black text-slate-900 mb-2">
            {question.name}
          </h1>
          <p className="text-slate-600 text-sm">
            {question.details}
          </p>
          <div className="mt-4 flex flex-col gap-2">
            {question.samples.map((s, i) => (
              <div key={i} className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs font-mono text-slate-700">
                <p><span className="font-bold">Input:</span> {question.function_name}({s.input.map((a) => JSON.stringify(a)).join(', ')})</p>
                <p><span className="font-bold">Expected:</span> {JSON.stringify(s.expected)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* rhs */}
      <div className="flex flex-col gap-4">
        <div className="bg-white rounded-xl border-2 border-slate-200 flex flex-col">
          {/* header */}
          <div className="flex items-center justify-between p-2  border-slate-200">
            <div className="flex items-center gap-2">
              <select 
                className="bg-transparent text-xs font-semibold text-slate-700
                focus:outline-none cursor-pointer py-1 px-2 rounded-xl hover:bg-slate-100">
                <option value="op1">option1</option>
                <option value="op2">option2</option>
                <option value="op3">option3</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <button
              type="button"
              className="flex items-center gap-2 p-2 text-xs font-bold text-slate-600 bg-slate-200/70
              hover:bg-slate-200 active:bg-slate-300 rounded-xl">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 text-slate-700">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                </svg>
                Run
              </button>
              <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center gap-2 p-2 text-xs font-bold text-lime-600 bg-slate-200/70
              hover:bg-slate-200 active:bg-slate-300 rounded-xl disabled:opacity-50">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                </svg>
                Submit
              </button>
            </div>

          </div>

        </div>
        {/* this and run in the same 'header' above the code */}
        {/* needa style code editor.  */}
        
        <div className="border-2 border-slate-200 rounded-xl">
          <CodeEditor value={code} onChange={setCode} unlockedCount={unlockedCount} onKeyLogged={handleKeyLogged}/>
          {/* idk how to make this longer */}
        </div>

        <div>
          {/* dont kniow what i need the div for but resiults go here */}
          {result && <TestResults result={result} />}
        </div>
      </div>
    </div>
  )
}
