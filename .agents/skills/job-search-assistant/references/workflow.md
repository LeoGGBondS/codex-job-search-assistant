# Find, screen, prepare, apply, track

## Discover

Use available search tools and employer career pages. Public Greenhouse, Lever, or Ashby pages can be sources where accessible; their names do not guarantee automation permission or a universal adapter. Read full current JDs and verify applications remain open. Never rank an unseen JD from a snippet alone. Search terms, job titles, locations, and new-grad/internship windows come from the local profile.

Respect each platform's applicable rules and access controls. Do not scrape or automate LinkedIn site interactions in this workflow. LinkedIn user-supplied JD text and links to corresponding employer jobs remain useful. Do not bypass sign-in restrictions, paywalls, browser security warnings, or anti-bot measures.

## Screen

Extract employer, title, stable job ID/link, location/work arrangement, type, level, dates, experience, required skills, authorization restrictions, and pay when stated. Distinguish confirmed hard mismatches, unknowns, and preferences. Provide concise fit evidence instead of invented match percentages. Do not reject just for missing preferred skills, ambiguous graduation-season labels, or refusal to sponsor when the candidate does not need sponsorship. Unknown GPA is not a failed GPA requirement; estimates cannot be entered as actual grades.

Record discovered candidates with the canonical job URL. Deduplicate before preparing or submitting. Skip clear mismatches with a reason; record skipped separately from an employer rejection. Favor evidence quality over hitting a volume target.

## Prepare

Use their original resume unchanged if suitable. When useful reorder projects/skills or edit a few supported bullets. Preserve the original and save the exact per-job submitted file. Do not create a cover letter unless required or requested. Use an available document/PDF workflow when editing those formats and inspect the result. Do not claim a PDF was created merely because a text draft exists.

## Apply

Check actual browser tools. If unavailable, prepare a local queue and explain the missing capability; do not claim standalone auto-apply. Review all required questions and use only confirmed answers. Optional demographic fields stay blank unless the user explicitly chooses responses. Stop only the affected application for unknown mandatory answers and continue others where possible.

Before sending personal data, follow the current tool's destination/data confirmation rules. A scoped consent record should contain company, destination domain, job ID(s), exact data categories, resume path/version, timestamp, and the user's confirming message/reference. It is an audit note, not permission to invent or widen authorization. Legal agreements, CAPTCHAs, account creation, and authentication requirements need whatever action-time confirmation/handoff the actual tool requires.

Run `python scripts/job_assistant.py gate --file work/candidate.json` immediately before submitting. A failed gate blocks submission. A passed gate checks only local duplication, status, and daily count; independently verify candidate eligibility, consent, URL, site rules, and current page state. Sequential execution is supported; do not run concurrent submitters against one local store. Never use hidden web endpoints or browser internals to bypass normal tool permissions.

After submission verify explicit receipt. Save confirmation URL, any application number, screenshot when supported, and the timestamp with timezone. Record `submission_unknown` if unclear, then inspect receipt/page state before any manual decision about retry. Do not blindly click again. If file upload is unavailable, try the browser's documented chooser mechanism; do not silently paste a materially different application or omit the resume.

## Records

Use `python scripts/job_assistant.py record --file work/candidate.json`, then `python scripts/job_assistant.py render`. Input fields: company, role, url, job_id (optional), status, notes, resume_path, submitted_at, submission_evidence. Optional id is stable if supplied; the helper deduplicates by company/job ID or canonical URL. Supported statuses include discovered, screened, skipped, drafted, needs_input, ready, submitted, submission_unknown, rejected, interview, withdrawn.

`submission_evidence` is required for submitted records. Do not demote or overwrite a confirmed submitted record accidentally. Preserve submitted_at and evidence if later recording interview/rejected/withdrawn. Daily counts include later outcome changes, so changing status cannot reset the submission cap. Rebuild the Markdown log after every material update and at the end of a run. Report actual successful submissions, remaining queue, and concrete blockers.
