import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from "react-router";
import Home from './pages/Home/Home.tsx'
import Profile from './pages/Profile/Profile.tsx'
import AppLayout from './shared/AppLayout.tsx'
import Work from './pages/Work/Work.tsx'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename="/">
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/work" element={<Work />} />
          <Route path="/work/:category" element={<Work />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
)