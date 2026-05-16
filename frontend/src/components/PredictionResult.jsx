export default function PredictionResult({ result }) {
  const {
    predicted_time,
    pace_per_mile,
    confidence_low,
    confidence_high,
    vs_average,
    splits,
    top_features,
  } = result

  const isFaster = vs_average.includes('faster')
  const maxImportance = Math.max(...top_features.map(f => f.importance))

  return (
    <div className="space-y-6 fade-in">
      {/* Hero result */}
      <div className="bg-gradient-to-br from-[#1e3a5f] to-[#1e293b] rounded-2xl p-8 text-center shadow-xl border border-slate-700">
        <p className="text-slate-400 text-sm font-medium uppercase tracking-widest mb-2">Your Predicted Finish Time</p>
        <div className="text-6xl font-black text-white mb-2">{predicted_time}</div>
        <div className="text-orange-400 font-semibold text-lg">{pace_per_mile} /mile</div>
        <div className="mt-4 text-sm text-slate-400">
          Confidence range: <span className="text-slate-200">{confidence_low} – {confidence_high}</span>
        </div>
        <div className={`mt-3 inline-block px-4 py-1.5 rounded-full text-sm font-semibold ${
          isFaster ? 'bg-green-900/60 text-green-400 border border-green-700' : 'bg-yellow-900/60 text-yellow-400 border border-yellow-700'
        }`}>
          {isFaster ? '🚀' : '🐢'} {vs_average}
        </div>
      </div>

      {/* Grid: splits + features */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Splits */}
        <div className="bg-[#1e293b] rounded-2xl p-6 border border-slate-700">
          <h3 className="text-white font-bold mb-4">📍 Pacing Plan</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 text-left">
                <th className="pb-2 font-medium">Checkpoint</th>
                <th className="pb-2 font-medium text-right">Elapsed Time</th>
              </tr>
            </thead>
            <tbody>
              {splits.map((s, i) => (
                <tr key={i} className={`border-t border-slate-700/50 ${s.label === 'Half' ? 'text-orange-400 font-semibold' : s.label === 'Finish' ? 'text-green-400 font-bold' : 'text-slate-300'}`}>
                  <td className="py-2">{s.label}</td>
                  <td className="py-2 text-right font-mono">{s.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Feature importance */}
        <div className="bg-[#1e293b] rounded-2xl p-6 border border-slate-700">
          <h3 className="text-white font-bold mb-4">🔍 Key Factors</h3>
          <p className="text-slate-400 text-xs mb-4">What influenced your prediction most</p>
          <div className="space-y-3">
            {top_features.map((f, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-300">{f.name}</span>
                  <span className="text-orange-400 font-mono text-xs">{f.importance.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-orange-500 to-orange-400 rounded-full transition-all duration-700"
                    style={{ width: `${(f.importance / maxImportance) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="text-center text-slate-500 text-sm">
        Want to improve your time? Log your training weeks in the <span className="text-orange-400">Training Log</span> tab.
      </div>
    </div>
  )
}
