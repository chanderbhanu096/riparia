import { useEffect, useRef, useState } from 'react'
import { submitObservation, clarify, getProtocol } from './api'
import Specimen, { IndicatorMark } from './Specimens'

// Context questions only. The indicator list comes from /api/protocol, served from
// the backend's field_protocol module, so ecological content has one home (D-021).
const CONTEXT = [
  { id: 'water_clarity', label: 'How clear is the water?',
    options: [['clear', 'Clear'], ['slightly_cloudy', 'Slightly cloudy'],
              ['cloudy', 'Cloudy'], ['very_turbid', 'Very murky']] },
  { id: 'flow', label: 'How fast is it flowing?',
    options: [['none', 'Still'], ['low', 'Slow'], ['moderate', 'Steady'], ['high', 'Fast']] },
  { id: 'surrounding_land_use', label: "What's around the stream?",
    options: [['park', 'Park or green space'], ['residential', 'Houses'],
              ['industrial', 'Industrial'], ['agricultural', 'Farmland'], ['mixed', 'A mix']] },
]
const CONTEXT_BY_ID = Object.fromEntries(CONTEXT.map(q => [q.id, q]))

const R = 'rounded-[6px]'          // controls only -- never rows, rules or panels
const CTRL = `${R} border border-edge bg-surface`

// A failure to reach the server is not a safety warning. Red is reserved for the
// citizen precaution (index.css, AUDIT.md D-028), so errors are ink with a retry.
function Problem({ children, onRetry }) {
  return (
    <div role="alert" className={`${R} border-2 border-ink bg-surface p-3.5`}>
      <p className="question">Could not save that</p>
      <p className="body-2 mt-1 text-muted text-pretty">{children}</p>
      {onRetry && (
        <button onClick={onRetry} className={`action mt-2.5 ${R} bg-ink px-4 py-2 text-ground`}>
          Try again
        </button>
      )}
    </div>
  )
}

export default function Capture({ onDone }) {
  const [protocol, setProtocol] = useState(null)
  const [protocolError, setProtocolError] = useState(null)
  const [answers, setAnswers] = useState({ indicators: [] })
  const [photo, setPhoto] = useState(null)
  const [preview, setPreview] = useState(null)
  const [siteName, setSiteName] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const loadProtocol = () =>
    getProtocol().then(p => { setProtocol(p); setProtocolError(null) })
                 .catch(e => setProtocolError(e.message))
  useEffect(() => { loadProtocol() }, [])

  const set = (k, v) => setAnswers(a => ({ ...a, [k]: v }))
  const toggle = v => setAnswers(a => ({
    ...a,
    indicators: a.indicators.includes(v)
      ? a.indicators.filter(x => x !== v) : [...a.indicators, v],
  }))

  async function send() {
    setBusy(true); setError(null)
    try {
      setResult(await submitObservation({
        answers, recordClass: 'authentic', siteName: siteName || 'Unnamed reach', photo,
      }))
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  if (result) return <Submitted result={result} onDone={onDone} />

  return (
    <div className="space-y-9">
      <div>
        <div className="meta meta-stage text-faint">Step one</div>
        <h2 className="display-1 mt-2 text-pretty">Report a stream</h2>
        <p className="measure body-1 mt-3 text-muted text-pretty">
          Answer what you can see. <strong className="font-semibold text-ink">“Not
          sure” is always a valid answer</strong> — it is more useful to us than a guess.
        </p>
      </div>

      <Field label="Which stream or reach is this?" htmlFor="site">
        <input id="site" value={siteName} onChange={e => setSiteName(e.target.value)}
          placeholder="e.g. Mondego tributary, by the footbridge"
          className={`${CTRL} body-1 w-full px-4 py-3 placeholder:text-faint focus:border-ink`} />
      </Field>

      <Field label="Photo of the stream" htmlFor="photo">
        <input id="photo" type="file" accept="image/*" capture="environment"
          onChange={e => {
            const f = e.target.files?.[0] || null
            setPhoto(f); setPreview(f ? URL.createObjectURL(f) : null)
          }}
          className={`body-2 block w-full file:mr-3 file:${R} file:border-0 file:bg-ink
                      file:px-4 file:py-3 file:text-[15px] file:font-semibold file:text-ground`} />
        {preview && <img src={preview} alt="The stream you photographed"
          className="mt-3 max-h-60 border border-rule" />}
      </Field>

      {CONTEXT.map(q => (
        <Field key={q.id} label={q.label}>
          <Choices name={q.id} value={answers[q.id]} onChange={v => set(q.id, v)}
            options={[...q.options, ['unsure', 'Not sure']]} />
        </Field>
      ))}

      <fieldset>
        <legend className="heading-2 text-pretty">Did you notice any of these?</legend>
        <p className="measure body-1 mt-2 text-muted text-pretty">
          Tick any that apply. Ticking none is a real answer — it means you looked.
        </p>

        {protocolError && (
          <div className="mt-4">
            <Problem onRetry={loadProtocol}>
              The list of things to look for could not be loaded, so it is not shown.
              You can still send what you have.
            </Problem>
          </div>
        )}
        {!protocol && !protocolError && (
          <p role="status" className="body-2 mt-4 text-muted">Loading the checklist…</p>
        )}

        <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {(protocol?.indicators || []).map(ind => {
            const on = answers.indicators.includes(ind.key)
            return (
              <button key={ind.key} type="button" aria-pressed={on}
                onClick={() => toggle(ind.key)}
                className={`lift ${R} flex min-h-[64px] items-center gap-3.5 border px-3.5 py-3
                            text-left ${on
                    ? 'border-ink bg-ink text-ground'
                    : 'border-edge bg-surface text-ink hover:border-ink'}`}>
                <span className={on ? 'text-ground' : 'text-muted'}>
                  <IndicatorMark indicator={ind.key} size={38} />
                </span>
                <span className="body-1 font-medium">{ind.label}</span>
                {/* a cue that survives forced colours and greyscale, not colour alone */}
                <span aria-hidden="true"
                      className={`meta ml-auto shrink-0 ${on ? 'text-ground' : 'invisible'}`}>✓</span>
              </button>
            )
          })}
        </div>
        {protocol && (
          <p className="measure body-2 mt-3 text-faint text-pretty">{protocol.note}</p>
        )}
      </fieldset>

      <Field label="Anything else worth knowing?" htmlFor="notes">
        <textarea id="notes" rows={3} value={answers.wildlife_seen || ''}
          onChange={e => set('wildlife_seen', e.target.value)}
          placeholder="Wildlife you saw, or anything that struck you as unusual"
          className={`${CTRL} body-1 w-full px-4 py-3 placeholder:text-faint focus:border-ink`} />
      </Field>

      {error && <Problem onRetry={send}>{error}</Problem>}

      <button onClick={send} disabled={busy}
        className={`lift ${R} action w-full bg-ink px-4 py-4 text-ground disabled:opacity-60`}>
        {busy ? 'Sending…' : 'Send observation'}
      </button>
    </div>
  )
}

function Submitted({ result, onDone }) {
  const [data, setData] = useState({ assessment: result.assessment })
  const [answered, setAnswered] = useState({})
  // Frozen at first render: answering a question removes it from the refreshed
  // assessment, so re-deriving would delete the question and its own answer.
  const [diffs] = useState(result.assessment.field_differentials || [])
  const tensions = result.assessment.detected_inconsistency || []
  const urgency = data.assessment.ecological_urgency
  const heading = useRef(null)

  // Move focus to the new heading so a keyboard or screen-reader user is not left
  // at the top of a page that has entirely changed (UX_REVIEW_GPT.md F6).
  useEffect(() => { heading.current?.focus() }, [])

  const n = diffs.length
  const checkTitle = n === 1 ? 'One quick check' : `${n} quick checks`

  return (
    <div className="space-y-8">
      <div className="border-b-[3px] border-ink pb-3">
        <h2 ref={heading} tabIndex={-1} className="display-1 outline-none">Recorded</h2>
        <p className="measure body-1 mt-2 text-muted text-pretty">
          Sent for review by a person. Nothing here is decided automatically.
        </p>
      </div>

      {/* Model-unavailable state (AUDIT.md A4/D-013): degraded, never dropped. */}
      {result.notice && (
        <p role="status" className="measure body-2 border border-rule bg-surface px-3.5 py-3
                                    text-muted text-pretty">
          {result.notice}
        </p>
      )}

      {n > 0 && (
        <section className="space-y-3">
          <div>
            {/* ink, not red: this is a prompt, not a safety warning (F7) */}
            <div className="meta meta-stage text-faint">While you're still there</div>
            <h3 className="heading-2 mt-1.5 text-pretty">{checkTitle}</h3>
            <p className="measure body-1 mt-1.5 text-muted text-pretty">
              These are the questions a river surveyor would ask on site. You can see
              what we can't, so you're the one who can answer them.
            </p>
          </div>
          {diffs.map(q => (
            <Differential key={q.id} q={q} id={result.id}
              done={answered[q.id]}
              onDone={(info, fresh) => { setAnswered(a => ({ ...a, [q.id]: info })); setData(fresh) }} />
          ))}
          <p className="body-2 text-faint">
            Drawings are schematic aids, not identification plates.
          </p>
        </section>
      )}

      {tensions.length > 0 && (
        <section className="space-y-3">
          <h3 className="heading-2">One thing we'd like to check</h3>
          <p className="measure body-1 text-muted text-pretty">
            These are questions, not corrections. You were there and we weren't —
            keeping your original answer is a perfectly good response.
          </p>
          {tensions.map(t => <TensionCard key={t.id} id={result.id} tension={t} />)}
        </section>
      )}

      <section className="border-t-[3px] border-ink pt-3">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <h3 className="heading-2 text-pretty">
            {urgency.level === 'high' ? 'Worth a prompt look' : 'What happens next'}
          </h3>
          <span className="meta meta-stage shrink-0 text-faint">Awaiting human review</span>
        </div>
        <ul className="measure mt-2 space-y-1.5">
          {urgency.reasons.map((r, i) => (
            <li key={i} className="body-1 text-muted text-pretty">{r}</li>
          ))}
        </ul>
      </section>

      <button onClick={onDone}
        className={`lift ${R} action w-full border-2 border-ink px-4 py-3.5 text-ink`}>
        Report another stream
      </button>
    </div>
  )
}

function Differential({ q, id, done, onDone }) {
  const [saving, setSaving] = useState(null)
  const [error, setError] = useState(null)

  async function pick(option) {
    if (saving) return                       // no double submits on a flaky connection
    setSaving(option.key); setError(null)
    try {
      const fresh = await clarify(id, {
        questionId: q.id, question: q.question, field: q.field,
        response: option.label, disagrees: false,
        indicator: q.indicator, optionKey: option.key,
      })
      const r = fresh.assessment.ecological_urgency.resolved?.[q.indicator]
      onDone({ explain: r?.explain || 'Recorded.', urgency: r?.urgency,
               oneHealth: r?.one_health }, fresh)
    } catch (e) { setError(e.message) } finally { setSaving(null) }
  }

  return (
    <div className="border border-rule bg-surface p-4">
      <p className="question text-pretty">{q.question}</p>
      {done ? (
        <div className="mt-3 space-y-2" role="status">
          <p className={`body-1 border-l-[3px] py-2 pl-3 text-pretty ${
            done.urgency === 'high' ? 'border-ochre bg-ochre-bg text-ink'
                                    : 'border-rule text-muted'}`}>
            {done.explain}
          </p>
          {done.oneHealth && (
            <p className="body-1 border-2 border-alarm bg-alarm-bg p-3 text-pretty">
              <span className="font-bold text-alarm">For you and anyone with you.</span>{' '}
              {done.oneHealth}
            </p>
          )}
        </div>
      ) : (
        <div className="mt-3 flex flex-col gap-2">
          {q.options.map(o => (
            <button key={o.key} onClick={() => pick(o)} disabled={Boolean(saving)}
              className={`lift ${R} flex min-h-11 items-center gap-3 border border-edge
                          bg-surface px-3 py-2.5 text-left hover:border-ink
                          disabled:opacity-60`}>
              <Specimen differential={q.id} option={o.key} size={52} />
              <span className="body-1">{o.label}</span>
              {saving === o.key && <span className="meta ml-auto text-faint">Saving…</span>}
            </button>
          ))}
          {error && <Problem onRetry={() => setError(null)}>{error}</Problem>}
        </div>
      )}
    </div>
  )
}

// A question about something the citizen already answered. "Let me update that" must
// actually COLLECT a new answer -- an earlier version stored the sentence "Citizen
// updated their answer after review" and told them their update had been saved, when
// nothing had been. A correction containing no correction is worse than no
// correction at all (UX_REVIEW_GPT.md F3).
function TensionCard({ id, tension }) {
  const [state, setState] = useState('idle')   // idle | editing | saving | kept | updated
  const [saved, setSaved] = useState('')
  const [text, setText] = useState('')
  const [error, setError] = useState(null)
  const field = CONTEXT_BY_ID[tension.field]

  async function send(response, disagrees) {
    if (state === 'saving') return
    setState('saving'); setError(null)
    try {
      await clarify(id, {
        questionId: tension.id, question: tension.question, field: tension.field,
        response, disagrees,
      })
      setSaved(response)
      setState(disagrees ? 'kept' : 'updated')
    } catch (e) { setError(e.message); setState('editing') }
  }

  if (state === 'kept' || state === 'updated') {
    return (
      <div className="border border-rule bg-surface p-4" role="status">
        <p className="question text-pretty">{tension.question}</p>
        <p className="body-1 mt-2 text-muted text-pretty">
          {state === 'kept'
            ? 'Recorded — your original answer stands, and the reviewer will see you confirmed it.'
            : 'Recorded, alongside your original answer:'}
        </p>
        {state === 'updated' && (
          <p className="body-1 mt-1 font-semibold text-pretty">“{saved}”</p>
        )}
      </div>
    )
  }

  return (
    <div className="border border-rule bg-surface p-4">
      <p className="question text-pretty">{tension.question}</p>

      {state === 'idle' ? (
        <div className="mt-3 flex flex-wrap gap-2">
          <button onClick={() => setState('editing')}
            className={`lift ${R} action min-h-11 bg-ink px-4 py-2.5 text-ground`}>
            Let me update that
          </button>
          <button onClick={() => send('Citizen confirmed their original answer', true)}
            className={`lift ${R} action min-h-11 border-2 border-ink px-4 py-2.5 text-ink`}>
            I'll keep my answer
          </button>
        </div>
      ) : (
        <div className="mt-3 space-y-2">
          <p className="meta meta-stage text-faint">Your new answer</p>
          {field ? (
            <div className="flex flex-wrap gap-2">
              {[...field.options, ['unsure', 'Not sure']].map(([v, l]) => (
                <button key={v} onClick={() => send(l, false)} disabled={state === 'saving'}
                  className={`lift ${R} body-1 min-h-11 border border-edge bg-surface px-4
                              py-2.5 hover:border-ink disabled:opacity-60`}>
                  {l}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap items-start gap-2">
              <input value={text} onChange={e => setText(e.target.value)}
                placeholder="What should it say instead?"
                className={`${CTRL} body-1 min-w-0 flex-1 px-4 py-2.5 placeholder:text-faint
                            focus:border-ink`} />
              <button onClick={() => send(text.trim(), false)}
                disabled={!text.trim() || state === 'saving'}
                className={`lift ${R} action min-h-11 bg-ink px-4 py-2.5 text-ground
                            disabled:opacity-60`}>
                {state === 'saving' ? 'Saving…' : 'Save'}
              </button>
            </div>
          )}
          {error && <Problem>{error}</Problem>}
          <button onClick={() => setState('idle')} className="body-2 text-muted underline">
            Cancel
          </button>
        </div>
      )}
    </div>
  )
}

function Field({ label, htmlFor, children }) {
  return (
    <fieldset className="space-y-2.5">
      <legend className="meta meta-stage text-faint">
        {htmlFor ? <label htmlFor={htmlFor}>{label}</label> : label}
      </legend>
      {children}
    </fieldset>
  )
}

function Choices({ name, value, onChange, options }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map(([v, l]) => (
        <label key={v}
          className={`chip lift ${R} body-1 min-h-11 cursor-pointer border px-4 py-2.5
            ${value === v ? 'border-ink bg-ink text-ground font-medium'
                          : 'border-edge bg-surface text-ink hover:border-ink'}
            ${v === 'unsure' ? 'italic' : ''}`}>
          <input type="radio" name={name} value={v} checked={value === v}
            onChange={() => onChange(v)} className="sr-only" />
          {l}
        </label>
      ))}
    </div>
  )
}
