import { useState } from 'react'
import { useParams } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import TestResults from '../components/TestResults'
import { useAuth } from '../auth/AuthContext'
import type { SubmitResponse } from '../types'

export default function Problem() {
  // the question id from the url, /problems/:id
  const { id } = useParams()
  const { refresh } = useAuth()
  const [code, setCode] = useState('')
  const [result, setResult] = useState<SubmitResponse | null>(null)

  // TODO:
  //   1. on mount, getQuestion(id) into state and setCode(question.starter_code)
  //   2. show name, details, difficulty and the sample test cases
  //   3. submit button -> submitCode(id, code), setResult, and if it passed
  //      call refresh() so the navbar coins + keyboard update
  //   4. disable the button while a submission is running (they take seconds)
  void id
  void refresh
  void setResult // delete these once you use them

  return (
    <div className="page">
      <h1>problem</h1>
      <CodeEditor value={code} onChange={setCode} />
      <button>submit</button>
      {result && <TestResults result={result} />}
    </div>
  )
}
