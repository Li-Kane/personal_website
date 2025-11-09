import './Home.css'
import { useEffect, useRef } from 'react'

function Home() {
  const wsRef = useRef<WebSocket | null>(null)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // Use environment variables with fallback to localhost for local development
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080'
  const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:3247'

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket(WS_URL)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }
    
    wsRef.current = ws

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [WS_URL])

  const handleMouseMove = (event: React.MouseEvent<HTMLIFrameElement>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const mouseData = {
        x: event.clientX,
        y: event.clientY,
      }
      wsRef.current.send(JSON.stringify(mouseData))
    }
  }

  return (
    <iframe 
      ref={iframeRef}
      id="sim-iframe" 
      src={SERVER_URL}
      onMouseMove={handleMouseMove}
    >
    </iframe>
  )
}

export default Home
