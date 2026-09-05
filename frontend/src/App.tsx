// routing. this is done for you - add a <Route> here when you add a page.

//? commented out authorisation for the moment - will do later. for the moment, this is just for frontend :3
//* everything thats commented out with //? is meant to be uncommented.
//! everything thats commented at the end with //! is meant to be commented after

import { Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import NavBar from './components/NavBar'
import { useAuth } from './auth/AuthContext'
import Home from './pages/Home'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Problems from './pages/Problems'
import Problem from './pages/Problem'
import Shop from './pages/Shop'
import Profile from './pages/Profile'
import Landing from './pages/Landing'

// wraps pages that need a login. kicks you to /login if you're not
function RequireAuth({ children }: { children: ReactNode }) {
  const { me, loading } = useAuth()
  if (loading) return <p>loading...</p>
  if (!me) return <Navigate to="/login" replace />
  return children
}

function IndexRoute() {
  const { me, loading } = useAuth()
  if (loading) return <p>loading...</p>
  return me ? <Home /> : <Landing />
}

export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<IndexRoute />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/problems" element={<RequireAuth><Problems /></RequireAuth>} />
        <Route path="/problems/:id" element={<RequireAuth><Problem /></RequireAuth>} />
        <Route path="/shop" element={<RequireAuth><Shop /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
      </Routes>
    </>
  )
}
