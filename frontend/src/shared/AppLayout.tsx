// SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
// SPDX-License-Identifier: GPL-3.0-or-later

// shared/AppLayout.tsx
import { Outlet } from "react-router";
import { WebSocketProvider } from "./WebSocketContext";
import styles from "./layout.module.css";
import Navbar from "./Navbar";
import KaranaViewer from "./KaranaViewer";

export default function AppLayout() {
  const SIM_WS_URL = import.meta.env.VITE_SIM_WS_URL;
  const SIM_HEALTH_URL = import.meta.env.VITE_SIM_HEALTH_URL;

  return (
    <WebSocketProvider>
      <div className={styles['app-layout']}>
        <Navbar />
        <main>
          <KaranaViewer
            simWsUrl={SIM_WS_URL}
            simHealthUrl={SIM_HEALTH_URL}
            className={styles['sim-viewer']}
          />
          <Outlet />
        </main>
      </div>
    </WebSocketProvider>
  );
}
