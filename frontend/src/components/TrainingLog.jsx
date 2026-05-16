import { useState } from 'react'

export default function TrainingLog() {
  const [rows, setRows] = useState([
    { week: 1, mileage: '', long_run: '', key_workout: '' },
  ])

  function addRow() {
    setRows(r => [...r, { week: r.length + 1, mileage: '', long_run: '', key_workout: '' }])
  }

  function updateRow(i, field, value) {
    setRows(r => r.map((row, idx) => idx === i ? { ...row, [field]: value } : row))
  }

  function deleteRow(i) {
    setRows(r => r.filter((_, idx) => idx !== i).map((row, idx) => ({ ...row, week: idx + 1 })))
  }

  const totalMileage = rows.reduce((sum, r) => sum + (parseFloat(r.mileage) || 0), 0)

  const inputClass = 'w-full bg-[#0f172a] border border-slate-700 rounded px-2 py-1.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-orange-500 transition-colors'

  return (
    <div className="bg-[#1e293b] rounded-2xl p-6 shadow-xl border border-slate-700">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white">📋 Training Log</h2>
          <p className="text-slate-400 text-sm">Track your weekly training leading up to race day</p>
        </div>
        <div className="text-right">
          <div className="text-orange-400 font-bold text-xl">{totalMileage.toFixed(1)}</div>
          <div className="text-slate-500 text-xs">total miles logged</div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-400 text-left border-b border-slate-700">
              <th className="pb-3 pr-2 font-medium w-16">Week</th>
              <th className="pb-3 pr-2 font-medium">Weekly Miles</th>
              <th className="pb-3 pr-2 font-medium">Long Run</th>
              <th className="pb-3 pr-2 font-medium">Key Workout</th>
              <th className="pb-3 w-8" />
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="border-b border-slate-700/40">
                <td className="py-2 pr-2">
                  <span className="text-slate-400 font-mono text-xs">W{row.week}</span>
                </td>
                <td className="py-2 pr-2">
                  <input
                    type="number" min="0" max="150" placeholder="e.g. 40"
                    className={inputClass}
                    value={row.mileage}
                    onChange={e => updateRow(i, 'mileage', e.target.value)}
                  />
                </td>
                <td className="py-2 pr-2">
                  <input
                    type="number" min="0" max="30" placeholder="e.g. 18"
                    className={inputClass}
                    value={row.long_run}
                    onChange={e => updateRow(i, 'long_run', e.target.value)}
                  />
                </td>
                <td className="py-2 pr-2">
                  <input
                    type="text" placeholder="e.g. 8×800m @ 5K pace"
                    className={inputClass}
                    value={row.key_workout}
                    onChange={e => updateRow(i, 'key_workout', e.target.value)}
                  />
                </td>
                <td className="py-2">
                  <button
                    onClick={() => deleteRow(i)}
                    className="text-slate-600 hover:text-red-400 transition-colors text-lg leading-none"
                    title="Delete row"
                  >
                    ×
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        onClick={addRow}
        className="mt-4 w-full py-2 border border-dashed border-slate-600 rounded-xl text-slate-400 hover:text-white hover:border-orange-500 text-sm transition-colors"
      >
        + Add Week
      </button>

      <p className="mt-4 text-xs text-slate-600 text-center">Data is stored locally in your browser session.</p>
    </div>
  )
}
