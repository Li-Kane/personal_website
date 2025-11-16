import './Home.css'
import { useRef } from 'react'
import { useWebSocket } from '../../shared/WebSocketContext'

function Home() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const { ws, connectionStatus } = useWebSocket()

  // Use environment variables with fallback to localhost for local development
  const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:3247'

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (ws && ws.readyState === WebSocket.OPEN && containerRef.current && connectionStatus.status === 'Connected') {
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
      ws.send(JSON.stringify(mouseData))
    }
  }

  if (false) {
    return (
      <div className="loading-container">
        <p className="loading-text">Connecting to server...</p>
      </div>
    )
  } else {
    return (
    <div 
      className="home-container" 
      onMouseMove={handleMouseMove} 
      ref={containerRef}
    >
      <iframe 
        className="sim-iframe" 
        src={SERVER_URL}
      >
      </iframe>
      <div className="overlay-text">
        <div className="title-container">
          <h1 className="title-text">Kane's Website</h1>
          <p className="subtitle-text">Aspiring Roboticist and Software Engineer</p>
        </div>
      </div>
    </div>
    )
  }
}

export default Home
