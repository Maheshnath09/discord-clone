import { format } from 'date-fns'
import ReactMarkdown from 'react-markdown'

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

interface ChatWindowProps {
  messages: Message[]
  typingUsers: Set<number>
  messagesEndRef: React.RefObject<HTMLDivElement>
  currentUserId?: number
}

// Animated typing dots component
function TypingDots() {
  return (
    <span className="inline-flex items-center space-x-0.5 ml-1">
      <span className="w-1.5 h-1.5 bg-discord-textMuted rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
      <span className="w-1.5 h-1.5 bg-discord-textMuted rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
      <span className="w-1.5 h-1.5 bg-discord-textMuted rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
    </span>
  )
}

export default function ChatWindow({ messages, typingUsers, messagesEndRef, currentUserId }: ChatWindowProps) {
  // Filter out current user from typing list
  const otherTypingUsers = Array.from(typingUsers).filter(id => id !== currentUserId)

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4">
      {messages.map((message) => (
        <div key={message.id} className="flex space-x-3 hover:bg-discord-darker/50 p-2 rounded">
          <div className="flex-shrink-0">
            {message.author.avatar_url ? (
              <img
                src={message.author.avatar_url}
                alt={message.author.username}
                className="w-10 h-10 rounded-full"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-discord-primary flex items-center justify-center text-white font-semibold">
                {message.author.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline space-x-2">
              <span className="font-semibold text-white">
                {message.author.display_name || message.author.username}
              </span>
              <span className="text-xs text-discord-textMuted">
                {format(new Date(message.created_at), 'HH:mm')}
              </span>
              {message.edited_at && (
                <span className="text-xs text-discord-textMuted italic">(edited)</span>
              )}
            </div>
            {message.content && (
              <div className="text-discord-text mt-1 prose prose-invert max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Real-time typing indicator */}
      {otherTypingUsers.length > 0 && (
        <div className="flex items-center px-2 py-1 text-discord-textMuted text-sm">
          <span className="font-medium text-white">
            {otherTypingUsers.length === 1
              ? 'Someone is typing'
              : `${otherTypingUsers.length} people are typing`}
          </span>
          <TypingDots />
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}




