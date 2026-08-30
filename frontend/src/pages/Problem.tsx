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
    <div className="m-4 p-4 page grid grid-cols-2 gap-2 text-slate-900">
      {/* lhs */}
      <div className="flex flex-col gap-4 bg-white p-5 rounded-xl border-2 border-slate-200">
        {/* im gonna put the keyboard here */}
        <div className="w-full bg-red-100">
          keyboard :3
        </div>
        <div>
          <h1 className="text-2xl font-black text-slate-900 mb-2">
            Question 1
          </h1>
          <p className="text-slate-600 text-sm">
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Corporis labore, tempora, recusandae velit delectus eligendi sint quis consectetur molestias minima numquam ducimus ea odit voluptas voluptatibus ab earum suscipit in.
          </p>
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
              className="flex items-center gap-2 p-2 text-xs font-bold text-lime-600 bg-slate-200/70
              hover:bg-slate-200 active:bg-slate-300 rounded-xl">
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
          <CodeEditor value={code} onChange={setCode}/>
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
