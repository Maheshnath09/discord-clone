import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'

export default function ProfilePage() {
  const { user, setAuth, accessToken } = useAuthStore()
  const [displayName, setDisplayName] = useState('')
  const [bio, setBio] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (user) {
      setDisplayName(user.display_name || '')
      setBio(user.bio || '')
    }
  }, [user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const response = await api.patch('/users/me', {
        display_name: displayName || null,
        bio: bio || null,
      })
      setAuth(response.data, accessToken!)
      setSuccess('Profile updated successfully')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/users/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setAuth(response.data, accessToken!)
      setSuccess('Avatar updated successfully')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload avatar')
    }
  }

  if (!user) {
    return <div className="p-6 text-discord-textMuted">Loading...</div>
  }

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin bg-discord-dark p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">Profile Settings</h1>

        {error && (
          <div className="p-3 bg-red-500/20 border border-red-500 rounded text-red-400 text-sm mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="p-3 bg-green-500/20 border border-green-500 rounded text-green-400 text-sm mb-4">
            {success}
          </div>
        )}

        <div className="bg-discord-darker rounded-lg p-6 space-y-6">
          {/* Avatar */}
          <div>
            <label className="block text-sm font-medium text-discord-textMuted mb-2">
              Avatar
            </label>
            <div className="flex items-center space-x-4">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.username}
                  className="w-20 h-20 rounded-full"
                />
              ) : (
                <div className="w-20 h-20 rounded-full bg-discord-primary flex items-center justify-center text-white text-2xl font-semibold">
                  {user.username.charAt(0).toUpperCase()}
                </div>
              )}
              <div>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarUpload}
                  className="text-sm text-discord-text"
                />
                <p className="text-xs text-discord-textMuted mt-1">
                  JPG, PNG or GIF. Max size 10MB.
                </p>
              </div>
            </div>
          </div>

          {/* Profile form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-discord-textMuted mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={user.username}
                disabled
                className="w-full px-4 py-2 bg-discord-dark border border-discord-light rounded text-discord-textMuted cursor-not-allowed"
              />
              <p className="text-xs text-discord-textMuted mt-1">Username cannot be changed</p>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-discord-textMuted mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={user.email}
                disabled
                className="w-full px-4 py-2 bg-discord-dark border border-discord-light rounded text-discord-textMuted cursor-not-allowed"
              />
            </div>

            <div>
              <label htmlFor="displayName" className="block text-sm font-medium text-discord-textMuted mb-2">
                Display Name
              </label>
              <input
                id="displayName"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full px-4 py-2 bg-discord-dark border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary"
              />
            </div>

            <div>
              <label htmlFor="bio" className="block text-sm font-medium text-discord-textMuted mb-2">
                Bio
              </label>
              <textarea
                id="bio"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 bg-discord-dark border border-discord-light rounded text-white focus:outline-none focus:ring-2 focus:ring-discord-primary resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-discord-primary hover:bg-discord-primaryHover text-white rounded transition-colors disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}



