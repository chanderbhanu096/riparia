import { useEffect, useState } from 'react'
import { getQueue, getObservation, submitReview } from './api'

const URGENCY = {
  high:   'bg-red-100 text-red-900 border-red-300',
  medium: 'bg-amber-100 text-amber-900 border-amber-300',
  low:    'bg-stream-100 text-stream-900 border-stream-300',
}

export default function Review() {
  const [queue, setQueue] = useState(null)
  const [openId, setOpenId] = useState(null)
  const [error, setError] = useState(null)

  const load = () => getQueue().then(setQueue).catch(e => setError(e.message))
  useEffect(() => { load() }, [])

  if (error) return <p role="alert" className="text-red-700">{error}</p>
  if (!queue) return <p className="text-stream-700">Loading queue…</p>
  if (openId) return <Detail id={openId} onBack={() => { setOpenId(null); load() }} />

  return (
    <div className="space-y-5">
      <header>
        <h2 className="text-2xl font-semibold text-stream-900">Review queue</h2>
        <p className="text-stream-700 mt-1">
          Ordered by <strong>what a review could change</strong>, not by arrival time.
          An uncertain report of something serious sits above a tidy report of
          nothing much — because that is where your time changes an outcome.
        </p>
        <p className="text-stream-700 mt-2 text-sm">
          Expert attention is the scarce resource in citizen science. This queue
          spends it deliberately.
        </p>
      </header>

      {queue.items.length === 0 && (
        <p className="text-stream-700">Nothing waiting. Submit an observation first.</p>
      )}

      <ul className="space-y-3">
        {queue.items.map(i => (
          <li key={i.id}>
            <button onClick={() => setOpenId(i.id)}
              className="w-full text-left rounded-lg border border-stream-300 p-4
                         hover:bg-stream-50">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-stream-900">
                    {i.site_name || 'Unnamed reach'}
                  </p>
                  <p className="text-sm text-stream-700 mt-0.5">
                    {i.assessment.triage.rationale}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1 shrink-0">
                  <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium
                                    ${URGENCY[i.assessment.ecological_urgency.level]}`}>
                    {i.assessment.ecological_urgency.level} consequence
                  </span>
                  {i.record_class !== 'authentic' && <SyntheticTag cls={i.record_class} />}
                  {i.review_status !== 'not_reviewed' && (
                    <span className="text-xs text-stream-600">
                      {i.review_status.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

// D-015: the three record classes stay visibly separate, everywhere, always.
// A judge must never have to wonder whether a record on screen is real.
function SyntheticTag({ cls }) {
  return (
    <span className="rounded-full border border-purple-300 bg-purple-100 px-2.5 py-0.5
                     text-xs font-medium text-purple-900">
      {cls === 'synthetic' ? 'simulated record' : 'evaluation case'}
    </span>
  )
}

function Detail({ id, onBack }) {
  const [data, setData] = useState(null)
  const [reviewer, setReviewer] = useState('')
  const [decision, setDecision] = useState('')
  const [note, setNote] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => { getObservation(id).then(setData).catch(e => setError(e.message)) }, [id])
  if (error) return <p role="alert" className="text-red-700">{error}</p>
  if (!data) return <p className="text-stream-700">Loading…</p>

  const { observation: o, assessment: a } = data

  async function save() {
    try { setData(await submitReview(id, { reviewer, decision, note })) }
    catch (e) { setError(e.message) }
  }

  return (
    <div className="space-y-6">
      <button onClick={onBack} className="text-stream-600 underline">← Back to queue</button>

      <div className="flex items-start justify-between gap-3">
        <h2 className="text-2xl font-semibold text-stream-900">
          {o.site_name || 'Unnamed reach'}
        </h2>
        {o.record_class !== 'authentic' && <SyntheticTag cls={o.record_class} />}
      </div>

      <div className="rounded-lg border border-stream-300 bg-stream-50 p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-stream-600">
          Why this is in front of you
        </p>
        <p className="mt-1 text-stream-900">{a.triage.rationale}</p>
      </div>

      {o.photo_path && <img src={o.photo_path} alt="Submitted stream photo"
        className="max-h-72 rounded-lg border border-stream-300" />}

      {/* Four dimensions, shown SEPARATELY. There is deliberately no combined
          score anywhere in this UI (AUDIT.md D-012). */}
      <section className="grid gap-3 sm:grid-cols-2">
        <Card title="Ecological urgency"
              sub="Could this matter, if it is accurate? Not reduced when a record is uncertain.">
          <span className={`inline-block rounded-full border px-2.5 py-0.5 text-sm
                            font-medium ${URGENCY[a.ecological_urgency.level]}`}>
            {a.ecological_urgency.level}
          </span>
          <ul className="mt-2 text-sm text-stream-700 list-disc pl-5">
            {a.ecological_urgency.reasons.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </Card>

        <Card title="Completeness" sub="What was recorded. Blanks are gaps, not mistakes.">
          <p className="text-stream-900">
            {a.completeness.answered} of {a.completeness.total} fields answered
          </p>
          {a.completeness.marked_unsure.length > 0 && (
            <p className="mt-1 text-sm text-stream-700">
              Marked “not sure”: {a.completeness.marked_unsure.join(', ')}
            </p>
          )}
          {a.completeness.missing.length > 0 && (
            <p className="mt-1 text-sm text-stream-700">
              Not recorded: {a.completeness.missing.join(', ')}
            </p>
          )}
        </Card>

        <Card title="Points raised with the citizen"
              sub="Questions asked, never corrections applied.">
          {a.detected_inconsistency.length === 0
            ? <p className="text-sm text-stream-700">None.</p>
            : <ul className="text-sm text-stream-700 list-disc pl-5">
                {a.detected_inconsistency.map(t => <li key={t.id}>{t.question}</li>)}
              </ul>}
        </Card>

        <Card title="Review status" sub="Only a named person can change this.">
          <p className="text-stream-900">{a.review_status.replace('_', ' ')}</p>
          {o.review && (
            <p className="mt-1 text-sm text-stream-700">
              {o.review.decision} — <em>{o.review.reviewer}</em>
            </p>
          )}
        </Card>
      </section>

      {/* What the citizen's own field answers resolved to. This is the section that
          shows the system working as intended: a person answered a field question
          and it changed the reading -- no model decided anything. */}
      {Object.keys(a.ecological_urgency.resolved || {}).length > 0 && (
        <section>
          <h3 className="text-lg font-semibold text-stream-900">
            What the citizen's field answers resolved
          </h3>
          <ul className="mt-2 space-y-2">
            {Object.entries(a.ecological_urgency.resolved).map(([ind, r]) => (
              <li key={ind} className="rounded-lg border border-stream-300 p-3">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm text-stream-900">{r.explain}</p>
                  <span className={`shrink-0 rounded-full border px-2 py-0.5 text-xs
                                    font-medium ${URGENCY[r.urgency]}`}>
                    {r.urgency}
                  </span>
                </div>
                <p className="mt-1 text-xs text-stream-700">
                  {r.reading === 'unresolved'
                    ? 'Not narrowed down — held at the highest reading it could be.'
                    : `Resolved by the citizen on site → ${r.reading.replace(/_/g, ' ')}`}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {a.ecological_urgency.one_health_notes?.length > 0 && (
        <section className="rounded-lg border border-amber-300 bg-amber-50 p-4">
          <h3 className="font-semibold text-amber-900">
            Precaution already given to the citizen
          </h3>
          <ul className="mt-2 space-y-1 text-sm text-amber-900 list-disc pl-5">
            {a.ecological_urgency.one_health_notes.map((n, i) => <li key={i}>{n}</li>)}
          </ul>
          <p className="mt-2 text-xs text-amber-900">
            Issued immediately on the citizen's own answer, before any review. If you
            disagree, say so in your assessment — they should be told.
          </p>
        </section>
      )}

      {/* Model output, shown with its reliability stated. A reviewer must be able
          to see what the model said AND that it is not dependable -- hiding either
          would be worse than not showing it at all (AUDIT.md D-023). */}
      {o.photo_findings?.model_description && (
        <section className="rounded-lg border border-stream-300 p-4">
          <h3 className="font-semibold text-stream-900">Automated photo note</h3>
          <p className="mt-1 text-sm text-stream-900 italic">
            “{o.photo_findings.model_description}”
          </p>
          <p className="mt-2 text-xs text-stream-700">
            Advisory only. This model has been observed describing detail that is not
            present in an image. It is used solely to raise questions for the citizen
            and has no effect on urgency, on the record, or on your decision.
          </p>
        </section>
      )}

      {/* The heart of the demo (D-015): what was first said, beside what was said
          after being prompted. The difference between those two is the product. */}
      <section>
        <h3 className="text-lg font-semibold text-stream-900">
          What the citizen reported
        </h3>
        <div className="mt-2 grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-stream-300 p-4">
            <p className="text-sm font-medium text-stream-600 uppercase tracking-wide">
              Original answers
            </p>
            <dl className="mt-2 space-y-1 text-sm">
              {Object.entries(o.answers).map(([k, v]) => (
                <div key={k} className="flex gap-2">
                  <dt className="text-stream-700">{k.replace(/_/g, ' ')}:</dt>
                  <dd className="text-stream-900 font-medium">
                    {Array.isArray(v) ? (v.join(', ') || 'none selected') : String(v)}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
          <div className="rounded-lg border border-stream-300 p-4">
            <p className="text-sm font-medium text-stream-600 uppercase tracking-wide">
              After clarification
            </p>
            {o.clarifications.length === 0
              ? <p className="mt-2 text-sm text-stream-700">No clarifications were needed.</p>
              : <ul className="mt-2 space-y-3 text-sm">
                  {o.clarifications.map((c, i) => (
                    <li key={i}>
                      <p className="text-stream-700">{c.question}</p>
                      <p className="text-stream-900 font-medium mt-0.5">{c.response}</p>
                      {c.citizen_disagrees && (
                        <p className="mt-1 inline-block rounded bg-stream-100 px-2 py-0.5
                                      text-xs text-stream-900">
                          Citizen stood by their original answer
                        </p>
                      )}
                    </li>
                  ))}
                </ul>}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-stream-300 p-4 space-y-3">
        <h3 className="text-lg font-semibold text-stream-900">Your assessment</h3>
        <p className="text-sm text-stream-700">
          Recorded as your attributed judgement, with your name against it — not as
          ground truth. Another reviewer may reach a different conclusion.
        </p>
        <label className="block">
          <span className="text-sm font-medium text-stream-900">Your name and role</span>
          <input value={reviewer} onChange={e => setReviewer(e.target.value)}
            placeholder="e.g. A. Ferreira, freshwater ecology"
            className="mt-1 w-full rounded-lg border border-stream-300 px-3 py-2" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-stream-900">Decision</span>
          <input value={decision} onChange={e => setDecision(e.target.value)}
            placeholder="e.g. escalate for site visit / usable as reported / needs resampling"
            className="mt-1 w-full rounded-lg border border-stream-300 px-3 py-2" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-stream-900">Reasoning</span>
          <textarea rows={3} value={note} onChange={e => setNote(e.target.value)}
            className="mt-1 w-full rounded-lg border border-stream-300 px-3 py-2" />
        </label>
        <button onClick={save} disabled={!reviewer.trim() || !decision.trim()}
          className="rounded-lg bg-stream-600 px-4 py-2.5 text-white disabled:opacity-60">
          Record my assessment
        </button>
      </section>
    </div>
  )
}

function Card({ title, sub, children }) {
  return (
    <div className="rounded-lg border border-stream-300 p-4">
      <h3 className="font-semibold text-stream-900">{title}</h3>
      <p className="text-xs text-stream-700 mt-0.5 mb-2">{sub}</p>
      {children}
    </div>
  )
}
