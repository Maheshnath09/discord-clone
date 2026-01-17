import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ChatLayout from './layouts/ChatLayout'
import RoomPage from './pages/RoomPage'
import RoomsPage from './pages/RoomsPage'
import ProfilePage from './pages/ProfilePage'

function App() {
  const { isAuthenticated, isLoading, checkAuth, accessToken } = useAuthStore()

  // Validate token and load user data on mount
  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  // Show loading indicator while checking auth
  if (isLoading && accessToken) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

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
