import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Signup() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    // TODO: check password === confirm first, then signup(username, password)
    // and navigate('/'). remember the backend wants password >= 8 chars
    setError('signup not implemented yet')
    void signup
    void navigate
  }

  return (
    <div className="page m-6 flex flex-col items-center justify-center">
      <div className="flex flex-col mb-2">
        {/* TEMP!! FIX LATER */}
        {error && <p className="error">{error}</p>}
        {/* FIX!! LATER */}
        <h1 className="text-3xl font-black text-lime-600">Create account</h1>
        <h2 className="text-xl text-slate-500">We're excited to have you!</h2>
      </div>

      <form onSubmit={handleSubmit} className="auth-form w-full max-w-md bg-white p-6 md:p-8 rounded-xl border-2 border-slate-200 flex flex-col gap-3">
        <div className="mb-2 flex items-center gap-3 bg-slate-50
        border-2 border-slate-200 rounded-full p-3 text-slate-400
        focus-within:bg-white focus-within:border-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75
            6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5
            0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933
            17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
          </svg>
          <input
            className="bg-transparent font-semibold text-slate-900 placeholder-slate-400
            focus:outline-none"
            placeholder="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div className="mb-2 flex items-center gap-3 w-full bg-slate-50
        border-2 border-slate-200 rounded-full p-3 text-slate-400
        focus-within:bg-white focus-within:border-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5
            10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75
            11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25
            2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25
            2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
          </svg>
          <input
            className="w-full bg-transparent font-semibold text-slate-900 placeholder-slate-400
            focus:outline-none"
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-3 w-full bg-slate-50
        border-2 border-slate-200 rounded-full p-3 text-slate-400
        focus-within:bg-white focus-within:border-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5
            10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75
            11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25
            2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25
            2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
          </svg>
          <input
            className="w-full bg-transparent font-semibold text-slate-900 placeholder-slate-400
            focus:outline-none"
            type="password"
            placeholder="confirm password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
        </div>

        <button
          type="submit"
          className="w-full mt-2 text-white font-bold p-3 rounded-full bg-lime-600 hover:bg-lime-700"
        >
          Sign up
        </button>
      </form>
      <p className="text-slate-500 text-center">
        Already have an account? <Link to="/login" className="text-lime-600">Login!</Link>
      </p>
    </div>
  )
}
