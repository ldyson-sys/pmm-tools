# Futureproof demo: data requests for Jin and Diego

From: Lewis
Date: 9 September 2026
Context: Gabe is presenting a live Claude + Maximizer MCP demo at Futureproof. The slot is 3.5 to 5 minutes and runs on the Futureproof demo tenant. I have dry-run both prompts against the tenant through the MCP connector. The connector works. The data underneath does not support the demo yet.

I have deliberately kept this list as short as possible. Everything I can do myself through the Demo Engine, I am doing myself. What follows is only the work that the Octopus API cannot reach.

---

## Confirmed scope

Jin has confirmed that DataHub investment accounts cannot be written through the Octopus API. The JSON import is the only path, so account data has to go through Diego.

I have re-cut the ask on that basis. Since checking, I found that Maximizer's estate-planning fields sit on the Address Book entry rather than on the account, and those are writable through the API. That means the estate side of the story is mine to build, and Diego's list is now only account types and cash balances.

---

## Diego: investments data

All of this is on one household plus three cash figures. No new households needed.

### 1. Rebuild the accounts on Peter and Mary Cameron Family (Coalmont, BC)

Their current two accounts are both typed "CAD LIRA" and both categorised "joint". Peter was born in 1942 and Mary in 1943, so they are 84 and 83. A LIRA cannot be held jointly, and at their ages the money would have been converted to a RRIF or LIF more than a decade ago. A room full of Canadian advisors will catch this immediately.

Please replace their two accounts with four:

| Owner | Type | Category | Market value | Cash |
|---|---|---|---|---|
| Peter Cameron | CAD RRIF | individual | 620,000 | 8,000 |
| Mary Cameron | CAD RRIF | individual | 410,000 | 6,000 |
| Peter Cameron | CAD LIF | individual | 185,000 | 4,000 |
| Joint | CAD Cash | joint | 0 | 312,000 |

Institution name on all four: Investia Financial Services Inc. Risk tolerance and objectives can stay as they are.

One thing to clear while you are in there: the beneficiary names currently on their accounts are "Henry Jenkins" and "Abigail Vance", who do not exist anywhere in this book. Please clear both. I am handling the beneficiary story through the estate-planning fields on the client records instead, so I do not need account-level beneficiaries populated at all.

### 2. Cash balances on three other households

Everything else in the book can stay as it is. I only need these four cash figures to be true, so that a question about idle cash returns a short, believable list:

- Peter and Mary Cameron Family: 312,000 (covered above)
- Hartfield Family (Kelowna, BC): 185,000
- Poulin, Jennifer and Wil (Calgary, AB): 142,000
- Vincent Household (Kelowna, BC): 118,000

Every other household must stay under 30,000, which is already true today. Please do not raise any others.

### 3. Not asking for

I am not asking you to pad the book out to a realistic household count or to scale total assets up. It would be the single biggest piece of work here and I can manage the risk by keeping book-level totals out of the questions Gabe asks. If that turns out to be wrong in rehearsal I will come back to you, but assume it is out of scope.

---

## Jin: three items

### 1. Confirm my PAT has write access to the Futureproof tenant

I need to create records through the API, not just read them. If the PAT I generate on the Futureproof site is read-only, or if writes are restricted, please tell me now and let me know what I need instead.

### 2. Two answers Gabe will be asked on stage

He will get these questions from the floor and I do not want him guessing:

- Where does client data go when an advisor connects Claude to Maximizer? What is the actual data path, and is anything retained or used for training?
- Can a customer do this today? My understanding is that OAuth is built but not in production, so it is PAT-only for now. Is that right, and what is the honest availability answer?

A third one if you know it: does the connector work with assistants other than Claude, or is that not accurate to claim yet?

### 3. Optional, only if it is quick

"Graham, Bill - Advocis Publishing Inc" is the second largest household in the tenant at 1.31M with no contacts attached, so it appears in any ranked list. In our sales demo tenant the equivalent record is a known broken orphan that rejects updates. If it is the same record here and it is safe to delete, please delete it. If not, I will rename it.

---

## What I am doing myself through the Demo Engine

Listing this so the split is clear and so nobody duplicates work:

- Renaming the three unrelated Cameron households so only one is called Cameron
- Adding two adult children to the Peter and Mary household as contacts, with birthdates
- Writing four back-dated notes carrying the story
- Creating back-dated phone call records and setting Date Last Contacted so the coverage-decay question returns exactly the three households I want
- Setting segmentation and next KYC review dates
- Building the estate-planning picture on the client records: will status and date last updated, executor named or not, named beneficiary for registered accounts, and last estate planning review
- Fixing the four households where city and province disagree (Ottawa listed as WA, Ottawa as TX, Dallas as NL, Dallas as BC)
- Moving or removing the three US households so the book reads as Canadian

---

## Timing

I need everything above in the tenant before I can rehearse, and I need rehearsal time before my first walkthrough with Gabe. Please tell me what is realistic and I will work back from that.

Thanks both.
