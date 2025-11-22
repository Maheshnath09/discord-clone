import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ChatLayout from './layouts/ChatLayout'
import RoomPage from './pages/RoomPage'
import RoomsPage from './pages/RoomsPage'
import ProfilePage from './pages/ProfilePage'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" />} />
        <Route path="/register" element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/" />} />
        <Route
          path="/"
          element={isAuthenticated ? <ChatLayout /> : <Navigate to="/login" />}
        >
          <Route index element={<RoomsPage />} />
          <Route path="rooms/:roomId" element={<RoomPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App



