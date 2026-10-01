// SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
// SPDX-License-Identifier: GPL-3.0-or-later

import { useEffect, useRef } from 'react'
import { useWebSocket } from './WebSocketContext'
import { useLocation } from 'react-router'
// @ts-ignore
import { initKaranaViewer } from './viewer'

interface KaranaViewerProps {
  simWsUrl?: string
  simHealthUrl?: string
  className?: string
}

/*
Used to load and show the custom Karana viewer I modified 
from kdFlex. I need to do this so I can route to my ssl certified server.
*/
function KaranaViewer({ simWsUrl, simHealthUrl, className = '' }: KaranaViewerProps) {
    const location = useLocation()
    const containerRef = useRef<HTMLDivElement>(null)
    const { ws, connectionStatus } = useWebSocket()
    // Show viewer only on home page
    const showViewer = location.pathname === '/';

  useEffect(() => {
    if (!containerRef.current) return

    // Initialize the viewer with our container
    const viewerCleanup = initKaranaViewer(containerRef.current, simWsUrl, simHealthUrl)

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
      
      // Clean up global variables
      delete (window as any).conn
      delete (window as any).scene
      delete (window as any).object_map
      delete (window as any).camera_controls_map
      delete (window as any).hud_camera
      delete (window as any).shadow_light
    }
  }, [simWsUrl, simHealthUrl])

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
