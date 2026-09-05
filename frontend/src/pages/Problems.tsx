import { Link } from 'react-router-dom';
import type { QuestionSummary } from '../types';
import { useEffect, useState } from 'react'
import { listQuestions } from '../api/questions';


const DIFFICULTY_COLOR = {
  easy: 'text-green-600',
  medium: 'text-yellow-600',
  hard: 'text-red-600',
} as const

const DIFFICULTY_LABEL = { easy: 'Easy', medium: 'Medium', hard: 'Hard' } as const

export default function Problems() {
  const [questions, setQuestions] = useState<QuestionSummary[]>([])
  const [search, setSearch] = useState('')

  useEffect(() => {
    listQuestions()
      .then(setQuestions)
      .catch((err) => console.error('Failed to load questions:', err))
  }, [])

  const filtered = questions.filter((q) =>
    q.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="page">
      <div className="">
        <div className="flex gap-1 mb-3 items-center">
          <div className="flex flex-1 items-center gap-3 h-12 px-3 bg-slate-50 border-2 border-slate-100
          rounded-xl text-slate-400
          focus-within:bg-white focus-within:border-slate-400 ">
            <input type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-full bg-transparent font-semibold text-slate-950 placeholder-slate-600/50
            focus: outline-none"/>
          </div>
          <button type="button"
          className="h-12 aspect-square bg-slate-50 border-2 border-slate-100 rounded-xl flex items-center justify-center text-slate-600
          hover:border-slate-400
          focus:bg-white focus:border-slate-400">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0
              0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
              </svg>
          </button>
          <button type="button"
          className="h-12 aspect-square bg-slate-50 border-2 border-slate-100 rounded-xl flex items-center justify-center text-slate-600
          hover:border-slate-400
          focus:bg-white focus:border-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 3c2.755
            0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25
            0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25
            2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659
            7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z" />
            </svg>
          </button>
        </div>
        <div className="flex flex-col">
          {filtered.map((q) => (
            <Link key={q.id} to={`/problems/${q.id}`}
            className={`flex items-center justify-between p-2 rounded-xl ${q.solved ? 'bg-lime-50' : 'bg-slate-50'}`}>
              <div className="flex items-center gap-3">
                <span className="w-6 h-6 text-lime-700 flex items-center justify-center font-bold text-lg">
                  {q.solved ? '✓' : ''}
                </span>
                <span className="font-bold text-gray-900">
                  {q.name}
                </span>
              </div>

              <span className={`font-black ${DIFFICULTY_COLOR[q.difficulty]}`}>
                {DIFFICULTY_LABEL[q.difficulty]}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
