import { useEffect, useState, useRef, useCallback } from 'react'
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
  const isConnectedRef = useRef(false)

  // Memoized message handler to prevent stale closures
  const handleNewMessage = useCallback((data: any) => {
    console.log('Received new message via WebSocket:', data)
    setMessages((prev) => {
      // Avoid duplicates by checking message ID
      if (prev.some((msg) => msg.id === data.id)) {
        return prev
      }
      return [...prev, data]
    })
  }, [])

  const handleTypingStart = useCallback((data: any) => {
    setTypingUsers((prev) => new Set(prev).add(data.user_id))
  }, [])

  const handleTypingStop = useCallback((data: any) => {
    setTypingUsers((prev) => {
      const next = new Set(prev)
      next.delete(data.user_id)
      return next
    })
  }, [])

  useEffect(() => {
    if (!roomId || !accessToken) return

    let isMounted = true
    isConnectedRef.current = false

    const loadRoom = async () => {
      try {
        const response = await api.get(`/rooms/${roomId}`)
        if (isMounted) setRoom(response.data)
        return response.data
      } catch (error) {
        console.error('Failed to load room:', error)
        return null
      }
    }

    const loadMessages = async () => {
      try {
        if (isMounted) setLoading(true)
        const response = await api.get(`/rooms/${roomId}/messages`, {
          params: { limit: 50 },
        })
        if (isMounted) setMessages(response.data.reverse()) // Reverse to show oldest first
      } catch (error) {
        console.error('Failed to load messages:', error)
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    // Auto-join public rooms to ensure user can send messages
    const autoJoinRoom = async () => {
      try {
        await api.post(`/rooms/${roomId}/join`)
        console.log('Auto-joined room', roomId)
      } catch (error: any) {
        // 400 means already a member, which is fine
        if (error.response?.status !== 400) {
          console.log('Could not auto-join room (may need invite):', error.response?.data?.detail)
        }
      }
    }

    const connectWebSocket = async () => {
      if (!roomId || !accessToken || isConnectedRef.current) return

      try {
        // Register listeners BEFORE connecting to avoid missing messages
        console.log('Registering WebSocket listeners for message.create, typing.start, typing.stop')
        wsClient.on('message.create', handleNewMessage)
        wsClient.on('typing.start', handleTypingStart)
        wsClient.on('typing.stop', handleTypingStop)

        console.log('Attempting WebSocket connection to room', roomId)
        await wsClient.connect(parseInt(roomId), accessToken)
        if (isMounted) {
          isConnectedRef.current = true
          console.log('WebSocket connected successfully')
        }
      } catch (error) {
        console.error('Failed to connect WebSocket:', error)
      }
    }

    // Load room, auto-join if public, then load messages and connect WebSocket
    const initRoom = async () => {
      const roomData = await loadRoom()
      if (roomData?.is_public) {
        await autoJoinRoom()
      }
      await loadMessages()
      await connectWebSocket()
    }

    initRoom()

    return () => {
      isMounted = false
      // Remove listeners and disconnect
      wsClient.off('message.create', handleNewMessage)
      wsClient.off('typing.start', handleTypingStart)
      wsClient.off('typing.stop', handleTypingStop)
      wsClient.disconnect()
      isConnectedRef.current = false
    }
  }, [roomId, accessToken, handleNewMessage, handleTypingStart, handleTypingStop])

  const handleSendMessage = async (content: string) => {
    if (!roomId || !content.trim()) return

    try {
      const res = await api.post(`/rooms/${roomId}/messages`, {
        content,
        content_type: 'text',
      })
      // Append created message immediately for snappy UI.
      // The WebSocket handler also has duplicate detection, so this is safe.
      const created = res.data
      setMessages((prev) => {
        // Avoid duplicates by checking message ID
        if (prev.some((msg) => msg.id === created.id)) {
          return prev
        }
        return [...prev, created]
      })
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
    <div className="flex-1 flex flex-col bg-discord-dark min-h-0 overflow-hidden">
      {/* Room header */}
      <div className="flex-shrink-0 p-4 border-b border-discord-darker bg-discord-dark">
        <h2 className="text-xl font-semibold text-white">{room.name}</h2>
        {room.description && (
          <p className="text-discord-textMuted text-sm mt-1">{room.description}</p>
        )}
      </div>

      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Chat area */}
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <ChatWindow
            messages={messages}
            typingUsers={typingUsers}
            messagesEndRef={messagesEndRef}
            currentUserId={user?.id}
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



