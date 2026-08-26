import type { SubmitResponse } from '../types'

interface TestResultsProps {
  result: SubmitResponse
}

export default function TestResults({ result }: TestResultsProps) {
  // TODO: one row per test - green tick or red cross, the input, expected vs
  // got, and the error message if there is one. show coins_earned when
  // first_solve is true
  return (
    <div className="test-results">
      <p>{result.passed ? 'all tests passed!' : 'some tests failed'}</p>
      <p>{result.results.length} tests ran</p>
    </div>
  )
}
