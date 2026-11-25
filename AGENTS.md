# Codex Job Search Assistant

Use `.agents/skills/job-search-assistant/SKILL.md` for candidate onboarding, job discovery, screening, applications, and tracking. All paths below are relative to this repository; never inherit the publisher's profile or schedule.

When the user starts using the assistant, check `personal/profile.json`. If it is missing or onboarding is incomplete, begin the conversational intake in the skill's `references/onboarding.md`. Start in the initialization message language (Chinese for “帮我初始化求职助手”, English for English); offer a language choice and general/precise application modes. Save the selected preferences and only confirmed candidate answers. A coding/maintenance request is not an instruction to collect a resume.

Candidate data belongs in ignored `personal/`, generated application files and dated reports in the configured Desktop folder (or the explicitly selected report directory), and scratch files in ignored `work/`. Never commit resumes, contact details, candidate profiles, consent records, screenshots, or application history. Do not force-add ignored files. Before publishing changes run `python scripts/check_public.py` and inspect the staged file list.

Python 3.10+ supports local records; `python -m unittest discover -s tests -v` runs tests. Use the bundled Python executable if `python` is unavailable. This repository does not install a browser, log into job boards, run a scheduler, or submit applications by itself. Check the actual Codex tools and their permission rules before promising these capabilities.

For each pending application, use its short case ID and case-specific lookup to minimize context. Providing a new document resumes that case for prerequisite review; it does not permit duplicate submissions. New profiles default to Desktop reports; older profiles migrate without moving files. Honor filesystem permissions before writing Desktop outputs.

All obstacles, including email verification and unforeseen tool/site errors, must be recorded with reason, next action and retry condition; unclear submission results remain submission_unknown. Offer optional transcripts and separately authorized email access at setup. Email tracking defaults off; a contact email or local opt-in setting is not a connected inbox. Read the skill references screening.md and email.md when relevant. Maintenance work must never connect/read the publisher's mailbox.

Initialization must create and verify the chosen Desktop folders/files using setup-desktop, not just configure a path. Its ignored personal/storage.json points helper commands at canonical private data. Read references/storage-permissions.md for scoped access and scheduled-run readiness. Existing access is reused; no unconditional daily permission requests or claims that a turn grant is permanent. Overview links are short; notes and recovery instructions are full-width.
