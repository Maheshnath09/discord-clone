import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

interface User {
  id: number
  username: string
  display_name: string | null
  avatar_url: string | null
}

interface SidebarProps {
  user: User | null
}

export default function Sidebar({ user }: SidebarProps) {
  const navigate = useNavigate()
  const { logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="w-60 bg-discord-darker flex flex-col">
      {/* User section */}
      <div className="p-4 border-b border-discord-dark">
        <Link
          to="/profile"
          className="flex items-center space-x-3 p-2 rounded hover:bg-discord-dark transition-colors"
        >
          <div className="w-10 h-10 rounded-full bg-discord-primary flex items-center justify-center text-white font-semibold">
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user.username} className="w-full h-full rounded-full" />
            ) : (
              <span>{user?.username?.charAt(0).toUpperCase() || 'U'}</span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white font-medium truncate">
              {user?.display_name || user?.username || 'User'}
            </p>
            <p className="text-discord-textMuted text-sm truncate">@{user?.username}</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto scrollbar-thin p-2">
        <Link
          to="/"
          className="block px-4 py-2 text-discord-text hover:bg-discord-dark rounded mb-1 transition-colors"
        >
          🏠 Home
        </Link>
        <Link
          to="/profile"
          className="block px-4 py-2 text-discord-text hover:bg-discord-dark rounded mb-1 transition-colors"
        >
          👤 Profile
        </Link>
      </nav>

      {/* Logout button */}
      <div className="p-4 border-t border-discord-dark">
        <button
          onClick={handleLogout}
          className="w-full px-4 py-2 bg-discord-danger hover:bg-red-600 text-white rounded transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  )
}



