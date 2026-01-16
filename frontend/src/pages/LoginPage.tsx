import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/login', { identifier, password })
      const { access_token } = response.data

      // Attach token before fetching user profile
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      const userResponse = await api.get('/users/me')
      setAuth(userResponse.data, access_token)

      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-discord-darkest px-4">
      <div className="w-full max-w-md p-8 bg-discord-dark rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-white mb-6 text-center">Welcome back!</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-500/20 border border-red-500 rounded text-red-400 text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="identifier" className="block text-sm font-medium text-discord-textMuted mb-2">
              Email or Username
            </label>
            <input
              id="identifier"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              className="w-full px-4 py-2 bg-discord-darker border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-discord-textMuted mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 bg-discord-darker border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-discord-primary hover:bg-discord-primaryHover text-white font-medium rounded transition-colors disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <p className="mt-4 text-center text-discord-textMuted text-sm">
          Need an account?{' '}
          <Link to="/register" className="text-discord-primary hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  )
}



