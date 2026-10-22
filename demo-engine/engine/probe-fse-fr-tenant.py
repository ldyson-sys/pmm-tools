#!/usr/bin/env python3
"""READ-ONLY snapshot of a Maximizer tenant. Writes NOTHING to the tenant.

Built for the French FSE tenant (MarketingFSPlusFrench, first contact
2026-10-21). Run it once against the French env and once against the English
FSE env, then compare the two JSON files: shared keys mean the French tenant
is a CLONE of FSE and needs a name-based tenant guard before any write (see
tenant_guard.py for why keys cannot tell clones apart).

Usage (the env file decides the tenant; source it in the SAME command):
  set -a; source fse-fr.env; set +a; python3 engine/probe-fse-fr-tenant.py /path/fr.json
  set -a; source .env; set +a;       python3 engine/probe-fse-fr-tenant.py /path/fse.json
"""

import json
import os
import sys
import time
from typing import List

import requests

BASE = os.environ.get("MAXIMIZER_BASE_URL", "https://api.maximizer.com/octopus").rstrip("/")
PAT = os.environ.get("MAXIMIZER_PAT")
COMPAT = {"AbEntryKey": "2.0"}


def call(endpoint: str, payload: dict) -> dict:
    for attempt in range(6):
        r = requests.post(f"{BASE}/{endpoint}",
                          headers={"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"},
                          json=payload, timeout=60)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", 0)) or 10 * (attempt + 1))
            continue
        r.raise_for_status()
        time.sleep(0.35)
        body = r.json()
        if body.get("Code") == -2:
            sys.exit("Token rejected (Code -2): expired or wrong tenant. Renew the PAT.")
        return body
    raise RuntimeError("rate-limited after 6 tries on %s" % endpoint)


def read_entries(entry_type: str) -> List[dict]:
    # An unknown field in Scope returns 0 rows, not an error, so fall back to narrower scopes.
    for fields in (["CompanyName", "FirstName", "LastName"], ["LastName"], []):
        sc = {"Key": 1, "Type": 1}
        for f in fields:
            sc[f] = 1
        res = call("Read", {"AbEntry": {"Scope": {"Fields": sc},
                                        "Criteria": {"SearchQuery": {"Type": {"$EQ": entry_type}}},
                                        "Options": {"Limit": 1000}}, "Compatibility": COMPAT})
        rows = res.get("AbEntry", {}).get("Data", [])
        if rows:
            return rows
    return []


def main() -> None:
    if not PAT or len(sys.argv) != 2:
        sys.exit("Usage: source an env file, then: python3 engine/probe-fse-fr-tenant.py <out.json>")
    out = {"base_url": BASE}

    res = call("Read", {"User": {"Scope": {"Fields": {"Key": 1, "DisplayName": 1, "FirstName": 1, "LastName": 1}},
                                 "Criteria": {"SearchQuery": {"LastName": {"$LIKE": "%"}}}}})
    out["users"] = res.get("User", {}).get("Data", [])

    entries = {}
    for t in ("Individual", "Contact", "Company"):
        for r_ in read_entries(t):
            entries[r_["Key"]] = r_
    out["entries"] = list(entries.values())

    res = call("Read", {"Schema": {"Scope": {"Fields": {"Key": 1, "Alias": 1, "Name": 1, "Assignable": 1, "Type": 1}},
                                   "Criteria": {"SearchQuery": {"Key": {"$TREE": "/AbEntry"}}}},
               "Compatibility": {"SchemaObject": "1.0"}})
    out["abentry_fields"] = res.get("Schema", {}).get("Data", [])

    res = call("Read", {"InteractionLog": {"Scope": {"Fields": {"Key": 1}}, "Options": {"Limit": 1000}}})
    out["interaction_count"] = len(res.get("InteractionLog", {}).get("Data", []))

    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("Snapshot written: %d users, %d entries, %d AbEntry fields, %d interactions. Nothing was changed."
          % (len(out["users"]), len(out["entries"]), len(out["abentry_fields"]), out["interaction_count"]))


if __name__ == "__main__":
    main()
