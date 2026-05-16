import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function AuthForm({ onAuth, onForgotPassword }) {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    const endpoint = mode === 'login' ? '/auth/login' : '/auth/register'
    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Something went wrong')
      localStorage.setItem('marathon_token', data.token)
      localStorage.setItem('marathon_email', data.email)
      onAuth(data.token, data.email)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const inputClass = 'w-full bg-[#0f172a] border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-orange-500 transition-colors'

  return (
    <div className="min-h-screen bg-[#0f172a] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-5xl">🏃</span>
          <h1 className="text-2xl font-bold text-white mt-3">Marathon Time Predictor</h1>
          <p className="text-slate-400 text-sm mt-1">ML-powered finish time forecasting</p>
        </div>

        <div className="bg-[#1e293b] rounded-2xl p-8 border border-slate-700 shadow-xl">
          <div className="flex rounded-lg overflow-hidden border border-slate-700 mb-6">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'login' ? 'bg-orange-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Log In
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'register' ? 'bg-orange-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Email</label>
              <input
                type="email" required placeholder="you@example.com"
                className={inputClass}
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Password</label>
              <input
                type="password" required placeholder={mode === 'register' ? 'At least 8 characters' : '••••••••'}
                className={inputClass}
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
            </div>

            {error && (
              <div className="bg-red-900/40 border border-red-700 rounded-lg p-3 text-red-300 text-sm">
                ⚠️ {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-colors"
            >
              {loading ? '...' : mode === 'login' ? 'Log In' : 'Create Account'}
            </button>

            {mode === 'login' && (
              <button type="button" onClick={onForgotPassword}
                className="w-full text-slate-500 hover:text-slate-300 text-sm transition-colors text-center">
                Forgot your password?
              </button>
            )}
          </form>
        </div>

        <p className="text-center text-slate-600 text-xs mt-4">
          Your training data is saved securely to your account.
        </p>
      </div>
    </div>
  )
}
