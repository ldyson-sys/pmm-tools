# Maximizer Release Automation — Handoff
Updated: 2026-06-29 · Session: Claude Code (Lewis's Mac)
Supersedes: `HANDOFF_2026-05-26_may-release-cycle.md` (kept as history)

## Context
Monthly workflow that turns a Microsoft Loop release page into two assets — a Zendesk release-notes article and a Resend customer email — saved for review, then published/sent manually. Project root: `/Users/lewisdyson/Claude Code/`. Workflow spec: `workflows/maximizer_release_automation.md`. Templates + scripts in `resources/`. Per-cycle outputs in `output/YYYY-MM-release/`. This session ran the **June 2026 (M6)** cycle end-to-end and hardened the workflow. **The cycle is COMPLETE: article published live and the customer broadcast sent** (2026-06-29).

## Decisions
- **Step 1 now works from a PDF export of the Loop page**, not live browser scraping. Rejected: Claude-in-Chrome scraping — Loop virtualizes the DOM (only visible slice present) and feature headings aren't semantic HTML, making it slow, lossy, and bad for image mapping. PDF carries full-res images + all text + positions.
- **Images mapped to features by PDF section position**, never by raw index. Rejected: "image NN = feature NN" — breaks whenever an excluded feature has images or a feature has 0/multiple. (In June it happened to align only because the 3 excluded features had no images.)
- **Edition names normalized to published style**: `FSE`→`Financial Services Edition`, `FSE+`→`Financial Services Edition +`, `All`→`All Editions`, `Base`→`Base Edition`, `Sales Leader`→`Sales Leader Edition`; **`Business+` kept as-is**; multiple joined by comma (`Financial Services Edition +, Business+`).
- **Body headings all H2; no H1 in body; release title lives in the Zendesk Title field.** Rejected: reviewer's "sections = H1" — would pollute the theme's auto-TOC and duplicate the title. Title format (locked): `Maximizer Cloud – {Month} {Year} ({Year} M{n})`, e.g. `Maximizer Cloud – June 2026 (2026 M6)`.
- **No in-body Table of Contents** (Zendesk theme generates one). **Edition/Area on separate rows** (blank line between). **No "Screenshots" label** before images. Images embedded as `<img style="max-width:650px;width:100%;height:auto;">`.
- **Features ordered by customer impact, not Loop order** — same order in article and email. June order: IQ Boost in Mobile, Investments Module, then Add start dates, online source, LLM streaming; Improvements after.
- **Email built by populating the branded shell `resources/email_template.html`** (tokens), never hand-rolled. Rejected: a bare custom body — it dropped the header banner + footer. Added a required **one-sentence intro** after the title (`{{INTRO_SENTENCE}}`). **Removed the "Share your Feedback" section** from the shell + template permanently.
- **Image hosting = HubSpot** (full pipeline now wired: extract → `hubspot_upload.py` → CDN URLs in both assets). WordPress killed earlier; the WP URLs remaining in the email shell are static branding assets only (banner/logos), which is fine.
- **Email title (name) = `What's New in Maximizer: [Month] [YYYY]`** (June 2026). Set in the email + template/workflow. Article title unchanged (`Maximizer Cloud – June 2026 (2026 M6)`); email subject unchanged (`Coming Soon: … – June 2026`).
- **Broadcast sends from `marketing@maximizer.com`** (domain's DKIM/SPF verified). Confirmed working — the earlier "domain blocks sending" assumption was wrong.

## Open items & blockers
- **June broadcast SENT (2026-06-29) — cycle done.** Resend broadcast `a5566d12-9779-4cff-a159-3b5dc7e2348c` to Release Notes audience, status `sent`. Article published live (URL in Tool knowledge).
- **One-off (2026-06-29):** the same email was also sent to the **CI Newsletter** audience (`082d3537-5ee3-4a6b-81c5-a732a738eae8`) at Lewis's explicit one-time request — broadcast `c04c18ee-3c17-441d-95f2-930de1ab15e0`. NOT standard: the workflow targets only the Release Notes audience. Do not repeat unless asked.
- **`maximizer.com` Resend domain = `partially_failed`** — but **sending works** (DKIM + SPF verified). Only the optional click/open-tracking records fail: `email` CNAME → `links1.resend-dns.com` (failed) and a pending CAA. IT to re-add those if open/click analytics are wanted; otherwise ignore.
- **Resend key**: a valid key is in `~/.zshrc` (line 9). It's sending-scoped, so `GET /domains` returns 403 — that's normal, not invalid. Keep it out of chat (every prior key died from being exposed and rotated).

## Next steps (in order)
1. **June cycle is done — nothing required.** Optionally monitor broadcast `a5566d12-9779-4cff-a159-3b5dc7e2348c` opens/clicks in Resend (note: click tracking is off until the tracking DNS is fixed).
2. (Optional) Have IT re-add the Resend tracking CNAME (`email` → `links1.resend-dns.com`) + CAA to clear the domain's `partially_failed` status and enable open/click tracking.
3. **Next cycle (M7):** the local scheduled task `maximizer-release-reminder` fires **July 17, 2026, ~9am Vancouver** (only when Claude Code is open; otherwise on next launch) → push notification + briefing. It's a reminder only — the cycle is run manually any time before end of July. To run: export the M7 Loop page to PDF → `python3 resources/loop_pdf_extract.py "<pdf>" output/2026-07-release/` → follow the workflow (parse/filter, generate article + email, create draft, review, publish via the translation-draft flag, send broadcast to Release Notes). M7 likely includes the two features deferred from M6 ("Maximizer Add-in in Outlook Calendar", "Teams Calling"). The old cloud routine `trig_01CnmNjhdL7thpPeahL9iCBQ` stays disabled.

## Tool knowledge & gotchas
- **Resend API + Python = blocked**: `urllib` hits Cloudflare error 1010 (403). Use `curl` with a browser `User-Agent` header. (`hubspot_upload.py` urllib works because it's a different host.)
- **Resend test sends**: `onboarding@resend.dev` only delivers to the account-owner address (`dysonmaximizer@gmail.com`). For any other recipient, send from the verified `marketing@maximizer.com`.
- **Zendesk**: subdomain `maximizer8634`; auth `ZENDESK_EMAIL`(`oulamurad@maximizer.com`)/`token:ZENDESK_API_TOKEN` from `~/.zshrc`. Create draft: `POST /api/v2/help_center/en-us/sections/23951413801741/articles.json` with `permission_group_id: 16069197925005` (Admins) + `draft:true`. Update body: `PUT /api/v2/help_center/articles/{id}/translations/en-us.json`.
- **June Zendesk article `46964089734541`** — PUBLISHED. Live: `https://support.maximizer.com/hc/en-us/articles/46964089734541-Maximizer-Cloud-June-2026-2026-M6` · admin: `https://maximizer8634.zendesk.com/hc/admin/articles/46964089734541`.
- **Zendesk publish gotcha**: the draft flag lives on the **translation**, not the article. To publish: `PUT /api/v2/help_center/articles/{id}/translations/en-us.json {"translation":{"draft":false}}`. Setting `{"article":{"draft":false}}` alone does NOT publish.
- **Published Zendesk articles return 403 to curl** (edge bot-protection) regardless of User-Agent — not a visibility problem (the known-live May article 403s identically). Don't gate a send on a curl check.
- **June broadcast id**: `a5566d12-9779-4cff-a159-3b5dc7e2348c` (status `sent`).
- **HubSpot**: portal `193809`, key `HUBSPOT_SERVICE_KEY` in `~/.zshrc` (Files scope, valid). CDN pattern: `https://193809.fs1.hubspotusercontent-na1.net/hubfs/193809/release-notes/YYYY-MM/release-YYYY-MM-NN.png`. PDF embeds full-res images.
- **New script** `resources/loop_pdf_extract.py` (needs `pymupdf`): writes `loop_text.txt` + `images/raw/NN.png` (doc order, chrome filtered) + `_image_context.json`. `requirements.txt` added (`markdown`, `pymupdf`).
- **June filter result**: 7 of 10 table rows had `Release Notes? = Yes`; rows 1/8/9 (French template, Outlook Calendar, Teams Calling — "announced with M7") excluded.

## Session preferences
- Editions in full published names; lead with highest-impact features; no "Share your Feedback" section; one-sentence intro under the email title; email must use the branded shell.
