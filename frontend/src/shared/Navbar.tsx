import { NavLink } from "react-router";
import { useState } from "react";
import "./layout.css";
import { useWebSocket } from "./WebSocketContext";

export default function Navbar() {
    const { connectionStatus } = useWebSocket();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const closeMenu = () => {
        setIsMenuOpen(false);
    };

    return (
        <header className="navbar">
          <div className="status">
            <div className={`circle-status nav-status ${connectionStatus.status}`}></div>
            <p className="nav-text nav-status">Status: {connectionStatus.status}</p>
            {connectionStatus.status === 'Queued' && (
              <p className="nav-text nav-status">({connectionStatus.queue_position})</p>
            )}
            {connectionStatus.message && (
              <p className="nav-text nav-status">({connectionStatus.message})</p>
            )}
          </div>
          
          <button className={`hamburger ${isMenuOpen ? 'open' : ''}`} onClick={toggleMenu} aria-label="Toggle menu">
            <span></span>
            <span></span>
            <span></span>
          </button>

          <nav className="nav-desktop">
            <NavLink className="nav-text nav-link" to="/">Home</NavLink>
            <NavLink className="nav-text nav-link" to="/profile">Profile</NavLink>
            <NavLink className="nav-text nav-link" to="/projects">Projects</NavLink>
          </nav>

          <nav className={`nav-mobile ${isMenuOpen ? 'open' : ''}`}>
            <NavLink className="nav-text nav-link" to="/" onClick={closeMenu}>Home</NavLink>
            <NavLink className="nav-text nav-link" to="/profile" onClick={closeMenu}>Profile</NavLink>
            <NavLink className="nav-text nav-link" to="/projects" onClick={closeMenu}>Projects</NavLink>
          </nav>
        </header>
    )
}