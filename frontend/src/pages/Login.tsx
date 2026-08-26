import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    // TODO: call login(username, password), navigate('/') on success,
    // setError with the message on failure
    setError('login not implemented yet')
    void login
    void navigate
  }

  return (
    <div className="page">
      <h1>login</h1>
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
        <button type="submit">login</button>
        {error && <p className="error">{error}</p>}
      </form>
      <p>
        no account? <Link to="/signup">sign up</Link>
      </p>
    </div>
  )
}
