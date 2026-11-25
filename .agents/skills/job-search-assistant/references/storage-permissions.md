# First-run storage and permissions

## Create and verify, do not just describe

Resolve the user's actual Desktop from their environment, including OneDrive/XDG redirection; display the path. A nonexistent registry Desktop or service-account home is not sufficient proof. If sources conflict, inspect existing locations and use the user-confirmed/observed Desktop, then pass its explicit path. Do not create a new unrelated Desktop tree because a guessed path does not exist.

After init and basic onboarding, run `python scripts/job_assistant.py setup-desktop --directory <actual-desktop>/Codex Job Search`. The helper copies private data from the current store, preserves old originals and dated history, creates personal/resumes/, personal/cover-letters/, daily/, the master report and a brief guide, and sets the chosen report directory. Dated case directories are created by artifact-dir when needed, not filled with fake application files. Missing transcripts, mail access and receipts stay missing; do not create placeholders implying they exist.

The command saves one ignored checkout-local personal/storage.json pointer to the canonical private data folder, only after successful copy, validation and render. Future helper commands automatically read that pointer, so the Desktop JSON is authoritative. Do not independently update a stale checkout snapshot. A repeated setup is idempotent and does not reapply jobs, erase facts or create duplicate records. Different destination files stop migration for review instead of being silently overwritten. The existing store can continue if setup fails before the pointer is published. Receipts and stable case IDs are preserved; this command is not a scheduler.

New structure:

```text
Codex Job Search/
  applications.md
  START_HERE.md or 使用说明.md
  daily/YYYY-MM-DD.md
  YYYY-MM-DD/J0001/             generated when a real case needs artifacts
  personal/
    profile.json
    applications.json
    consents.json
    experience.md
    resumes/
    cover-letters/
```

## Request only necessary access

First use existing access. `check-access` probes create/write/close/delete of its own temporary file in the report/data directories; it stores no credentials and grants nothing. Do not request access unconditionally at every run. If the actual operation is denied, request write access to the one chosen job-search directory with a clear purpose. Batch access needs within that directory. A nonexistent child folder may require the Desktop parent's create-directory permission once; request that only after a real parent-creation denial, create the selected child, and keep later access scoped to the child. Do not request all home folders or disable approvals to solve this.

Where the host offers a remembered/session/project permission, explain and let the user choose it. Verify the returned scope; a setting in profile.json, an OAuth connection, or an instruction saying 'always allow' cannot create OS/host permission. Do not claim permanent access if the tool grants only this turn. Do not edit global security settings or generate config claimed to be automatically active. Managed workspace policy may restrict persistence.

If the actual dialog offers only Allow once, accept that evidence: there is no Always option in that flow. Do not keep asking the user to find one or to repeat the same grant as a supposed permanent fix. Explain the limitation and offer a supported project/workspace location or host configuration outside this one-time prompt, without claiming it is already configured. Keep the chosen Desktop location until the user approves an alternative.

## Daily unattended readiness

Keep two states separate: (1) the task is scheduled and active; (2) the scheduled runtime can access its files and tools without asking. Before enabling a schedule, verify directory creation, check-access and render in the permitted environment, resolve absolute checkout/storage paths, and inspect the actual scheduler result. If a scheduler-context test is available, test the report-only path there without new applications; do not claim an ordinary chat test proves a background permission grant. If unavailable, state background access is not independently verified.

Each run loads the canonical pointer/profile, uses already available access, checks write access before application work, then updates existing files. On missing runtime access, record the permission blocker in an already-writable local status file and issue one focused notice; do not keep launching per-file approval requests, silently write to a stale snapshot or perform a submission that cannot be recorded. Resume once the scoped permission is restored. Separate employer consent, authentication, CAPTCHA and newly required facts may still need user participation; saved folder access does not waive those rules.

If persistent Desktop access is unavailable, offer a user-selected writable workspace location for canonical data/reports, with an optional manual Desktop export, or help the user choose the supported host permission settings. Never silently change the requested output location. The agent cannot guarantee always-on execution, saved permissions, browser sessions or third-party availability. Keep the machine/app available as required by the actual scheduler. See [official permissions](https://learn.chatgpt.com/docs/permissions) and [scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app).

## Readable output

The master/daily reports use a five-column overview with short Job/CV/Proof (岗位/简历/回执) links. Time, notes, blocker reasons, next actions and resume conditions use full-width paragraphs under each case. Link destinations and immutable evidence stay intact; shorten visible labels, not URLs or filenames on disk. Relative file links must resolve from both the master and daily directories, including spaces, parentheses and # characters. Historical daily documents remain preserved; do not reconstruct old outcomes from current state just to restyle them.
