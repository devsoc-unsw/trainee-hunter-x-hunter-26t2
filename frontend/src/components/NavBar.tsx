import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function NavBar() {
  const { me } = useAuth()

  // TODO: show coins + username when logged in, a logout button that calls
  // logout() and navigates home, and login/signup links when logged out
  return (
    <nav className="navbar bg-blue-300">
      {/* work on making this look better. this blue is just to show that its the navbar for the moment. */}
      <Link to="/">Home </Link>
      <Link to="/problems">Problems </Link>
      <Link to="/shop">Shop </Link>
      <Link to="/profile">Profile </Link>
      <span className="navbar-right">
        {me ? `${me.username} - ${me.coins} coins` : <Link to="/login">Login</Link>}
      </span>
    </nav>
  )
}
