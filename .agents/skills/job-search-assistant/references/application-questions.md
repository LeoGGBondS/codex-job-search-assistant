# Application-question handling

Read this when a form asks questions beyond the initial intake. Learn reusable question meanings and browser procedures; do not publish a real candidate's answers, employer-specific private responses, receipt data or verification codes.

## Resolve facts without repeated interviews

| Question family | Handling |
|---|---|
| Current city/state/country | Ask the candidate if unknown. A target city, relocation preference or university address is not their residence. Store current_location separately from target_locations. |
| Office ranking | Use the user's explicit ordering. When the user accepts all locations, select an offered any-office choice rather than inventing a ranking. Ask only if a ranking is required and no suitable flexibility option exists. |
| Engineering ranking/archetype | The user can delegate resume-based ranking. If delegated, map actual experience to the available choices, explain the proposed order, and preserve it in job-specific records. Do not invent unsupported options or call an available category an exact synonym for a different one. |
| Earliest start / quarter | Combine actual availability with this role's requirements, including whether it requires completion of the current degree before starting. Choose a period containing a truthful start date; do not treat readiness to work as an already-completed degree. |
| Education level and dates | Distinguish current graduate enrollment from a completed undergraduate degree. Use the actual institution, degree, discipline and dates. A form's bachelor's-enrollment requirement may make a graduate candidate a stretch match; disclose that uncertainty instead of silently treating it as met. |
| GPA, transcript and test scores | Separate actual grades, estimates and unpublished grades. Leave optional fields blank when requested; never fill an estimate as actual GPA. A mandatory transcript or unavailable official answer blocks that application, not every other application. |
| Active offers / deadlines | Ask explicitly if unknown. Never turn silence into no deadline. Store the confirmed answer with date and context, because it can change. A text field phrased 'if yes' can still be mandatory. |
| Current/previous employer and title | Use resume-backed experience, explicitly recognizing an internship and previous employment. Do not imply a past employer is current employment. |
| Prior company employment, internship count, academic awards | Use confirmed history; a resume's silence does not prove no previous work or no awards. Ask if mandatory and unknown. Never invent a second internship to meet a threshold. |
| How did you hear about the job? | Use the actual discovery source. When found through web search and no matching option exists, select Other if offered. Do not claim a referral, conference attendance or LinkedIn discovery that did not occur. |
| Work authorization / sponsorship | Reuse confirmed country-specific answers and distinguish current authorization from future sponsorship. Keep permanent residency, citizenship and security clearance separate. |
| Self-identification | Leave optional demographic fields blank unless the user chooses otherwise. If required, use a non-disclosure option only within the user's selected preferences/tool rules; never guess ethnicity, disability, veteran status or gender. |

Ask a small bundle of missing questions; continue other independent applications while waiting. A factual answer to a recruiter-coordination question is not a legal commitment. Agreements, privacy attestations, authentication and challenges still follow the active tool's actual confirmation rules.

## Inspect the live form, not just visible stars

A visual asterisk can be absent even when runtime validation marks a field required. Inspect labels, instructions and conditional controls before submit. If validation explicitly rejects a missing field, treat that as a known non-submission, collect the missing fact, correct it, then submit again. If a request instead has an ambiguous network/result state, record submission_unknown and verify before any retry. A missing confirmation is never proof of success.

Match selection values to visible options. For example, an application may label a country with its abbreviation rather than its full name; clear an unsuccessful filter and read the actual options. Typing a location string without selecting the matching city suggestion is not a completed location field.

## Uploads and email verification

Use the browser's documented file chooser. If a public application is embedded and upload events are unavailable, the page-exposed public employer/ATS application URL may be opened directly within the same approved destination and data scope. Preserve the same job ID, avoid hidden endpoints, and do not submit both copies. Recheck the complete form before using the direct version.

When a site sends a code to the user's email, report that the application is pending verification, not submitted. Prefer letting the user complete the step; if they provide the code for this specific step and current tool rules permit entry, use it only there. Follow action-time confirmation requirements for CAPTCHAs or human challenges. Do not retrieve codes from unrelated accounts, bypass verification, store codes in a profile/consent/history file, or publish them.

For one-character verification boxes, respect maxlength and the component's keyboard behavior. If bulk fill is not accepted, inspect the visible field state, clear using normal selection/backspace, and enter with normal key events. Do not mutate page internals or force-enable a disabled submit button. Follow the UI for expired/incorrect codes; never guess codes or automatically request repeated codes.

## Improve this reusable assistant

When the user requests shared-agent improvements, generalize question families and procedures in this file. Keep personal answers only in ignored personal/profile.json, experience.md, consents.json or local application records. Do not hard-code a particular person's city, education, grades, authorization, rankings or no-deadline answer as defaults. Validate helper changes, run the public-source preflight, and publish only reusable code and guidance.
