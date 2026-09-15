import { useRef, useState } from 'react'
import Capture from './Capture'
import Review from './Review'
import Sites from './Sites'

const VIEWS = [['citizen', 'Report a stream'], ['reviewer', 'Review observations'], ['sites', 'One Health summary']]

export default function App() {
  const [mode, setMode] = useState('citizen')
  const [key, setKey] = useState(0)
  const [reviewVisited, setReviewVisited] = useState(false)
  const main = useRef(null)
  function newReport() {
    setKey(k => k + 1)
    requestAnimationFrame(() => { main.current?.focus(); window.scrollTo({ top: 0 }) })
  }
  function navigate(next) {
    if (next === 'reviewer') setReviewVisited(true)
    setMode(next)
    requestAnimationFrame(() => main.current?.focus())
  }
  return (
    <div className="app-shell">
      <a href="#main" className="skip-link">Skip to content</a>
      <header className="site-header page-gutter">
        <button className="brand" onClick={() => navigate('citizen')} aria-label="Riparia home">
          <svg viewBox="0 0 36 40" fill="none" aria-hidden="true"><path d="M6 2c25 10-18 21 9 36M18 2c25 10-18 21 9 36M30 2c25 10-18 21 9 36" stroke="currentColor" strokeWidth="2.5"/></svg>
          <span>RIPARIA<span className="brand-caption">THE CITIZEN FIELD STATION</span></span>
        </button>
        <nav className="main-nav" aria-label="Main navigation">
          {VIEWS.map(([m, label]) => (
            <button key={m} onClick={() => navigate(m)} aria-current={mode === m ? 'page' : undefined}
              className={mode === m ? 'nav-item active' : 'nav-item'}>{label}</button>
          ))}
        </nav>
        <span className="prototype-label"><span aria-hidden="true">◇</span> Research prototype</span>
      </header>
      <main id="main" ref={main} tabIndex={-1} className="page-gutter main-content">
        {/* Visiting another view must not discard a citizen's unfinished report. */}
        <div hidden={mode !== 'citizen'}><Capture active={mode === 'citizen'} key={key} onDone={newReport} /></div>
        {reviewVisited && <div hidden={mode !== 'reviewer'}><Review active={mode === 'reviewer'} onReport={() => navigate('citizen')} /></div>}
        {mode === 'sites' && <Sites onReview={() => navigate('reviewer')} />}
      </main>
      <footer className="site-footer page-gutter">
        <div className="footer-top"><span className="footer-wordmark">RIPARIA</span><span>For the water. For the life around it.</span></div>
        <div className="footer-bottom">
          <p>OneAquaHealth IEEE Global Hackathon 2026 · Track 3<br />Independent prototype; not affiliated with the OneAquaHealth consortium.</p>
          <p>Drawings are schematic aids, not identification plates. Practice reports are labelled simulated. Human review is always required.</p>
          <a href="https://github.com/chanderbhanu096/riparia" target="_blank" rel="noreferrer">Explore the project ↗</a>
        </div>
      </footer>
    </div>
  )
}
