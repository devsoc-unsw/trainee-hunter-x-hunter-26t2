import { useAuth } from '../auth/AuthContext'

export default function Profile() {
  const { me } = useAuth()

  // TODO: show stats (coins, solved count, keys unlocked), the inventory
  // (listInventory), and an edit-username form that calls updateUsername
  // then refresh()
  return (
    <div className="page">
      <h1>profile</h1>
      {me && <p>{me.username}</p>}
    </div>
  )
}
