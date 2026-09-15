import { useState } from 'react'
import Capture from './Capture'
import Review from './Review'

// Broadsheet (AUDIT.md D-028): a field observation sheet. Bodoni for the masthead
// and one heavy rule beneath it -- and nowhere else. Everything a person actually
// reads is set in Archivo.
export default function App() {
  const [mode, setMode] = useState('citizen')
  const [key, setKey] = useState(0)

  return (
    <div className="min-h-screen bg-ground text-ink">
      <header className="mx-auto max-w-3xl px-5 pt-4">
        <div className="flex items-baseline justify-between gap-4 border-b-[3px] border-ink pb-2">
          <h1 className="font-display text-[25px] font-bold tracking-[0.02em] leading-none">
            RIPARIA
          </h1>
          <nav className="flex gap-4" aria-label="Switch role">
            {[['citizen', 'Report'], ['reviewer', 'Review']].map(([m, label]) => (
              <button key={m} onClick={() => setMode(m)} aria-current={mode === m}
                className={`text-[12px] font-bold uppercase tracking-[0.16em] pb-0.5
                  ${mode === m
                    ? 'text-ink border-b-2 border-ink'
                    : 'text-faint border-b-2 border-transparent hover:text-ink'}`}>
                {label}
              </button>
            ))}
          </nav>
        </div>
        <p className="py-1.5 text-[12.5px] text-muted border-b border-rule">
          AI asks the question. You answer it. A named reviewer decides.
        </p>
      </header>

      <main className="mx-auto max-w-3xl px-5 py-5">
        {mode === 'citizen'
          ? <Capture key={key} onDone={() => setKey(k => k + 1)} />
          : <Review />}
      </main>

      <footer className="mx-auto max-w-3xl px-5 pb-10 pt-2">
        <div className="border-t border-rule pt-3 text-[12px] leading-[17px] text-faint">
          Prototype for the OneAquaHealth IEEE Global Hackathon 2026, Track 3. Not
          affiliated with the OneAquaHealth consortium. Drawings are schematic aids
          shown beside the descriptions, not identification plates, and have not been
          validated against field examples. Records marked <em>simulated</em> are
          generated for demonstration and are not real observations.
        </div>
      </footer>
    </div>
  )
}
