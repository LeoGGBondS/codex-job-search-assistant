# Optional recurring operation

Only configure a schedule when the local user requests it. Ask local time, IANA timezone, daily submission cap, and relevant preferences if not already confirmed. Store the choices under profile.schedule; it begins disabled.

Discover the Codex Automations tool (search for automation_update) and follow its current schema. Prefer a heartbeat on the user's active chat unless they ask for separate runs. Use the actual tool to create/update the automation; never present an instruction file as proof that a schedule is running. If unavailable, leave scheduling inactive, explain the limitation, and support manual runs. Do not silently install cron jobs, background processes, CI auto-submit jobs, or use the publisher's automation ID.

The automation's prompt must use the absolute path of THIS checkout, read the latest local profile/experience/history, discover and screen public jobs, lightly edit only as needed, and execute only authorized supported submissions within the chosen daily cap. It must preserve date/GPA distinctions, scoped confirmation, tool/site constraints, deduplication, uncertain-submission handling, and verified receipts. Run the local record renderer and provide the output document link after real changes. The cap is a maximum, never a promised throughput.

Changing profile.schedule alone does not create a live scheduler. Mark enabled only after the scheduler actually reports success, store its returned ID locally, and keep the scheduler and profile consistent on updates. Explain any required logged-in session, machine availability, tool availability, or runtime constraints based on what the scheduler actually documents; do not promise always-on operation. Enable no schedule during the initial download/bootstrap.
