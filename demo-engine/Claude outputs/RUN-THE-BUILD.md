# Building the Futureproof book: step by step

Time: about 20 minutes, most of it waiting. Do the steps in order. Do not skip step 4, the test run.

Everything you need is already on your Mac. You do not need to download anything from the chat.

---

## Step 1. Open Terminal

Press Command + Space, type `Terminal`, press Return.

---

## Step 2. Go to the demo engine folder

Copy this line, paste it into Terminal, press Return.

```
cd "/Users/lewisdyson/Claude Code/demo-engine"
```

Nothing visible happens. That is correct.

---

## Step 3. Check the files arrived

Copy, paste, press Return.

```
ls stories/futureproof/ && wc -l stories/futureproof/futureproof-new-households.csv
```

You should see two file names and the number **53**.

If you see 53, carry on. If you see anything else, stop and tell Claude in the chat.

---

## Step 4. Start Claude Code

Copy, paste, press Return.

```
claude
```

Wait for the prompt to appear.

---

## Step 5. Run the test batch first

This creates only three households, so that if anything is wrong you have three records to clean up instead of fifty-two.

Copy everything in the box below and paste it into Claude Code, then press Return.

```
Read CLAUDE.md and docs/futureproof-tenant.md in full before doing anything.

TEST RUN ONLY. Do not process the whole file.

Source the Futureproof environment in the same command as every API call:
set -a; source futureproof.env; set +a

Read stories/futureproof/BUILD-INSTRUCTIONS.md. Follow it exactly, with one change: process ONLY the first three rows of stories/futureproof/futureproof-new-households.csv (FP001, FP002, FP003). Do Part 1 only. Do not touch Part 2 or Part 3 yet.

Create manifests/futureproof/build-the-book.json and record every key as you create it.

When the three are done, read them back and show me, for each one: the household name, city, province, postal code, segmentation, next KYC review, date last contacted, and the names and birthdates of its contacts. Confirm the address stored by reading the Address object by ParentKey, not by an AbEntry-scope read.

Then stop and wait for me.
```

This takes about a minute.

---

## Step 6. Check the three records

Read what Claude Code shows you and check all four of these:

1. Three households exist: Charbonneau Household, Gilles and Renee Desrosiers Family, Pierre-Luc and Sylvie Boissonneault Family.
2. Cities are Kelowna, Vernon and Penticton, all in BC.
3. Every one has a segmentation, a next KYC review date, and a date last contacted. None of these is blank.
4. The contacts have birthdates.

If all four are right, go to step 7.

If anything is blank or wrong, type this into Claude Code and press Return:

```
Stop. Do not create anything else. Tell me exactly which field failed to store and what the API returned. Then delete the three households and their contacts using the manifest, in reverse order, and confirm the tenant is back to 23 households.
```

Then paste what it says back into the chat with Claude.

---

## Step 7. Run the rest

Copy, paste into Claude Code, press Return.

```
The test batch is correct. Continue.

Process the remaining 49 rows (FP004 to FP052) exactly the same way, appending to the same manifest. Pace at roughly 0.35 seconds per call and honour Retry-After.

Then do Part 2 and Part 3 of stories/futureproof/BUILD-INSTRUCTIONS.md in full.

Tell me before you start each part, and report the verification numbers from Part 3 when you finish.
```

This takes about five minutes. You can leave it running.

---

## Step 8. Check the final numbers

When it finishes, Claude Code reports several numbers. Check these three:

1. **Total households: 75.** If it is not 75, something part-failed.
2. **Maximum days since contact.** Every household must be inside 90 days except Peter and Mary Cameron, Hartfield and Vincent. If any others are over 90, the demo's second question will return the wrong answer.
3. **Non-Canadian provinces: zero.**

---

## Step 9. Look at it yourself

Open the Futureproof site in your browser and look at the Address Book.

Three things to eyeball:

1. The names look like real families, not like test data.
2. Only one household is called Cameron. The other two are now Marchetti and Antonelli.
3. Pick any new household at random and open it. It should have a city, a postal code, and one or two contacts with birthdates.

---

## Step 10. Save the work

Type this into Claude Code and press Return.

```
Update docs/futureproof-tenant.md with everything you learned in this run, then commit. Do not push.
```

---

## Step 11. Send me the manifest

Copy, paste into Terminal, press Return.

```
cat manifests/futureproof/build-the-book.json | pbcopy
```

That copies the manifest to your clipboard. Paste it into the chat with Claude. It contains the household keys, which are what Diego's accounts file has to be built against.

---

## If something goes wrong at any point

Type this into Claude Code:

```
Stop. Do not create or delete anything else. Tell me in plain language what happened, what state the tenant is in now, and how many households currently exist.
```

Then paste the answer into the chat. Do not try to fix it yourself and do not re-run the build, because re-running over a partial run creates duplicates.
