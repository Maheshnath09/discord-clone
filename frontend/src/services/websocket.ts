export type WebSocketMessage = {
  type: string
  data: any
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private roomId: number | null = null
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private listeners: Map<string, Set<(data: any) => void>> = new Map()
  private connectionId = 0 // Track connection attempts to handle race conditions
  private isIntentionalDisconnect = false // Track if disconnect was intentional
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  connect(roomId: number, token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // If already connected to the same room, resolve immediately
      if (this.ws?.readyState === WebSocket.OPEN && this.roomId === roomId) {
        resolve()
        return
      }

      // If connecting to a different room, close existing connection first
      if (this.ws && this.roomId !== roomId) {
        this.ws.close()
        this.ws = null
      }

      // Increment connection ID to track this specific connection attempt
      const currentConnectionId = ++this.connectionId
      this.roomId = roomId
      this.token = token
      this.isIntentionalDisconnect = false
      this.reconnectAttempts = 0

      // Clear any pending reconnect
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout)
        this.reconnectTimeout = null
      }

      // Use wss:// in production, ws:// in development
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = import.meta.env.VITE_WS_URL || window.location.host.replace(':3000', ':8000')
      const wsUrl = `${protocol}//${host}/api/v1/ws/rooms/${roomId}?token=${token}`

      const ws = new WebSocket(wsUrl)
      this.ws = ws

      ws.onopen = () => {
        // Check if this connection is still valid (not superseded by another)
        if (this.connectionId !== currentConnectionId) {
          ws.close()
          return
        }
        this.reconnectAttempts = 0
        console.log(`WebSocket connected to room ${roomId}`)
        resolve()
      }

      ws.onerror = (error) => {
        // Only reject if this is still the current connection attempt
        if (this.connectionId === currentConnectionId) {
          console.error('WebSocket error:', error)
          reject(error)
        }
      }

      ws.onmessage = (event) => {
        // Only handle messages if this is still the current connection
        if (this.connectionId !== currentConnectionId) return
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        // Only handle close if this is still the current connection
        if (this.connectionId !== currentConnectionId) return

        console.log(`WebSocket closed: code=${event.code}, reason=${event.reason}`)
        this.ws = null

        // Only attempt reconnect if not intentionally disconnected
        if (!this.isIntentionalDisconnect && this.token && this.roomId) {
          this.attemptReconnect(this.roomId, this.token)
        }
      }
    })
  }

  private attemptReconnect(roomId: number, token: string) {
    if (this.isIntentionalDisconnect) {
      return
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000)
    console.log(`Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`)

    this.reconnectTimeout = setTimeout(() => {
      if (!this.isIntentionalDisconnect) {
        this.connect(roomId, token).catch(console.error)
      }
    }, delay)
  }

  disconnect() {
    console.log('WebSocket intentional disconnect')
    this.isIntentionalDisconnect = true

    // Clear any pending reconnect
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.roomId = null
    this.token = null
    this.reconnectAttempts = 0
    this.listeners.clear()
  }

  send(type: string, data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: (data: any) => void) {
    this.listeners.get(event)?.delete(callback)
  }

  removeAllListeners() {
    this.listeners.clear()
  }

  private handleMessage(message: WebSocketMessage) {
    console.log('WebSocket received message:', message.type, message.data)
    const callbacks = this.listeners.get(message.type)
    if (callbacks) {
      console.log(`Dispatching ${message.type} to ${callbacks.size} listeners`)
      callbacks.forEach((callback) => callback(message.data))
    }
  }
}

export const wsClient = new WebSocketClient()

