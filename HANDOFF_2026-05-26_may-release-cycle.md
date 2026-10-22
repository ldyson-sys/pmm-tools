# Maximizer Release Automation — Session Handoff
_Session dates: May 26-27, 2026 (continued across two sittings)_
_Scope: May 2026 release execution + structural cleanups + routine rework + image hosting pivot_
_Prior handoff: `HANDOFF_2026-05-25_routine-email.md`_

---

## TL;DR

- **May 2026 release: SENT.** Zendesk article published, Resend broadcast sent to the Release Notes audience. Cycle complete.
- **Workflow shifted to manual-kickoff.** Cron routine is now a reminder, not an unattended runner. Workflow file rewritten accordingly.
- **In-app notification step removed entirely** (Zendesk Announcements requires Enterprise plan).
- **Heading-based feature classification implemented** in workflow file (`Release Notes?` column = master filter; H1 heading = type).
- **Image hosting pivoted: WordPress KILLED, HubSpot LIVE.** WP admin denied the request. HubSpot Files API tested end-to-end (smoke test upload succeeded, URL serves via Cloudflare CDN). `resources/hubspot_upload.py` committed. Workflow file Step 3a still pending.
- **`~/CLAUDE.md` updated** with Lewis's full writing-style and behavioural instructions (mirrors claude.ai web settings, which do not auto-sync to Claude Code).

---

## May 2026 release — COMPLETE

### Generated in this session
Location: `output/2026-05-release/`

| File | Size | Status |
|---|---|---|
| `zendesk_article.md` | 11 KB | Published to Zendesk |
| `email_draft.html` | 33 KB | Sent via Resend |
| `email_subject.txt` | 81 B | "Coming Soon: IQ Boost in Outlook, Fireflies, and Smarter Email Sync – May 2026" |
| `release_payload.json` | 2.6 KB | Final state: broadcast + Zendesk IDs recorded |

### Resend broadcast (SENT)
- Broadcast ID: `ebbd60b7-2841-48bf-9fcd-b2ca90d3da51`
- URL: https://resend.com/broadcasts/ebbd60b7-2841-48bf-9fcd-b2ca90d3da51
- Status: **sent**
- Audience: `97c42e60-038b-401f-a81b-a2bb57786f19` (Release Notes)
- From: `marketing@maximizer.com`

### Zendesk article (PUBLISHED)
- Article ID: `46160257756813`
- Live URL: https://support.maximizer.com/hc/en-us/articles/46160257756813-Maximizer-Cloud-May-2026
- Admin editor URL: https://maximizer8634.zendesk.com/hc/admin/articles/46160257756813
- Section: Release Notes → Cloud (`23951413801741`)
- Status: **published** (visible to customers)
- Conversion: markdown → HTML via Python `markdown` library (3.9), with `tables`, `fenced_code`, and `toc` extensions. The `markdown` package was `pip install`'d this session — first time it was needed. Worth adding to a `requirements.txt` for the project.

### Items included (6) vs excluded (3)

Master filter (`Release Notes? = Yes`) + H1 classification:

**New Features (4):**
1. Move policies and accounts when moving, merging or converting contacts — FSE+ | Web
2. IQ Boost in Outlook — FSE+, Business+ | Outlook
3. Exclude contacts from Email Auto-save — All | Outlook
4. Fireflies Integration — All | Web

**Improvements (2):**
1. IQ Boost Anonymizer in Timeline Summary + Meeting Preparation — FSE+, Business+ | Web
2. Improved Corporate Entity Matching for Investia & iAPW Data Sync — FSE | Web

**Excluded (3, all `Release Notes? = No`):**
- New iA Wizard
- Outlook Calendar Sync recurring-appointment fix ("No need for marketing announcement")
- IQ Boost in Mobile ("Customer release postponed until M6")

### Manual steps that were completed
Per Lewis on May 27: "Successful send for this cycle." All eight steps from the May 26 plan executed (review drafts, upload screenshots, publish Zendesk, substitute URL + screenshots in Resend, send broadcast).

### Caveats / flags from the cycle (kept for reference)
- **Release Date in article**: used `May 26, 2026` (publish day). Loop page stated `May 27, 2026`. Adjust if you'd rather use the Loop date.
- **Customer release dates are staggered**: Move policies + the two improvements go live May 27. IQ Boost Outlook + Email Auto-save go live Jun 2. Fireflies goes live Jun 9. Article doesn't currently mention the staggering — decide if you want an inline note or two separate articles.
- **Loop title quirk**: page reads "Maximizer Cloud - May 2026.5" (trailing `.5`). Treated as "May 2026" throughout. Flag to PMs.

---

## Routine automation — current state

### Routine
- ID: `trig_01CnmNjhdL7thpPeahL9iCBQ`
- URL: https://claude.ai/code/routines/trig_01CnmNjhdL7thpPeahL9iCBQ
- Schedule: `0 16 17 * *` (17th of each month, 9am Vancouver time during PDT)
- **DST caveat**: cron is timezone-fixed. In PST months (Nov–Mar), fires at 8am Vancouver. Accept seasonal drift or swap manually in winter.
- Enabled: **false** (intentional — see structural note below)
- Next run (if enabled): 2026-06-17 16:03 UTC

### Routine prompt body contains
- `RESEND_API_KEY`: the current active key (pasted via web UI by Lewis; intentionally not refetched in chat)
- `ROUTINE_ID` / `ROUTINE_LINK`: real values for `trig_01CnmNjhdL7thpPeahL9iCBQ`
- `GITHUB_REPO_URL`: `https://github.com/dysonmaximizer-sys/claude`
- Full Steps 0–4 (capture metadata, clone repo, run workflow, write briefing, send completion email)

### Structural decision: routine is now a reminder, not a runner
The workflow's Step 1 reads Microsoft Loop via the Claude in Chrome browser extension. A remote unattended fire has no browser, so the routine cannot execute the workflow end-to-end. Decided this session:

- Routine fires on the 17th → sends Lewis a completion email saying "failed: no operator input"
- That email is the **reminder** to manually kick off the workflow
- Lewis runs the workflow manually any time before EOM (this session set the precedent)
- Workflow file's Trigger + Timing Schedule sections updated to reflect this

### Pre-enable blockers (when/if you decide to flip enabled=true)
1. **GitHub App install** on `dysonmaximizer-sys/claude` — without it, the routine's Step 1 clone fails. Install at https://claude.ai/code/onboarding?magic=github-app-setup. (Lower priority now that routine is a reminder, not a runner.)
2. **Sender domain `marketing@maximizer.com`** must be verified in Resend, otherwise the routine's email step returns 403. Check at https://resend.com/domains. Verifying needs IT to add DNS records (TXT/SPF + CNAME/DKIM).

---

## Workflow file changes this session

All in `workflows/maximizer_release_automation.md`.

| Section | Change |
|---|---|
| Purpose | "three assets" → "two assets"; in-app parked note added |
| Trigger | Rewritten — manual kickoff, cron is a reminder only |
| Timing Schedule | Rewritten — flexible trigger date, hard rule "must finish before EOM"; example updated to May 2026 |
| Step 2 | **Rewritten** — Rule 1 master filter (`Release Notes? = Yes` gospel), Rule 2 H1 classification (`New Features` → Feature, `Improvements` → Improvement, `Fixes`/other → omit). Admin & Configuration Updates globally omitted. |
| Step 3 Asset 1 | Simplified Fixes/Admin omission bullet (no longer references per-item tagging) |
| Step 3 Asset 3 (in-app notification) | **Removed entirely** |
| Step 4 | Dropped `inapp_notification.txt` from file table; dropped `in_app_summary` from JSON schema |
| Step 5 | Dropped in-app review checklist bullet |
| Step 6 | Dropped in-app reference from CS team email body template |
| Step 7a | Dropped "Activate the in-app notification" action |
| Step 7a (cont.) manual publishing | Subsection removed |
| Error Handling Summary | Updated "Zero rows with `Release Notes?` = True" row to reflect new combined criterion |

`resources/screenshot_inject.py` left as-is (still the live mechanism). Retirement deferred until HubSpot upload path is wired into the workflow file and proven on a real release end-to-end.

---

## Image hosting — pivoted to HubSpot

### WordPress: KILLED
WP admin denied the request to create an application password / service account. WP path is dead. No further action on WP.

### HubSpot: LIVE (API working, script committed, workflow not yet wired)

**Direction:**
- PMs paste images into Loop (already do this, no new ask)
- Workflow will extract pasted images from Loop, save locally, upload each to HubSpot Files under `/release-notes/YYYY-MM/`
- Both the Zendesk article and the Resend email reference the HubSpot CDN URLs directly
- Replaces the Zendesk-attachment filename matching that `screenshot_inject.py` currently does

**Auth setup (DONE):**
- HubSpot moved Private Apps to "Legacy" status. **Service Keys** are the current recommendation. HubSpot admin created a Service Key with `Files` scope only.
- Auth: `Authorization: Bearer ${HUBSPOT_SERVICE_KEY}` (confirmed by admin per HubSpot docs)
- Token in `~/.zshrc` as `HUBSPOT_SERVICE_KEY` (line 11)

**Smoke test (DONE, May 27):**
- Endpoint confirmed: `POST https://api.hubapi.com/files/v3/files` (multipart upload)
- 1x1 PNG uploaded successfully, HTTP 201
- File served back via Cloudflare CDN, HTTP 200, correct content-type, CORS open
- URL pattern: `https://{portalId}.fs1.hubspotusercontent-na1.net/hubfs/{portalId}/{folderPath}/{filename}` — portal ID for Maximizer is `193809`
- Smoke test file lives at `/release-notes/_smoke-test/release-automation-smoke-test.png`; safe to delete in HubSpot Files UI as cleanup

**Script (COMMITTED):**
- `resources/hubspot_upload.py` — reads a folder of images, uploads each to `/release-notes/YYYY-MM/release-YYYY-MM-NN.{ext}`, writes `hubspot_urls.json` mapping original filename → CDN URL
- Single retry on network error, hard fail on 4xx, exits 2 if any upload failed
- Folder path auto-derived from `output/YYYY-MM-release/...` structure

### Still pending for the HubSpot path to be production-ready

1. **Workflow file: add Step 3a** that calls `hubspot_upload.py` between Step 2 parse and Step 3 asset generation. Not yet written.
2. ~~**Step 1: extract Loop pasted images to local disk**~~ **DONE 2026-05-28.** Method: in-page JS filters `<img>` to `data:image/`, builds a `{filename: base64}` JSON, blob-downloads to `~/Downloads/loop_images.json` via synthetic `<a download>` click; local Python decodes to `output/YYYY-MM-release/images/raw/`. See the "Loop image extraction — proven method" block in the Open Items section below.
3. **Retire `resources/screenshot_inject.py`** — only after the HubSpot path has been proven on a real release cycle (not just smoke-tested).

### Trade-offs Lewis explicitly accepted before going with HubSpot
- URLs are on `hubspotusercontent-na1.net`, not `maximizer.com`. Lewis was unsure but comfortable with the trade-off.
- Vendor lock-in: if Maximizer leaves HubSpot or downgrades the tier, every release notes article published from this point breaks. Lewis acknowledged.
- File storage quota: unknown current usage, but release notes images are tiny (~1.5 GB per year). Lewis to verify if it ever becomes a concern.

---

## API key history (security)

### Resend
Within this session:
1. **Original `re_Durh...t81o`** — from prior handoff, exposed in chat. Lewis deleted in Resend.
2. **Second `re_G7L9...maRS`** — created by Lewis, pasted via web UI into routine. Leaked back via routine update API response. Lewis rotated.
3. **Third (only known to Lewis)** — currently inside the routine prompt body. Never seen in chat.
4. **Fourth `re_gNbDg...dux1`** — created by Lewis for local CLI use. Currently in `~/.zshrc` line 9. **Was typed in chat for the ~/.zshrc edit**, so present in transcript. This key was used to send the May 2026 broadcast.

### HubSpot
- **`pat-na1-...` (Service Key)** — created by HubSpot admin with `Files` scope only. Currently in `~/.zshrc` line 11 as `HUBSPOT_SERVICE_KEY`. Lewis pasted it via a `read -s` prompt in terminal, so the key never appeared in chat or shell history. **Not in the transcript.**

### If this transcript leaves Lewis's machine
- Rotate `re_gNbDg...dux1` (revoke at https://resend.com/api-keys; create new; update `~/.zshrc`)
- The HubSpot Service Key is safe — never in chat
- The routine's Resend key (#3) is safe — never in chat

---

## Open items carrying forward

| # | Item | Status |
|---|---|---|
| 1 | **HubSpot path: wire workflow Step 3a** to call `hubspot_upload.py` | Script ready; `--folder` override added 2026-05-28. Workflow file edit still pending. |
| 2 | ~~**HubSpot path: extract Loop pasted images** to local disk in Step 1~~ | **DONE 2026-05-28.** Proven end-to-end on the May 2026 Loop page. Method below. |
| 3 | `marketing@maximizer.com` domain verification in Resend | Pending; IT to add DNS records. **Did NOT block the May 2026 broadcast** (verify why — possibly already verified, or Resend allowed unverified send) |
| 4 | GitHub App install on `dysonmaximizer-sys/claude` | Pending; lower priority now that routine is reminder-only |
| 5 | Rotate Resend key #4 (in chat transcript) | Optional; do if transcript leaves machine |
| 6 | **Workflow file gap**: Step 4 implies Zendesk draft creation via API but no explicit instruction. Was missed initially in the May cycle, recovered manually. Add explicit "Step 4b — Create Zendesk draft via Help Center API" to the workflow file. | One-line workflow file edit; do next session |
| 7 | Add `requirements.txt` listing Python deps (`markdown>=3.9`) — installed ad-hoc this session | Optional but cleaner |
| 8 | Delete smoke test file in HubSpot at `/release-notes/_smoke-test/` | Optional housekeeping |
| 9 | ~~Delete smoke test files in HubSpot at `/release-notes/_smoke-test-extraction/` (8 files from 2026-05-28 extraction proof)~~ | **DONE 2026-05-28** (confirmed by Lewis) |
| 10 | ~~**HubSpot recompresses PNGs at upload**~~ | **DONE 2026-05-28** — Lewis eyeballed served PNGs against originals; recompression acceptable. Path is good to use as-is. |
| 11 | **Heading structure on the May Loop page is `<h2>` not `<h1>`** (0 h1 / 1 h2 detected). Workflow Step 2's "H1 = classification" rule will return 0 features if it relies strictly on `<h1>`. Probe actual heading hierarchy on the next Loop page and align the classification rule. | **Open** — medium risk for next cycle |

### Loop image extraction — proven method (closes #2)

In-page (via Chrome extension JS tool):

1. Find `<img>` elements where `src` starts with `data:image/`. On the May 2026 page this returned 8 images (PM-pasted screenshots) cleanly, separate from 25 Loop UI icons (https, 150×150) and 2 avatars (blob:, 48×48).
2. Strip the `data:image/...;base64,` prefix, build `{"01.png": "<base64>", ..., "08.png": "<base64>"}`, JSON-stringify.
3. Create a Blob, generate an object URL, click a synthetic `<a download>`. Saves to `~/Downloads/loop_images.json` in one shot.

Local:

4. Python decodes the JSON, writes each `<name>.png` to `output/YYYY-MM-release/images/raw/`.

**Why not a local HTTP receiver:** tried it. Chrome blocks HTTPS-public-origin (`loop.cloud.microsoft`) → HTTP-private-IP (`127.0.0.1`) POSTs silently — preflight succeeds, body never sends, no console error. Adding `Access-Control-Allow-Private-Network: true` did not unblock. The receiver path is a dead end; do not pursue.

### Killed / no-longer-needed
- ~~Screenshot naming brief to PMs~~ — superseded by image hosting path; not needed
- ~~Feature Type column in Loop~~ — superseded by H1 classification; not needed
- ~~Zendesk in-app notification step~~ — removed from workflow entirely
- ~~WordPress image hosting~~ — WP admin denied request; pivoted to HubSpot
- ~~Customer release date staggering note in Zendesk article~~ — May cycle published without it; no customer complaints reported. Default for future cycles: omit unless dates span very widely.
- ~~Loop page title quirk flag to PMs~~ — May cycle shipped fine; cosmetic only

---

## Files modified this session

- `workflows/maximizer_release_automation.md` — 13 edits across all sections
- `~/.zshrc` — `RESEND_API_KEY` value updated (line 9), `HUBSPOT_SERVICE_KEY` added (line 11)
- `~/CLAUDE.md` — full writing-style + behavioural instructions appended (mirrors claude.ai web settings)
- `output/2026-05-release/` — created, populated with 4 files, all shipped
- `resources/hubspot_upload.py` — new file, ready for use; `--folder` override added 2026-05-28 (smoke-test bypass for the YYYY-MM regex; keeps original filenames)

## Files NOT touched (still as-is)

- `resources/screenshot_inject.py` — still the live mechanism for screenshot injection until HubSpot path is wired end-to-end and proven on a real release
- `resources/email_template.md` / `email_template.html` — not touched
- `resources/release_notes_template.md` — not touched
- Prior handoffs (`HANDOFF.md`, `HANDOFF_2026-05-25_routine-email.md`) — left intact for history

---

## How to resume next session

1. Open this handoff
2. May 2026 cycle is **done**. Archive `output/2026-05-release/` if you want to keep the workspace tidy, otherwise leave it as a reference for next month.
3. Next biggest unblock: HubSpot path Step 1 image extraction (open item #2). Investigate by opening any Loop page with pasted images and probing the DOM via the Chrome extension to see whether image bytes are reachable.
4. After Step 1 image extraction works, add workflow Step 3a (open item #1) and end-to-end test on a non-production folder.
5. Otherwise free to pick from the open items list, or wait for the June reminder email on the 17th.
