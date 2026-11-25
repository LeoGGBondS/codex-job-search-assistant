# Screening before expensive preparation

Read the current full JD and accessible application requirements before tailoring or uploading. Use profile.screening_policy as adjustable defaults, never as fabricated candidate preferences. First collect a small set of strong leads; spend effort on likely eligible, completable applications rather than counting clicks.

## Eligibility and fit

Record location/onsite expectations, employment type, graduation window, degree level, experience, mandatory skills, work authorization and explicitly stated pay. Compare against confirmed candidate facts. Clear hard mismatch → skipped with evidence; an unknown mandatory fact/material → needs_input, not rejected. Preferred skills are a ranking factor. Explain fit with two or three source-backed facts and any gaps; do not invent percentages.

Inspect required transcripts, actual GPA, portfolio, essays, account setup and verification before generating a resume. A role restricted to currently enrolled BS students is not automatically a match for an MS candidate. Preserve ambiguous cases for review rather than changing education dates or inferring qualifications. If pay or commute constraints are unknown, do not invent them; collect only if relevant.

## Freshness and effort

Start with postings demonstrably published in the past 24 hours; expand to 48 hours when too few fit, then to older still-open strong matches. Unknown publication time means unknown, not fresh. Never drop an excellent older job solely because of age. Persist observed published_at/checked_at and the source when available; recheck openness before submitting.

Among similarly suitable roles, prioritize forms supported by current tools that reuse available materials, do not require a new account, and have at most one custom question. Record the actual question count, required materials and account/verification burden, not an assumed ATS-wide rating. More complex but strong matches can still be selected; defer the affected case with the specific reason and next action if it cannot be completed now. Never spend indefinitely retrying a form to hit a daily target.

Optional screening fields on a job record: screening = {fit_evidence: [], gaps: [], checked_at, published_at, publication_source, required_materials: [], custom_question_count, account_required, effort_notes, priority_reason}. These are observations and ranking evidence, not an ATS score. Store concise notes in the chosen report language. Reuse role-specific factual resume variants in general mode and the local answer bank; create new precise exports only for selected roles.

## Learning from outcomes

Review repeated blockers after a run. Propose a reusable answer or material once, scoped to its meaning; do not silently generalize employer-specific answers. Ask before changing user preferences. Report confirmed submissions, pending reasons and useful next actions, including runs with zero successes.

The emphasis on phased screening, freshness and application effort was informed by [ApplyPilot's setup workflow](https://github.com/yvonnehe772/applypilot/blob/main/references/setup-workflow.md) and [application playbook](https://github.com/yvonnehe772/applypilot/blob/main/references/application-playbook.md). This reference is an independently written adaptation of those workflow ideas; no browser implementation is imported.

## Company preferences and evidence

Use profile.company_preferences for discovery query variants and ranking, alongside role/location/level. Treat preferred stages, size bands, industries and target companies as soft boosts unless explicitly listed as hard constraints; apply excluded_companies as explicit exclusions. No preference or a skipped question means broad coverage. Do not silently narrow every query to startups or only the user's named companies. Search beyond the target list unless the user says “only”.

Do not infer headcount, funding stage or industry from the ATS vendor, company name or a job title. Prefer current company disclosures/career pages and clearly dated reliable company profiles; record source and checked_at for stage/headcount observations under screening.company_evidence. Employee counts can be ranges or estimates; preserve uncertainty. Unknown or stale size/stage stays unknown, with no invented match. If an explicit hard company constraint cannot be verified, queue only that affected case for review; a soft preference with missing evidence should not block an otherwise suitable job. Re-evaluate after preference changes without reopening submitted applications.

## Suggested discovery sources

These are workflow recommendations, not installed integrations, a complete job index, or evidence of broad ATS support. Select sources based on the candidate's goals and available tools. Recheck each source's current capabilities/access rules when needed. Keep discovery source URLs separately from the canonical employer application URL, so cross-postings deduplicate.

| Source | Suggested use | Execution limit |
|---|---|---|
| Employer career pages | Verify the live JD and actual application destination; maintain a user-approved target-company watchlist | Read accessible public pages; do not invent company-specific adapters |
| [LinkedIn](https://www.linkedin.com/help/linkedin/answer/a511279/job-alerts-on-linkedin?lang=en) | Broad discovery, job alerts and user-provided leads | No LinkedIn scraping/automated site interaction in this workflow; use supplied JD text, permitted public search leads or separately authorized alert emails, then find the employer page |
| [Greenhouse / MyGreenhouse](https://support.greenhouse.io/hc/en-us/articles/43418495049499-MyGreenhouse-FAQ-for-Candidates) | Employer-hosted jobs plus the MyGreenhouse candidate portal for discovery/applications/tracking | Do not assume all employers participate in the portal or every form behaves identically; verify each job/receipt |
| [Lever](https://www.lever.co/) / [Ashby](https://www.ashbyhq.com/) | Employer-hosted career pages and application forms | ATS vendors, not a guarantee of an exhaustive cross-company search or supported automation; inspect the actual page |
| [Wellfound](https://wellfound.com/jobs/) | Add startup-focused roles to the shortlist | Confirm seniority and startup fit; no assumed account/session or supported automatic application |
| [YC Jobs](https://www.ycombinator.com/jobs) | Discover roles at YC startups and build a startup company watchlist | Filter role/level carefully; YC affiliation is not evidence of current headcount, funding or new-grad suitability |
| [Handshake](https://joinhandshake.com/students/) / university career portal | Internship, early-career and campus recruiting leads when relevant | User's own institution/account only; authenticated access depends on tools and permission, with no automatic login promise |

For a general software internship/new-grad search, combine broad discovery, university opportunities if applicable, and employer pages; add startup sources according to the user's preferences. Prioritize job fit and reliable completion over a particular ATS brand. No fixed source percentages or submission guarantees.
