import { useEffect, useRef, useState } from 'react'
import { submitObservation, clarify, getProtocol, getObservation } from './api'
import Specimen, { IndicatorMark } from './Specimens'
import RiverScene from './RiverScene'

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
function Problem({ children, onRetry, title = 'Could not save that' }) {
  return (
    <div role="alert" className={`${R} border-2 border-ink bg-surface p-3.5`}>
      <p className="question">{title}</p>
      <p className="body-2 mt-1 text-muted text-pretty">{children}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className={`action mt-2.5 min-h-11 ${R} bg-ink px-4 py-2 text-ground`}>
          Try again
        </button>
      )}
    </div>
  )
}

export default function Capture({ onDone, active = true }) {
  const [protocol, setProtocol] = useState(null)
  const [protocolError, setProtocolError] = useState(null)
  const [answers, setAnswers] = useState({ indicators: [] })
  const [photo, setPhoto] = useState(null)
  const [preview, setPreview] = useState(null)
  const [siteName, setSiteName] = useState('')
  const [recordClass, setRecordClass] = useState('authentic')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const loadProtocol = () =>
    getProtocol().then(p => { setProtocol(p); setProtocolError(null) })
                 .catch(e => setProtocolError(e.message))
  useEffect(() => { loadProtocol() }, [])
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview) }, [preview])

  const set = (k, v) => setAnswers(a => ({ ...a, [k]: v }))
  const toggle = v => setAnswers(a => ({
    ...a,
    indicators: a.indicators.includes(v)
      ? a.indicators.filter(x => x !== v) : [...a.indicators, v],
  }))

  async function send() {
    if (busy) return
    setBusy(true); setError(null)
    // An empty checklist means the citizen looked and saw none. If the list never
    // loaded, record the field as missing instead of inventing that observation.
    const submittedAnswers = { ...answers }
    if (!protocol) delete submittedAnswers.indicators
    try {
      const saved = await submitObservation({
        answers: submittedAnswers, recordClass, siteName: siteName.trim() || 'Unnamed reach', photo,
      })
      setResult({ ...saved, submittedAnswers })
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  if (result) return <Submitted result={result} recordClass={recordClass} onDone={onDone} active={active}
    original={{ answers: result.observation?.answers || result.submittedAnswers,
      siteName: result.observation?.site_name || siteName.trim() || 'Unnamed reach', preview }} protocol={protocol} />

  return (
    <div className="capture-page space-y-6">
      <section className="capture-hero">
        <div className="hero-copy">
          <div className="meta meta-stage text-faint">Citizen field notes</div>
          <h2 className="hero-title display-1 mt-4">Notice something.<br /><em>Make it matter.</em></h2>
          <p className="measure body-1 mt-5 text-muted text-pretty">
            A closer look at your local stream can start with you. Record what you
            notice, answer a field question when needed, and leave the decision to a person.
          </p>
          <div className="hero-footnote meta mt-7 flex items-center gap-3 text-faint">
            <span className="h-px w-8 bg-edge" aria-hidden="true" />
            Urban streams. Shared health.
          </div>
        </div>
        <div className="hero-scene" aria-hidden="true"><RiverScene /></div>
      </section>

      <ol className="workflow-strip grid grid-cols-1 border-y border-rule py-4 sm:grid-cols-3">
        <li aria-current="step" className="flex items-center gap-3 px-1 py-2">
          <span className="meta flex h-8 w-8 shrink-0 items-center justify-center bg-ink text-ground">01</span>
          <span className="body-2 font-semibold">You observe</span>
        </li>
        <li className="flex items-center gap-3 px-1 py-2 text-muted">
          <span className="meta flex h-8 w-8 shrink-0 items-center justify-center border border-rule">02</span>
          <span className="body-2">Clarify if needed</span>
        </li>
        <li className="flex items-center gap-3 px-1 py-2 text-muted">
          <span className="meta flex h-8 w-8 shrink-0 items-center justify-center border border-rule">03</span>
          <span className="body-2">A person reviews</span>
        </li>
      </ol>

      <form onSubmit={e => { e.preventDefault(); send() }} aria-busy={busy}>
        <fieldset disabled={busy} className="min-w-0 space-y-5">
        <div className="record-mode flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="heading-2">Your field observation</h3>
            <p className="body-2 mt-1 text-muted">Answer what you can. “Not sure” is more useful than a guess.</p>
          </div>
          <Field label="Report type">
            <Choices name="record_class" value={recordClass} onChange={setRecordClass}
              options={[["authentic", "Real observation"], ["synthetic", "Practice report"]]} />
          </Field>
        </div>
        {recordClass === 'synthetic' && (
          <p role="status" className="body-2 border border-rule bg-surface px-4 py-3 text-muted">
            Practice mode: this report will be labelled synthetic and kept separate from real observations.
          </p>
        )}

        <div className="field-workspace grid items-start gap-5 lg:grid-cols-[1.35fr_1fr]">
          <section className="field-panel border border-rule bg-surface p-5 sm:p-7" aria-labelledby="observe-heading">
            <SectionHeading number="01" id="observe-heading" title="What do you notice?"
              description="Tick any that apply. Ticking none is a real answer — it means you looked." />
            <fieldset className="mt-5">
              <legend className="sr-only">Did you notice any of these?</legend>
              {protocolError && (
                <Problem title="Checklist unavailable" onRetry={loadProtocol}>
                  The list of things to look for could not be loaded, so it is not shown.
                  You can still send what you have.
                </Problem>
              )}
              {!protocol && !protocolError && (
                <p role="status" className="body-2 py-6 text-muted">Loading the checklist…</p>
              )}
              <div className="indicator-grid grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                {(protocol?.indicators || []).map(ind => {
                  const on = answers.indicators.includes(ind.key)
                  return (
                    <button key={ind.key} type="button" aria-pressed={on}
                      onClick={() => toggle(ind.key)}
                      className={`indicator-choice lift ${R} flex min-h-[88px] items-center gap-3 border p-3.5 text-left ${on
                        ? 'border-ink bg-ink text-ground'
                        : 'border-edge bg-surface text-ink hover:border-ink'}`}>
                      <span aria-hidden="true" className={`shrink-0 ${on ? 'text-ground' : 'text-muted'}`}>
                        <IndicatorMark indicator={ind.key} size={44} />
                      </span>
                      <span className="body-1 font-medium">{ind.label}</span>
                      <span aria-hidden="true" className={`meta ml-auto shrink-0 ${on ? 'text-ground' : 'invisible'}`}>✓</span>
                    </button>
                  )
                })}
              </div>
              {protocol && <p className="body-2 mt-4 text-faint text-pretty">{protocol.note}</p>}
            </fieldset>

            <div className="mt-6 border-t border-rule pt-5">
              <Field label="Anything else worth knowing?" htmlFor="notes">
                <textarea id="notes" rows={3} value={answers.wildlife_seen || ''}
                  onChange={e => set('wildlife_seen', e.target.value)}
                  placeholder="Wildlife you saw, or anything that struck you as unusual"
                  className={`${CTRL} body-1 w-full px-4 py-3 placeholder:text-faint focus:border-ink`} />
              </Field>
            </div>
          </section>

          <section className="field-panel border border-rule bg-surface p-5 sm:p-7" aria-labelledby="context-heading">
            <SectionHeading number="02" id="context-heading" title="Give it a little context"
              description="A place, a photo, and the conditions you can see." />
            <div className="mt-5 space-y-6">
              <Field label="Which stream or reach is this?" htmlFor="site">
                <input id="site" value={siteName} onChange={e => setSiteName(e.target.value)}
                  placeholder="e.g. Mondego tributary, by the footbridge"
                  className={`${CTRL} body-1 w-full px-4 py-3 placeholder:text-faint focus:border-ink`} />
              </Field>
              <Field label="Photo of the stream" htmlFor="photo">
                <div className="photo-field border border-dashed border-edge bg-ground p-4">
                  <input id="photo" type="file" accept="image/*" capture="environment"
                    onChange={e => {
                      const file = e.target.files?.[0] || null
                      setPhoto(file)
                      setPreview(file ? URL.createObjectURL(file) : null)
                    }}
                    className="body-2 block w-full min-w-0 file:mr-3 file:rounded-[6px] file:border-0 file:bg-ink file:px-4 file:py-3 file:text-[15px] file:font-semibold file:text-ground" />
                  <p className="body-2 mt-3 text-muted">A photo helps a reviewer see what you saw. You can also report without one.</p>
                  {preview && <img src={preview} alt="The stream you photographed"
                    className="mt-3 max-h-64 max-w-full border border-rule object-contain" />}
                </div>
              </Field>
              <div className="space-y-5 border-t border-rule pt-5">
                {CONTEXT.map(q => (
                  <Field key={q.id} label={q.label}>
                    <Choices name={q.id} value={answers[q.id]} onChange={v => set(q.id, v)}
                      options={[...q.options, ['unsure', 'Not sure']]} />
                  </Field>
                ))}
              </div>
            </div>
          </section>
        </div>

        {error && <Problem onRetry={send}>{error} Your answers are still here.</Problem>}
        <div className="capture-submit flex flex-col gap-5 border border-rule bg-surface p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
          <div>
            <p className="question">Your words stay yours.</p>
            <p className="body-2 mt-1 max-w-[64ch] text-muted">
              Any clarification is saved alongside your original answer. Nothing is accepted or rejected automatically.
            </p>
          </div>
          <button type="submit" disabled={busy}
            className={`lift ${R} action flex min-h-14 shrink-0 items-center justify-center gap-8 bg-ink px-6 py-4 text-ground disabled:opacity-60`}>
            {busy ? 'Sending…' : recordClass === 'synthetic' ? 'Send practice report' : 'Send observation'}
            <span aria-hidden="true">↗</span>
          </button>
        </div>
        </fieldset>
      </form>
    </div>
  )
}

function SectionHeading({ number, id, title, description }) {
  return (
    <div className="flex items-start gap-3.5">
      <span className="section-number meta mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center border border-rule">{number}</span>
      <div>
        <h3 id={id} className="heading-2 text-pretty">{title}</h3>
        <p className="body-2 mt-2 text-muted text-pretty">{description}</p>
      </div>
    </div>
  )
}

function Submitted({ result, recordClass, original, protocol, onDone, active }) {
  const [data, setData] = useState(result)
  const [answered, setAnswered] = useState({})
  const [refreshError, setRefreshError] = useState(null)
  const [refreshAttempt, setRefreshAttempt] = useState(0)
  const refreshVersion = useRef(0)
  // Frozen at first render: answering a question removes it from the refreshed
  // assessment, so re-deriving would delete the question and its own answer.
  const [diffs] = useState(result.assessment.field_differentials || [])
  const tensions = result.assessment.detected_inconsistency || []
  const urgency = data.assessment.ecological_urgency
  const reviewStatus = data.assessment.review_status
  const reviewed = reviewStatus === 'reviewer_assessed'
  const review = data.observation?.review
  const reviewLabel = reviewed ? 'Reviewer assessed'
    : reviewStatus === 'in_review' ? 'In human review' : 'Awaiting human review'
  const heading = useRef(null)

  // Move focus to the new heading so a keyboard or screen-reader user is not left
  // at the top of a page that has entirely changed (UX_REVIEW_GPT.md F6).
  useEffect(() => { if (active) heading.current?.focus() }, [active])

  // The report stays mounted when a person visits the reviewer desk. Refresh its
  // current status on return without removing the citizen's answered cards.
  useEffect(() => {
    if (!active) return
    const version = ++refreshVersion.current
    getObservation(result.id).then(fresh => {
      if (version !== refreshVersion.current) return
      setData(fresh)
      setRefreshError(null)
    }).catch(e => {
      if (version === refreshVersion.current) setRefreshError(e.message)
    })
    return () => { if (version === refreshVersion.current) refreshVersion.current += 1 }
  }, [active, result.id, refreshAttempt])

  const n = diffs.length
  const checkTitle = n === 1 ? 'One quick check' : `${n} quick checks`

  return (
    <div className="submitted-page space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-5 border-b-[3px] border-ink pb-6">
        <div>
        <div className="meta meta-stage mb-3 text-faint">Observation recorded</div>
        <h2 ref={heading} tabIndex={-1} className="display-1 outline-none">A closer look starts here.</h2>
        <p className="measure body-1 mt-2 text-muted text-pretty" aria-live="polite">
          {reviewed ? 'A named reviewer has recorded an assessment. Your original report is preserved.'
            : reviewStatus === 'in_review' ? 'A person is reviewing your report. Your original report is preserved.'
            : 'Your report is in the review queue. A person makes the decision.'}
        </p>
        </div>
        <span className="meta border border-rule bg-surface px-3 py-2">
          {recordClass === 'synthetic' ? 'Practice report · synthetic' : 'Real observation'}
        </span>
      </div>

      {/* Model-unavailable state (AUDIT.md A4/D-013): degraded, never dropped. */}
      {result.notice && (
        <p role="status" className="body-2 border border-rule bg-surface px-4 py-3
                                    text-muted text-pretty">
          {result.notice}
        </p>
      )}
      {refreshError && (
        <Problem title="Latest review status unavailable" onRetry={() => setRefreshAttempt(n => n + 1)}>
          Showing the last saved status. Your report and answers are still here. {refreshError}
        </Problem>
      )}

      <div className="submitted-layout grid items-start gap-6 lg:grid-cols-[1.5fr_1fr]">
      <div className="space-y-6">
      {n > 0 ? (
        <section className="space-y-4">
          <div>
            {/* ink, not red: this is a prompt, not a safety warning (F7) */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="meta meta-stage text-faint">While you're still there</div>
              <span className="meta text-faint">{Object.keys(answered).length} of {n} answered</span>
            </div>
            <h3 className="heading-2 mt-2 text-pretty">{checkTitle}</h3>
            <p className="measure body-1 mt-1.5 text-muted text-pretty">
              These are the questions a river surveyor would ask on site. You can see
              what we can't, so you're the one who can answer them.
            </p>
          </div>
          {diffs.map(q => (
            <Differential key={q.id} q={q} id={result.id} active={active}
              done={answered[q.id]}
              onDone={(info, fresh) => {
                refreshVersion.current += 1
                setAnswered(a => ({ ...a, [q.id]: info }))
                setData(fresh)
                setRefreshError(null)
              }} />
          ))}
          <p className="body-2 text-faint">
            Drawings are schematic aids, not identification plates.
          </p>
        </section>
      ) : (
        <section className="field-panel border border-rule bg-surface p-6">
          <SectionHeading number="✓" title="Your field notes are saved"
            description={Array.isArray(original.answers.indicators)
              ? reviewed ? 'Your original field notes are preserved alongside the named assessment.'
                : "No field clarification is needed for the indicators you selected. Your report still needs a person's review."
              : 'The checklist was unavailable when you sent this report. Your other field notes are preserved.'} />
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
      </div>

      <aside className="space-y-5" aria-label="Your record and next steps">
      <section className="field-panel border border-rule bg-surface p-5 sm:p-6">
        <div className="meta meta-stage text-faint">{reviewLabel}</div>
        <div className="mt-3 flex flex-wrap items-baseline justify-between gap-3">
          <h3 className="heading-2 text-pretty">
            {reviewed ? 'Human assessment recorded'
              : urgency.level === 'high' ? 'Worth a prompt look' : 'What happens next'}
          </h3>
        </div>
        {reviewed && review && (
          <div className="mt-3 space-y-2 border-b border-rule pb-4">
            <p className="body-1 font-semibold whitespace-pre-wrap break-words">{review.decision}</p>
            <p className="body-2 text-muted">Recorded by {review.reviewer}</p>
            {review.note && <p className="body-2 whitespace-pre-wrap break-words text-muted">{review.note}</p>}
          </div>
        )}
        <ul className="measure mt-2 space-y-1.5">
          {urgency.reasons.map((r, i) => (
            <li key={i} className="body-1 text-muted text-pretty">{r}</li>
          ))}
        </ul>
        <p className="body-2 mt-4 border-t border-rule pt-4 text-faint">
          This is a prompt for review, not a water-quality classification or a finding that the water is safe.
        </p>
      </section>

      <section className="field-panel border border-rule bg-surface p-5 sm:p-6">
        <div className="meta meta-stage text-faint">Original report · preserved</div>
        <h3 className="heading-2 mt-3 break-words">{original.siteName}</h3>
        {original.preview && <img src={original.preview} alt="Your original stream photograph"
          className="mt-4 max-h-64 max-w-full border border-rule object-contain" />}
        <dl className="mt-4 space-y-3">
          {CONTEXT.map(q => (
            <div key={q.id} className="border-t border-rule pt-3">
              <dt className="body-2 text-faint">{q.label}</dt>
              <dd className="body-1 mt-1">{q.options.find(([v]) => v === original.answers[q.id])?.[1]
                || (original.answers[q.id] === 'unsure' ? 'Not sure' : 'Not answered')}</dd>
            </div>
          ))}
          <div className="border-t border-rule pt-3">
            <dt className="body-2 text-faint">Things you noticed</dt>
            <dd className="body-1 mt-1">{!Array.isArray(original.answers.indicators)
              ? 'Not recorded — checklist unavailable'
              : original.answers.indicators.length
                ? original.answers.indicators.map(key => protocol?.indicators.find(ind => ind.key === key)?.label || key).join(', ')
                : 'None selected'}</dd>
          </div>
          {original.answers.wildlife_seen && <div className="border-t border-rule pt-3">
            <dt className="body-2 text-faint">Your notes</dt>
            <dd className="body-1 mt-1 whitespace-pre-wrap break-words">{original.answers.wildlife_seen}</dd>
          </div>}
        </dl>
      </section>
      <button onClick={onDone}
        className={`lift ${R} action w-full border-2 border-ink px-4 py-3.5 text-ink`}>
        Report another stream
      </button>
      </aside>
      </div>
    </div>
  )
}

function Differential({ q, id, done, onDone, active }) {
  const [saving, setSaving] = useState(null)
  const [error, setError] = useState(null)
  const [retryOption, setRetryOption] = useState(null)
  const feedback = useRef(null)
  const previouslyDone = useRef(Boolean(done))

  useEffect(() => {
    if (done && !previouslyDone.current && active) feedback.current?.focus()
    previouslyDone.current = Boolean(done)
  }, [done, active])

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
      onDone({ response: option.label, explain: r?.explain || 'Recorded.', urgency: r?.urgency,
               oneHealth: r?.one_health }, fresh)
    } catch (e) { setError(e.message); setRetryOption(option) } finally { setSaving(null) }
  }

  return (
    <div className="differential-panel border border-rule bg-surface p-5 sm:p-6">
      <p className="question text-pretty">{q.question}</p>
      {done ? (
        <div ref={feedback} tabIndex={-1} className="mt-3 space-y-2" role="status">
          <p className="body-2 font-semibold">Your answer: {done.response}</p>
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
        <div className="differential-options mt-4 flex flex-col gap-3">
          {q.options.map(o => (
            <button key={o.key} onClick={() => pick(o)} disabled={Boolean(saving)}
              className={`lift ${R} flex min-h-14 items-center gap-4 border border-edge
                          bg-surface px-4 py-3 text-left hover:border-ink
                          disabled:opacity-60`}>
              <Specimen differential={q.id} option={o.key} size={62} />
              <span className="body-1">{o.label}</span>
              {saving === o.key && <span className="meta ml-auto text-faint">Saving…</span>}
            </button>
          ))}
          {error && <Problem onRetry={retryOption ? () => pick(retryOption) : undefined}>{error}</Problem>}
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
              <input value={text} onChange={e => setText(e.target.value)} aria-label="Your new answer"
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
          <button onClick={() => setState('idle')} disabled={state === 'saving'}
            className="body-2 min-h-11 px-1 text-muted underline disabled:opacity-60">
            Cancel
          </button>
        </div>
      )}
    </div>
  )
}

function Field({ label, htmlFor, children }) {
  return (
    <fieldset className="min-w-0 space-y-2.5">
      <legend className="question text-ink">
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
          {l}{value === v && <span aria-hidden="true" className="ml-2">✓</span>}
        </label>
      ))}
    </div>
  )
}
