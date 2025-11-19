import { NavLink, useLocation } from "react-router";
import { useState } from "react";
import styles from "./layout.module.css";
import { useWebSocket } from "./WebSocketContext";

export default function Navbar() {
    const { connectionStatus } = useWebSocket();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const location = useLocation();

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const closeMenu = () => {
        setIsMenuOpen(false);
    };

    return (
        <header className={`${styles.navbar} ${location.pathname === '/' ? styles['navbar-home'] : styles['navbar-default']}`}>
          <div className={styles.status}>
            <div className={`${styles['circle-status']} ${styles[connectionStatus.status]}`}></div>
            <p className={`${styles['nav-text']} ${styles['nav-status']}`}>Status: {connectionStatus.status}</p>
            {connectionStatus.status === 'Queued' && (
              <p className={`${styles['nav-text']} ${styles['nav-status']}`}>({connectionStatus.queue_position})</p>
            )}
            {connectionStatus.message && (
              <p className={`${styles['nav-text']} ${styles['nav-status']}`}>({connectionStatus.message})</p>
            )}
          </div>

          <button className={`${styles.hamburger} ${isMenuOpen ? styles.open : ''}`} onClick={toggleMenu} aria-label="Toggle menu">
            <span></span>
            <span></span>
            <span></span>
          </button>

          <nav className={styles['nav-desktop']}>
            <NavLink className={`${styles['nav-text']} ${styles['nav-link']}`} to="/">Home</NavLink>
            <NavLink className={`${styles['nav-text']} ${styles['nav-link']}`} to="/profile">Profile</NavLink>
            <NavLink className={`${styles['nav-text']} ${styles['nav-link']}`} to="/projects">Projects</NavLink>
          </nav>

          <nav className={`${styles['nav-mobile']} ${isMenuOpen ? styles.open : ''}`}>
            <NavLink className={`${styles['nav-text']} ${styles['nav-link']}`} to="/" onClick={closeMenu}>Home</NavLink>
            <NavLink className={`${styles['nav-text']} ${styles['nav-link']}`} to="/profile" onClick={closeMenu}>Profile</NavLink>
            <NavLink className={`${styles['nav-text']} ${styles['nav-link']}`} to="/projects" onClick={closeMenu}>Projects</NavLink>
          </nav>
        </header>
    )
}