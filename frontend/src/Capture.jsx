import { useEffect, useState } from 'react'
import { submitObservation, clarify, getProtocol } from './api'
import Specimen from './Specimens'

// Context questions only. The indicator list is NOT hardcoded here -- it comes from
// /api/protocol, served from the backend's field_protocol module, so ecological
// content has exactly one home (AUDIT.md D-021).
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

const Kicker = ({ children, tone = 'muted' }) => (
  <div className={`text-[12px] font-bold uppercase tracking-[0.18em] ${
    tone === 'alarm' ? 'text-alarm' : 'text-faint'}`}>{children}</div>
)

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
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-[28px] leading-[30px] font-bold text-pretty">
          Report a stream
        </h2>
        <p className="mt-2 text-[15px] leading-[21px] text-muted text-pretty">
          Answer what you can see. <strong className="font-semibold text-ink">“Not
          sure” is always a valid answer</strong> — it is more useful to us than a guess.
        </p>
      </div>

      <Field label="Which stream or reach is this?">
        <input value={siteName} onChange={e => setSiteName(e.target.value)}
          placeholder="e.g. Mondego tributary, by the footbridge"
          className="w-full border border-rule bg-surface px-3 py-2.5 text-[15px]
                     placeholder:text-faint" />
      </Field>

      <Field label="Photo of the stream">
        <input type="file" accept="image/*" capture="environment"
          onChange={e => {
            const f = e.target.files?.[0] || null
            setPhoto(f); setPreview(f ? URL.createObjectURL(f) : null)
          }}
          className="block w-full text-[14px] file:mr-3 file:border-0 file:bg-ink
                     file:px-4 file:py-2.5 file:text-[13px] file:font-semibold
                     file:uppercase file:tracking-[0.1em] file:text-ground" />
        {preview && <img src={preview} alt="The stream you photographed"
          className="mt-3 max-h-60 border border-rule" />}
      </Field>

      {CONTEXT.map(q => (
        <Field key={q.id} label={q.label}>
          <Choices name={q.id} value={answers[q.id]} onChange={v => set(q.id, v)}
            options={[...q.options, ['unsure', 'Not sure']]} />
        </Field>
      ))}

      <Field label="Did you notice any of these?">
        <p className="mb-2.5 text-[13.5px] leading-[19px] text-muted">
          Tick any that apply. Ticking none is a real answer — it means you looked.
        </p>
        <div className="flex flex-wrap gap-2">
          {(protocol?.indicators || []).map(ind => {
            const on = answers.indicators.includes(ind.key)
            return (
              <button key={ind.key} type="button" aria-pressed={on}
                onClick={() => toggle(ind.key)}
                className={`min-h-11 border px-3 py-2 text-left text-[14px] leading-[19px]
                  ${on ? 'border-ink bg-ink text-ground font-medium'
                       : 'border-rule bg-surface text-ink hover:border-ink'}`}>
                {ind.label}
              </button>
            )
          })}
        </div>
        {protocol && <p className="mt-2.5 text-[12.5px] leading-[17px] text-faint">{protocol.note}</p>}
      </Field>

      <Field label="Anything else worth knowing?">
        <textarea rows={3} value={answers.wildlife_seen || ''}
          onChange={e => set('wildlife_seen', e.target.value)}
          placeholder="Wildlife you saw, or anything that struck you as unusual"
          className="w-full border border-rule bg-surface px-3 py-2.5 text-[15px]
                     placeholder:text-faint" />
      </Field>

      {error && <p role="alert" className="border-2 border-alarm bg-alarm-bg px-3 py-2.5
                                           text-[14px] text-alarm">{error}</p>}

      <button onClick={send} disabled={busy}
        className="w-full bg-ink px-4 py-3.5 text-[13px] font-bold uppercase
                   tracking-[0.16em] text-ground disabled:opacity-60">
        {busy ? 'Sending…' : 'Send observation'}
      </button>
    </div>
  )
}

function Submitted({ result, onDone }) {
  const [data, setData] = useState({ assessment: result.assessment })
  const [answered, setAnswered] = useState({})
  // Frozen at first render: answering a question correctly removes it from the
  // refreshed assessment, so re-deriving the list would delete the question and its
  // own answer from the screen.
  const [diffs] = useState(result.assessment.field_differentials || [])
  const tensions = result.assessment.detected_inconsistency || []
  const urgency = data.assessment.ecological_urgency

  async function answerDifferential(q, option) {
    const fresh = await clarify(result.id, {
      questionId: q.id, question: q.question, field: q.field,
      response: option.label, disagrees: false,
      indicator: q.indicator, optionKey: option.key,
    })
    const r = fresh.assessment.ecological_urgency.resolved?.[q.indicator]
    setAnswered(a => ({ ...a, [q.id]: {
      explain: r?.explain || 'Recorded.', urgency: r?.urgency, oneHealth: r?.one_health,
    } }))
    setData(fresh)
  }

  return (
    <div className="space-y-6">
      <div className="border-b-[3px] border-ink pb-3">
        <h2 className="font-display text-[26px] leading-[29px] font-bold">Recorded</h2>
        <p className="mt-1.5 text-[15px] leading-[21px] text-muted text-pretty">
          Sent for review by a person. Nothing here is decided automatically.
        </p>
      </div>

      {/* Model-unavailable state (AUDIT.md A4/D-013): degraded, never dropped. */}
      {result.notice && (
        <p role="status" className="border border-rule bg-surface px-3.5 py-3
                                    text-[14px] leading-[20px] text-muted text-pretty">
          {result.notice}
        </p>
      )}

      {diffs.length > 0 && (
        <section className="space-y-3">
          <div>
            <Kicker tone="alarm">While you're still there</Kicker>
            <h3 className="mt-1.5 font-display text-[22px] leading-[25px] font-bold text-pretty">
              One quick check
            </h3>
            <p className="mt-1.5 text-[14.5px] leading-[20px] text-muted text-pretty">
              These are the questions a river surveyor would ask on site. You can see
              what we can't, so you're the one who can answer them.
            </p>
          </div>
          {diffs.map(q => (
            <div key={q.id} className="border border-rule bg-surface p-4">
              <p className="text-[15px] leading-[21px] text-pretty">{q.question}</p>
              {answered[q.id] ? (
                <div className="mt-3 space-y-2">
                  <p className={`border-l-[3px] py-2 pl-3 text-[14px] leading-[20px] text-pretty
                    ${answered[q.id].urgency === 'high'
                      ? 'border-ochre bg-ochre-bg text-ink' : 'border-rule text-muted'}`}>
                    {answered[q.id].explain}
                  </p>
                  {answered[q.id].oneHealth && (
                    <p className="border-2 border-alarm bg-alarm-bg p-3 text-[15px]
                                  leading-[21px] text-pretty">
                      <span className="font-bold text-alarm">For you and anyone with you.</span>{' '}
                      {answered[q.id].oneHealth}
                    </p>
                  )}
                </div>
              ) : (
                <div className="mt-3 flex flex-col gap-2">
                  {q.options.map(o => (
                    <button key={o.key} onClick={() => answerDifferential(q, o)}
                      className="flex min-h-11 items-center gap-3 border border-rule
                                 bg-surface px-3 py-2.5 text-left hover:border-ink">
                      <Specimen differential={q.id} option={o.key} size={52}
                                alt={`Schematic drawing: ${o.label}`} />
                      <span className="text-[15px] leading-[20px]">{o.label}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          <p className="text-[12px] leading-[16px] text-faint">
            Drawings are schematic aids, not identification plates.
          </p>
        </section>
      )}

      {tensions.length > 0 && (
        <section className="space-y-3">
          <h3 className="font-display text-[20px] leading-[24px] font-bold">
            One thing we'd like to check
          </h3>
          <p className="text-[14px] leading-[20px] text-muted text-pretty">
            These are questions, not corrections. You were there and we weren't —
            keeping your original answer is a perfectly good response.
          </p>
          {tensions.map(t => <TensionCard key={t.id} id={result.id} tension={t} />)}
        </section>
      )}

      <section className="border-t-[3px] border-ink pt-3">
        <div className="flex items-baseline justify-between gap-3">
          <h3 className="font-display text-[19px] leading-[23px] font-bold text-pretty">
            {urgency.level === 'high' ? 'Worth a prompt look' : 'What happens next'}
          </h3>
          <span className="shrink-0 whitespace-nowrap text-[11.5px] font-bold uppercase
                           tracking-[0.16em] text-faint">Awaiting review</span>
        </div>
        <ul className="mt-2 space-y-1.5">
          {urgency.reasons.map((r, i) => (
            <li key={i} className="text-[14.5px] leading-[20px] text-muted text-pretty">{r}</li>
          ))}
        </ul>
      </section>

      <button onClick={onDone}
        className="w-full border-2 border-ink px-4 py-3 text-[13px] font-bold
                   uppercase tracking-[0.16em] text-ink">
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
    <div className="border border-rule bg-surface p-4">
      <p className="text-[15px] leading-[21px] text-pretty">{tension.question}</p>
      {state ? (
        <p className="mt-2.5 text-[14px] leading-[20px] text-muted text-pretty">
          {state === 'kept'
            ? 'Recorded — your original answer stands, and the reviewer will see you confirmed it.'
            : 'Recorded — your update sits alongside your original answer.'}
        </p>
      ) : (
        <div className="mt-3 flex flex-wrap gap-2">
          <button onClick={() => respond('Citizen updated their answer after review', false)}
            className="min-h-11 bg-ink px-3.5 py-2 text-[13px] font-semibold text-ground">
            Let me update that
          </button>
          <button onClick={() => respond('Citizen confirmed their original answer', true)}
            className="min-h-11 border-2 border-ink px-3.5 py-2 text-[13px] font-semibold text-ink">
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
      <legend className="text-[15px] font-semibold text-ink">{label}</legend>
      {children}
    </fieldset>
  )
}

function Choices({ name, value, onChange, options }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map(([v, l]) => (
        <label key={v}
          className={`min-h-11 cursor-pointer border px-3.5 py-2.5 text-[14px] leading-[19px]
            ${value === v ? 'border-ink bg-ink text-ground font-medium'
                          : 'border-rule bg-surface text-ink hover:border-ink'}
            ${v === 'unsure' ? 'italic' : ''}`}>
          <input type="radio" name={name} value={v} checked={value === v}
            onChange={() => onChange(v)} className="sr-only" />
          {l}
        </label>
      ))}
    </div>
  )
}
