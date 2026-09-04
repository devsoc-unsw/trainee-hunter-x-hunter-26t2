// keeps track of who's logged in. the provider shell is done for you,
// the three functions inside are the stubs.

import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { setToken } from '../api/client'
import * as authApi from '../api/auth'
import type { Me } from '../types'

interface AuthState {
  // null = not logged in (or still loading)
  me: Me | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  signup: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  // call after anything that changes coins/solves so the navbar updates
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null)
  const [loading, setLoading] = useState(true)

  // on page load, if there's a token in localStorage, try to fetch /users/me
  // with it. if that fails the token is stale, throw it away
  useEffect(() => {
    async function restore() {
      // GET /users/me isn't implemented yet (blocked on routers/users.py +
      // keyboard.py). Once it lands, this should call getMe(), setMe(...),
      // and setToken(null) on failure, per the original TODO.
      setLoading(false)
    }
    restore()
  }, [])

  async function login(username: string, password: string) {
    const { token } = await authApi.login(username, password)
    setToken(token)
  }

  async function signup(username: string, password: string) {
    const { token } = await authApi.signup(username, password)
    setToken(token)
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // ignore - we're clearing local state regardless
    } finally {
      setToken(null)
      setMe(null)
    }
  }

  async function refresh() {
    // re-fetch /users/me and setMe - blocked on GET /users/me, out of scope here
    throw new Error('not implemented')
  }

  return (
    <AuthContext.Provider value={{ me, loading, login, signup, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}

// use this in components: const { me, logout } = useAuth()
// eslint-disable-next-line react-refresh/only-export-components -- hooks are fine to export here
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside <AuthProvider>')
  return ctx
}
