# Codex Job Search Assistant

Use `.agents/skills/job-search-assistant/SKILL.md` for candidate onboarding, job discovery, screening, applications, and tracking. All paths below are relative to this repository; never inherit the publisher's profile or schedule.

When the user starts using the assistant, check `personal/profile.json`. If it is missing or onboarding is incomplete, begin the conversational intake in the skill's `references/onboarding.md`. Ask in the user's language and save only their confirmed answers. A coding/maintenance request is not an instruction to collect a resume.

Candidate data belongs in ignored `personal/`, generated application files in ignored `outputs/`, and scratch files in ignored `work/`. Never commit resumes, contact details, candidate profiles, consent records, screenshots, or application history. Do not force-add ignored files. Before publishing changes run `python scripts/check_public.py` and inspect the staged file list.

Python 3.10+ supports local records; `python -m unittest discover -s tests -v` runs tests. Use the bundled Python executable if `python` is unavailable. This repository does not install a browser, log into job boards, run a scheduler, or submit applications by itself. Check the actual Codex tools and their permission rules before promising these capabilities.
