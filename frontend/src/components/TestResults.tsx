import type { TestResult } from '../types'

interface TestResultsProps {
  passed: boolean
  results: TestResult[]
  // 'run' judged the samples only, 'submit' judged everything and can pay out
  kind: 'run' | 'submit'
  coinsEarned?: number
  firstSolve?: boolean
}

// python-flavoured: a returned None comes over the wire as null, and 'None'
// is what the user typed, so it's what they should read back
function formatValue(value: unknown) {
  if (value === null || value === undefined) return 'None'
  return JSON.stringify(value)
}

export default function TestResults({
  passed,
  results,
  kind,
  coinsEarned = 0,
  firstSolve = false,
}: TestResultsProps) {
  const passedCount = results.filter((t) => t.passed).length
  const total = results.length
  const label = kind === 'run' ? 'sample tests' : 'tests'

  return (
    <div className="bg-white border-2 border-slate-200 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className={`font-black ${passed ? 'text-lime-600' : 'text-red-600'}`}>
            {passed
              ? kind === 'run'
                ? 'Samples passed - ready to submit'
                : 'All tests passed!'
              : 'Some tests failed'}
          </p>
          <p className="text-xs font-bold text-slate-500 mt-0.5">
            {passedCount} / {total} {label} passed
          </p>
        </div>
        {firstSolve && coinsEarned > 0 && (
          <span className="text-xs font-bold text-yellow-700 bg-amber-50 border border-amber-200 rounded-full px-3 py-1 whitespace-nowrap">
            🪙 +{coinsEarned} coins
          </span>
        )}
      </div>

      {/* a bar, so 7/9 reads at a glance without counting rows */}
      <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${passed ? 'bg-lime-500' : 'bg-red-400'}`}
          style={{ width: total === 0 ? '0%' : `${(passedCount / total) * 100}%` }}
        />
      </div>

      <div className="flex flex-col gap-2">
        {results.map((t, i) => (
          <div
            key={i}
            className={`p-3 rounded-xl border text-xs font-mono ${
              t.passed
                ? 'bg-lime-50 border-lime-200 text-slate-700'
                : 'bg-red-50 border-red-200 text-slate-700'
            }`}
          >
            <p className="font-bold mb-1">
              {t.passed ? '✓' : '✗'} Test {i + 1}
              {t.hidden && (
                <span className="ml-2 font-normal text-slate-500">hidden test</span>
              )}
            </p>

            {/* a hidden case carries the pass/fail bit and nothing else - the
                backend blanks the rest so one wrong submission can't be used
                to read the whole answer key */}
            {t.hidden ? (
              <p className="text-slate-500">
                {t.passed
                  ? 'passed'
                  : 'failed. the first failing hidden test is shown in full above.'}
              </p>
            ) : (
              <>
                <p>Input: {t.input.map((a) => formatValue(a)).join(', ')}</p>
                <p>Expected: {formatValue(t.expected)}</p>
                <p>Got: {formatValue(t.got)}</p>
              </>
            )}

            {t.error && (
              <pre className="text-red-600 mt-1 whitespace-pre-wrap break-words">
                {t.error}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
