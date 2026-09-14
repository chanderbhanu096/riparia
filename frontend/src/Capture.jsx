import { useEffect, useState } from 'react'
import { submitObservation, clarify, getProtocol, getObservation } from './api'

// Context questions only. The indicator list is NOT hardcoded here -- it comes
// from /api/protocol, which is served from the backend's field_protocol module.
// Domain content has exactly one home, and this component holds no ecological
// knowledge of its own (AUDIT.md D-021).
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

export default function Capture({ onDone }) {
  const [protocol, setProtocol] = useState(null)
  const [answers, setAnswers] = useState({ indicators: [] })
  const [photo, setPhoto] = useState(null)
  const [preview, setPreview] = useState(null)
  const [siteName, setSiteName] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => { getProtocol().then(setProtocol).catch(e => setError(e.message)) }, [])

  const set = (k, v) => setAnswers(a => ({ ...a, [k]: v }))
  const toggle = (v) => setAnswers(a => ({
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
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-stream-900">Report a stream</h2>
        <p className="text-stream-700 mt-1">
          Answer what you can see. <strong>“Not sure” is always a valid answer</strong> —
          it is more useful to us than a guess.
        </p>
      </header>

      <Field label="Which stream or reach is this?">
        <input value={siteName} onChange={e => setSiteName(e.target.value)}
          placeholder="e.g. Mondego tributary, by the footbridge"
          className="w-full rounded-lg border border-stream-300 px-3 py-2" />
      </Field>

      <Field label="Photo of the stream">
        <input type="file" accept="image/*" capture="environment"
          onChange={e => {
            const f = e.target.files?.[0] || null
            setPhoto(f); setPreview(f ? URL.createObjectURL(f) : null)
          }}
          className="block w-full text-sm file:mr-3 file:rounded-lg file:border-0
                     file:bg-stream-600 file:px-4 file:py-2 file:text-white" />
        {preview && <img src={preview} alt="The stream you photographed"
          className="mt-3 max-h-56 rounded-lg border border-stream-300" />}
      </Field>

      {CONTEXT.map(q => (
        <Field key={q.id} label={q.label}>
          <Choices name={q.id} value={answers[q.id]} onChange={v => set(q.id, v)}
            options={[...q.options, ['unsure', 'Not sure']]} />
        </Field>
      ))}

      <Field label="Did you notice any of these?">
        <p className="text-sm text-stream-700 mb-2">
          Tick any that apply. Ticking none is a real answer — it means you looked.
        </p>
        <div className="flex flex-wrap gap-2">
          {(protocol?.indicators || []).map(ind => {
            const on = answers.indicators.includes(ind.key)
            return (
              <button key={ind.key} type="button" aria-pressed={on}
                onClick={() => toggle(ind.key)}
                className={`rounded-full border px-3 py-1.5 text-sm text-left ${on
                  ? 'bg-stream-600 text-white border-stream-600'
                  : 'bg-white text-stream-900 border-stream-300'}`}>
                {ind.label}
              </button>
            )
          })}
        </div>
        {protocol && (
          <p className="mt-2 text-xs text-stream-700">{protocol.note}</p>
        )}
      </Field>

      <Field label="Anything else worth knowing?">
        <textarea rows={3} value={answers.wildlife_seen || ''}
          onChange={e => set('wildlife_seen', e.target.value)}
          placeholder="Wildlife you saw, or anything that struck you as unusual"
          className="w-full rounded-lg border border-stream-300 px-3 py-2" />
      </Field>

      {error && <p role="alert" className="text-red-700">{error}</p>}

      <button onClick={send} disabled={busy}
        className="w-full rounded-lg bg-stream-600 px-4 py-3 text-white font-medium
                   disabled:opacity-60">
        {busy ? 'Sending…' : 'Send observation'}
      </button>
    </div>
  )
}

function Submitted({ result, onDone }) {
  const [data, setData] = useState({ assessment: result.assessment })
  const [answered, setAnswered] = useState({})

  // Frozen at first render. Answering a question removes it from the refreshed
  // assessment (correctly -- it no longer needs asking), so re-deriving the list
  // from `data` would delete the question and its own answer from the screen.
  const [diffs] = useState(result.assessment.field_differentials || [])
  const tensions = result.assessment.detected_inconsistency || []

  async function answerDifferential(q, option) {
    const fresh = await clarify(result.id, {
      questionId: q.id, question: q.question, field: q.field,
      response: option.label, disagrees: false,
      indicator: q.indicator, optionKey: option.key,
    })
    // Read back the resolved reading so the citizen learns what their own
    // observation meant. The teaching moment is the point: this is the difference
    // between extracting data from people and building capability in them.
    const r = fresh.assessment.ecological_urgency.resolved?.[q.indicator]
    setAnswered(a => ({ ...a, [q.id]: {
      explain: r?.explain || 'Recorded.',
      urgency: r?.urgency,
      oneHealth: r?.one_health,
    } }))
    setData(fresh)
  }

  return (
    <div className="space-y-5">
      <div className="rounded-lg bg-stream-50 border border-stream-300 p-4">
        <h2 className="text-xl font-semibold text-stream-900">Thank you — it's recorded</h2>
        <p className="text-stream-700 mt-1">
          Your report has been sent for review by a person. Nothing about it is
          decided automatically.
        </p>
      </div>

      {/* Model-unavailable state (AUDIT.md A4 / D-013). The observation is kept in
          full and routed to a human; degraded, never dropped. */}
      {result.notice && (
        <p role="status"
           className="rounded-lg bg-amber-50 border border-amber-300 p-3 text-amber-900">
          {result.notice}
        </p>
      )}

      {diffs.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-lg font-semibold text-stream-900">
            While you're still there — one quick check
          </h3>
          <p className="text-stream-700 text-sm">
            These are the questions a river surveyor would ask on site. You can see
            what we can't, so you're the one who can answer them.
          </p>
          {diffs.map(q => (
            <div key={q.id} className="rounded-lg border border-stream-300 p-4">
              <p className="text-stream-900">{q.question}</p>
              {answered[q.id] ? (
                <div className="mt-3 space-y-2">
                  <p className={`rounded-lg border p-3 text-sm ${
                    answered[q.id].urgency === 'high'
                      ? 'bg-red-50 border-red-300 text-red-900'
                      : 'bg-stream-50 border-stream-300 text-stream-900'}`}>
                    {answered[q.id].explain}
                  </p>
                  {answered[q.id].oneHealth && (
                    <p className="rounded-lg bg-amber-50 border border-amber-300 p-3
                                  text-sm text-amber-900">
                      <strong>For you and anyone with you: </strong>
                      {answered[q.id].oneHealth}
                    </p>
                  )}
                </div>
              ) : (
                <div className="mt-3 flex flex-col gap-2">
                  {q.options.map(o => (
                    <button key={o.key} onClick={() => answerDifferential(q, o)}
                      className="rounded-lg border border-stream-600 px-3 py-2 text-sm
                                 text-left text-stream-700 hover:bg-stream-50">
                      {o.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </section>
      )}

      {tensions.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-lg font-semibold text-stream-900">
            One thing we'd like to check with you
          </h3>
          <p className="text-stream-700 text-sm">
            These are questions, not corrections. You were there and we weren't —
            keeping your original answer is a perfectly good response.
          </p>
          {tensions.map(t => (
            <TensionCard key={t.id} id={result.id} tension={t} />
          ))}
        </section>
      )}

      <button onClick={onDone}
        className="w-full rounded-lg border border-stream-600 px-4 py-3 text-stream-700">
        Report another stream
      </button>
    </div>
  )
}

function TensionCard({ id, tension }) {
  const [state, setState] = useState(null)
  async function respond(response, disagrees) {
    await clarify(id, {
      questionId: tension.id, question: tension.question, field: tension.field,
      response, disagrees,
    })
    setState(disagrees ? 'kept' : 'updated')
  }
  return (
    <div className="rounded-lg border border-stream-300 p-4">
      <p className="text-stream-900">{tension.question}</p>
      {state ? (
        <p className="mt-2 text-sm text-stream-600">
          {state === 'kept'
            ? '✓ Recorded — your original answer stands, and the reviewer will see you confirmed it.'
            : '✓ Recorded — your update sits alongside your original answer.'}
        </p>
      ) : (
        <div className="mt-3 flex flex-wrap gap-2">
          <button onClick={() => respond('Citizen updated their answer after review', false)}
            className="rounded-lg bg-stream-600 px-3 py-2 text-sm text-white">
            Let me update that
          </button>
          <button onClick={() => respond('Citizen confirmed their original answer', true)}
            className="rounded-lg border border-stream-600 px-3 py-2 text-sm text-stream-700">
            I'll keep my answer
          </button>
        </div>
      )}
    </div>
  )
}

function Field({ label, children }) {
  return (
    <fieldset className="space-y-2">
      <legend className="font-medium text-stream-900">{label}</legend>
      {children}
    </fieldset>
  )
}

function Choices({ name, value, onChange, options }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map(([v, l]) => (
        <label key={v}
          className={`cursor-pointer rounded-full border px-3 py-1.5 text-sm ${
            value === v ? 'bg-stream-600 text-white border-stream-600'
                        : 'bg-white text-stream-900 border-stream-300'} ${
            v === 'unsure' ? 'italic' : ''}`}>
          <input type="radio" name={name} value={v} checked={value === v}
            onChange={() => onChange(v)} className="sr-only" />
          {l}
        </label>
      ))}
    </div>
  )
}
