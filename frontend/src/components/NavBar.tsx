import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function NavBar() {
  const { me } = useAuth()

  // TODO: show coins + username when logged in, a logout button that calls
  // logout() and navigates home, and login/signup links when logged out
  return (
    <nav className="navbar sticky bg-slate-50 border-b border-slate-200/80 px-6 py-3">
      <div className="mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6 font-semibold text-slate-500">
          <Link to="/" className="hover:text-slate-900">Home</Link>
          <Link to="/problems" className="hover:text-slate-900">Problems</Link>
          <Link to="/shop" className="hover:text-slate-900">Shop</Link>
        </div>
        <div className="flex items-center gap-4 font-semibold text-slate-500">
          {me ? (
            <Link to="/profile" className="hover:text-slate-900">
              {`${me.username} - ${me.coins} coins`}
            </Link>
          ) : (
            <Link to="/login" className="hover:text-slate-900">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  )
}
