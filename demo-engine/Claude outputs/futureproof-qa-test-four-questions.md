# Futureproof QA test: the four stage questions

Purpose: run each question in Claude with the Maximizer connector, compare against the expected result, mark pass or fail. Three clean passes in a row on every question is the bar before recording or freezing the prompt card.

Ground truth below was pulled from the Futureproof tenant on 11 September 2026 (one `investments_household_aum` call, 75 households, 146 accounts, total AUM $100.54M, total cash $3.21M). Q1 idle cash and Q4 are verified against live data. Q1 coverage decay, Q2 and Q3 are marked where I could not verify.

How to run: fresh chat per run. Paste the prompt verbatim. Time it from send to last token. Record the result in the sheet at the bottom. Delete any tasks created before the next run.

---

## Q1a. Audit the book

Prompt (verbatim):
"Audit my book. Where is client cash sitting idle, and which of my most valuable households have I gone quiet on when something is coming up for them? Rank both by dollar value."

### Expected: idle cash

Exactly four households, in this order, with these figures (rounding is fine):

| Rank | Household | Cash |
|---|---|---|
| 1 | Peter and Mary Cameron Family, Coalmont BC | $660,000 |
| 2 | Hartfield Family, Kelowna BC | $377,130 |
| 3 | Poulin, Jennifer and Wil, Calgary AB | $311,396 |
| 4 | Vincent Household, Kelowna BC | $240,234 |

Next highest is $51,476 (Rouleau), so the four separate cleanly. Total above the gap: about $1.59M.

Pass: all four named, correct order, no fifth household, figures within 2 percent.
Fail: any household missing, any household added, or Claude picks a threshold that pulls in the $40K to $51K tail (Rouleau, Thibodeau, Szabo, Lemieux). If it does, add "above $100,000" to the prompt and re-freeze.

### Expected: coverage decay

Three households: Cameron, Hartfield, Vincent, each with a milestone reason (Peter's KYC review due 20 November; Hartfield KYC 24 November; Vincent KYC 18 March). Cameron should top both lists.

**Current state: FAIL. Do not record until fixed.**

The "Days Since Last Contacted" field the connector reads shows: Cameron null (never contacted), Hartfield 65, Vincent 55. No A-tier household is at or over 90 days. The back-dated calls in the handoff have either not landed or have not recalculated into that field. Two consequences on stage: Claude either returns zero gone-quiet households, or reports the Camerons as never contacted, which reads as broken data.

Fix options, pick one today:
1. Confirm the back-dated interactions exist on Cameron, Hartfield and Vincent and find out from Jin whether field 838 recalculates overnight or has to be set directly. If it recalculates, re-test Saturday morning.
2. Change the threshold to 60 days. Today that returns Desrosiers (71), Dallaire (69), Lindqvist (65), Hartfield (65) among A-tier. Cameron is still null and still absent, so this alone does not save the hero.
3. Make sure Cameron has at least one logged interaction, dated 104 days back, so the field reads a number rather than null.

Pass (after fix): exactly Cameron, Hartfield, Vincent, each with a reason drawn from the record, Cameron on both lists.

### Also check
- Claude's answer names provinces. Every household in the current top 50 is BC, AB or ON. No US locations appeared in the pull. Pass.
- "Vincent  Household" has a double space in its name. Cosmetic, but it will show on screen. Fix in the tenant.
- Latency under 25 seconds. The single-call pattern ran in about 15 seconds from a cloud container; time it on Gabe's laptop.

## Q1b. Create the tasks

Prompt:
"Create a task for each of those three households, due Friday, titled "Call re idle cash and upcoming milestone", and put a one-line reason in each."

Pass: three tasks, one per household, due Friday 18 September, exact title, each with a reason that matches the Q1a answer. Open the Cameron household in Maximizer and confirm the task is visible on the record.
Fail: task on the wrong record, wrong date, reason invented.
After every run: delete the three tasks or the next run shows six.

## Q1c. The Camerons' story

Prompt:
"Tell me the Camerons' story in under 120 words, then what I should raise with them. Use only what is in Maximizer."

Pass: resolves to Peter and Mary (Coalmont) without asking which Camerons; under 120 words; every fact traceable to a note, contact or account on the record; the raise list includes the idle cash and the estate or beneficiary gap.
Fail: asks which Camerons (means another Cameron household still exists); mentions the property sale, Mary's retirement or Claire unless those notes are actually in the tenant; any invented fact; over 120 words.
Check the record yourself first: how many notes are on the household, what they say, and whether the two adult children are attached. Claude cannot tell a story that is not there.
Note: Cameron holds four accounts and two contacts, AUM $3.09M, cash $660K. If Claude quotes different totals, that is a fail.

## Q2. Turning 71

Prompt:
"How many of my clients turn 71 in the next 24 months, and how much RRSP money will have to convert to a RRIF?"

Not verified in this pull. Before testing, check two things in the tenant: which contacts have a birthdate between 12 September 1955 and 11 September 1957 (that is who turns 71 by September 2028), and whether those people hold accounts typed RRSP. Peter and Mary Cameron are 84 and 83 and will not appear.
Pass: a count, a named list, and an RRSP total that you can reproduce by adding the account values yourself.
Fail: zero clients (no birthdates seeded in range), a list that includes anyone outside the range, or an RRSP figure you cannot reconcile.

## Q3. Registered money with no named beneficiary

Prompt:
"How much of my A-clients' registered money sits in accounts with no named beneficiary?"

Not verified in this pull. Known risk: the beneficiary story was built on the Address Book estate-planning fields, and account-level beneficiary fields were cleared on the Cameron accounts. Claude may read the account field, find it blank on many accounts, and report a much larger number than intended.
Before testing, decide which reading you want. Then check: how many A-tier (Segmentation 1) accounts of type RRSP, RRIF, LIF, LIRA or TFSA have a blank account-level beneficiary. If it is most of them, either populate beneficiaries on every account except the deliberate gap, or reword the question to point at the estate-planning field.
A-tier households in the tenant today: Charbonneau, Desrosiers, Boissonneault, Lindqvist, Cameron, Hartfield, Ferreira, Ishikawa, Dallaire, Yamashita, Nakamura, Vincent. Twelve.
Pass: a figure you can reproduce, and a short list of which accounts, with Cameron in it.
Fail: figure includes non-A households, includes non-registered accounts, or cannot be reconciled.

## Q4. Top ten share and last contact

Prompt:
"What share of my book is in my top ten households, and when did I last speak to each of them?"

### Expected (verified)

Top ten by AUM, total $37.28M of $100.54M, so about 37 percent.

| Rank | Household | AUM | Days since last contact |
|---|---|---|---|
| 1 | Charbonneau Household | $6.36M | 50 |
| 2 | Gilles and Renee Desrosiers Family | $5.28M | 71 |
| 3 | Pierre-Luc and Sylvie Boissonneault Family | $4.42M | 20 |
| 4 | Desmond and Colette Lindqvist Family | $3.76M | 65 |
| 5 | Peter and Mary Cameron Family | $3.09M | none logged |
| 6 | Hartfield Family | $3.02M | 65 |
| 7 | Milena and Dmitri Ferreira Family | $3.02M | 34 |
| 8 | Takeshi and Hiroko Ishikawa Family | $2.91M | 45 |
| 9 | Dallaire Household | $2.78M | 69 |
| 10 | Jun and Mei Yamashita Family | $2.64M | 17 |

Pass: same ten households, share between 36 and 38 percent, a last-contact date or day count per household.
Fail: Cameron shows as never contacted (same root cause as Q1a; fix that and this clears). "Graham, Bill - Advocis Publishing Inc" is number eleven at $2.61M with zero contacts, so it will not appear in a top ten today, but any value change above $30K pushes it in. Rename or remove it anyway.

---

## Run sheet

| Run | Q1a cash | Q1a decay | Q1b | Q1c | Q2 | Q3 | Q4 | Longest wait (s) | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| 3 | | | | | | | | | |

Rule: three consecutive passes per question. One fail resets the count for that question. Anything over 25 seconds gets reworded and retested.

## Status as of 11 September

Verified passing today: Q1a idle cash, Q4 ranking and share.
Verified failing today: Q1a coverage decay (no A-tier household at 90 days; Cameron has no contact logged), and therefore the Cameron row in Q4.
Not yet checked: Q1c notes and children on the Cameron record, Q2 birthdates and RRSP accounts, Q3 account-level beneficiaries.
