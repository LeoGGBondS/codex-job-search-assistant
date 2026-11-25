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

## Pending obstacles, optional materials and email

Every unfinished attempt is recorded with a **reason, next action and retry condition**: email verification, login/CAPTCHA, missing transcript/GPA, unanswered required questions, upload problems, unavailable tools, site failures, missing consent and unforeseen obstacles. Unclear submission results remain **Receipt unverified** in the pending section and are checked before any retry. Codes are never saved. Continue with the short case ID after resolving the blocker; successful applications are never automatically reapplied.

During initialization, the assistant also offers **optional transcripts/supporting documents** and **optional Gmail or other supported mailbox access**. Both can be skipped. Keeping a transcript locally does not authorize sending it to every employer. Early screening checks required materials, eligibility, posting freshness and form effort before spending time tailoring.

**We recommend a separate email account for job searching.** It reduces unrelated messages to process and limits exposure of personal mail. This is optional. Providing a contact address does not grant inbox access. Email features remain off unless you explicitly opt in and complete an available provider connector's authorization flow. A job-only query/label reduces what the assistant reads but does not narrow a provider's underlying OAuth permissions; review the actual consent screen.

With working authorized email tools, the assistant reads job-related messages within the agreed scope and organizes acknowledgements, assessments, interviews, rejections, offers, deadlines and next actions in the existing reports. Ambiguous messages remain unlinked for review. It stores minimal summaries/message references, not complete mailboxes or verification codes. Verification assistance is a separate opt-in and still follows the current tool's rules. No mailbox connection means **no email features**; job discovery, applications and manual updates still work. No automatic replies are sent.

This repository does **not** include a Gmail OAuth client, credentials or a standalone mail reader. The installed Codex environment must supply a compatible connector; if none is available, email access stays unavailable. `configure-email` records preferences only, not a connection. Disable using `python scripts/job_assistant.py configure-email --disable`; revoke provider access separately in the provider's settings. Existing private history is retained.

The helper also provides `block` for structured obstacles and `email-event --file work/event.json` for validated metadata ingested by the agent. Email categories alone never change an application's submission/outcome status. See [email workflow](.agents/skills/job-search-assistant/references/email.md) for the schema and [screening checklist](.agents/skills/job-search-assistant/references/screening.md) for ranking rules. Screening workflow ideas were informed by [ApplyPilot](https://github.com/yvonnehe772/applypilot); we do not claim those ideas as unique features.

## Job sources and company preferences

At setup, the assistant asks an optional bundled question about **company stage, employee count, industry, target companies and companies to avoid**. Choose several or “no preference”; change them later. Startup preference and company size are separate. Preferences guide ranking unless you explicitly make them hard constraints; unknown company data is not invented. Existing users can add these preferences without repeating setup.

Suggested source mix: **employer career pages** for current JDs; **LinkedIn** for broad leads/alerts; **Greenhouse/MyGreenhouse, Lever and Ashby** for employer listings and applications; **Wellfound and YC Jobs** for startup discovery; **Handshake or your university's portal** for relevant internships/new-grad hiring. Greenhouse also offers a candidate search/tracking portal, while Lever/Ashby are primarily employer recruiting systems. A source recommendation does not install an adapter or authorize site automation, inbox access or account creation. LinkedIn automated site interactions remain outside this workflow. See the [source and company screening guide](.agents/skills/job-search-assistant/references/screening.md) for official links and access limits.
