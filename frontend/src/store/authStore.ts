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
  isLoading: boolean
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
      isLoading: true,

      setAuth: (user, token) => {
        set({ user, accessToken: token, isAuthenticated: true, isLoading: false })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },

      logout: async () => {
        try {
          await api.post('/auth/logout')
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({ user: null, accessToken: null, isAuthenticated: false, isLoading: false })
          delete api.defaults.headers.common['Authorization']
        }
      },

      checkAuth: async () => {
        const { accessToken } = get()

        if (!accessToken) {
          set({ isAuthenticated: false, isLoading: false })
          return
        }

        // Ensure the Authorization header is set
        api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

        try {
          const response = await api.get('/users/me')
          set({ user: response.data, isAuthenticated: true, isLoading: false })
        } catch (error) {
          // Token invalid or expired - clear auth state
          set({ user: null, accessToken: null, isAuthenticated: false, isLoading: false })
          delete api.defaults.headers.common['Authorization']
        }
      },
    }),
    {
      name: 'auth-storage',
      // Use localStorage to persist across page refreshes and browser sessions
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      }),
      // Restore the Authorization header when the store is rehydrated from storage
      onRehydrateStorage: () => (state) => {
        if (state?.accessToken) {
          api.defaults.headers.common['Authorization'] = `Bearer ${state.accessToken}`
        }
      },
    }
  )
)
