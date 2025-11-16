// shared/AppLayout.tsx
import { Outlet } from "react-router";
import { WebSocketProvider } from "./WebSocketContext";
import "./layout.css";
import Navbar from "./Navbar";

export default function AppLayout() {

  return (
    <WebSocketProvider>
      <div className="app-layout">
        <Navbar />
        <main className="content">
          <Outlet />
        </main>
      </div>
    </WebSocketProvider>
  );
}
