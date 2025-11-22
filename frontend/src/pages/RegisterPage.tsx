import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [displayName, setDisplayName] = useState('')
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
      const response = await api.post('/auth/register', {
        email,
        username,
        password,
        display_name: displayName || undefined,
      })
      const { access_token } = response.data

      // Attach token before fetching user profile
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      const userResponse = await api.get('/users/me')
      setAuth(userResponse.data, access_token)

      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-discord-darkest">
      <div className="w-full max-w-md p-8 bg-discord-dark rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-white mb-6 text-center">Create an account</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-500/20 border border-red-500 rounded text-red-400 text-sm">
              {error}
            </div>
          )}
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-discord-textMuted mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 bg-discord-darker border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
            />
          </div>
          
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-discord-textMuted mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-2 bg-discord-darker border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
            />
          </div>
          
          <div>
            <label htmlFor="displayName" className="block text-sm font-medium text-discord-textMuted mb-2">
              Display Name (optional)
            </label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
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
              minLength={6}
              className="w-full px-4 py-2 bg-discord-darker border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-discord-primary hover:bg-discord-primaryHover text-white font-medium rounded transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        
        <p className="mt-4 text-center text-discord-textMuted text-sm">
          Already have an account?{' '}
          <Link to="/login" className="text-discord-primary hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}



