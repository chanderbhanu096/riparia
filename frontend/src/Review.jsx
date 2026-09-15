import { useEffect, useState } from 'react'
import { getQueue, getObservation, submitReview, getProtocol } from './api'

const R = 'rounded-[6px]'   // controls only

// The reviewer surfaces are an information system, not a newspaper (AUDIT.md D-028).
// Bodoni appears on the page title and nowhere else; rows are hairline-ruled and
// column-aligned; nothing is inverted or shouted.
//
// Three rules this file exists to keep:
//   1. Consequence, completeness and review status stay THREE SEPARATE, text-labelled
//      things. Merging them into one badge would rebuild the single trust score
//      D-012 removed.
//   2. Ecological urgency never wears the citizen precaution's red, and is always
//      phrased as POTENTIAL consequence -- it is a triage judgement about whether a
//      person should look, not an ecological classification and not a verdict.
//   3. Routine reports look routine.

const CONSEQUENCE = {
  high:   { label: 'High',   dot: 'bg-ochre',  text: 'text-ochre font-semibold' },
  medium: { label: 'Medium', dot: 'bg-faint',  text: 'text-muted' },
  low:    { label: 'Low',    dot: 'bg-rule',   text: 'text-faint' },
}

const STATUS = {
  not_reviewed:      'Not yet reviewed',
  in_review:         'In review',
  reviewer_assessed: 'Reviewer assessed',
}

// Field keys are internal identifiers, not copy.
const pretty = k => k.replace(/_/g, ' ')

const Label = ({ children }) => (
  <span className="meta meta-stage text-faint">{children}</span>
)
const Value = ({ children, className = '' }) => (
  <span className={`meta ${className}`}>{children}</span>
)

// D-015: the three record classes stay visibly separate, everywhere. A judge must
// never have to wonder whether a record on screen is real.
const ClassTag = ({ cls }) => cls === 'authentic' ? null : (
  <span className="meta meta-stage border border-rule px-1.5 py-0.5 text-faint">
    {cls === 'synthetic' ? 'simulated' : 'evaluation case'}
  </span>
)

export default function Review() {
  const [queue, setQueue] = useState(null)
  const [openId, setOpenId] = useState(null)
  const [error, setError] = useState(null)

  const load = () => getQueue().then(setQueue).catch(e => setError(e.message))
  useEffect(() => { load() }, [])

  if (error) return (
    <div role="alert" className={`${R} border-2 border-ink bg-surface p-4`}>
      <p className="heading-2">Could not load the queue</p>
      <p className="body-2 mt-1 text-muted">{error}</p>
      <button onClick={() => { setError(null); load() }}
        className={`action mt-3 ${R} min-h-11 bg-ink px-4 py-2.5 text-ground`}>Try again</button>
    </div>
  )
  if (!queue) return <p role="status" className="body-1 text-muted">Loading queue…</p>
  if (openId) return <Detail id={openId} onBack={() => { setOpenId(null); load() }} />

  return (
    <div className="space-y-5">
      <div>
        <h2 className="display-1">Review queue</h2>
        <p className="measure body-1 mt-3 text-muted text-pretty">
          Ordered by what a review could change, not by arrival time. An uncertain
          report of something serious sits above a tidy report of nothing much,
          because that is where your time changes an outcome.
        </p>
      </div>

      {queue.items.length === 0 && (
        <p role="status" className="body-1 border border-rule bg-surface px-4 py-3 text-muted">
          Nothing waiting. Submit an observation first.
        </p>
      )}

      <ul className="border-t border-rule">
        {queue.items.map(i => {
          const a = i.assessment
          const c = CONSEQUENCE[a.ecological_urgency.level]
          const open = a.completeness.missing.length + a.completeness.marked_unsure.length
                     + a.detected_inconsistency.length
                     + (a.ecological_urgency.unresolved_indicators?.length || 0)
          return (
            <li key={i.id} className="border-b border-rule">
              <button onClick={() => setOpenId(i.id)}
                className="flex w-full items-start gap-4 bg-surface px-4 py-3.5 text-left
                           hover:bg-ground">
                <span className={`mt-2 h-2.5 w-2.5 shrink-0 ${c.dot}`} aria-hidden="true" />
                <span className="min-w-0 flex-1">
                  <span className="flex flex-wrap items-baseline gap-2">
                    <span className="body-1 font-semibold">
                      {i.site_name || 'Unnamed reach'}
                    </span>
                    <ClassTag cls={i.record_class} />
                  </span>
                  <span className="measure body-2 mt-1 block text-muted text-pretty">
                    {a.triage.rationale}
                  </span>
                  {/* three separate, labelled facts -- never one merged badge */}
                  <span className="mt-2 flex flex-wrap gap-x-5 gap-y-1">
                    <span><Label>Potential consequence</Label>{' '}<Value className={c.text}>{c.label}</Value></span>
                    <span><Label>Open points</Label>{' '}<Value className="text-muted">{open || 'none'}</Value></span>
                    <span><Label>Status</Label>{' '}<Value className="text-muted">{STATUS[i.review_status]}</Value></span>
                  </span>
                </span>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function Detail({ id, onBack }) {
  const [data, setData] = useState(null)
  const [reviewer, setReviewer] = useState('')
  const [decision, setDecision] = useState('')
  const [note, setNote] = useState('')
  const [error, setError] = useState(null)
  const [savingReview, setSavingReview] = useState(false)
  const [protocol, setProtocol] = useState(null)

  useEffect(() => { getObservation(id).then(setData).catch(e => setError(e.message)) }, [id])
  useEffect(() => { getProtocol().then(setProtocol).catch(() => {}) }, [])
  if (!data) return <p role="status" className="body-1 text-muted">Loading…</p>

  const { observation: o, assessment: a } = data
  const u = a.ecological_urgency
  const c = CONSEQUENCE[u.level]
  const resolved = Object.entries(u.resolved || {})

  // A failed save must never take the reviewer's typed assessment with it.
  async function save() {
    if (savingReview) return
    setSavingReview(true); setError(null)
    try { setData(await submitReview(id, { reviewer, decision, note })) }
    catch (e) { setError(e.message) } finally { setSavingReview(false) }
  }

  // Indicator keys are internal ids; show the words the citizen actually saw.
  const indicatorLabel = k =>
    protocol?.indicators?.find(i => i.key === k)?.label || pretty(k)

  return (
    <div className="space-y-6">
      <button onClick={onBack}
        className="meta meta-stage -ml-2 inline-flex min-h-11 items-center px-2 text-muted
                   hover:text-ink">
        ← Back to queue
      </button>

      <div className="border-b-[3px] border-ink pb-3">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <h2 className="display-1">{o.site_name || 'Unnamed reach'}</h2>
          <ClassTag cls={o.record_class} />
        </div>
        <p className="measure body-1 mt-2.5 text-muted text-pretty">
          <Label>Why this is in front of you</Label> {a.triage.rationale}
        </p>
      </div>

      {/* The four dimensions, kept separate and labelled. No combined score exists
          anywhere in this system (AUDIT.md D-012). */}
      <dl className="border-t border-rule">
        <Row label="Potential consequence"
             hint="Whether a person should look, and how soon. Not reduced when a record is uncertain, and not an ecological classification.">
          <span className={`${c.text} text-[15px]`}>{c.label}</span>
          <ul className="mt-1.5 space-y-1">
            {u.reasons.map((r, i) => (
              <li key={i} className="text-[14px] leading-[20px] text-muted text-pretty">{r}</li>
            ))}
          </ul>
        </Row>

        <Row label="Completeness" hint="What was recorded. Blanks are gaps, not mistakes.">
          <span className="text-[15px]">
            {a.completeness.answered} of {a.completeness.total} fields answered
          </span>
          {a.completeness.marked_unsure.length > 0 && (
            <p className="mt-1 text-[14px] leading-[20px] text-muted">
              Marked “not sure”: {a.completeness.marked_unsure.map(pretty).join(', ')}
            </p>
          )}
          {a.completeness.missing.length > 0 && (
            <p className="mt-1 text-[14px] leading-[20px] text-muted">
              Not recorded: {a.completeness.missing.map(pretty).join(', ')}
            </p>
          )}
        </Row>

        <Row label="Points raised with the citizen" hint="Questions asked, never corrections applied.">
          {a.detected_inconsistency.length === 0
            ? <span className="text-[14px] text-muted">None.</span>
            : <ul className="space-y-1">
                {a.detected_inconsistency.map(t => (
                  <li key={t.id} className="text-[14px] leading-[20px] text-muted text-pretty">{t.question}</li>
                ))}
              </ul>}
        </Row>

        <Row label="Review status" hint="Only a named person can change this.">
          <span className="text-[15px]">{STATUS[a.review_status]}</span>
          {o.review && (
            <p className="mt-1 text-[14px] leading-[20px] text-muted text-pretty">
              {o.review.decision} — <em>{o.review.reviewer}</em>
            </p>
          )}
        </Row>
      </dl>

      {o.photo_path && (
        <div>
          <Label>Photograph</Label>
          <img src={o.photo_path} alt="Submitted stream photo"
               className="mt-1.5 max-h-72 border border-rule" />
        </div>
      )}

      {resolved.length > 0 && (
        <section>
          <h3 className="heading-2">
            What the citizen's field answers resolved
          </h3>
          <ul className="mt-2 border-t border-rule">
            {resolved.map(([ind, r]) => (
              <li key={ind} className="border-b border-rule bg-surface px-4 py-3">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-[14.5px] leading-[20px] text-pretty">{r.explain}</p>
                  <span className={`shrink-0 text-[12.5px] ${CONSEQUENCE[r.urgency].text}`}>
                    {CONSEQUENCE[r.urgency].label}
                  </span>
                </div>
                <p className="mt-1 text-[12.5px] leading-[17px] text-faint">
                  {r.reading === 'unresolved'
                    ? 'Not narrowed down — held at the highest reading it could be.'
                    : `Resolved by the citizen on site → ${r.reading.replace(/_/g, ' ')}`}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {u.one_health_notes?.length > 0 && (
        <section className="border-2 border-alarm bg-alarm-bg p-4">
          <h3 className="text-[13px] font-bold uppercase tracking-[0.14em] text-alarm">
            Precaution already given to the citizen
          </h3>
          <ul className="mt-2 space-y-1.5">
            {u.one_health_notes.map((n, i) => (
              <li key={i} className="text-[14.5px] leading-[20px] text-pretty">{n}</li>
            ))}
          </ul>
          <p className="mt-2 text-[12.5px] leading-[17px] text-muted text-pretty">
            Issued immediately on the citizen's own answer, before any review. If you
            disagree, say so in your assessment — they should be told.
          </p>
        </section>
      )}

      {/* Model output, shown with its reliability stated. Hiding either the note or
          the caveat would be worse than not showing it (AUDIT.md D-023). */}
      {o.photo_findings?.model_description && (
        <section className="border border-rule bg-surface p-4">
          <Label>Automated photo note</Label>
          <p className="mt-1.5 text-[14.5px] leading-[20px] italic text-pretty">
            “{o.photo_findings.model_description}”
          </p>
          <p className="mt-2 text-[12.5px] leading-[17px] text-muted text-pretty">
            Advisory only. This model has been observed describing detail that is not
            present in an image. It is used solely to raise questions for the citizen
            and has no effect on consequence, on the record, or on your decision.
          </p>
        </section>
      )}

      <section>
        <h3 className="heading-2">
          What the citizen reported
        </h3>
        <div className="mt-2 grid gap-4 sm:grid-cols-2">
          <div className="border border-rule bg-surface p-4">
            <Label>Original answers</Label>
            <dl className="mt-2 space-y-1">
              {Object.entries(o.answers).map(([k, v]) => (
                <div key={k} className="flex gap-2 text-[14px] leading-[20px]">
                  <dt className="text-muted">{pretty(k)}:</dt>
                  <dd className="font-medium">
                    {Array.isArray(v)
                      ? (v.map(indicatorLabel).join(', ') || 'none selected')
                      : String(v)}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
          <div className="border border-rule bg-surface p-4">
            <Label>After clarification</Label>
            {o.clarifications.length === 0
              ? <p className="mt-2 text-[14px] text-muted">No clarifications were needed.</p>
              : <ul className="mt-2 space-y-3">
                  {o.clarifications.map((cl, i) => (
                    <li key={i}>
                      <p className="text-[13.5px] leading-[19px] text-muted text-pretty">{cl.question}</p>
                      <p className="mt-0.5 text-[14px] font-medium leading-[20px] text-pretty">{cl.response}</p>
                      {cl.citizen_disagrees && (
                        <p className="mt-1 text-[12.5px] font-semibold text-ink">
                          Citizen stood by their original answer
                        </p>
                      )}
                    </li>
                  ))}
                </ul>}
          </div>
        </div>
      </section>

      <section className="border-t-[3px] border-ink pt-4">
        <h3 className="heading-2">Your assessment</h3>
        <p className="mt-1.5 text-[14px] leading-[20px] text-muted text-pretty">
          Recorded as your attributed judgement, with your name against it — not as
          ground truth. Another reviewer may reach a different conclusion.
        </p>
        <div className="mt-3 space-y-3">
          <label className="block">
            <span className="body-1 font-semibold">Your name and role</span>
            <input value={reviewer} onChange={e => setReviewer(e.target.value)}
              placeholder="e.g. A. Ferreira, freshwater ecology"
              className={`mt-1.5 w-full ${R} border border-edge bg-surface px-4 py-3 body-1
                          placeholder:text-faint focus:border-ink`} />
          </label>
          <label className="block">
            <span className="body-1 font-semibold">Decision</span>
            <input value={decision} onChange={e => setDecision(e.target.value)}
              placeholder="e.g. escalate for site visit / usable as reported / needs resampling"
              className={`mt-1.5 w-full ${R} border border-edge bg-surface px-4 py-3 body-1
                          placeholder:text-faint focus:border-ink`} />
          </label>
          <label className="block">
            <span className="body-1 font-semibold">Reasoning</span>
            <textarea rows={3} value={note} onChange={e => setNote(e.target.value)}
              className={`mt-1.5 w-full ${R} border border-edge bg-surface px-4 py-3 body-1
                          focus:border-ink`} />
          </label>
          {error && (
            <div role="alert" className={`${R} border-2 border-ink bg-surface p-3.5`}>
              <p className="question">Could not save your assessment</p>
              <p className="body-2 mt-1 text-muted">{error} — your text above has been kept.</p>
            </div>
          )}
          <button onClick={save} disabled={!reviewer.trim() || !decision.trim() || savingReview}
            className={`lift ${R} action min-h-11 bg-ink px-5 py-3 text-ground disabled:opacity-60`}>
            {savingReview ? 'Saving…' : 'Record my assessment'}
          </button>
        </div>
      </section>
    </div>
  )
}

function Row({ label, hint, children }) {
  return (
    <div className="grid gap-1 border-b border-rule py-3 sm:grid-cols-[minmax(0,13rem)_1fr] sm:gap-4">
      <dt>
        <Label>{label}</Label>
        <p className="mt-0.5 text-[12px] leading-[16px] text-faint text-pretty">{hint}</p>
      </dt>
      <dd>{children}</dd>
    </div>
  )
}
