import { NavLink } from "react-router";
import "./layout.css";
import { useWebSocket } from "./WebSocketContext";

export default function Navbar() {
    const { connectionStatus } = useWebSocket();

    return (
        <header className="navbar">
          <div className="status">
            <div className={`circle-status ${connectionStatus.status}`}></div>
            <p className="nav-text">Status: {connectionStatus.status}</p>
            {connectionStatus.status === 'Queued' && (
              <p className="nav-text">  ({connectionStatus.queue_position})</p>
            )}
          </div>
          <nav>
            <NavLink className="nav-text nav-link" to="/">Home</NavLink>
            <NavLink className="nav-text nav-link" to="/profile">Profile</NavLink>
            <NavLink className="nav-text nav-link" to="/projects">Projects</NavLink>
          </nav>
        </header>
    )
}