# Connect the Demo Engine to the Futureproof tenant

Follow the two steps in order. Step 1 is yours, step 2 is a prompt to paste into Claude Code.

---

## Step 1: create the token (you, not Claude)

1. Sign in to the Futureproof demo site.
2. Go to your user preferences and create a Personal Access Token. Copy it.
3. Open Terminal and run this, one line at a time. Replace the two placeholder values. Do not paste the token into any chat window.

```
cd "/Users/lewisdyson/Claude Code/demo-engine"
printf 'MAXIMIZER_PAT=%s\nMAXIMIZER_BASE_URL=%s\n' 'PASTE_TOKEN_HERE' 'https://PASTE_FUTUREPROOF_URL_HERE' > futureproof.env
grep -c . futureproof.env
```

The last command should print `2`. If it prints anything else, the file did not write correctly.

4. Confirm the file is ignored by git:

```
git check-ignore futureproof.env && echo "ignored, good"
```

If that prints nothing, stop and tell Claude Code before going further.

---

## Step 2: paste this into Claude Code

> Read CLAUDE.md first, in full.
>
> We are adding a THIRD tenant to this repo: the Futureproof demo tenant. It follows exactly the same pattern as the Business+ tenant, so mirror that structure rather than inventing a new one.
>
> I have already created `futureproof.env` at the repo root with MAXIMIZER_PAT and MAXIMIZER_BASE_URL. It is gitignored. Do not read, print, echo or commit the token.
>
> Set up the following:
>
> 1. `manifests/futureproof/` and `stories/futureproof/` directories.
> 2. `docs/futureproof-tenant.md` as the knowledge file for this tenant. Do NOT assume any FSE field ID, pick-list value, user, or module exists here. Every fact goes in that file, not in CLAUDE.md.
> 3. `engine/probe-futureproof-tenant.py`, modelled on `engine/probe-bizplus-tenant.py`. Read-only. It must not write anything.
> 4. Add a short section to CLAUDE.md under "Auth & environments" naming the third tenant, its env file, and pointing to `docs/futureproof-tenant.md`. Extend the cross-tenant safety note so it covers three tenants, not two.
>
> Then run the probe with `set -a; source futureproof.env; set +a` in the SAME command as the run, and report:
>
> - Whether authentication succeeded, and the Maximizer version
> - The current household count and total number of AbEntry records
> - Whether the PAT has WRITE access. Test this the safest way you can: create one throwaway note on a record I will name, read it back, then delete it. Tell me the result before doing anything else. If write access fails, stop and tell me.
> - Whether `Udf/$TYPEID(124)` (Birthdate), `Udf/$TYPEID(60059)` (Date Last Contacted), `Udf/$TAG(WME_CLIENTINFO_SEGMENTATION)` and `Udf/$TYPEID(956)` (named beneficiary for registered accounts) exist in this tenant and are assignable. Confirm the TYPEIDs match; they vary per tenant and must not be assumed from the FSE tenant.
> - The validated household create shape for this tenant.
>
> Record everything you learn in `docs/futureproof-tenant.md` as you go. Do not create any households yet. Report back and wait.
>
> One correction to carry into this tenant's doc: accounts in the Futureproof tenant are DataHub UDO records (`@DataHubAccount`) parented directly to the household AbEntry key. They cannot be written through Octopus and are seeded separately by Diego. Note that in the tenant doc so no future session wastes time probing it.

---

## Step 3: only after the probe reports clean

A second prompt for creating the households. I will write it once you confirm the household count and target, since the names, cities, segmentation and contact history all have to be defined before anything is created.
