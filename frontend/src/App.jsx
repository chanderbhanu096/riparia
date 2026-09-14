import { useState } from 'react'
import Capture from './Capture'
import Review from './Review'

// Two modes, one toggle. No router: there are two views and a detail pane, and
// react-router would be a dependency earning nothing. ponytail: add routing only
// if deep links to an observation are ever needed.
export default function App() {
  const [mode, setMode] = useState('citizen')
  const [key, setKey] = useState(0)

  return (
    <div className="min-h-screen bg-white text-stream-900">
      <header className="border-b border-stream-300 bg-stream-50">
        <div className="mx-auto max-w-3xl px-4 py-4">
          <div className="flex items-baseline justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-xl font-bold text-stream-900">RIPARIA</h1>
              <p className="text-sm text-stream-700">
                AI asks. The person answers. A reviewer decides.
              </p>
            </div>
            <nav className="flex gap-1 rounded-lg border border-stream-300 bg-white p-1"
                 aria-label="Switch role">
              {[['citizen', 'Report'], ['reviewer', 'Review']].map(([m, label]) => (
                <button key={m} onClick={() => setMode(m)} aria-current={mode === m}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium ${
                    mode === m ? 'bg-stream-600 text-white' : 'text-stream-700'}`}>
                  {label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-6">
        {mode === 'citizen'
          ? <Capture key={key} onDone={() => setKey(k => k + 1)} />
          : <Review />}
      </main>

      <footer className="mx-auto max-w-3xl px-4 py-8 text-xs text-stream-700">
        Prototype for the OneAquaHealth IEEE Global Hackathon 2026, Track 3.
        Not affiliated with the OneAquaHealth consortium. Records marked
        “simulated” are generated for demonstration and are not real observations.
      </footer>
    </div>
  )
}
