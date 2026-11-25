# Optional recurring operation

Only configure a schedule when the local user requests it. Ask local time, IANA timezone, daily submission cap, and relevant preferences if not already confirmed. Store the choices under profile.schedule; it begins disabled.

Discover the Codex Automations tool (search for automation_update) and follow its current schema. Prefer a heartbeat on the user's active chat unless they ask for separate runs. Use the actual tool to create/update the automation; never present an instruction file as proof that a schedule is running. If unavailable, leave scheduling inactive, explain the limitation, and support manual runs. Do not silently install cron jobs, background processes, CI auto-submit jobs, or use the publisher's automation ID.

The automation's prompt must use the absolute path of THIS checkout, read the latest local profile/experience/history, discover and screen public jobs, lightly edit only as needed, and execute only authorized supported submissions within the chosen daily cap. It must preserve date/GPA distinctions, scoped confirmation, tool/site constraints, deduplication, uncertain-submission handling, and verified receipts. Run the local record renderer and provide the output document link after real changes. The cap is a maximum, never a promised throughput.

Changing profile.schedule alone does not create a live scheduler. Mark enabled only after the scheduler actually reports success, store its returned ID locally, and keep the scheduler and profile consistent on updates. Explain any required logged-in session, machine availability, tool availability, or runtime constraints based on what the scheduler actually documents; do not promise always-on operation. Enable no schedule during the initial download/bootstrap.

Read the saved language, application mode and output directory each run. General mode reuses/lightly edits; precise mode tailors and verifies a one-page ATS-friendly export from any-length sources. Reuse the factual experience bank; do not reread all resumes or the entire report when working on one pending ID.

Refresh the same Desktop master report and current local-date daily record after each run, including a run with no new successful submissions. Keep historical daily files. Save all new artifacts/receipts in local-date/case-ID directories. Pending IDs can be resumed after the user provides materials; do not repeatedly attempt a still-blocked case on each scheduled run. Scheduling does not waive consent or receipt checks. The output helper does not itself create a schedule.

## Optional email sync and blockers

Include email sync in a recurring prompt only after explicit user opt-in: read references/email.md, verify the current connector/account, search within the agreed job-mail scope, ingest minimal deduplicated events and refresh reports. No connection/permission means no email feature. Never put codes or credentials in the prompt or output. Verification assistance remains separately opt-in and subject to actual tool rules. Email access does not permit sending replies. A connector failure should not prevent unrelated job discovery/submissions.

Use references/screening.md for early material checks, freshness and effort prioritization. Record every blocked/unsupported/uncertain attempt with a reason, next action and retry condition. Report pending IDs as well as successes; do not repeatedly attempt unresolved cases or silently omit site failures.
