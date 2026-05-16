import { useState } from 'react'
import RunnerForm from './components/RunnerForm'
import PredictionResult from './components/PredictionResult'
import TrainingLog from './components/TrainingLog'
import AuthForm from './components/AuthForm'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('marathon_token'))
  const [email, setEmail] = useState(() => localStorage.getItem('marathon_email') || '')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState('predict')

  function handleAuth(newToken, newEmail) {
    setToken(newToken)
    setEmail(newEmail)
  }

  function handleLogout() {
    localStorage.removeItem('marathon_token')
    localStorage.removeItem('marathon_email')
    setToken(null)
    setEmail('')
    setResult(null)
  }

  async function handleSubmit(formData) {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return <AuthForm onAuth={handleAuth} />
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-100">
      <header className="border-b border-slate-700 bg-[#0f172a] sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🏃</span>
            <div>
              <h1 className="text-xl font-bold text-white">Marathon Time Predictor</h1>
              <p className="text-xs text-slate-400">ML-powered finish time forecasting</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex gap-2">
              <button onClick={() => setTab('predict')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === 'predict' ? 'bg-orange-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}>
                Predict
              </button>
              <button onClick={() => setTab('log')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === 'log' ? 'bg-orange-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}>
                Training Log
              </button>
            </div>
            <div className="flex items-center gap-2 border-l border-slate-700 pl-3">
              <span className="text-slate-500 text-xs hidden sm:block">{email}</span>
              <button onClick={handleLogout}
                className="text-slate-400 hover:text-red-400 text-xs transition-colors">
                Log out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {tab === 'predict' ? (
          <div className="space-y-8">
            <RunnerForm onSubmit={handleSubmit} loading={loading} />
            {error && (
              <div className="bg-red-900/40 border border-red-700 rounded-xl p-4 text-red-300">
                ⚠️ {error}
              </div>
            )}
            {result && <PredictionResult result={result} />}
          </div>
        ) : (
          <TrainingLog token={token} />
        )}
      </main>
    </div>
  )
}
