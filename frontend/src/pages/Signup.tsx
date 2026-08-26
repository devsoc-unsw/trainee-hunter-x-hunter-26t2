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
    <div className="page">
      <h1>sign up</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          type="password"
          placeholder="confirm password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />
        <button type="submit">sign up</button>
        {error && <p className="error">{error}</p>}
      </form>
      <p>
        already have an account? <Link to="/login">login</Link>
      </p>
    </div>
  )
}
