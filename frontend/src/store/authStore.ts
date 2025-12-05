import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: number
  username: string
  email: string
  display_name: string | null
  bio: string | null
  avatar_url: string | null
}

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string) => void
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      
      setAuth: (user, token) => {
        set({ user, accessToken: token, isAuthenticated: true })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },
      
      logout: async () => {
        try {
          await api.post('/auth/logout')
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({ user: null, accessToken: null, isAuthenticated: false })
          delete api.defaults.headers.common['Authorization']
        }
      },
      
      checkAuth: async () => {
        const { accessToken } = get()
        if (!accessToken) {
          set({ isAuthenticated: false })
          return
        }
        
        try {
          const response = await api.get('/users/me')
          set({ user: response.data, isAuthenticated: true })
        } catch (error) {
          set({ user: null, accessToken: null, isAuthenticated: false })
          delete api.defaults.headers.common['Authorization']
        }
      },
    }),
    {
      name: 'auth-storage',
      // Use sessionStorage so different tabs/windows can have independent
      // authentication state (localStorage is shared across tabs).
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({ accessToken: state.accessToken }),
    }
  )
)

