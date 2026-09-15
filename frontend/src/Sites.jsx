import { useEffect, useState } from 'react'
import { getSites } from './api'

const CLASSES = [['authentic', 'Real observations'], ['synthetic', 'Practice reports'], ['evaluation', 'Evaluation cases']]
const date = value => value ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'No approved report yet'

export default function Sites({ onReview }) {
  const [recordClass, setRecordClass] = useState('authentic')
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [reload, setReload] = useState(0)
  useEffect(() => {
    let cancelled = false
    getSites(recordClass).then(value => { if (!cancelled) setData(value) })
      .catch(e => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [recordClass, reload])
  return (
    <div>
      <div className="page-intro">
        <div><span className="meta meta-stage text-faint">From observation to action</span>
          <h2 className="display-1">One stream. Connected health.</h2>
          <p className="body-1 text-muted">A traceable picture of what people reported, what a reviewer decided, and why it may matter for the life around the water.</p></div>
        <p className="intro-aside">Original report →<br />Field clarification →<br />Named human decision</p>
      </div>
      <div className="filter-tabs" aria-label="Record type">{CLASSES.map(([value, label]) => <button key={value} className="filter-tab" aria-pressed={recordClass === value} onClick={() => { if (value !== recordClass) { setData(null); setError(null); setRecordClass(value) } }}>{label}</button>)}</div>
      {recordClass !== 'authentic' && <p role="status" className="body-2 mb-5 border border-edge rounded-[6px] p-4">{recordClass === 'synthetic' ? 'Simulated practice reports. These demonstrate the workflow and are not evidence about a real stream.' : 'Evaluation cases. These test the workflow and are not real field observations.'}</p>}
      {error && <div role="alert" className="field-panel"><h3 className="heading-2">Could not load the summaries</h3><p className="body-1 my-3">{error}</p><button className="secondary-button" onClick={() => { setError(null); setData(null); setReload(n => n + 1) }}>Try again</button></div>}
      {!data && !error && <p role="status" className="body-1 py-8">Loading site evidence…</p>}
      {data && <>
        <div className="metric-strip">
          <div className="metric"><span className="meta meta-stage text-faint">Reported sites</span><b>{data.count}</b></div>
          <div className="metric"><span className="meta meta-stage text-faint">Approved for summary</span><b>{data.approved_count}</b></div>
          <div className="metric"><span className="meta meta-stage text-faint">Not included</span><b>{data.pending_count}</b></div>
        </div>
        {data.sites.length === 0 && <div className="empty-state"><span className="meta meta-stage text-faint">Evidence begins with people</span><h3>No site reports in this category yet.</h3><p className="body-1 text-muted measure">Submit an observation, then let a named reviewer assess it and explicitly approve its inclusion. Practice reports appear in their own tab.</p><button className="primary-button" onClick={onReview}>Go to the review desk ↗</button></div>}
        <div className="site-grid">{data.sites.map(site => <SiteCard key={site.site_key} site={site} onReview={onReview} />)}</div>
        <section className="mt-8 border-t border-rule pt-6"><h3 className="heading-2">What this evidence can tell us</h3>
          <div className="pathway">
            <div><span className="meta text-faint">01 / THE STREAM</span><h4>A reported change</h4><p>Original field notes and citizen clarifications stay visible. They describe observations, not measured water quality.</p></div>
            <div><span className="meta text-faint">02 / PEOPLE & ANIMALS</span><h4>A potential contact pathway</h4><p>Protocol precautions are shown when a field answer calls for them. No exposure, illness or water safety is inferred.</p></div>
            <div><span className="meta text-faint">03 / PROPOSED NEXT STEP</span><h4>A human-led handoff</h4><p>The reviewer records a decision. Local investigation is a proposed downstream step; this app does not send an alert to an authority.</p></div>
          </div>
          <details className="body-2 text-muted"><summary className="min-h-11 cursor-pointer py-3 font-semibold">Scope and limitations</summary><ul className="list-disc pl-5 space-y-2">{data.limitations.map((text, i) => <li key={i}>{text}</li>)}<li>Downloads contain provenance JSON and, where relevant, a proposed FHIR R4 mapping. FHIR conformance and integration with a receiving system have not been validated.</li></ul></details>
        </section>
      </>}
    </div>
  )
}

function SiteCard({ site, onReview }) {
  return (
    <article className="site-card">
      <header><div><span className="meta meta-stage text-faint">{site.record_class === 'authentic' ? 'Reported location' : site.record_class === 'synthetic' ? 'Simulated location' : 'Evaluation location'}</span><h3 className="break-words">{site.site_name}</h3><p className="body-2 text-faint mt-2">Last approval: {date(site.latest_approved_at)}</p></div>
        {site.approved_count > 0 ? <a className="primary-button shrink-0" href={site.export_url} download>Download evidence ↗</a> : <button className="secondary-button" onClick={onReview}>Review observations</button>}</header>
      <div className="site-content">
        <section><h4 className="question">The evidence at this site</h4><p className="body-1 text-muted mt-3">{site.summary}</p><p className="body-2 text-faint mt-3">{site.pending_count} report{site.pending_count === 1 ? '' : 's'} not included: no current explicit approval.</p>
          {site.approved_count > 0 && <p className="body-2 mt-4"><span className="font-semibold text-ochre">{site.high_urgency_count} with high potential consequence.</span> This is review urgency, not an ecological status classification.</p>}
          {site.one_health_notes.length > 0 ? <div className="mt-5 border-2 border-alarm bg-alarm-bg p-4"><h4 className="question text-alarm">Precaution linked to the field answer</h4>{site.one_health_notes.map((note, i) => <p key={i} className="body-1 mt-3">{note}</p>)}<p className="body-2 mt-3">Based on the reported field answer; not a confirmed diagnosis or exposure.</p></div> : <p className="body-2 text-muted mt-5 border border-rule p-4">No protocol-specific contact precaution is recorded in this approved evidence. That does not establish that the water is safe.</p>}
        </section>
        <section><h4 className="question">Named decisions & source records</h4>{!site.records.length && <p className="body-1 text-faint mt-3">A reviewer must explicitly approve a report before its content appears here.</p>}
          <ul className="mt-3 space-y-4">{site.records.map(record => <li key={record.id} className="border border-rule p-4 rounded-[6px]">
            <div className="flex flex-wrap justify-between gap-2"><span className="meta text-faint">{record.id}</span><span className="meta text-faint">{date(record.created_at)}</span></div>
            <p className="body-1 font-semibold mt-3">{record.review.decision}</p><p className="body-2 text-muted mt-1">Recorded by {record.review.reviewer}</p>
            {record.review.note && <p className="body-2 text-muted whitespace-pre-wrap mt-3">{record.review.note}</p>}
            <details className="body-2 mt-3"><summary className="min-h-11 py-3 cursor-pointer">Read the field interpretation</summary><ul className="space-y-2 text-muted">{record.assessment.ecological_urgency.reasons.map((reason, i) => <li key={i}>{reason}</li>)}</ul></details>
            <a href={record.export_url} download className="body-2 inline-flex items-center min-h-11 underline underline-offset-4">Download this record ↗</a>
          </li>)}</ul>
        </section>
      </div>
    </article>
  )
}
