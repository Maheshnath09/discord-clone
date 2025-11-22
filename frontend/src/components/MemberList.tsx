import { useEffect, useState } from 'react'
import api from '../services/api'

interface Member {
  id: number
  user_id: number
  role: string
  user: {
    id: number
    username: string
    display_name: string | null
    avatar_url: string | null
  }
}

interface MemberListProps {
  roomId: number
}

export default function MemberList({ roomId }: MemberListProps) {
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMembers()
  }, [roomId])

  const loadMembers = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/rooms/${roomId}/members`)
      setMembers(response.data)
    } catch (error) {
      console.error('Failed to load members:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-60 bg-discord-darker border-l border-discord-dark p-4 overflow-y-auto scrollbar-thin">
      <h3 className="text-sm font-semibold text-discord-textMuted uppercase mb-4">
        Members — {members.length}
      </h3>
      
      {loading ? (
        <div className="text-discord-textMuted text-sm">Loading...</div>
      ) : (
        <div className="space-y-2">
          {members.map((member) => (
            <div
              key={member.id}
              className="flex items-center space-x-2 p-2 rounded hover:bg-discord-dark transition-colors"
            >
              {member.user.avatar_url ? (
                <img
                  src={member.user.avatar_url}
                  alt={member.user.username}
                  className="w-8 h-8 rounded-full"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-discord-primary flex items-center justify-center text-white text-xs font-semibold">
                  {member.user.username.charAt(0).toUpperCase()}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm truncate">
                  {member.user.display_name || member.user.username}
                </p>
                {member.role !== 'member' && (
                  <p className="text-xs text-discord-textMuted capitalize">{member.role}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}



