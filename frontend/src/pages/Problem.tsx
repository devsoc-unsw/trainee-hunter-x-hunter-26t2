import { useEffect, useState } from 'react'
import { Navigate, useParams } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import TestResults from '../components/TestResults'
import { useAuth } from '../auth/AuthContext'
import Keyboard from '../components/Keyboard';
import { getQuestion, runCode, submitCode } from '../api/questions'
import { ApiError } from '../api/client'
import type { QuestionDetail, TestResult } from '../types'

// what came back from the last Run or Submit. kind tells TestResults whether
// '3/3 passed' means the samples or the real thing
interface Outcome {
  kind: 'run' | 'submit'
  passed: boolean
  results: TestResult[]
  coins_earned?: number
  first_solve?: boolean
}

const DIFFICULTY_COLOR = {
  easy: 'text-green-600',
  medium: 'text-yellow-600',
  hard: 'text-red-600',
} as const

export default function Problem() {
  // the question id from the url, /problems/:id.
  //
  // keying the page on it means clicking through to another problem remounts
  // this component with fresh state, rather than needing an effect that
  // reaches back and clears half a dozen useStates by hand.
  const { id } = useParams()
  if (!id) return <Navigate to="/problems" replace />
  return <ProblemPage key={id} id={id} />
}

function ProblemPage({ id }: { id: string }) {
  const { refresh, me } = useAuth()
  const [question, setQuestion] = useState<QuestionDetail | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [code, setCode] = useState('')
  const [outcome, setOutcome] = useState<Outcome | null>(null)
  const [judgeError, setJudgeError] = useState<string | null>(null)
  // which button is in flight, so only that one shows a spinner
  const [busy, setBusy] = useState<'run' | 'submit' | null>(null)

  const [activeKey, setActiveKey] = useState<string | null>(null)
  const [pressCounts, setPressCounts] = useState<Record<string, number>>({})

  const unlockedCount = me?.unlocked_keys ?? 0

  const handleKeyLogged = (key: string) => {
    setActiveKey(key)
    setPressCounts((prev) => ({
      ...prev,
      [key]: (prev[key] || 0) + 1,
    }))
  }

  useEffect(() => {
    let stale = false

    getQuestion(id)
      .then((q) => {
        // in dev, strict mode runs this effect twice - don't let the first
        // response land after the second and stomp the editor
        if (stale) return
        setQuestion(q)
        setCode(q.starter_code)
      })
      .catch((err) => {
        if (stale) return
        setLoadError(err instanceof ApiError ? err.message : 'Could not load this question')
      })

    return () => {
      stale = true
    }
  }, [id])

  async function judge(kind: 'run' | 'submit') {
    if (busy) return
    setBusy(kind)
    setOutcome(null)
    setJudgeError(null)

    try {
      if (kind === 'run') {
        const result = await runCode(id, code)
        setOutcome({ kind, ...result })
      } else {
        const result = await submitCode(id, code)
        setOutcome({ kind, ...result })
        if (result.passed) {
          // coins and unlocked_keys both live on /users/me, so one refresh
          // updates the navbar's coin count AND grows the keyboard on the
          // left of this very page
          await refresh()
          setQuestion((q) => (q ? { ...q, solved: true } : q))
        }
      }
    } catch (err) {
      setJudgeError(err instanceof ApiError ? err.message : 'Something went wrong')
    } finally {
      setBusy(null)
    }
  }

  if (loadError) {
    return (
      <div className="m-4 p-4 page text-slate-900">
        <p className="font-bold text-red-600">{loadError}</p>
      </div>
    )
  }

  if (!question) {
    return (
      <div className="m-4 p-4 page text-slate-500">
        <p>loading...</p>
      </div>
    )
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
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-black text-slate-900">
              {question.name}
            </h1>
            <span className={`font-black text-sm ${DIFFICULTY_COLOR[question.difficulty]}`}>
              {question.difficulty}
            </span>
            {question.solved && (
              <span className="text-xs font-bold text-lime-700 bg-lime-50 border border-lime-200 rounded-full px-3 py-1">
                ✓ solved
              </span>
            )}
          </div>
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
              {/* python only - the judge runs cpython in a subprocess and
                  nothing else, so don't offer languages we can't grade */}
              <span className="text-xs font-semibold text-slate-700 py-1 px-2">
                Python
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
              type="button"
              onClick={() => judge('run')}
              disabled={busy !== null}
              title="Check your code against the sample tests. Doesn't count as a submission."
              className="flex items-center gap-2 p-2 text-xs font-bold text-slate-600 bg-slate-200/70
              hover:bg-slate-200 active:bg-slate-300 rounded-xl disabled:opacity-50">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 text-slate-700">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                </svg>
                {busy === 'run' ? 'Running...' : 'Run'}
              </button>
              <button
              type="button"
              onClick={() => judge('submit')}
              disabled={busy !== null}
              title="Grade against every test case. A first solve pays coins."
              className="flex items-center gap-2 p-2 text-xs font-bold text-lime-600 bg-slate-200/70
              hover:bg-slate-200 active:bg-slate-300 rounded-xl disabled:opacity-50">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                </svg>
                {busy === 'submit' ? 'Judging...' : 'Submit'}
              </button>
            </div>

          </div>

        </div>

        <CodeEditor value={code} onChange={setCode} unlockedCount={unlockedCount} onKeyLogged={handleKeyLogged}/>

        <div>
          {busy && (
            <p className="text-xs font-bold text-slate-500">
              running your code in a sandbox...
            </p>
          )}
          {judgeError && (
            <p className="text-xs font-bold text-red-600">{judgeError}</p>
          )}
          {outcome && !busy && (
            <TestResults
              kind={outcome.kind}
              passed={outcome.passed}
              results={outcome.results}
              coinsEarned={outcome.coins_earned}
              firstSolve={outcome.first_solve}
            />
          )}
        </div>
      </div>
    </div>
  )
}
