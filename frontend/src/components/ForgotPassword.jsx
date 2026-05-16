import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ForgotPassword({ onBack }) {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      if (!res.ok) throw new Error('Something went wrong')
      setSent(true)
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
          <h1 className="text-2xl font-bold text-white mt-3">Forgot Password</h1>
          <p className="text-slate-400 text-sm mt-1">We'll send a reset link to your email</p>
        </div>

        <div className="bg-[#1e293b] rounded-2xl p-8 border border-slate-700 shadow-xl">
          {sent ? (
            <div className="text-center space-y-4">
              <div className="text-4xl">📬</div>
              <p className="text-white font-semibold">Check your inbox</p>
              <p className="text-slate-400 text-sm">
                If <span className="text-orange-400">{email}</span> is registered, you'll receive a reset link shortly. It expires in 1 hour.
              </p>
              <button onClick={onBack}
                className="mt-4 text-slate-400 hover:text-white text-sm transition-colors underline underline-offset-2">
                Back to login
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Email address</label>
                <input type="email" required placeholder="you@example.com"
                  className={inputClass}
                  value={email}
                  onChange={e => setEmail(e.target.value)} />
              </div>

              {error && (
                <div className="bg-red-900/40 border border-red-700 rounded-lg p-3 text-red-300 text-sm">
                  ⚠️ {error}
                </div>
              )}

              <button type="submit" disabled={loading}
                className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-colors">
                {loading ? 'Sending…' : 'Send Reset Link'}
              </button>

              <button type="button" onClick={onBack}
                className="w-full text-slate-400 hover:text-white text-sm transition-colors">
                ← Back to login
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
