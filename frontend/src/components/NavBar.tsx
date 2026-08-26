import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function NavBar() {
  const { me } = useAuth()

  // TODO: show coins + username when logged in, a logout button that calls
  // logout() and navigates home, and login/signup links when logged out
  return (
    <nav className="navbar">
      <Link to="/">home</Link>
      <Link to="/problems">problems</Link>
      <Link to="/shop">shop</Link>
      <Link to="/profile">profile</Link>
      <span className="navbar-right">
        {me ? `${me.username} - ${me.coins} coins` : <Link to="/login">login</Link>}
      </span>
    </nav>
  )
}
