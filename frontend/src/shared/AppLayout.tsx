// shared/AppLayout.tsx
import { Outlet } from "react-router";
import { WebSocketProvider } from "./WebSocketContext";
import styles from "./layout.module.css";
import Navbar from "./Navbar";
import KaranaViewer from "./KaranaViewer";

export default function AppLayout() {
  const SERVER_URL = import.meta.env.VITE_SERVER_URL;

  return (
    <WebSocketProvider>
      <div className={styles['app-layout']}>
        <Navbar />
        <main>
          <KaranaViewer
            serverUrl={SERVER_URL}
            className={styles['sim-viewer']}
          />
          <Outlet />
        </main>
      </div>
    </WebSocketProvider>
  );
}
