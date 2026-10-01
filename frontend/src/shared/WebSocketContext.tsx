// SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
// SPDX-License-Identifier: GPL-3.0-or-later

import { createContext, useContext, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'

interface Connection {
  status: 'Connected' | 'Queued' | 'Disconnected'
  queue_position?: number
  message?: string
}

interface WebSocketContextType {
  ws: WebSocket | null
  connectionStatus: Connection
}

const WebSocketContext = createContext<WebSocketContextType | null>(null)

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const ws = useRef<WebSocket | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<Connection>({ status: 'Disconnected' })

  const WS_URL = import.meta.env.VITE_CONTROLS_WS_URL

  useEffect(() => {
    ws.current = new WebSocket(WS_URL)
    
    ws.current.onopen = () => {
      console.log('WebSocket connected')
    }
    
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data)
      if (message.status === 'Queued') {
        setConnectionStatus({ status: 'Queued', queue_position: message.queue_position })
      } else if (message.status === 'Connected') {
        setConnectionStatus({ status: 'Connected' })
      }
    }
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus({ status: 'Disconnected', message: 'WebSocket error' })
    }
    
    ws.current.onclose = (event) => {
      setConnectionStatus({ status: 'Disconnected', message: event.reason || 'Connection closed' })
    }

    return () => {
      ws.current?.close()
    }
  }, [WS_URL])

  return (
    <WebSocketContext.Provider value={{ ws: ws.current, connectionStatus }}>
      {children}
    </WebSocketContext.Provider>
  )
}
