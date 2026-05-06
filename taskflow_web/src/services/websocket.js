export class BoardWebSocket {
  constructor(boardId, handlers = {}) {
    this.boardId = boardId
    this.handlers = handlers
    this.ws = null
    this.reconnectDelay = 2000
    this.shouldReconnect = true
    this.connect()
  }

  connect() {
    const url = `ws://localhost:8000/ws/board/${this.boardId}/`
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('[WS] Connected to board', this.boardId)
      this.reconnectDelay = 2000
      this.handlers.onConnected?.()
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        switch (data.type) {
          case 'task_moved':
            this.handlers.onTaskMoved?.(data)
            break
          case 'task_created':
            this.handlers.onTaskCreated?.(data)
            break
          case 'task_updated':
            this.handlers.onTaskUpdated?.(data)
            break
          case 'task_deleted':
            this.handlers.onTaskDeleted?.(data)
            break
          case 'connected':
            break
          default:
            console.log('[WS] Unknown message type:', data.type)
        }
      } catch (e) {
        console.error('[WS] Parse error:', e)
      }
    }

    this.ws.onerror = (err) => {
      console.warn('[WS] Error:', err)
    }

    this.ws.onclose = () => {
      console.log('[WS] Disconnected')
      this.handlers.onDisconnected?.()
      if (this.shouldReconnect) {
        setTimeout(() => this.connect(), this.reconnectDelay)
        this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000)
      }
    }
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  disconnect() {
    this.shouldReconnect = false
    this.ws?.close()
  }
}
