import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import api from '../services/api'

// Generate a unique tab ID for this browser tab instance
// This helps isolate sessions when tabs are duplicated
const generateTabId = () => `tab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
const TAB_ID = generateTabId()

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
  tabId: string | null  // Track which tab owns this session
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
      tabId: null,

      setAuth: (user, token) => {
        set({ user, accessToken: token, isAuthenticated: true, tabId: TAB_ID })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },

      logout: async () => {
        try {
          await api.post('/auth/logout')
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({ user: null, accessToken: null, isAuthenticated: false, tabId: null })
          delete api.defaults.headers.common['Authorization']
        }
      },

      checkAuth: async () => {
        const { accessToken, tabId } = get()

        // If this session was created by a different tab (e.g., tab was duplicated),
        // invalidate it to force fresh login
        if (tabId && tabId !== TAB_ID) {
          console.log('Session from different tab detected, clearing auth state')
          set({ user: null, accessToken: null, isAuthenticated: false, tabId: null })
          delete api.defaults.headers.common['Authorization']
          return
        }

        if (!accessToken) {
          set({ isAuthenticated: false })
          return
        }

        // Ensure the Authorization header is set
        api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

        try {
          const response = await api.get('/users/me')
          set({ user: response.data, isAuthenticated: true, tabId: TAB_ID })
        } catch (error) {
          set({ user: null, accessToken: null, isAuthenticated: false, tabId: null })
          delete api.defaults.headers.common['Authorization']
        }
      },
    }),
    {
      name: 'auth-storage',
      // Use sessionStorage so different tabs/windows can have independent
      // authentication state (localStorage is shared across tabs).
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({ accessToken: state.accessToken, tabId: state.tabId }),
      // Restore the Authorization header when the store is rehydrated from storage
      onRehydrateStorage: () => (state) => {
        if (state?.accessToken) {
          // Check if this tab owns the session
          if (state.tabId && state.tabId !== TAB_ID) {
            // Session was created by different tab (duplicated tab), don't restore
            console.log('Ignoring session from duplicated tab')
            return
          }
          api.defaults.headers.common['Authorization'] = `Bearer ${state.accessToken}`
          // Mark as authenticated if we have a token
          // The checkAuth will verify it's still valid
          state.isAuthenticated = true
        }
      },
    }
  )
)


