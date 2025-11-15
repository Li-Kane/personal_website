import './Home.css'
import { useEffect, useRef, useState } from 'react'

interface Connection {
  status: 'Connected' | 'Queued' | 'Disconnected' | 'Error'
  queue_position?: number
}

function Home() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<Connection>({ status: 'Disconnected' })

  // Use environment variables with fallback to localhost for local development
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080'
  const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:3247'

  // Establish WebSocket connection
  useEffect(() => {
    ws.current = new WebSocket(WS_URL)
    ws.current.onopen = () => {
      console.log('WebSocket connected')
    }
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data)
      console.log('WebSocket message received:', message)
      if (message.status === 'Queued') {
        setConnectionStatus({ status: 'Queued', queue_position: message.queue_position })
      } else if (message.status === 'Connected') {
        setConnectionStatus({ status: 'Connected' })
      }
    }
    ws.current.onerror = (error) => {
      // couldn't connect to websocket (maybe our server is down)
      console.error('WebSocket error:', error)
      setConnectionStatus({ status: 'Error' })
    }
    ws.current.onclose = () => {
      console.log('WebSocket disconnected')
      setConnectionStatus({ status: 'Disconnected' })
    }

    return () => {
      ws.current?.close()
    }
  }, [])

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect()
      const x = (2 * event.clientX / rect.width) - 1;
      const y = 1 - (2 * event.clientY / rect.height);
      const ratio = rect.width / rect.height;
      // output the NDC coordinates to the console
      const mouseData = {
        x: x,
        y: y,
        ratio: ratio
      }
      ws.current.send(JSON.stringify(mouseData))
    }
  }

  return (
    <div 
      id="home-container" 
      onMouseMove={handleMouseMove} 
      ref={containerRef}
    >
      <iframe 
        id="sim-iframe" 
        src={SERVER_URL}
      >
      </iframe>
      <div id="overlay-text">
        <p>Connection Status: {connectionStatus.status}</p>
        {connectionStatus.status === 'Queued' && (
          <p>Your position in queue: {connectionStatus.queue_position}</p>
        )}
        <div id="title-container">
          <h1 id="title-text">Kane's Website</h1>
          <p id="subtitle-text">Aspiring Roboticist and Software Engineer</p>
        </div>
      </div>
    </div>
  )
}

export default Home
