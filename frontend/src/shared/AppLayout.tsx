// shared/AppLayout.tsx
import { Outlet, NavLink } from "react-router";
import "./layout.css";

export default function AppLayout() {
  return (
    <div id="app-layout">
      <header id="navbar">
        <nav>
          <NavLink className="nav-link" to="/">Home</NavLink>
          <NavLink className="nav-link" to="/profile">Profile</NavLink>
          <NavLink className="nav-link" to="/projects">Projects</NavLink>
        </nav>
      </header>
      <main id="content">
        <Outlet />
      </main>
    </div>
  );
}
