# Codex Job Search Assistant

English | [简体中文](README_CN.md)

Use Codex to find suitable jobs, prepare applications, and keep a private application log. A guided first conversation collects your own resume and preferences.

This repository contains a **Codex skill and local recordkeeping tools**. The Python helper does not require a model API key. Your Codex account and available search, browser, document, and scheduling tools provide the agent capabilities. No personal information from the publisher is included.

## Get started

1. Download and extract this repository, or clone it locally.
2. Open the folder as your workspace in Codex.
3. Say **“Initialize my job assistant.”** You can also invoke **`$job-search-assistant`** explicitly.
4. Choose English or Chinese output and General or Precise application mode. The assistant then asks for your resume, target roles, locations, graduation/start dates, and work-authorization answers as needed. Multi-page resumes and multiple source files are accepted; confirmed information is not repeatedly requested.
5. The assistant configures a **Codex Job Search** folder on your actual Desktop. Choose a time, timezone, and daily cap if you want scheduled runs. Otherwise, run it manually.

A Chinese initialization message starts onboarding in Chinese; an English message starts in English. You can override the language or change it later. Application materials follow the JD's language independently of the report language.

Downloading the repository does not launch a questionnaire, enable a schedule, or submit applications. Begin a conversation in Codex to start onboarding. Repository guidance lives in `AGENTS.md` and `.agents/skills/job-search-assistant/`; see the [official skill documentation](https://learn.chatgpt.com/docs/build-skills) for loading behavior. If the skill is not selected automatically, invoke `$job-search-assistant`.

## Application modes

| Mode | Behavior |
|---|---|
| **General** | Reuse your existing resume when suitable; make small, relevant wording or ordering changes when helpful. |
| **Precise** | Read all relevant source pages and tailor a truthful, JD-specific, one-page resume using ATS-friendly formatting conventions. Verify the exported page count, readability, and text order before upload. |

Precise mode requires document/PDF tools available in your Codex environment. It preserves your originals and the exact submitted version. It does not invent skills or achievements, guarantee an ATS score, or promise an interview. A text draft is not a verified PDF. Cover letters are prepared only when required or requested.

## What it does

- Discover public job postings based on your preferences and read the full JD before screening.
- Distinguish hard requirements, preferred qualifications, and unknown information.
- Prepare materials and use available browser tools to execute authorized applications.
- Track each job's status, dates, submitted resume, confirmation evidence, and missing information.
- Create daily automations when requested and supported by your Codex environment.

The Python helper itself does not search the web, operate a browser, or create a scheduler. Without browser tools, the assistant prepares an application queue and explains the missing capability. Daily caps are limits, not promised application counts.

LinkedIn scraping and automated site interactions are outside this workflow; supplied JD text and links to employer applications remain useful. A new employer's first receipt of personal data, verification challenges, account flows, or legal agreements may require confirmation or your participation under the active tool's rules. The agent does not bypass these requirements or guess unknown answers.

## Resume a pending case

Each application has a stable short ID such as **J0001**. Say **“Resume J0001”** and attach the missing material, such as a transcript. Original job links also work, but short IDs usually need less context than long URLs.

The assistant reads that case, checks the new material and current JD, resolves remaining blockers, and continues the application when ready. Supplying a file does not itself submit an application. Confirmed submissions and uncertain results are checked before any further action; they are never automatically reapplied.

## Desktop reports and language

New users get one stable Desktop folder:

```text
Codex Job Search/
  applications.md
  daily/
    YYYY-MM-DD.md
  YYYY-MM-DD/
    J0001/
      resume.pdf
      confirmation.jpg
```

- `applications.md` is the master log and updates in place.
- `daily/YYYY-MM-DD.md` records cases created, changed, or submitted on that date in your timezone. Today's file refreshes during the day; older dates are preserved.
- Materials and receipts are grouped by local date and case ID.
- Headings, statuses, notes, and summaries follow your selected report language. Proper names and actual job titles are retained.
- Reports refresh when a run executes, including daily scheduled runs after a real schedule is configured. Installing the repository alone does not create daily updates.

The assistant resolves your actual Desktop, including supported redirected Desktop paths. If that location is unavailable or requires access, choose an explicit directory or grant the specific access requested by your environment. It will not silently claim a different folder is your Desktop.

Existing installations retain their current output directory and history during migration. Ask Codex to run `configure --output-dir desktop` to send future reports to the Desktop; old reports are not deleted.

## Keep candidate data private

| Location | Contents | Published to GitHub by default? |
|---|---|---|
| `personal/` | Source resumes, profile, experience bank, consent records, raw application history | No |
| Desktop `Codex Job Search/` | Master/daily reports, application materials, receipts | No; outside the repository |
| `outputs/` | Legacy or explicitly selected in-repository output directory | No |
| `work/` | Temporary inputs and intermediate files | No |
| `.agents/`, `scripts/`, `tests/` | Reusable workflow and recordkeeping tools | Yes |

`.gitignore` protects normal commits, not forced additions, files already committed, or unrelated sync services. Run the publishing check and review staged files before sharing changes. Never force-add candidate data. Applying still sends the approved information to the employer's application system; local storage does not mean an application is never transmitted.

## Optional local commands

Python 3.10+ is required for the recordkeeping helper. Codex can run these commands for you, using its bundled Python if available. On Windows, install the timezone dependency with `python -m pip install -r requirements.txt` if needed.

```sh
python scripts/job_assistant.py init --message "Initialize my job assistant"
python scripts/job_assistant.py configure --language en --mode general --output-dir desktop
python scripts/job_assistant.py status
python scripts/job_assistant.py record --file work/candidate.json
python scripts/job_assistant.py gate --file work/candidate.json
python scripts/job_assistant.py render
python scripts/job_assistant.py lookup J0001
python scripts/job_assistant.py resume J0001 --material personal/transcript.pdf
python -m unittest discover -s tests -v
python scripts/check_public.py
```

The resume-material path above is an example; supply your actual local file. Use `configure --language zh --mode precise` to switch to Chinese and Precise mode, or `--language en --mode general` for English and General mode.

See [examples/candidate.json](examples/candidate.json) for a synthetic record. Keep real inputs in `work/`. A submitted record requires a timezone-aware `submitted_at` and explicit `submission_evidence`. An unclear result uses `submission_unknown` and cannot be retried automatically.

`gate` checks local state, duplicates, and the daily cap. It does not establish eligibility, consent, or site permission. Use one sequential application runner per local store; do not run concurrent submitters.

## Validation and contributions

The tests cover local profiles, deduplication, receipt requirements, timezone-based caps, language selection, dated reports, and pending-case resumption. They do not prove AI job matching, resume quality, or live browser submission works on every site.

Contribute reusable code, documentation, and synthetic fixtures only. Do not include real candidate data. Licensed under the [MIT License](LICENSE).
