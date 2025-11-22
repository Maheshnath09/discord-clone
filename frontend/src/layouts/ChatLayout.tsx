import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import { useAuthStore } from '../store/authStore'

export default function ChatLayout() {
  const { user } = useAuthStore()

  return (
    <div className="flex h-screen bg-discord-darkest">
      <Sidebar user={user} />
      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}



