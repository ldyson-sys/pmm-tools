# Maximizer Release Automation — Handoff
Updated: 2026-09-29 · Session: Claude Code (Lewis's Mac)
Supersedes: `HANDOFF_2026-09-01_august-release-cycle.md` (kept as history; its Decisions and Gotchas still apply unless overridden below)

## Context
Monthly workflow that turns a PDF export of the Microsoft Loop release page into a Zendesk release-notes article and a Resend customer email. Project root: `/Users/lewisdyson/Claude Code/`. Workflow spec: `workflows/maximizer_release_automation.md`. Templates + scripts in `resources/`. Per-cycle outputs in `output/YYYY-MM-release/`. This session ran the **September 2026 (M9)** cycle from `~/Downloads/2026 M9.pdf`.

**Status: SEPTEMBER (M9) CYCLE COMPLETE, INSIDE THE MONTH.** Run, reviewed, published and sent on 2026-09-29, one day **before** the Loop release date (September 30). First cycle to finish on time since the end-of-month rule was written down.
- Zendesk article **49253196008589** `Maximizer Cloud – September 2026.9`, created as a draft by API and **published by Lewis manually**. Live at `https://support.maximizer.com/hc/en-us/articles/49253196008589-Maximizer-Cloud-September-2026-9`.
- Test emails to lewisdyson@maximizer.com: `01a0ee6d-a5b3-7528-9aad-7e2360d90f41` (v1), `01a0ee7c-4711-755e-95a0-a6d704ff39c9` (v2, after Lewis's edits).
- **Broadcast `ed4564fa-ae5d-498f-8468-dbd0899cf34d`**, sent **once**, to Release Notes audience `97c42e60-038b-401f-a81b-a2bb57786f19`. Status confirmed `sent` at 2026-09-29 18:48:30 UTC. The id is recorded in `release_payload.json`, which blocks any re-send.

## Decisions
- **The Sync Report row was DROPPED even though the Loop table marks it `Yes` (2026-09-29, Lewis-directed).** This overrides Rule 1 ("the table is gospel") for this row only. The M9 row "Sync report for Plug & Play (iAPW) & Investia integrations" is the same feature M8 already announced as the Investments Sync Report (article 48586130966285, broadcast 2026-09-01). Announcing it again as new would have contradicted the August email. The M9 Loop entry also said `FSE+` only, which conflicts with the M8 ruling of FSE + FSE+. Rejected: re-announcing it as a New Feature. **Standing check: before drafting, compare every `Yes` row against the previous cycle's published article. PMs carry rows over.** Its images 07/08 were uploaded to HubSpot but are unused.
- **Workflows was ordered ahead of Outlook appointment saving, even though Outlook is available on more editions.** Workflows is FSE+ / Business+ only. The Outlook save is All Editions, but per the Loop Notes it only works when automated Calendar sync is turned off. That prerequisite counts as a narrowing under the availability rule, so the tie went to impact. Lewis did not object. Final order in both assets: Workflows for opportunities and cases → Outlook: save appointments to Maximizer → Shared email addresses for Email 2 and Email 3 → Keyboard shortcuts for navigation → Insurance Data Hub: import status emails (FSE+ only, so last).
- **"Keyboard shortcuts added back" was reworded to present tense.** The Loop said they were "added back"; the copy just says they exist. Same principle as M8's "don't frame a benefit as relief from a defect we shipped".
- **The email carries ONE image per feature, maximum (Lewis-directed).** Workflows has 5 images in the article (01–05) and only 01 in the email. Rejected: 4 images in the email, which made it too long.
- **Email images were sized below the 600px cap (Lewis said "a little big").** Final widths: 01 = 520, 06 = 460, 09 = 460, recorded as `email_image_widths` in `release_payload.json`. Going smaller would make the in-screenshot text unreadable (~7px). Treat ~460–520 as the working range for dialog and panel screenshots. The spec's 600 cap is a ceiling, not the target. **The article images were left at the 650 cap**; Lewis did not ask to change the live article. The spec has not been edited to reflect this yet (see Open items).
- **The email went out with the `Coming Soon:` subject because the send was 1 day before the release date.** Subject: `Coming Soon: Workflows for Opportunities and Cases, Plus Outlook Appointment Saving – September 2026`. This follows the M8 rule: before the release date → Coming Soon; on or after → Now Available.
- **On-Premise is not mentioned.** The Loop listed the Outlook feature as "Cloud and On-premise". The article is Cloud release notes, so that was omitted.
- **Lewis authorised the broadcast in chat this cycle ("Send broadcast"), and Claude ran it.** This time the auto-mode classifier did **not** block `POST /broadcasts`. The human-in-the-loop decision from M8 still stands: only send on Lewis's explicit instruction in chat, per cycle.

## Open items & blockers
- **RESOLVED: the broadcast reached `sent`** (18:48:30 UTC). Never re-run `send_broadcast.sh` for M9. It refuses anyway, because `resend_broadcast_id` is populated.
- **The spec does not yet reflect this session's email rules.** The one-image-per-feature and ~460–520px email widths live only in this handoff. Update `workflows/maximizer_release_automation.md` Step 3b and the Asset 2 image rules if Lewis wants them to be standing rules. Ask first; he gave them as M9 edits.
- **Keyboard shortcuts and Insurance notifications shipped without screenshots** (none on the Loop page). This is the same accepted exception as M8's "Save Outgoing Emails".
- Carried over, unchanged: the `maximizer.com` Resend domain is still `partially_failed` (tracking records only; sending works). The reminder task is still local-only.

## Next steps (in order)
1. Ask Lewis whether to write the one-image-per-feature email rule and the smaller email widths into the spec.
2. **Next cycle (M10, October 2026):** export the Loop page to PDF, then run `python3 resources/loop_pdf_extract.py "<pdf>" output/2026-10-release/`. Title: `Maximizer Cloud – October 2026.10`. Read the real system date and the Loop release date before choosing the subject prefix.
3. For M10, copy `send_broadcast.sh`, `md2zd.py` and `build_m9_email.py` from `output/2026-09-release/` into the new folder. The send script resolves paths relative to its own location. The builder has M9 feature copy and absolute M9 paths hardcoded, so edit both.

## Tool knowledge & gotchas
- **`output/2026-09-release/send_broadcast.sh` is the send path now.** It refuses to run if `resend_broadcast_id` is set, checks the full subject of every `sent` broadcast via `GET /broadcasts/{id}` and aborts on a match, writes the id to the payload **before** calling `/send`, and prints `SENT OK … DO NOT RUN AGAIN`. This fixes the root cause of the M8 3x incident. The audience id is hardcoded to `97c42e60-...`.
- **`output/2026-09-release/md2zd.py`** converts `zendesk_article.md` into Zendesk HTML: h2, p, ol/ul, `wysiwyg-image-resized` images, and the line after each image becomes `<p><em>` caption. It also writes the create payload. Set `permission_group_id: 16069197925005` and `user_segment_id: null` to match prior months.
- **Email builder:** `output/2026-09-release/build_m9_email.py`. It fills `resources/email_template.html` with the M8 [A]/[B]/[C] block markup. `{{LEARN_MORE_URL}}` is replaced in a second step, after the article id exists.
- **`curl` on the public article URL returns 403** (Cloudflare bot check), even when the article is published. Check publish state with the anonymous API instead: `GET https://maximizer8634.zendesk.com/api/v2/help_center/en-us/articles/{id}.json` and read the `draft` field.
- **M9 filter result:** all 6 table rows are `Yes`, and 1 was dropped by decision (Sync Report). Classification: 2 New Features (Workflows, Outlook appointments) and 3 Improvements. No Fixes.
- **M9 image mapping (confirmed by viewing each PNG, since `preceding_text` was page chrome again):** `01–05` → Workflows (entity dropdown, templates grid, Start a workflow, Regarding card, Entity filter), `06` → Outlook Save appointment vs Sync Enabled, `07–08` → Sync Report (unused), `09` → User Profile shared email. None are portrait; `04` is narrow (431px), so it keeps its native width.
- **The Loop page template is copied into the PDF** (`{{Feature Name}}` placeholders on pages 9–10). Ignore everything after the last real feature.
- **Zendesk auth verified 2026-09-29** with `GET /api/v2/users/me.json` → 200, Oula Murad, admin. HubSpot uploads: all 9 returned 200. The Resend key worked for both `/emails` and `/broadcasts`.

## Session preferences
- Keep the email lean: one image per feature, and screenshots sized so they don't dominate the column.
- Lewis wants a fresh `[DRAFT]` test after every round of email edits, before broadcasting.
