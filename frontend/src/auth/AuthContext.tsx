// keeps track of who's logged in. the provider shell is done for you,
// the three functions inside are the stubs.

import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { getToken, setToken } from '../api/client'
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
      // TODO: if getToken() is null, just setLoading(false).
      // otherwise getMe(), setMe(...), and on error setToken(null)
      // delete these three lines once you use them
      void setMe
      void getToken
      void setToken
      setLoading(false)
    }
    restore()
  }, [])

  async function login(_username: string, _password: string) {
    // call api/auth login, setToken with the result, then fetch me
    throw new Error('not implemented')
  }

  async function signup(_username: string, _password: string) {
    // same shape as login but hits signup
    throw new Error('not implemented')
  }

  async function logout() {
    // tell the backend, then setToken(null) and setMe(null).
    // clear local state even if the backend call fails
    throw new Error('not implemented')
  }

  async function refresh() {
    // re-fetch /users/me and setMe
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
