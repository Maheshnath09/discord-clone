import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'

interface Room {
  id: number
  name: string
  description: string | null
  is_public: boolean
  member_count: number | null
  created_at: string
  is_member?: boolean
  membership_role?: string | null
  can_join?: boolean
}

export default function RoomsPage() {
  const { user } = useAuthStore()
  const [rooms, setRooms] = useState<Room[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [joiningRoomId, setJoiningRoomId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [createError, setCreateError] = useState<string | null>(null)
  const [createSuccess, setCreateSuccess] = useState<string | null>(null)
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
    is_public: true,
  })
  const [creating, setCreating] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const loadRooms = useCallback(async () => {
    try {
      setLoading(true)
      const response = await api.get('/rooms', {
        params: { search, limit: 50 },
      })
      setRooms(response.data)
      setError(null)
    } catch (err: any) {
      console.error('Failed to load rooms:', err)
      setError(err.response?.data?.detail || 'Failed to load rooms')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => {
    loadRooms()
  }, [loadRooms])

  const handleJoinRoom = async (roomId: number) => {
    setJoiningRoomId(roomId)
    try {
      await api.post(`/rooms/${roomId}/join`)
      await loadRooms()
    } catch (err: any) {
      console.error('Failed to join room', err)
      setError(err.response?.data?.detail || 'Unable to join room')
    } finally {
      setJoiningRoomId(null)
    }
  }

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setCreateError(null)
    setCreateSuccess(null)
    try {
      await api.post('/rooms', {
        name: createForm.name,
        description: createForm.description || undefined,
        is_public: createForm.is_public,
      })
      setCreateSuccess('Room created successfully!')
      setCreateForm({ name: '', description: '', is_public: true })
      await loadRooms()
    } catch (err: any) {
      console.error('Failed to create room', err)
      setCreateError(err.response?.data?.detail || 'Unable to create room')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-discord-dark">
      <div className="p-6 border-b border-discord-darker">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Discover Rooms</h1>
            <p className="text-sm text-discord-textMuted">
              Join public rooms or create your own community.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Search rooms..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full md:w-72 px-4 py-2 bg-discord-darker border border-discord-light rounded text-white placeholder-discord-textMuted focus:outline-none focus:ring-2 focus:ring-discord-primary"
            />
            {user && (
              <button
                onClick={() => setShowCreateForm((prev) => !prev)}
                className="px-4 py-2 bg-discord-primary hover:bg-discord-primaryHover text-white rounded transition-colors"
              >
                {showCreateForm ? 'Close' : 'Create Room'}
              </button>
            )}
          </div>
        </div>
        {showCreateForm && user && (
          <form onSubmit={handleCreateRoom} className="mt-4 bg-discord-darker rounded-lg p-4 space-y-3">
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="block text-sm mb-1 text-discord-textMuted">Room name</label>
                <input
                  type="text"
                  value={createForm.name}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, name: e.target.value }))}
                  required
                  maxLength={100}
                  className="w-full px-3 py-2 bg-discord-dark border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
                />
              </div>
              <div>
                <label className="block text-sm mb-1 text-discord-textMuted">Visibility</label>
                <select
                  value={createForm.is_public ? 'public' : 'private'}
                  onChange={(e) =>
                    setCreateForm((prev) => ({ ...prev, is_public: e.target.value === 'public' }))
                  }
                  className="w-full px-3 py-2 bg-discord-dark border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
                >
                  <option value="public">Public (anyone can join)</option>
                  <option value="private">Private (invite only)</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm mb-1 text-discord-textMuted">Description</label>
              <textarea
                value={createForm.description}
                onChange={(e) =>
                  setCreateForm((prev) => ({ ...prev, description: e.target.value }))
                }
                rows={3}
                className="w-full px-3 py-2 bg-discord-dark border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary resize-none"
                placeholder="Tell others what this room is about..."
              />
            </div>
            {createError && (
              <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/40 px-3 py-2 rounded">
                {createError}
              </div>
            )}
            {createSuccess && (
              <div className="text-sm text-green-400 bg-green-500/10 border border-green-500/30 px-3 py-2 rounded">
                {createSuccess}
              </div>
            )}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={creating}
                className="px-5 py-2 bg-discord-primary hover:bg-discord-primaryHover text-white rounded transition-colors disabled:opacity-50"
              >
                {creating ? 'Creating...' : 'Create Room'}
              </button>
            </div>
          </form>
        )}
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-6">
        {error && (
          <div className="mb-4 text-sm text-red-400 bg-red-500/10 border border-red-500/30 px-3 py-2 rounded">
            {error}
          </div>
        )}
        {loading ? (
          <div className="text-discord-textMuted">Loading rooms...</div>
        ) : rooms.length === 0 ? (
          <div className="text-discord-textMuted">No rooms found</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {rooms.map((room) => {
              const isOwner = room.membership_role === 'owner'
              const isAdmin = room.membership_role === 'admin'
              return (
                <div
                  key={room.id}
                  className="p-4 bg-discord-darker rounded-lg border border-transparent hover:border-discord-primary/40 transition-colors flex flex-col gap-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <Link
                        to={`/rooms/${room.id}`}
                        className="text-white font-semibold text-lg hover:underline"
                      >
                        {room.name}
                      </Link>
                      {room.description && (
                        <p className="text-discord-textMuted text-sm mt-1 line-clamp-2">
                          {room.description}
                        </p>
                      )}
                    </div>
                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded ${
                        room.is_public
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-yellow-500/20 text-yellow-300'
                      }`}
                    >
                      {room.is_public ? 'Public' : 'Private'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm text-discord-textMuted">
                    <span>{room.member_count || 0} members</span>
                    <div className="flex items-center gap-2">
                      {room.is_member ? (
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            isOwner
                              ? 'bg-purple-500/20 text-purple-300'
                              : isAdmin
                              ? 'bg-blue-500/20 text-blue-300'
                              : 'bg-discord-dark text-discord-text'
                          }`}
                        >
                          {isOwner ? 'Owner' : isAdmin ? 'Admin' : 'Member'}
                        </span>
                      ) : room.can_join ? (
                        <button
                          onClick={() => handleJoinRoom(room.id)}
                          disabled={joiningRoomId === room.id}
                          className="px-3 py-1.5 bg-discord-primary hover:bg-discord-primaryHover text-white rounded text-xs transition-colors disabled:opacity-50"
                        >
                          {joiningRoomId === room.id ? 'Joining...' : 'Join Room'}
                        </button>
                      ) : (
                        <span className="text-xs text-yellow-300">Invite required</span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}



