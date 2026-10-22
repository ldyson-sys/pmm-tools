# Futureproof QA: coverage-decay fix, threshold, Q2 and Q3 verification

Date: 11 September 2026. Source: live reads of the Futureproof tenant (75 households, 146 accounts, 123 contacts) plus the demo-engine repo docs.

---

## 1. Why the back-dated interactions did not work, and the prompt that fixes it

The root cause is documented in the engine's own CLAUDE.md: "Days Since Last Contacted" (field 838) is a formula off "Date Last Contacted" (field 60059), and 60059 does **not** populate from back-dated interactions. It only moves when you write it directly, or when a same-day action (task or appointment creation) auto-sets it. So creating back-dated calls changed nothing; the field has to be set by hand.

That second behaviour is a live trap for rehearsals. Q1b creates tasks on Cameron, Hartfield and Vincent. If task creation auto-sets Date Last Contacted to today (the engine notes say it likely does), every Q1b run resets the three households to zero days and the next Q1a run returns nobody. The fix script therefore has to be re-runnable after every rehearsal, and you need to run it after every Q1b, not once.

### Paste this into Claude Code, opened in the demo-engine folder

```
Read CLAUDE.md, docs/futureproof-tenant.md and the maximizer-demo-engine skill before writing anything. This is the FUTUREPROOF tenant: source futureproof.env in the same command as every run, and call assert_tenant("futureproof", call) from engine/tenant_guard.py before the first write. Do not touch .env or bizplus.env.

Task: make the coverage-decay half of the stage demo true, and make it re-runnable.

Write engine/fix-futureproof-coverage-decay.py. It must:

1. Resolve these three households by key from manifests/futureproof/abentry-keys.json, falling back to an AbEntry read on LastName if a key is missing: "Peter and Mary Cameron Family", "Hartfield Family", "Vincent  Household" (note the double space in the stored name; match loosely).

2. Compute dates relative to the run date (rule 7, never hardcode): Cameron = today minus 104 days, Hartfield = today minus 97 days, Vincent = today minus 91 days.

3. Set Date Last Contacted, Udf/$TYPEID(60059), on each household to that date as "YYYY-MM-DD". Read it back and print the value. Never write Days Since Last Contacted (838); it is a formula.

4. If manifests/futureproof/coverage-decay.json does not exist, also create one back-dated phone call per household (InteractionLog type 60001, outbound, 15 to 25 minutes, User = MASTER key VXNlcglNQVNURVI=, dated the same day as step 3, converted Pacific to UTC via zoneinfo America/Vancouver) with a plain subject such as "Portfolio review call" for Cameron, "Semi-annual review call" for Hartfield, "TFSA and account review call" for Vincent. Do not invent facts that are not already in the household notes. Record every created key in manifests/futureproof/coverage-decay.json. If the manifest exists, skip this step so re-runs do not duplicate calls.

5. Sweep the audit notes this run generated (rule 5): search Notes on the three households by creator and time window, delete the "changed from X to Y" entries created in the last 10 minutes, keep everything else.

6. Verify: read Days Since Last Contacted (838) and Segmentation (154) across every Individual in the tenant. Print the three target households with their day counts, and list any OTHER household with 838 at or above 90. There should be none. Also print the count of A-tier (Segmentation "1") households and confirm the three targets are all "1".

7. Optional, only if it is a one-line change: rename the Vincent household LastName from "Vincent  Household" (two spaces) to "Vincent Household" and confirm the MCP connector still resolves it.

Report in plain language: what was written, the three read-back values, any household over 90 days, and the exact command to re-run this after every rehearsal of the task-creation prompt.
```

After it runs, re-run Q1a in Claude and confirm exactly Cameron, Hartfield and Vincent come back. Then run Q1b once, re-run Q1a, and see whether the three dropped out. If they did, task creation auto-sets the field and the re-run rule is confirmed.

---

## 2. How to change the threshold to 60 days

You do not need to, once section 1 lands. The three households will sit at 104, 97 and 91 days, and the next highest A-tier household is Desrosiers at 71, so any threshold between 72 and 91 gives the same three names. Leave 90 alone.

If you still want to control it, the frozen question never names a number, so Claude picks one. Two ways to pin it without changing what Gabe says on stage:

1. **Project instructions in the Claude app.** Run the demo from a Claude Project and put this in its custom instructions: "In this book, a household has gone quiet when Days Since Last Contacted is 60 or more. My most valuable households are those with Segmentation = A Client. Idle cash means a household cash balance above $100,000." This is the single best hardening step available; it also removes the threshold variance you would otherwise see across ten runs. If anyone asks on stage, Gabe can say the assistant has been told how this book defines its terms, which is true and is how any advisor would set it up.

2. **Change the spoken question.** Add "no contact in 60 days or more" to Q1. That means going back to the organizer, since the question list has gone to all five vendors. Not worth it.

At 60 days with today's data, A-tier returns Desrosiers (71), Dallaire (69), Lindqvist (65) and Hartfield (65). Cameron is still absent because the field is null. So 60 days does not save the hero household; only section 1 does.

---

## 3. Q2 verified: who turns 71 in the next 24 months

Window: born 12 September 1955 to 11 September 1957 (turns 71 between now and 11 September 2028). From the 123 contacts:

| Contact | Born | Turns 71 | Household | Segment | RRSP on the household |
|---|---|---|---|---|---|
| Clement Villeneuve | 21 Jan 1957 | Jan 2028 | Clement and Genevieve Villeneuve Family, Peachland | B | $824,600 (one account, beneficiary Genevieve) |
| Genevieve Villeneuve | 24 Feb 1957 | Feb 2028 | same household | B | same account |
| Hugo Moreau | 4 Mar 1957 | Mar 2028 | Hugo and Sylvie Moreau Family, Canmore | C | $696,000 (beneficiary Sylvie) |
| Sylvie Deschamps | 11 Aug 1957 | Aug 2028 | Sylvie and Gilles Deschamps Family, Victoria | B | $954,800 (beneficiary Gilles) |
| Bill Burgerson | 21 Jan 1956 | Jan 2027 | no household with accounts | none | none |

Expected answer: four clients (five if Claude counts Burgerson, who has no assets), three households, about **$2.48M** of RRSP money to convert (market value plus cash; $2.41M if Claude quotes market value only). Accounts are parented to the household, not the person, so Claude cannot tell whose RRSP the Villeneuve account is; both spouses are in the window, so it does not matter.

Pass: those three households named, a count of four or five, a total between $2.4M and $2.5M.

Two edge cases that will cause run-to-run variance:
- Pierre-Luc Boissonneault (A-tier, $4.42M household) turned 71 on 16 August 2026, 26 days ago, and still holds a $2.03M RRSP that must convert by 31 December 2026. He is outside a strict 24-month window but is the single most urgent RRIF conversion in the book. Some runs will include him, some will not. Decide which you want and, if you want him in, add "including anyone who has already turned 71 this year" to the project instructions. Sylvie Moreau (turned 71 in June 2026) is the same case, smaller.
- **Data realism problem, bigger than Q2.** About eighteen households have a spouse already past 71 (born 1955 or earlier) still holding an account typed RRSP: Ferreira, Lindqvist, Beauchamp, Bouchard, Bhattacharya, Antonelli, Kowalczyk, Kaczmarek, Oyelaran, Kuznetsov, Marchetti, Szabo, Halvorsen, Rasmussen, Bissonnette, Wiebe, Yamashita and Boissonneault. An RRSP cannot exist past 31 December of the year the holder turns 71; a room of Canadian advisors knows that. Claude may volunteer it ("note: 18 clients over 71 still show RRSP accounts") and it reads as broken data. Fix is Diego's: retype those accounts to CAD RRIF. It is a find-and-replace on the account type in his JSON, not a rebuild. Ask today. If he cannot, add to the project instructions: "Do not comment on account types relative to client age unless asked."

Not a Q2 problem but seen in the same pull: Peter and Mary Cameron's household has only two contacts. The two adult children from the handoff are not attached yet. Q1c will have no family tree to tell.

---

## 4. Q3 verified: A-clients' registered money with no named beneficiary

Twelve A-tier households (Segmentation 1): Charbonneau, Desrosiers, Boissonneault, Lindqvist, Cameron, Hartfield, Ferreira, Ishikawa, Dallaire, Yamashita, Nakamura, Vincent. Registered account types present: RRSP, RRIF, LIF, LIRA, TFSA.

Account-level beneficiary field, A-tier registered accounts, blank or "N/A":

| Household | Accounts with no beneficiary | Registered money exposed |
|---|---|---|
| Charbonneau Household, Kelowna | RRSP, TFSA, RRIF (all three blank) | $6,360,000 |
| Vincent Household, Kelowna | RRSP and LIF (both read "N/A") | $2,479,213 |
| Dallaire Household, Victoria | RRSP, TFSA, RRIF (all three blank) | $2,780,000 |
| Peter and Mary Cameron Family | Mary's RRIF (blank; Peter's RRIF and LIF name Mary) | $832,000 |

Expected answer: about **$12.45M** across four A households (about $9.97M and three households if Claude treats Vincent's "N/A" as a named value rather than a blank). Every other A-tier registered account names a spouse. The AUM total for the twelve A households is $42.2M, so the exposed share is roughly 30 percent.

Pass: those four households, a figure between $12.2M and $12.5M, Cameron included.

What this means for the story:
- The Camerons are the smallest item on the list, not the headline. Charbonneau (a 47-year-old with $6.36M and no beneficiary on anything) is. That is a defensible, arguably stronger, audit answer, but it is not the Cameron estate story you built on the Address Book fields. Decide which you want. If you want the Camerons alone, Diego needs to add beneficiaries to Charbonneau and Dallaire and set Vincent's two to a name. If you are happy with the book-level answer, leave it.
- Vincent's "N/A" is the variance risk. Some runs will count it as blank, some as a value. Ask Diego to make it either empty or a real name so the figure is stable.
- Pattern behind it: every single-contact household Diego padded has blank beneficiaries (Charbonneau, Dallaire, Rasmussen, Cormier, Lachapelle, Fournier, Halvorsen, Petrenko, Thibodeau, Bissonnette, Szabo, Kaur, Achebe, Adeyemi, Marchetti, Kuznetsov, Rousseau, Ouellette, Gauthier); every couple names the spouse. Only Charbonneau and Dallaire are A-tier, which is why the Q3 list is short.
- Diego did not clear the Cameron account beneficiaries as asked; he set Mary on Peter's two accounts and left Mary's RRIF blank. That is better than what was asked for. Keep it.
- The Hartfield beneficiaries are "Olivia Clarke" and "Amelia Clarke", who exist nowhere in the book. Same landmine as the old Cameron ones. Not a Q3 fail (they are named), but if Claude reads Hartfield's accounts in Q1c-style detail it will report money left to strangers. Ask Diego to change them to Paige and Brad Hartfield.

---

## 5. Order of work for today

1. Paste the section 1 prompt into Claude Code and run it. Re-test Q1a. (You, 30 minutes.)
2. Send Diego three asks in one message: retype RRSP to RRIF on the eighteen over-71 households; make Vincent's beneficiary blank or named; change Hartfield's beneficiaries to Paige and Brad. Optional fourth: add beneficiaries on Charbonneau and Dallaire if you want the Camerons to headline Q3.
3. Attach Claire and Daniel to the Cameron household through the engine (the handoff item that has not landed) or Q1c has no tree.
4. Set up the Claude Project with the section 2 instructions before any hardening run, so all ten runs share the same definitions.
5. After every Q1b rehearsal: delete the three tasks, re-run the coverage-decay script.
