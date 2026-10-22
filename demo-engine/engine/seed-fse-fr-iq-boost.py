#!/usr/bin/env python3
"""
Préparé pour la revue (French FSE, IQ Boost) - story seeder.

Tenant: French FSE (MarketingFSPlusFrench), env file fse-fr.env.
Adapts the Halloran pattern to the existing Famille Dubois-Lefebvre household
(Montreal; Mathieu 68, Elodie 67, Camille 28). Retirees, so the beat is the
chalet, not the REEE:

  1. Estate-planning note (~2 years back) + OPEN task, deliberately old:
     "Revoir le testament et la designation des beneficiaires quand Camille
     achetera sa propriete".
  2. Thin "before" note (~7 months back).
  3. Spring review note (~5 months back): chalet bought 1996 for $145k,
     now ~$650k.
  4. Incoming call from Elodie (~9 weeks back): possibly selling the chalet,
     wants to understand capital-gains tax; mentions IN PASSING that Camille
     just bought a condo in Rosemont (the line IQ Boost should connect to
     the old task).
  5. Outgoing call to Mathieu (~3 weeks back): confirms today's annual
     review; wants to weigh selling vs keeping the chalet for Camille with
     life insurance covering the tax.
  6. EXISTING records updated (prior values kept in the manifest):
     insurance opportunity close date + description, household profile
     (Segmentation A, Chalet value, Date Last Contacted), Mathieu's next KYC
     review, and fictional contact details (@mail.test, 555 phone).

The household is NOT created or deleted by this story. --cleanup deletes the
created records and restores every prior value.

Run:    cd "$HOME/Claude Code/demo-engine"
        set -a; source fse-fr.env; set +a; python3 engine/seed-fse-fr-iq-boost.py            # dry run
        set -a; source fse-fr.env; set +a; python3 engine/seed-fse-fr-iq-boost.py --apply
Clean:  set -a; source fse-fr.env; set +a; python3 engine/seed-fse-fr-iq-boost.py --cleanup
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

try:
    import requests
except ImportError:
    sys.exit("pip3 install requests --break-system-packages")

from tenant_guard import assert_tenant

BASE = os.environ.get("MAXIMIZER_BASE_URL", "https://api.maximizer.com/octopus").rstrip("/")
PAT = os.environ.get("MAXIMIZER_PAT")
HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "..", "manifests", "fse-fr", "iq-boost-dubois-lefebvre-manifest.json")
COMPAT = {"AbEntryKey": "2.0"}

MASTER = "VXNlcglNQVNURVI="  # rule 10: explicit owner, displays "Barb Smith"
LDYSON = "VXNlcglMRFlTT04="
TODAY = datetime.now()

HH = "SW5kaXZpZHVhbAkyNjAxMTYyNTA0NTAzMjQwNDAwMDFDCTA="       # Famille Dubois-Lefebvre
MATHIEU = "Q29udGFjdAkyNjAxMTYyNTA0NTAzMjQwNDAwMDFDCTE="
ELODIE = "Q29udGFjdAkyNjAxMTYyNTA0NTAzMjQwNDAwMDFDCTI="
CAMILLE = "Q29udGFjdAkyNjAxMTYyNTA0NTAzMjQwNDAwMDFDCTM="
OPP = "T3Bwb3J0dW5pdHkJMjYwMTE2MjUxODE2Mjk5NzIwMDAzTwkw"       # Nouvelle police d'assurance

SEGMENTATION = "Udf/$TAG(WME_CLIENTINFO_SEGMENTATION)"
NEXT_KYC = "Udf/$TAG(WME_CLIENTINFO_REV_NEXTKYC)"
CHALET = "Udf/$TAG(WME_KYCETC_BALANCE_FIX_COTTAGE)"
LAST_CONTACTED = "Udf/$TYPEID(60059)"

# ---- Story content (French). Lewis approves this text before --apply. ----

NOTE_ESTATE = (
    "Revue de planification successorale avec Mathieu et Élodie. Testaments notariés "
    "à jour (2019). Bénéficiaires des REER et des CELI : le conjoint, puis Camille. "
    "Le chalet de Val-David doit éventuellement revenir à Camille. À revoir quand "
    "Camille achètera sa propriété (projet d'achat d'ici deux ou trois ans).")
TASK_ESTATE = "Revoir le testament et la désignation des bénéficiaires quand Camille achètera sa propriété"
NOTE_THIN = "Revue annuelle avec Mathieu et Élodie. Discuté du chalet."
NOTE_SPRING = (
    "Revue de printemps avec Mathieu et Élodie (en personne). Portefeuille rééquilibré "
    "(environ 50/50). Prestations du RRQ et de la PSV en place depuis l'an dernier. "
    "CELI cotisés au maximum pour 2026. Chalet de Val-David acheté en 1996 pour "
    "145 000 $, valeur estimée à environ 650 000 $. Aucune décision à prendre pour l'instant.")
CALL_ELODIE_SUBJECT = "Appel d'Élodie - vente possible du chalet"
CALL_ELODIE = (
    "Élodie envisage de vendre le chalet de Val-David d'ici un an ou deux. Elle veut "
    "comprendre l'impôt sur le gain en capital avant de décider. Elle a mentionné en "
    "passant que Camille vient d'acheter un condo dans Rosemont. Aucune décision pour l'instant.")
CALL_MATHIEU_SUBJECT = "Appel à Mathieu - confirmation de la revue annuelle"
CALL_MATHIEU = (
    "Revue annuelle confirmée. Mathieu veut discuter du chalet : le vendre maintenant, "
    "ou le garder pour Camille et prévoir une assurance-vie pour couvrir l'impôt au décès.")
OPP_DESCRIPTION = (
    "Assurance-vie conjointe payable au dernier décès pour couvrir l'impôt sur le gain "
    "en capital du chalet de Val-David.")

IQ_QUESTIONS = [
    "Qu'est-ce que je dois revoir avec la famille Dubois-Lefebvre ?",
    "Où en sont Mathieu et Élodie concernant la vente du chalet ?",
    "Qu'est-ce qui a changé récemment pour Camille ?",
]


def d(days_offset: int, hm: str = "10:00") -> str:
    """Intended-Pacific wall clock -> UTC string (CLAUDE.md rule 7b)."""
    from zoneinfo import ZoneInfo
    day = TODAY + timedelta(days=days_offset)
    hour, minute = int(hm[:2]), int(hm[3:5])
    local = day.replace(hour=hour, minute=minute, second=0, microsecond=0,
                        tzinfo=ZoneInfo("America/Vancouver"))
    return local.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S")


def day(days_offset: int) -> str:
    return (TODAY + timedelta(days=days_offset)).strftime("%Y-%m-%d")


def call(endpoint: str, payload: dict, quiet: bool = False) -> dict:
    for attempt in range(6):
        time.sleep(0.4)  # 429 pacing per CLAUDE.md
        r = requests.post(f"{BASE}/{endpoint}",
                          headers={"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"},
                          json=payload, timeout=30)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", "2")) or 5)
            continue
        r.raise_for_status()
        data = r.json()
        if data.get("Code") == -2:
            sys.exit("Token rejected (Code -2): the French PAT expired. Renew fse-fr.env.")
        if data.get("Code", 0) != 0 and not quiet:
            print(f"  !! Code={data.get('Code')} on {endpoint}: {json.dumps(data, ensure_ascii=False)[:500]}")
        return data
    raise RuntimeError("rate-limited after 6 tries on %s" % endpoint)


def created_key(data: dict, obj: str) -> Optional[str]:
    return data.get(obj, {}).get("Data", {}).get("Key")


def _save(manifest: dict) -> None:
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def remember(manifest: dict, kind: str, key: Optional[str], label: str) -> None:
    if key:
        manifest.setdefault("records", []).append({"kind": kind, "key": key, "label": label})
        _save(manifest)  # incremental: a mid-run crash must not orphan keys (rule 3)
        print(f"  + {kind}: {label}")
    else:
        print(f"  - FAILED {kind}: {label}")


def read_entry(key: str, fields: list) -> dict:
    sc = {"Key": 1}
    for f in fields:
        sc[f] = 1
    data = call("Read", {"AbEntry": {"Scope": {"Fields": sc},
                                     "Criteria": {"SearchQuery": {"Key": {"$EQ": key}}}},
                         "Compatibility": COMPAT})
    rows = data.get("AbEntry", {}).get("Data", [])
    return rows[0] if rows else {}


def update_entry(manifest: dict, key: str, label: str, values: dict) -> None:
    """Capture prior values, then update. Read back to verify."""
    readable = [f for f in values if f not in ("Email1", "Phone1")]
    prior = read_entry(key, readable + ["Email", "Phone"])
    manifest.setdefault("modified", []).append({"key": key, "label": label, "prior": prior,
                                                "new": values})
    _save(manifest)
    data = call("Update", {"AbEntry": {"Data": dict({"Key": key}, **values)}, "Compatibility": COMPAT})
    after = read_entry(key, readable + ["Email", "Phone"])
    bad = [f for f in readable if str(after.get(f)).strip("[]'\"") != str(values[f])]
    print(f"  {'~' if data.get('Code') == 0 and not bad else '!! CHECK'} {label}: "
          f"{', '.join(values)}{' (read-back mismatch: ' + ', '.join(bad) + ')' if bad else ''}")


def phone_type_key() -> str:
    data = call("Read", {"InteractionLog": {"FieldOptions": {"Type": [{"Key": 1, "DisplayValue": 1}]}},
                         "Compatibility": COMPAT}, quiet=True)
    for opt in data.get("InteractionLog", {}).get("FieldOptions", {}).get("Type", []) or []:
        label = str(opt.get("DisplayValue", "")).lower()
        if "phone" in label or "téléphon" in label or "appel" in label:
            return str(opt.get("Key"))
    return "60001"  # validated phone-call type on FSE (same field IDs here)


def create_note(manifest: dict, text: str, days_ago: int, hm: str) -> None:
    data = call("Create", {"Note": {"Data": {"Key": None, "ParentKey": HH,
                                             "DateTime": d(-days_ago, hm), "Text": text}}})
    remember(manifest, "Note", created_key(data, "Note"), text[:50])


def create_call(manifest: dict, phone: str, subject: str, text: str, days_ago: int,
                start: str, end: str, direction: int, label: str) -> None:
    data = call("Create", {"InteractionLog": {"Data": {
        "Key": None, "Subject": subject, "Description": text, "Type": phone,
        "StartDate": d(-days_ago, start), "EndDate": d(-days_ago, end),
        "User": MASTER, "AbEntryKey": HH, "Direction": direction,
    }}, "Compatibility": COMPAT})
    remember(manifest, "InteractionLog", created_key(data, "InteractionLog"), label)


def note_keys() -> set:
    keys = set()
    for parent in (HH, MATHIEU, ELODIE, CAMILLE):
        data = call("Read", {"Note": {"Scope": {"Fields": {"Key": 1}},
                                      "Criteria": {"SearchQuery": {"ParentKey": {"$EQ": parent}}}}},
                    quiet=True)
        keys |= {n["Key"] for n in data.get("Note", {}).get("Data", []) or []}
    return keys


def sweep_audit_notes(manifest: dict, before: set) -> None:
    """Rule 5: delete notes that appeared during the run and are not ours. Compares
    against a pre-run snapshot, NOT a time window: this tenant stamps audit notes
    with Pacific wall-clock time labelled Z (validated 2026-10-21), so a UTC
    cutoff misses them."""
    ours = {r["key"] for r in manifest.get("records", [])}
    stray = note_keys() - before - ours
    for key in stray:
        call("Delete", {"Note": {"Data": {"Key": key}}}, quiet=True)
    print(f"  audit notes swept: {len(stray)}")


def check_display_name() -> None:
    data = call("Read", {"User": {"Scope": {"Fields": {"Key": 1, "DisplayName": 1, "FirstName": 1,
                                                       "LastName": 1}},
                                  "Criteria": {"SearchQuery": {"LastName": {"$LIKE": "%"}}}}})
    for u in data.get("User", {}).get("Data", []):
        if u.get("Key") == LDYSON:
            shown = " / ".join(str(u.get(f)) for f in ("DisplayName", "FirstName", "LastName"))
            if "Dyson" in shown or "Lewis" in shown:
                sys.exit("STOP: user LDYSON still shows a real name (%s).\n"
                         "  Notes created now would be stamped with it. Rename LDYSON in\n"
                         "  Administrator first, then re-run. Nothing was written." % shown)
            print("  name check OK: LDYSON shows as %s" % shown)


def print_plan() -> None:
    print("DRY RUN - nothing is written. Content and dates (Pacific):\n")
    rows = [
        (d(-730, "14:30"), "Note", NOTE_ESTATE),
        (d(-730, "17:00"), "Task (OPEN, Barb Smith)", TASK_ESTATE),
        (d(-210, "16:05"), "Note", NOTE_THIN),
        (d(-150, "14:30"), "Note", NOTE_SPRING),
        (d(-63, "11:10"), "Incoming call: " + CALL_ELODIE_SUBJECT, CALL_ELODIE),
        (d(-21, "09:40"), "Outgoing call: " + CALL_MATHIEU_SUBJECT, CALL_MATHIEU),
    ]
    for when, what, text in rows:
        print(f"[{when[:10]}] {what}\n    {text}\n")
    print("Existing records updated (prior values saved for cleanup):")
    print(f"  Opportunity 'Nouvelle police d'assurance': close date {day(45)}; description:\n    {OPP_DESCRIPTION}")
    print(f"  Household: Segmentation A, Chalet 650 000 $, Date Last Contacted {day(-21)}")
    print(f"  Mathieu: Next KYC review {day(0)} (today); Date Last Contacted {day(-21)}")
    print(f"  Élodie: Date Last Contacted {day(-21)}")
    print("  Contact details: emails -> @mail.test, phone -> (555) 010-4412")
    print("\nIQ Boost questions to test in the UI (on the household record):")
    for q in IQ_QUESTIONS:
        print("  - " + q)


def cleanup() -> None:
    if not os.path.exists(MANIFEST):
        sys.exit(f"No manifest at {MANIFEST} - nothing to clean.")
    with open(MANIFEST) as f:
        manifest = json.load(f)
    before = note_keys() - {r["key"] for r in manifest.get("records", [])}
    for rec in reversed(manifest.get("records", [])):
        data = call("Delete", {rec["kind"]: {"Data": {"Key": rec["key"]}}}, quiet=True)
        print(f"  {'deleted' if data.get('Code', 0) == 0 else 'FAILED to delete'} {rec['kind']}: {rec['label']}")
    for mod in reversed(manifest.get("modified", [])):
        prior = {k: v for k, v in mod["prior"].items() if k in mod["new"]}
        for k, v in list(prior.items()):
            if isinstance(v, list):
                prior[k] = v[0] if v else ""
            elif v is None:
                prior[k] = ""
        if "Email1" in mod["new"]:
            prior["Email1"] = {"Address": mod["prior"].get("Email", ""), "Default": True}
        if "Phone1" in mod["new"]:
            prior["Phone1"] = {"Number": mod["prior"].get("Phone", "")}
        obj = mod.get("object", "AbEntry")
        data = call("Update", {obj: {"Data": dict({"Key": mod["key"]}, **prior)}, "Compatibility": COMPAT},
                    quiet=True)
        print(f"  {'restored' if data.get('Code', 0) == 0 else 'FAILED to restore'} {mod['label']}")
    sweep_audit_notes({"records": []}, before)
    os.remove(MANIFEST)
    print("Manifest removed. The household itself was never created by this story and stays.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--cleanup", action="store_true")
    args = ap.parse_args()

    if not PAT:
        sys.exit("Load the French token first: set -a; source fse-fr.env; set +a")
    if not (args.apply or args.cleanup):
        print_plan()
        return

    assert_tenant("fse-fr", call)
    if args.cleanup:
        cleanup()
        return
    if os.path.exists(MANIFEST):
        sys.exit(f"Manifest already exists ({MANIFEST}). Run --cleanup first.")
    check_display_name()

    before = note_keys()
    manifest = {"story": "fse-fr-iq-boost-dubois-lefebvre", "tenant": "fse-fr",
                "created": TODAY.isoformat()}
    _save(manifest)

    print("1) History notes ...")
    create_note(manifest, NOTE_ESTATE, 730, "14:30")
    create_note(manifest, NOTE_THIN, 210, "16:05")
    create_note(manifest, NOTE_SPRING, 150, "14:30")

    print("2) The forgotten task (~2 years back, still open) ...")
    data = call("Create", {"Task": {"Data": {"Key": None, "Activity": TASK_ESTATE,
                                             "DateTime": d(-730, "17:00"), "AbEntryKey": HH,
                                             "AssignedTo": MASTER}}, "Compatibility": COMPAT})
    remember(manifest, "Task", created_key(data, "Task"), "Old estate task (2 yrs back)")

    print("3) Calls ...")
    phone = phone_type_key()
    create_call(manifest, phone, CALL_ELODIE_SUBJECT, CALL_ELODIE, 63, "11:10", "11:24", 1,
                "Élodie chalet call (~9 weeks back)")
    create_call(manifest, phone, CALL_MATHIEU_SUBJECT, CALL_MATHIEU, 21, "09:40", "09:48", 2,
                "Mathieu confirmation call (~3 weeks back)")

    print("4) Existing opportunity ...")
    prior = call("Read", {"Opportunity": {"Scope": {"Fields": {"Key": 1, "CloseDate": 1, "Description": 1}},
                                          "Criteria": {"SearchQuery": {"Key": {"$EQ": OPP}}}}})
    new = {"CloseDate": day(45), "Description": OPP_DESCRIPTION}
    manifest.setdefault("modified", []).append({
        "object": "Opportunity", "key": OPP, "label": "Opportunity 'Nouvelle police d'assurance'",
        "prior": (prior.get("Opportunity", {}).get("Data") or [{}])[0], "new": new})
    _save(manifest)
    data = call("Update", {"Opportunity": {"Data": dict({"Key": OPP}, **new)}})
    print(f"  {'~' if data.get('Code') == 0 else '!! CHECK'} opportunity close date + description")

    print("5) Profiles and contact details ...")
    update_entry(manifest, HH, "Household profile",
                 {SEGMENTATION: "1", CHALET: 650000, LAST_CONTACTED: day(-21),
                  "Phone1": {"Number": "(555) 010-4412"}})
    update_entry(manifest, MATHIEU, "Mathieu",
                 {NEXT_KYC: day(0), LAST_CONTACTED: day(-21),
                  "Email1": {"Address": "mathieu.dubois@mail.test", "Default": True},
                  "Phone1": {"Number": "(555) 010-4412"}})
    update_entry(manifest, ELODIE, "Élodie",
                 {LAST_CONTACTED: day(-21),
                  "Email1": {"Address": "elodie.lefebvre@mail.test", "Default": True},
                  "Phone1": {"Number": "(555) 010-4413"}})
    update_entry(manifest, CAMILLE, "Camille",
                 {"Email1": {"Address": "camille.dubois@mail.test", "Default": True},
                  "Phone1": {"Number": "(555) 010-4414"}})

    print("6) Sweeping audit notes ...")
    sweep_audit_notes(manifest, before)

    _save(manifest)
    print(f"\nDone: {len(manifest.get('records', []))} records created, "
          f"{len(manifest.get('modified', []))} existing records updated. Manifest: {MANIFEST}")
    print("\nIQ Boost questions to test in the UI (on the household record):")
    for q in IQ_QUESTIONS:
        print("  - " + q)


if __name__ == "__main__":
    main()
