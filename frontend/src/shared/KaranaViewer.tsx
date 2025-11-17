import { useEffect, useRef } from 'react'
import { useWebSocket } from './WebSocketContext'
import { useLocation } from 'react-router'

interface KaranaViewerProps {
  serverUrl?: string
  className?: string
}

/*
Used to load and show the custom Karana viewer I modified 
from kdFlex. I need to do this so I can route to my ssl certified server.
*/
function KaranaViewer({ serverUrl, className = '' }: KaranaViewerProps) {
    const location = useLocation()
    const containerRef = useRef<HTMLDivElement>(null)
    const { ws, connectionStatus } = useWebSocket()
    // Show viewer only on home page
    const showViewer = location.pathname === '/';

  useEffect(() => {
    if (!containerRef.current) return

    // Extract hostname:port from serverUrl (remove http:// or https://)
    let wsUrl: string
    if (serverUrl) {
      wsUrl = serverUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')
    } else {
      wsUrl = window.location.host
    }

    // Set the global variable for the Karana viewer
    (window as any).KARANA_WEBUI_URL = wsUrl

    // Check if script is already loaded
    const existingScript = document.querySelector('script[src="/viewer.js"]')
    let viewerCleanup: (() => void) | null = null
    
    if (existingScript) {
      // Script already loaded, just initialize
      if ((window as any).initKaranaViewer && containerRef.current) {
        viewerCleanup = (window as any).initKaranaViewer(containerRef.current)
      }
    } else {
      // Load the script first
      const script = document.createElement('script')
      script.src = '/viewer.js'
      script.type = 'module'
      
      script.onload = () => {
        console.log('Karana viewer loaded successfully')
        // Initialize the viewer with our container
        if ((window as any).initKaranaViewer && containerRef.current) {
          viewerCleanup = (window as any).initKaranaViewer(containerRef.current)
        }
      }

      script.onerror = () => {
        console.error('Failed to load Karana viewer script')
      }

      document.head.appendChild(script)
    }

    // Cleanup function
    return () => {
      // Call viewer's cleanup
      if (viewerCleanup) {
        viewerCleanup()
      }
      
      // Clear the container
      if (containerRef.current) {
        containerRef.current.innerHTML = ''
      }
      
      // Clean up global variables (but keep script and initKaranaViewer for reuse)
      delete (window as any).KARANA_WEBUI_URL
      delete (window as any).conn
      delete (window as any).scene
      delete (window as any).object_map
      delete (window as any).camera_controls_map
      delete (window as any).hud_camera
      delete (window as any).shadow_light
    }
  }, [serverUrl])

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

  return (
    <div 
      ref={containerRef} 
      className={className}
      onMouseMove={handleMouseMove} 
      style={{ 
        width: '100%', 
        height: '100%',
        overflow: 'hidden',
        display: showViewer ? 'block' : 'none'
      }}
    />
  )
}

export default KaranaViewer
