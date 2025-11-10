// shared/AppLayout.tsx
import { Outlet, NavLink } from "react-router";
import "./layout.css";

export default function AppLayout() {
  return (
    <div className="app-layout">
      <header className="navbar">
        <nav>
          <NavLink className="nav-link" to="/">Home</NavLink>
          <NavLink className="nav-link" to="/profile">Profile</NavLink>
          <NavLink className="nav-link" to="/projects">Projects</NavLink>
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
