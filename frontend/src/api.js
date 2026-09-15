// Thin fetch wrapper. Everything is multipart/form-data because the capture
// endpoint takes a photo alongside the answers.

export async function submitObservation({ answers, recordClass, siteName, photo }) {
  const fd = new FormData()
  fd.append('answers_json', JSON.stringify(answers))
  fd.append('record_class', recordClass)
  if (siteName) fd.append('site_name', siteName)
  if (photo) fd.append('photo', photo)
  const r = await fetch('/api/observations', { method: 'POST', body: fd })
  if (!r.ok) throw new Error(`submit failed (${r.status})`)
  return r.json()
}

export async function getProtocol() {
  const r = await fetch('/api/protocol')
  if (!r.ok) throw new Error(`protocol failed (${r.status})`)
  return r.json()
}

export async function clarify(id, { questionId, question, field, response, disagrees,
                                    indicator, optionKey }) {
  const fd = new FormData()
  fd.append('question_id', questionId)
  fd.append('question', question)
  fd.append('field', field)
  fd.append('response', response)
  fd.append('citizen_disagrees', disagrees ? 'true' : 'false')
  if (indicator) fd.append('indicator', indicator)
  if (optionKey) fd.append('option_key', optionKey)
  const r = await fetch(`/api/observations/${id}/clarify`, { method: 'POST', body: fd })
  if (!r.ok) throw new Error(`clarify failed (${r.status})`)
  return r.json()
}

export async function getQueue() {
  const r = await fetch('/api/queue')
  if (!r.ok) throw new Error(`queue failed (${r.status})`)
  return r.json()
}

export async function getObservation(id) {
  const r = await fetch(`/api/observations/${id}`)
  if (!r.ok) throw new Error(`fetch failed (${r.status})`)
  return r.json()
}

export async function submitReview(id, { reviewer, decision, note, approvedForSummary = false, reviewedContentSha256 }) {
  const fd = new FormData()
  fd.append('reviewer', reviewer)
  fd.append('decision', decision)
  fd.append('note', note || '')
  fd.append('approved_for_summary', String(approvedForSummary))
  if (reviewedContentSha256) fd.append('reviewed_content_sha256', reviewedContentSha256)
  const r = await fetch(`/api/observations/${id}/review`, { method: 'POST', body: fd })
  if (!r.ok) {
    const detail = await r.json().catch(() => ({}))
    throw new Error(detail.detail || `Could not save review (${r.status})`)
  }
  return r.json()
}

export async function getSites(recordClass = 'authentic') {
  const r = await fetch(`/api/sites?record_class=${encodeURIComponent(recordClass)}`)
  if (!r.ok) throw new Error(`Could not load site summaries (${r.status})`)
  return r.json()
}
