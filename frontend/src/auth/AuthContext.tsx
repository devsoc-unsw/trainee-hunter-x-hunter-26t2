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

// =============================================================================
// !!! HARDCODED DUMMY DATA !!! fake auth so the frontend works without the
// backend. any username/password logs in. swap every function body marked
// "DUMMY" below for the real api/auth + api/user calls when the backend exists.
// =============================================================================
const FAKE_USERNAME_KEY = 'fake_username'

function fakeMe(username: string): Me {
  return { id: 'u-1', username, coins: 135, solved_count: 3, unlocked_keys: 7 }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null)
  const [loading, setLoading] = useState(true)

  // on page load, if there's a token in localStorage, try to fetch /users/me
  // with it. if that fails the token is stale, throw it away
  useEffect(() => {
    async function restore() {
      //! DUMMY: real version should getMe() and setToken(null) on failure
      if (getToken()) {
        setMe(fakeMe(localStorage.getItem(FAKE_USERNAME_KEY) ?? 'usernameee :3'))
      }
      setLoading(false)
    }
    restore()
  }, [])

  //! DUMMY: always succeeds. real version calls api/auth login then getMe()
  async function login(username: string, _password: string) {
    setToken('fake-token')
    localStorage.setItem(FAKE_USERNAME_KEY, username)
    setMe(fakeMe(username))
  }

  //! DUMMY: same as login. real version hits signup
  async function signup(username: string, password: string) {
    await login(username, password)
  }

  async function logout() {
    //! DUMMY: real version tells the backend first
    setToken(null)
    localStorage.removeItem(FAKE_USERNAME_KEY)
    setMe(null)
  }

  async function refresh() {
    //! DUMMY: real version re-fetches /users/me
    if (getToken()) {
      setMe(fakeMe(localStorage.getItem(FAKE_USERNAME_KEY) ?? 'usernameee :3'))
    }
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
