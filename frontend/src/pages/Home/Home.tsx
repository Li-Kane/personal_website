import './Home.css'
import { useEffect, useRef } from 'react'

function Home() {
  const wsRef = useRef<WebSocket | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)

  // Use environment variables with fallback to localhost for local development
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080'
  const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:3247'

  useEffect(() => {
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;
    const baseDelay = 1000; // Initial delay in ms
    const maxDelay = 30000; // Maximum delay of 30 seconds
    
    const connectWebSocket = () => {
      const ws = new WebSocket(WS_URL)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        reconnectAttempts = 0; // Reset attempts on successful connection
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++;
          // Exponential backoff: delay = baseDelay * 2^(attempts - 1)
          const exponentialDelay = Math.min(
            baseDelay * Math.pow(2, reconnectAttempts - 1),
            maxDelay
          );
          setTimeout(() => {
            connectWebSocket(); // Recursively reconnect
          }, exponentialDelay);
        } else {
          console.error('Max reconnect attempts reached. Could not reconnect to WebSocket.')
        }
      }
      
      wsRef.current = ws
    }
    
    // Initial connection
    connectWebSocket()

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [WS_URL])

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && containerRef.current) {
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
      wsRef.current.send(JSON.stringify(mouseData))
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
        <h1 id="title-text">Kane's Website</h1>
        <p id="subtitle-text">Aspiring Roboticist and Software Engineer</p>
      </div>
    </div>
  )
}

export default Home
