import Keyboard from '../components/Keyboard'
import { useAuth } from '../auth/AuthContext'

export default function delHome() {
  const { me } = useAuth()

  // TODO: this is the main screen - the keyboard front and centre, with
  // solved count / progress towards the next key
  return (
    <div className="page">
      <h1>trainee hunter</h1>
      {me ? (
        <Keyboard unlockedCount={me.unlocked_keys} />
      ) : (
        <p>log in to see your keyboard grow</p>
      )}
    </div>
  )
}
