# Futureproof demo spec

Version 0.1, 9 September 2026. Owner: Lewis. Presenter: Gabe. Technical: Jin (MCP, tenant), Diego (investments data).

Status of every figure in the answer keys below: proposed seed value, not yet in the tenant. Nothing in this spec is true until the data workstream lands and a rehearsal run confirms it.

## 1. Frame

Audience: Futureproof stage slot, Canadian-heavy financial advisor crowd. Slot length: TBC (drives how many beats survive; see section 8).

Persona: Adam the Advisor. Senior portfolio manager, owns the book, pays for the CRM, resistant to novelty, respects his time.

Master value prop: Know the story behind your book.

Barbecue version: You can ask your CRM where money is sitting idle and which good clients you have gone quiet on, and it tells you, then books the calls.

Hero: Claude, on Gabe's laptop, talking to Maximizer through the MCP connector. Maximizer's UI appears only as proof (the record the answer came from, the task that landed), never as a tour.

Rules: no form fill, no prompts without a decision attached, no live typing (paste from the prompt card or use voice input), every beat ends in Maximizer.

## 2. Arc

Cold open (45 seconds, no AI mentioned). Three questions on screen: Where in my book is money doing nothing? Which of my best clients have I gone quiet on, right when something is coming up for them? What is the story behind the family walking in at 2pm? "Most advisors need an afternoon and three systems to answer those. Watch."

Beat 1, audit the book (3 to 4 minutes). Beat 2, one story (3 minutes). Optional Beat 3, the meeting just ended (2 to 3 minutes, see section 5). Beat 4, Gabe zooms out (60 to 90 seconds, no demo).

## 3. Beat 1: audit the book

Prompt 1a (paste verbatim):
"Audit my book. Where is client cash sitting idle, and which of my most valuable households have I gone quiet on when something is coming up for them? Rank both by dollar value."

Answer key (what Claude must return, in this order):

Idle cash. Four households with cash above $100K, ranked:
1. Peter and Mary Cameron Family, Coalmont BC, cash $312,000 (property sale, June 2026)
2. Hartfield Family, Kelowna BC, cash $185,000
3. Poulin, Jennifer and Wil, Calgary AB, cash $142,000
4. Vincent Household, Kelowna BC, cash $118,000
Total idle above threshold: about $757,000. Everyone else under $30K.

Coverage decay. Top-quintile households (top 20% by AUM) with no logged interaction in 90 or more days AND a milestone inside 60 days. Exactly three:
1. Peter and Mary Cameron Family: last contact 104 days ago; Mary turns 71 in 14 months (RRIF conversion planning window), Peter's KYC review due in 41 days
2. Hartfield Family: last contact 97 days ago; Robert Hartfield turns 65 in 33 days
3. Vincent Household: last contact 91 days ago; TFSA contribution room unused this year, annual review due in 52 days

Aha: the Camerons top both lists. Gabe does not need to say it; the audience sees it.

Coda prompt 1b:
"Create a task for each of those three households, due Friday, titled 'Call re idle cash and upcoming milestone', and put a one-line reason in each."

Gabe switches to Maximizer, opens the Cameron household, shows the task with its reason. Line: "That was a report and a to-do list. It took 40 seconds."

Data dependencies: cash outliers seeded on exactly those four households; interaction history on every top-quintile household with silences on exactly those three; birthdates on Mary Cameron, Peter Cameron, Robert Hartfield; KYC review date field on Peter; TFSA data on Vincent; every other top-quintile household must have a logged interaction inside 90 days or the list balloons.

Failure modes: Claude returns more than three households (fix: tighten interaction seeding), Claude picks a different threshold (fix: name it in the prompt, "above $100,000"), latency over 25 seconds (fix: split 1a into two prompts).

## 4. Beat 2: one story

Prompt 2a:
"Tell me the Camerons' story. Who they are, how their money is set up, what has changed for them lately, and what I should raise when I see them."

Answer key:

Who: Peter (68) and Mary (69) Cameron, Coalmont BC, clients since 2014. Daughter Claire Cameron (36, Vancouver) in the family tree, not a client. Son Daniel (33, Calgary) in the tree, not a client.

Money: household AUM about $1.22M across Peter's RRIF, Mary's RRSP, joint non-registered, plus $312K cash following the June 2026 sale of the Coalmont rental property (note dated 18 June 2026).

What changed: property sold; Mary retired in March 2026 (note); Claire mentioned as "asking about a first home" in the March note; last contact 104 days ago.

What to raise: deploy the $312K (Mary's TFSA room, non-registered, or RRIF strategy); Mary's RRIF conversion timeline before age 71; Peter's KYC review due in 41 days; introduction to Claire, who is looking at a first home and has no advisor on file.

Aha: family tree, accounts, notes, and dates combined into one page of judgement in 15 seconds. This is the master value prop performed.

Gabe switches to Maximizer: the Cameron family tree with Claire and Daniel, then the 18 June note. Line: "Every fact it just used was already in there. It read the story. I did not have to."

Data dependencies: Cameron tree with two adult children with birthdates and cities; three to five back-dated notes with texture (property sale, Mary's retirement, Claire's first home); account types matching the story; client-since date.

Failure modes: Claude invents details not in the record (fix: add "use only what is in Maximizer" to the prompt and check every rehearsal for hallucinated facts); story too long for the screen (fix: "in under 150 words").

## 5. Optional Beat 3: the meeting just ended

Include only if Gabe wants a write-heavy moment and the slot is 12 minutes or more. Lewis's view: this is closer to AI notetaker territory than to Maximizer's story, so it is optional, not default.

Setup: a short recorded call (Fathom) with a colleague playing Peter Cameron, covering the cash, the RRIF question, and Claire.

Prompt 3a:
"I just finished a call with Peter Cameron. Read the transcript, log the meeting note on the Cameron household, create the follow-ups we agreed, and draft my recap email to Peter."

Answer key: note logged on the household with a four-line summary; three tasks (send Mary's RRIF projection, book Claire intro call, prepare deployment options for $312K); Outlook draft to Peter in Gabe's drafts folder.

Gabe switches to Maximizer: the note and tasks, timestamped. Then Outlook: the draft.

Dependencies: Fathom connector on Gabe's Claude, Microsoft 365 connector, a staged recording. Three connectors means three failure points; this beat needs the most rehearsal and is the first to cut if time is short.

## 6. Beat 4: Gabe zooms out (talking points, not a script)

None of this worked because the AI is clever. It worked because the data underneath was structured: households, family relationships, accounts, interactions, dates. A CRM that stores contacts cannot do this. A CRM built around the book can. The advisors who get the most out of AI in the next two years will be the ones whose data is ready for it. Close on the value prop.

Claims to verify with Jin before Gabe says them: "works with any assistant your firm approves" (what does the connector actually support today), "available now" (OAuth is not in production; PAT only), "your data is not used to train anything" (what is the actual data path).

## 7. Data spec for Jin and Diego

Investments (Diego, JSON import):
- Pad to 60 to 80 households, 1 to 5 accounts each, varied balances, total book $90M to $120M
- Cash outliers exactly as in section 3 (Cameron $312K, Hartfield $185K, Poulin $142K, Vincent $118K); all others under $30K
- Cameron accounts: Peter RRIF, Mary RRSP, joint non-registered, cash
- Vincent: no TFSA account
- Beneficiary and institution fields populated (not used in this demo, but blanks look like broken data if anyone zooms in)

CRM (Jin, or demo engine if repointed to the Futureproof tenant):
- Rename or remove "Graham, Bill - Advocis Publishing Inc" as a household
- Birthdates: Mary Cameron (turns 71 in 14 months), Peter Cameron (68), Robert Hartfield (turns 65 in 33 days), plus plausible birthdates across the top quintile
- KYC review date on Peter Cameron: 41 days out
- Client-since date on the Camerons: 2014
- Cameron family tree: Claire (36, Vancouver) and Daniel (33, Calgary), not clients
- Cameron notes: 18 June 2026 property sale ($312K proceeds), March 2026 Mary retired and Claire asking about a first home, one routine review note from 2025
- Interaction history: every top-quintile household has a logged call, email, or appointment inside the last 90 days EXCEPT Cameron (104 days), Hartfield (97 days), Vincent (91 days)
- Workflow templates: optional, for Q&A only

## 8. Timing budget

Cold open 0:45. Beat 1 with coda 3:30. Beat 2 3:00. Beat 4 1:30. Total without optional Beat 3: about 9 minutes plus transitions. With Beat 3: about 12 minutes. If the slot is under 8 minutes, cut the coda and shorten Beat 2 to the "what to raise" section only.

## 9. Plumbing checklist (Lewis)

- PAT created on the Futureproof site and pasted into Claude desktop config on Gabe's Mac (not only Lewis's)
- Tool-call detail collapsed or hidden; chat font readable at projector resolution; dark or light theme chosen to match venue lighting
- Voice input tested, or prompt card open in a second window for pasting
- Every prompt timed; anything over 25 seconds is split or reworded
- Hotspot tested as the primary connection; venue wifi is the fallback, not the plan

## 10. Hardening protocol

Run each prompt ten times after data lands. Log: households returned, order, any invented fact, wall time. Tighten wording until ten runs match. Freeze the prompt card. Record one clean end-to-end run as the backup; load it on a second device.

## 11. Gabe sessions

Session 1 (walkthrough): run the arc, capture edits, agree the Beat 4 talking points and the three Q&A answers. Session 2 (final): full run on hotspot at projector resolution, Jin present for technical questions, backup video tested.

## 12. Q&A prep for Gabe

Where does my client data go? (Jin to confirm the data path.) Can I have this today? (Honest availability answer; OAuth not in production.) Does it work with Copilot or ChatGPT? (Jin to confirm what the connector supports.) What stops it making things up? (Answer: it reads records, and the demo showed the records; hallucination is a real risk, so the answer should not overclaim.)

## 13. Open items

- Slot length and festival date
- Demo engine repoint to the Futureproof tenant, or Jin seeds by hand
- Whether Gabe wants optional Beat 3
- Whether the Camerons should stay the hero household or Jin prefers another family already built out
