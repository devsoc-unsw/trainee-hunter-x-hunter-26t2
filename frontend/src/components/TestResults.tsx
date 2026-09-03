import type { SubmitResponse } from '../types'

interface TestResultsProps {
  result: SubmitResponse
}

export default function TestResults({ result }: TestResultsProps) {
  return (
    <div className="bg-white border-2 border-slate-200 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <p className={`font-black ${result.passed ? 'text-lime-600' : 'text-red-600'}`}>
          {result.passed ? 'All tests passed!' : 'Some tests failed'}
        </p>
        {result.first_solve && result.coins_earned > 0 && (
          <span className="text-xs font-bold text-yellow-700 bg-amber-50 border border-amber-200 rounded-full px-3 py-1">
            🪙 +{result.coins_earned} coins
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2">
        {result.results.map((t, i) => (
          <div key={i}
          className={`p-3 rounded-xl border text-xs font-mono ${t.passed ? 'bg-lime-50 border-lime-200 text-slate-700' : 'bg-red-50 border-red-200 text-slate-700'}`}>
            <p className="font-bold mb-1">
              {t.passed ? '✓' : '✗'} Test {i + 1}
            </p>
            <p>Input: {t.input.map((a) => JSON.stringify(a)).join(', ')}</p>
            <p>Expected: {JSON.stringify(t.expected)}</p>
            <p>Got: {JSON.stringify(t.got)}</p>
            {t.error && <p className="text-red-600 mt-1">{t.error}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}
