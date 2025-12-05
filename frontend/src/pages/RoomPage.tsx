import { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'
import { wsClient } from '../services/websocket'
import { useAuthStore } from '../store/authStore'
import ChatWindow from '../components/ChatWindow'
import MessageComposer from '../components/MessageComposer'
import MemberList from '../components/MemberList'

interface Message {
  id: number
  content: string | null
  author: {
    id: number
    username: string
    display_name: string | null
    avatar_url: string | null
  }
  created_at: string
  edited_at: string | null
}

interface Room {
  id: number
  name: string
  description: string | null
  is_public: boolean
}

export default function RoomPage() {
  const { roomId } = useParams<{ roomId: string }>()
  const [room, setRoom] = useState<Room | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [typingUsers, setTypingUsers] = useState<Set<number>>(new Set())
  const { user, accessToken } = useAuthStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!roomId || !accessToken) return

    loadRoom()
    loadMessages()
    connectWebSocket()

    return () => {
      wsClient.disconnect()
    }
  }, [roomId, accessToken])

  const loadRoom = async () => {
    try {
      const response = await api.get(`/rooms/${roomId}`)
      setRoom(response.data)
    } catch (error) {
      console.error('Failed to load room:', error)
    }
  }

  const loadMessages = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/rooms/${roomId}/messages`, {
        params: { limit: 50 },
      })
      setMessages(response.data.reverse()) // Reverse to show oldest first
    } catch (error) {
      console.error('Failed to load messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const connectWebSocket = () => {
    if (!roomId || !accessToken) return

    wsClient.connect(parseInt(roomId), accessToken).then(() => {
      // Listen for new messages
      wsClient.on('message.create', (data: any) => {
        // Append new incoming message to state
        setMessages((prev) => (prev ? [...prev, data] : [data]))
      })

      // Listen for typing indicators
      wsClient.on('typing.start', (data: any) => {
        setTypingUsers((prev) => new Set(prev).add(data.user_id))
      })

      wsClient.on('typing.stop', (data: any) => {
        setTypingUsers((prev) => {
          const next = new Set(prev)
          next.delete(data.user_id)
          return next
        })
      })
    })
  }

  const handleSendMessage = async (content: string) => {
    if (!roomId || !content.trim()) return

    try {
      const res = await api.post(`/rooms/${roomId}/messages`, {
        content,
        content_type: 'text',
      })
      // Append created message immediately for snappy UI.
      const created = res.data
      setMessages((prev) => (prev ? [...prev, created] : [created]))
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const handleTyping = (isTyping: boolean) => {
    if (!roomId) return
    wsClient.send(isTyping ? 'typing.start' : 'typing.stop', {})
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (loading && !room) {
    return (
      <div className="flex-1 flex items-center justify-center text-discord-textMuted">
        Loading room...
      </div>
    )
  }

  if (!room) {
    return (
      <div className="flex-1 flex items-center justify-center text-discord-textMuted">
        Room not found
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col bg-discord-dark">
      {/* Room header */}
      <div className="p-4 border-b border-discord-darker bg-discord-dark">
        <h2 className="text-xl font-semibold text-white">{room.name}</h2>
        {room.description && (
          <p className="text-discord-textMuted text-sm mt-1">{room.description}</p>
        )}
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          <ChatWindow
            messages={messages}
            typingUsers={typingUsers}
            messagesEndRef={messagesEndRef}
          />
          <MessageComposer
            onSend={handleSendMessage}
            onTyping={handleTyping}
          />
        </div>

        {/* Member list (hidden on small screens) */}
        <div className="hidden md:block">
          <MemberList roomId={parseInt(roomId!)} />
        </div>
      </div>
    </div>
  )
}



