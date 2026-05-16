import { useState } from 'react'

const STEPS = ['Demographics', 'Training Data', 'Race History']

function parsePRtoMinutes(str) {
  if (!str || str.trim() === '') return null
  const parts = str.trim().split(':').map(Number)
  if (parts.some(isNaN)) return null
  if (parts.length === 2) return parts[0] + parts[1] / 60
  if (parts.length === 3) return parts[0] * 60 + parts[1] + parts[2] / 60
  return null
}

export default function RunnerForm({ onSubmit, loading }) {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState({
    age: '',
    gender: 'M',
    weight_lbs: '',
    height_ft: '',
    height_in: '',
    weekly_mileage: '',
    long_run_miles: '',
    avg_pace_min: '',
    avg_pace_sec: '',
    runs_per_week: '',
    weeks_training: '',
    cross_training: false,
    cross_training_hours: '',
    first_marathon: false,
    previous_marathons: '',
    half_pr: '',
    ten_k_pr: '',
    five_k_pr: '',
  })

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }))

  function handleSubmit() {
    const pace = parseFloat(form.avg_pace_min) + parseFloat(form.avg_pace_sec || 0) / 60
    const height = parseFloat(form.height_ft || 0) * 12 + parseFloat(form.height_in || 0)
    const payload = {
      age: parseInt(form.age),
      gender: form.gender,
      weight_lbs: parseFloat(form.weight_lbs),
      height_inches: height,
      weekly_mileage: parseFloat(form.weekly_mileage),
      long_run_miles: parseFloat(form.long_run_miles),
      avg_pace_min_per_mile: pace,
      runs_per_week: parseInt(form.runs_per_week),
      weeks_training: parseInt(form.weeks_training),
      cross_training_hours: form.cross_training ? parseFloat(form.cross_training_hours || 0) : 0,
      first_marathon: form.first_marathon,
      previous_marathons: form.first_marathon ? 0 : parseInt(form.previous_marathons || 0),
      half_marathon_pr_minutes: parsePRtoMinutes(form.half_pr),
      ten_k_pr_minutes: parsePRtoMinutes(form.ten_k_pr),
      five_k_pr_minutes: parsePRtoMinutes(form.five_k_pr),
    }
    onSubmit(payload)
  }

  const inputClass = 'w-full bg-[#0f172a] border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-orange-500 transition-colors'
  const labelClass = 'block text-sm font-medium text-slate-300 mb-1'

  return (
    <div className="bg-[#1e293b] rounded-2xl p-6 shadow-xl">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          {STEPS.map((s, i) => (
            <div key={i} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                  i < step ? 'bg-orange-500 text-white' :
                  i === step ? 'bg-orange-500 text-white ring-4 ring-orange-500/30' :
                  'bg-slate-700 text-slate-400'
                }`}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span className={`text-xs mt-1 font-medium ${i === step ? 'text-orange-400' : 'text-slate-500'}`}>{s}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-2 mb-4 ${i < step ? 'bg-orange-500' : 'bg-slate-700'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step 1: Demographics */}
      {step === 0 && (
        <div className="space-y-4 fade-in">
          <h2 className="text-lg font-semibold text-white mb-4">Tell us about yourself</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Age</label>
              <input type="number" min="16" max="85" placeholder="35" className={inputClass}
                value={form.age} onChange={e => set('age', e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Gender</label>
              <select className={inputClass} value={form.gender} onChange={e => set('gender', e.target.value)}>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="NB">Non-binary</option>
              </select>
            </div>
          </div>
          <div>
            <label className={labelClass}>Weight (lbs)</label>
            <input type="number" min="80" max="350" placeholder="155" className={inputClass}
              value={form.weight_lbs} onChange={e => set('weight_lbs', e.target.value)} />
          </div>
          <div>
            <label className={labelClass}>Height</label>
            <div className="flex gap-2">
              <input type="number" min="4" max="7" placeholder="5 ft" className={inputClass}
                value={form.height_ft} onChange={e => set('height_ft', e.target.value)} />
              <input type="number" min="0" max="11" placeholder="10 in" className={inputClass}
                value={form.height_in} onChange={e => set('height_in', e.target.value)} />
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Training */}
      {step === 1 && (
        <div className="space-y-4 fade-in">
          <h2 className="text-lg font-semibold text-white mb-4">Your training data</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Weekly Mileage (avg last 12 weeks)</label>
              <input type="number" min="5" max="120" placeholder="35" className={inputClass}
                value={form.weekly_mileage} onChange={e => set('weekly_mileage', e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Longest Run (miles)</label>
              <input type="number" min="5" max="26.2" step="0.5" placeholder="20" className={inputClass}
                value={form.long_run_miles} onChange={e => set('long_run_miles', e.target.value)} />
            </div>
          </div>
          <div>
            <label className={labelClass}>Average Easy Run Pace (min:sec per mile)</label>
            <div className="flex gap-2 items-center">
              <input type="number" min="5" max="20" placeholder="9 min" className={inputClass}
                value={form.avg_pace_min} onChange={e => set('avg_pace_min', e.target.value)} />
              <span className="text-slate-400">:</span>
              <input type="number" min="0" max="59" placeholder="30 sec" className={inputClass}
                value={form.avg_pace_sec} onChange={e => set('avg_pace_sec', e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Runs Per Week</label>
              <input type="number" min="1" max="14" placeholder="5" className={inputClass}
                value={form.runs_per_week} onChange={e => set('runs_per_week', e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Weeks of Training</label>
              <input type="number" min="4" max="52" placeholder="16" className={inputClass}
                value={form.weeks_training} onChange={e => set('weeks_training', e.target.value)} />
            </div>
          </div>
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-orange-500"
                checked={form.cross_training} onChange={e => set('cross_training', e.target.checked)} />
              <span className="text-sm text-slate-300">I do cross training (cycling, swimming, etc.)</span>
            </label>
            {form.cross_training && (
              <div className="mt-2">
                <input type="number" min="0" max="20" placeholder="Hours per week" className={inputClass}
                  value={form.cross_training_hours} onChange={e => set('cross_training_hours', e.target.value)} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 3: Race History */}
      {step === 2 && (
        <div className="space-y-4 fade-in">
          <h2 className="text-lg font-semibold text-white mb-4">Race history</h2>
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-orange-500"
                checked={form.first_marathon} onChange={e => set('first_marathon', e.target.checked)} />
              <span className="text-sm text-slate-300">This will be my first marathon</span>
            </label>
          </div>
          {!form.first_marathon && (
            <div>
              <label className={labelClass}>Previous marathons completed</label>
              <input type="number" min="1" max="100" placeholder="2" className={inputClass}
                value={form.previous_marathons} onChange={e => set('previous_marathons', e.target.value)} />
            </div>
          )}
          <div className="pt-2">
            <p className="text-sm text-slate-400 mb-3">Personal records (optional — improves accuracy)</p>
            <div className="space-y-3">
              <div>
                <label className={labelClass}>Half Marathon PR (mm:ss)</label>
                <input type="text" placeholder="e.g. 1:55:00" className={inputClass}
                  value={form.half_pr} onChange={e => set('half_pr', e.target.value)} />
              </div>
              <div>
                <label className={labelClass}>10K PR (mm:ss)</label>
                <input type="text" placeholder="e.g. 52:30" className={inputClass}
                  value={form.ten_k_pr} onChange={e => set('ten_k_pr', e.target.value)} />
              </div>
              <div>
                <label className={labelClass}>5K PR (mm:ss)</label>
                <input type="text" placeholder="e.g. 24:15" className={inputClass}
                  value={form.five_k_pr} onChange={e => set('five_k_pr', e.target.value)} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between mt-8 pt-4 border-t border-slate-700">
        <button
          onClick={() => setStep(s => s - 1)}
          disabled={step === 0}
          className="px-5 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          ← Back
        </button>
        {step < 2 ? (
          <button
            onClick={() => setStep(s => s + 1)}
            className="px-6 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-sm font-bold transition-colors"
          >
            Next →
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-6 py-2 bg-orange-500 hover:bg-orange-600 disabled:opacity-60 text-white rounded-lg text-sm font-bold transition-colors"
          >
            {loading ? '⏳ Predicting...' : '🏁 Predict My Time'}
          </button>
        )}
      </div>
    </div>
  )
}
