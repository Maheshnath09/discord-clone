import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import { useAuthStore } from '../store/authStore'
import { useState } from 'react'

export default function ChatLayout() {
  const { user } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-discord-darkest">
      {/* Mobile backdrop */}
      <div
        className={`fixed inset-0 bg-black/50 z-30 md:hidden ${sidebarOpen ? 'block' : 'hidden'}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar: slides in on small screens, static on md+ */}
      <div
        className={`fixed inset-y-0 left-0 z-40 w-64 transform transition-transform md:static md:translate-x-0 md:w-60 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar user={user} />
      </div>

      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar for mobile to toggle sidebar */}
        <div className="md:hidden flex items-center justify-between p-2 border-b border-discord-darker bg-discord-darker">
          <button
            onClick={() => setSidebarOpen(true)}
            className="px-3 py-1 rounded bg-discord-primary text-white"
            aria-label="Open sidebar"
          >
            ☰
          </button>
          <div className="text-sm font-medium text-white">Discord-like Chat App</div>
          <div style={{ width: 40 }} />
        </div>

        <Outlet />
      </main>
    </div>
  )
}



