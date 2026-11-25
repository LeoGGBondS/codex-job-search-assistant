# Find, screen, prepare, apply, track

## Discover

Use available search tools and employer career pages. Public Greenhouse, Lever, or Ashby pages can be sources where accessible; their names do not guarantee automation permission or a universal adapter. Read full current JDs and verify applications remain open. Never rank an unseen JD from a snippet alone. Search terms, job titles, locations, and new-grad/internship windows come from the local profile.

Respect each platform's applicable rules and access controls. Do not scrape or automate LinkedIn site interactions in this workflow. LinkedIn user-supplied JD text and links to corresponding employer jobs remain useful. Do not bypass sign-in restrictions, paywalls, browser security warnings, or anti-bot measures.

## Screen

Extract employer, title, stable job ID/link, location/work arrangement, type, level, dates, experience, required skills, authorization restrictions, and pay when stated. Distinguish confirmed hard mismatches, unknowns, and preferences. Provide concise fit evidence instead of invented match percentages. Do not reject just for missing preferred skills, ambiguous graduation-season labels, or refusal to sponsor when the candidate does not need sponsorship. Unknown GPA is not a failed GPA requirement; estimates cannot be entered as actual grades.

Record discovered candidates with the canonical job URL. Deduplicate before preparing or submitting. Skip clear mismatches with a reason; record skipped separately from an employer rejection. Favor evidence quality over hitting a volume target.

## Prepare

Use profile.application_mode (or the user's per-case override). Accept multi-page resumes and multiple source files in both modes. Read every relevant page; cache a factual experience bank locally so later jobs do not require reprocessing the whole source. Keep all originals unchanged.

### General applications

Reuse the current resume when suitable. Only reorder or lightly reword supported experience when useful. Do not default to a cover letter or a full rewrite. This is the efficient mode; it does not promise a new one-page export for every job.

### Precise applications

1. Read the full JD and all relevant source resume pages. Match concrete requirements to evidence, distinguishing mandatory qualifications from preferences.
2. Select the strongest truthful experience, skills and projects for that job. Use relevant JD terminology only where factually supported; never add a skill, credential, result or number because a keyword is present.
3. Produce a one-page resume in the JD's application language. Use a single column, ordinary headings, selectable text, readable body size and clear chronology. Avoid graphics, text boxes, nested tables and keyword stuffing. Prioritize and shorten content before reducing font size or margins. ATS-friendly conventions improve readability but do not guarantee an ATS score or interview.
4. Use available document/PDF authoring tools. Render the exported file, verify page count equals one, inspect for clipping and legibility, then extract its text to check section order, dates, contact information and key content. Reflow and repeat if it spills onto a second page. If required facts cannot fit legibly, ask which lower-priority content may be omitted; do not upload a multi-page file while claiming it is the precise one-page version.
5. Save the file and a brief factual change record under the configured report directory/local-date/case-ID. Preserve the exact submitted version. Before transmission, honor any constraint limiting consent to an original unchanged resume.

Use an available document/PDF workflow when editing those formats; if the environment cannot create/verify an export, explain that limitation rather than claiming success. A text draft is not a verified PDF. Reports and application material can use different languages. Do not create a cover letter unless required or requested.

## Apply

Check actual browser tools. If unavailable, prepare a local queue and explain the missing capability; do not claim standalone auto-apply. Review all required questions and use only confirmed answers. For new/conditional questions, use [application-questions.md](application-questions.md); ask only unresolved blocking facts and save confirmed reusable answers locally. Optional demographic fields stay blank unless the user explicitly chooses responses. Stop only the affected application for unknown mandatory answers and continue others where possible.

Before sending personal data, follow the current tool's destination/data confirmation rules. A scoped consent record should contain company, destination domain, job ID(s), exact data categories, resume path/version, timestamp, and the user's confirming message/reference. It is an audit note, not permission to invent or widen authorization. Legal agreements, CAPTCHAs, account creation, and authentication requirements need whatever action-time confirmation/handoff the actual tool requires.

Run `python scripts/job_assistant.py gate --file work/candidate.json` immediately before submitting. A failed gate blocks submission. A passed gate checks only local duplication, status, and daily count; independently verify candidate eligibility, consent, URL, site rules, and current page state. Sequential execution is supported; do not run concurrent submitters against one local store. Never use hidden web endpoints or browser internals to bypass normal tool permissions.

After submission verify explicit receipt. Save confirmation URL, any application number, screenshot when supported, and the timestamp with timezone. Record `submission_unknown` if unclear, then inspect receipt/page state before any manual decision about retry. Do not blindly click again. If file upload is unavailable, try the browser's documented chooser mechanism; do not silently paste a materially different application or omit the resume.

## Records

Use `python scripts/job_assistant.py record --file work/candidate.json`, then `python scripts/job_assistant.py render`. Input fields: company, role, url, job_id (optional), status, notes, resume_path, submitted_at, submission_evidence. Optional id is stable if supplied; the helper deduplicates by company/job ID or canonical URL. Supported statuses include discovered, screened, skipped, drafted, needs_input, ready, submitted, submission_unknown, rejected, interview, withdrawn.

`submission_evidence` is required for submitted records. Do not demote or overwrite a confirmed submitted record accidentally. Preserve submitted_at and evidence if later recording interview/rejected/withdrawn. Daily counts include later outcome changes, so changing status cannot reset the submission cap. Rebuild the Markdown log after every material update and at the end of a run. Report actual successful submissions, remaining queue, and concrete blockers.

## Resume a pending case

Prefer the stable short case ID over repeating full context. `lookup J0001` or lookup with the original URL returns one record. `resume J0001 --material <local-file>` attaches supplied local material and flags a review request; it does not submit, erase blockers, or imply every prerequisite is satisfied. Answers may be provided through --answers-file when explicitly confirmed by the user.

Read that case's blocking_items and the supplied materials, revisit the live JD and application status, and update only the resolved facts. Ask only remaining necessary questions. Mark ready and clear blockers only after verifying they are resolved, then use the usual consent, gate, submission and receipt process. If the job is closed, record that reason. Confirmed submissions and submission_unknown cases cannot be reapplied automatically. A request to provide an additional document to an already-submitted employer is a distinct follow-up, not a fresh application.

## Dated localized outputs

Write human-facing headings, status labels, blocker descriptions and summaries in profile.language (zh/en); retain proper names and actual job titles. Machine JSON keys stay stable. The helper localizes its own labels, not arbitrary candidate text, so the agent writes notes in the chosen report language.

`render` updates report-root/applications.md and report-root/daily/YYYY-MM-DD.md in the user's timezone. Each row has its short case ID and update/submission dates. The master contains all records; the daily document contains cases created, changed or submitted that date. Refresh the same day's file during the day and preserve previous days. Use `artifact-dir J0001` for the dated material/receipt directory. If Desktop access is denied, obtain the exact needed permission or a user-chosen alternative; never silently claim files are on the Desktop.
