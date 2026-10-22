#!/usr/bin/env python3
"""
French FSE book of business: creates ~32 Quebec households so the tenant
looks like a real advisor's book around the Dubois-Lefebvre IQ Boost story.

Tenant: French FSE (MarketingFSPlusFrench), env file fse-fr.env.
Households are Individual-typed with the name in LastName (same shape as the
existing Famille Dubois-Lefebvre; see docs/futureproof-tenant.md section 2).
Each household gets members (birthdates, occupation, @mail.test, 555 phones),
Segmentation, Record Type, Next KYC review, Date Last Contacted, and one
back-dated history note; about half also get a logged call (owner MASTER,
rule 10). Fields are addressed by $TAG/$TYPEID because $NAME paths are French
on this tenant.

Deterministic: the same run date gives the same book. Dates are relative to
the run date (rule 7).

Run:    cd "$HOME/Claude Code/demo-engine"
        set -a; source fse-fr.env; set +a; python3 engine/seed-fse-fr-book.py            # dry run
        set -a; source fse-fr.env; set +a; python3 engine/seed-fse-fr-book.py --apply
Clean:  set -a; source fse-fr.env; set +a; python3 engine/seed-fse-fr-book.py --cleanup
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta
from typing import List, Optional

try:
    import requests
except ImportError:
    sys.exit("pip3 install requests --break-system-packages")

from tenant_guard import assert_tenant

BASE = os.environ.get("MAXIMIZER_BASE_URL", "https://api.maximizer.com/octopus").rstrip("/")
PAT = os.environ.get("MAXIMIZER_PAT")
HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "..", "manifests", "fse-fr", "book-of-business-manifest.json")
COMPAT = {"AbEntryKey": "2.0"}

MASTER = "VXNlcglNQVNURVI="  # rule 10: explicit owner, displays "Barb Smith"
TODAY = datetime.now()

SEGMENTATION = "Udf/$TAG(WME_CLIENTINFO_SEGMENTATION)"   # 1=A 2=B 3=C 4=D 5=Gold
RECORD_TYPE = "Udf/$TAG(WME_CLIENTINFO_RECORDTYPE)"      # 1=Client 2=Prospect
NEXT_KYC = "Udf/$TAG(WME_CLIENTINFO_REV_NEXTKYC)"
LAST_CONTACTED = "Udf/$TYPEID(60059)"
BIRTHDATE = "Udf/$TYPEID(124)"
OCCUPATION = "Udf/$TAG(WME_KYCETC_EMPLOY_OCCUPATION)"

# (city, province, FSA prefix, street)
PLACES = [
    ("Montréal", "QC", "H2V", "avenue Bernard Ouest"), ("Montréal", "QC", "H1V", "rue Ontario Est"),
    ("Montréal", "QC", "H4A", "avenue de Monkland"), ("Montréal", "QC", "H2S", "rue Saint-Hubert"),
    ("Laval", "QC", "H7N", "boulevard des Laurentides"), ("Longueuil", "QC", "J4H", "rue Saint-Charles Ouest"),
    ("Brossard", "QC", "J4W", "boulevard de Rome"), ("Boucherville", "QC", "J4B", "boulevard de Mortagne"),
    ("Québec", "QC", "G1R", "Grande Allée Ouest"), ("Québec", "QC", "G1S", "avenue Maguire"),
    ("Lévis", "QC", "G6V", "rue Saint-Laurent"), ("Sherbrooke", "QC", "J1H", "rue King Ouest"),
    ("Gatineau", "QC", "J8Y", "boulevard Saint-Joseph"), ("Trois-Rivières", "QC", "G9A", "rue des Forges"),
    ("Terrebonne", "QC", "J6W", "rue Saint-Louis"), ("Blainville", "QC", "J7C", "boulevard du Curé-Labelle"),
    ("Saint-Jérôme", "QC", "J7Z", "rue De Martigny Ouest"), ("Mont-Royal", "QC", "H3P", "chemin Lucerne"),
    ("Moncton", "NB", "E1C", "rue Main"), ("Ottawa", "ON", "K1N", "rue Dalhousie"),
]

# Household archetypes. Each contact: (first, last, age, occupation).
# Couples often keep their own surnames in Quebec, hence "Famille A-B".
HOUSEHOLDS = [
    ("Famille Tremblay", [("Gilles", "Tremblay", 71, "Retraité"), ("Monique", "Tremblay", 69, "Retraitée")], "retired"),
    ("Famille Gagnon-Roy", [("Patrick", "Gagnon", 44, "Ingénieur"), ("Julie", "Roy", 42, "Infirmière")], "family"),
    ("Famille Côté", [("Louise", "Côté", 76, "Retraitée")], "widow"),
    ("Famille Bouchard-Morin", [("Éric", "Bouchard", 52, "Propriétaire d'entreprise"), ("Nathalie", "Morin", 50, "Comptable")], "owner"),
    ("Famille Gauthier", [("Marc-André", "Gauthier", 35, "Développeur"), ("Sophie", "Gauthier", 33, "Enseignante")], "young"),
    ("Famille Lavoie-Fortin", [("Daniel", "Lavoie", 63, "Directeur des ventes"), ("Chantal", "Fortin", 61, "Pharmacienne")], "preretire"),
    ("Famille Pelletier", [("Jean-François", "Pelletier", 47, "Médecin"), ("Isabelle", "Pelletier", 46, "Avocate")], "professional"),
    ("Famille Bélanger", [("Robert", "Bélanger", 67, "Retraité"), ("Diane", "Bélanger", 66, "Retraitée")], "retired"),
    ("Famille Nguyen", [("Minh", "Nguyen", 49, "Propriétaire d'entreprise"), ("Linh", "Tran", 47, "Pharmacienne")], "owner"),
    ("Famille Lévesque-Bergeron", [("Simon", "Lévesque", 39, "Électricien"), ("Annie", "Bergeron", 38, "Hygiéniste dentaire")], "family"),
    ("Famille Haddad", [("Karim", "Haddad", 55, "Ingénieur"), ("Rania", "Haddad", 53, "Professeure")], "preretire"),
    ("Famille Paquette", [("Sylvain", "Paquette", 58, "Fonctionnaire")], "single"),
    ("Famille Girard-Simard", [("Julien", "Girard", 31, "Analyste financier"), ("Laurence", "Simard", 30, "Physiothérapeute")], "young"),
    ("Famille Rossi", [("Antonio", "Rossi", 73, "Retraité"), ("Maria", "Rossi", 70, "Retraitée")], "retired"),
    ("Famille Caron", [("Benoît", "Caron", 45, "Policier"), ("Marie-Ève", "Caron", 43, "Travailleuse sociale")], "family"),
    ("Famille Joseph", [("Jean-Robert", "Joseph", 60, "Chauffeur d'autobus"), ("Marlène", "Joseph", 57, "Préposée aux bénéficiaires")], "preretire"),
    ("Famille Beaulieu", [("Catherine", "Beaulieu", 41, "Gestionnaire de projet")], "single"),
    ("Famille Cloutier-Dubé", [("Alexandre", "Cloutier", 50, "Dentiste"), ("Valérie", "Dubé", 48, "Designer")], "professional"),
    ("Famille Poirier", [("Normand", "Poirier", 79, "Retraité"), ("Ginette", "Poirier", 77, "Retraitée")], "retired"),
    ("Famille Benali", [("Youssef", "Benali", 37, "Technicien en informatique"), ("Samira", "Benali", 35, "Infirmière")], "family"),
    ("Famille Fournier", [("Luc", "Fournier", 54, "Agriculteur"), ("Hélène", "Fournier", 53, "Agricultrice")], "owner"),
    ("Famille Lapointe", [("Martine", "Lapointe", 65, "Retraitée")], "widow"),
    ("Famille Chen-Leclerc", [("David", "Chen", 43, "Architecte"), ("Émilie", "Leclerc", 41, "Notaire")], "professional"),
    ("Famille Martel", [("Yves", "Martel", 62, "Camionneur"), ("Sylvie", "Martel", 60, "Secrétaire médicale")], "preretire"),
    ("Famille Nadeau", [("Olivier", "Nadeau", 29, "Ingénieur logiciel")], "young_single"),
    ("Famille Thibault-Vachon", [("Stéphane", "Thibault", 48, "Directeur d'école"), ("Josée", "Vachon", 47, "Orthophoniste")], "family"),
    ("Famille Papadopoulos", [("Nikos", "Papadopoulos", 66, "Restaurateur"), ("Eleni", "Papadopoulos", 64, "Restauratrice")], "owner"),
    ("Famille Bédard", [("François", "Bédard", 70, "Retraité"), ("Lise", "Bédard", 68, "Retraitée")], "retired"),
    ("Famille Gagné", [("Kevin", "Gagné", 34, "Plombier"), ("Audrey", "Gagné", 32, "Éducatrice")], "young"),
    ("Famille Ouellet", [("Richard", "Ouellet", 57, "Comptable agréé"), ("Johanne", "Ouellet", 56, "Conseillère RH")], "preretire"),
    ("Famille Lebrun", [("Pierre", "Lebrun", 46, "Courtier immobilier")], "prospect"),
    ("Famille Vaillancourt", [("Maxime", "Vaillancourt", 38, "Entrepreneur"), ("Roxanne", "Vaillancourt", 36, "Graphiste")], "prospect"),
]

# One history note per archetype. {a} / {b} = first names.
NOTES = {
    "retired": "Revue annuelle avec {a} et {b}. Décaissements du FERR maintenus. Discuté du fractionnement du revenu de pension et des dons aux petits-enfants.",
    "family": "Rencontre avec {a} et {b}. Cotisations au REEE des enfants confirmées pour cette année. Révision de l'assurance-vie à prévoir.",
    "widow": "Appel de suivi avec {a}. Revenu du FERR suffisant. Souhaite revoir son testament avec la notaire l'an prochain.",
    "owner": "Rencontre avec {a} et {b}. Discuté de la rémunération salaire ou dividendes et de la planification de la relève de l'entreprise.",
    "young": "Première rencontre avec {a} et {b}. Projet d'achat d'une maison d'ici deux ans. Ouverture d'un CELIAPP recommandée.",
    "preretire": "Revue avec {a} et {b}. Retraite visée dans trois à cinq ans. Projection de revenu de retraite à préparer, incluant le RRQ.",
    "professional": "Revue annuelle avec {a} et {b}. REER cotisé au maximum. Discuté de l'assurance invalidité et du compte non enregistré.",
    "single": "Revue annuelle avec {a}. Répartition de l'actif inchangée. Intérêt pour un CELI supplémentaire.",
    "young_single": "Première rencontre avec {a}. Régime collectif de l'employeur en place. Ouverture d'un CELI et d'un CELIAPP.",
    "prospect": "Premier contact avec {a} (recommandation d'un client). Rencontre de découverte à planifier.",
}
CALLS = {
    "retired": "Appel de {a} : question sur le retrait minimum du FERR cette année.",
    "family": "Appel de {b} : demande de relevé du REEE pour la déclaration de revenus.",
    "widow": "Appel de {a} : confirmation du rendez-vous de revue annuelle.",
    "owner": "Appel de {a} : question sur un prêt à l'entreprise et l'impact sur le portefeuille.",
    "young": "Appel de {b} : documents reçus pour l'ouverture du CELIAPP.",
    "preretire": "Appel de {a} : question sur le moment de commencer la rente du RRQ.",
    "professional": "Appel de {b} : changement de bénéficiaire sur le CELI.",
    "single": "Appel de {a} : mise à jour de l'adresse courriel.",
    "young_single": "Appel de {a} : question sur la cotisation de l'employeur au régime collectif.",
    "prospect": "Appel à {a} : rencontre de découverte proposée.",
}
SEGMENT = {"retired": "1", "owner": "1", "professional": "1", "preretire": "2", "widow": "2",
           "family": "2", "single": "3", "young": "3", "young_single": "4", "prospect": "4"}


def ascii_slug(s: str) -> str:
    table = str.maketrans("éèêëàâäîïôöùûüçÉÈ", "eeeeaaaiioouuucEE")
    return s.translate(table).lower().replace(" ", "").replace("'", "")


def build_book() -> List[dict]:
    rng = random.Random(TODAY.strftime("%Y%m%d"))
    book = []
    for i, (name, members, kind) in enumerate(HOUSEHOLDS):
        city, prov, fsa, street = PLACES[i % len(PLACES)]
        postal = "%s %d%s%d" % (fsa, rng.randint(1, 9), rng.choice("ABCEGHJKLMNPRSTVXY"), rng.randint(1, 9))
        phone = "(555) 01%d-%04d" % (i % 10, 2000 + i * 37)
        # Date Last Contacted spread: ~35% this week, ~35% 1-3 weeks, ~30% 3-6 weeks.
        bucket = rng.random()
        last_days = rng.randint(1, 6) if bucket < 0.35 else rng.randint(7, 21) if bucket < 0.7 else rng.randint(22, 42)
        contacts = []
        for first, last, age, job in members:
            born = TODAY - timedelta(days=age * 365 + rng.randint(15, 350))
            contacts.append({"first": first, "last": last, "birthdate": born.strftime("%Y-%m-%d"),
                             "occupation": job[:29],  # some text UDFs cap at 29 chars (CLAUDE.md)
                             "email": "%s.%s@mail.test" % (ascii_slug(first), ascii_slug(last))})
        a = members[0][0]
        b = members[1][0] if len(members) > 1 else a
        book.append({
            "name": name, "kind": kind, "contacts": contacts, "phone": phone,
            "address": {"AddressLine1": "%d %s" % (rng.randint(100, 9800), street), "City": city,
                        "StateProvince": prov, "Country": "Canada", "ZipCode": postal},
            "segmentation": SEGMENT[kind],
            "record_type": "2" if kind == "prospect" else "1",
            "next_kyc": (TODAY + timedelta(days=rng.randint(10, 330))).strftime("%Y-%m-%d"),
            "last_contacted_days": last_days,
            "note": NOTES[kind].format(a=a, b=b),
            "note_days": last_days if kind != "prospect" else last_days + 3,
            "call": CALLS[kind].format(a=a, b=b) if i % 2 == 0 else None,
            "call_days": last_days,
        })
    return book


def d(days_offset: int, hm: str) -> str:
    """Intended-Pacific wall clock -> UTC string (CLAUDE.md rule 7b)."""
    from zoneinfo import ZoneInfo
    day = TODAY + timedelta(days=days_offset)
    local = day.replace(hour=int(hm[:2]), minute=int(hm[3:5]), second=0, microsecond=0,
                        tzinfo=ZoneInfo("America/Vancouver"))
    return local.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S")


def call(endpoint: str, payload: dict, quiet: bool = False) -> dict:
    for attempt in range(6):
        time.sleep(0.35)  # 429 pacing per CLAUDE.md
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
            print(f"  !! Code={data.get('Code')} on {endpoint}: {json.dumps(data, ensure_ascii=False)[:400]}")
        return data
    raise RuntimeError("rate-limited after 6 tries on %s" % endpoint)


def created_key(data: dict, obj: str) -> Optional[str]:
    return data.get(obj, {}).get("Data", {}).get("Key")


def _save(manifest: dict) -> None:
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def remember(manifest: dict, kind: str, key: Optional[str], label: str) -> Optional[str]:
    if key:
        manifest.setdefault("records", []).append({"kind": kind, "key": key, "label": label})
        _save(manifest)  # incremental: a mid-run crash must not orphan keys (rule 3)
    else:
        print(f"  - FAILED {kind}: {label}")
    return key


def phone_type_key() -> str:
    data = call("Read", {"InteractionLog": {"FieldOptions": {"Type": [{"Key": 1, "DisplayValue": 1}]}},
                         "Compatibility": COMPAT}, quiet=True)
    for opt in data.get("InteractionLog", {}).get("FieldOptions", {}).get("Type", []) or []:
        label = str(opt.get("DisplayValue", "")).lower()
        if "phone" in label or "téléphon" in label or "appel" in label:
            return str(opt.get("Key"))
    return "60001"


def seed(book: List[dict]) -> None:
    manifest = {"story": "fse-fr-book-of-business", "tenant": "fse-fr", "created": TODAY.isoformat()}
    _save(manifest)
    phone = phone_type_key()
    households = []
    for hh in book:
        data = call("Create", {"AbEntry": {"Data": {
            "Key": None, "Type": "Individual", "LastName": hh["name"], "Address": hh["address"],
            "Phone1": {"Number": hh["phone"]}}}, "Compatibility": COMPAT})
        key = remember(manifest, "AbEntry", created_key(data, "AbEntry"), hh["name"])
        if not key:
            sys.exit("Household create failed - stopping. Cleanup removes what was made.")
        households.append(key)
        dlc = (TODAY - timedelta(days=hh["last_contacted_days"])).strftime("%Y-%m-%d")
        call("Update", {"AbEntry": {"Data": {
            "Key": key, SEGMENTATION: hh["segmentation"], RECORD_TYPE: hh["record_type"],
            LAST_CONTACTED: dlc}}, "Compatibility": COMPAT})
        for c in hh["contacts"]:
            cdata = call("Create", {"AbEntry": {"Data": {
                "Key": None, "Type": "Contact", "ParentKey": key,
                "FirstName": c["first"], "LastName": c["last"],
                "Email": {"Address": c["email"]}, "Phone1": {"Number": hh["phone"]},
                "Address": hh["address"], BIRTHDATE: c["birthdate"], OCCUPATION: c["occupation"],
                NEXT_KYC: hh["next_kyc"], LAST_CONTACTED: dlc,
            }}, "Compatibility": COMPAT})
            remember(manifest, "AbEntry", created_key(cdata, "AbEntry"), f"{c['first']} {c['last']}")
        ndata = call("Create", {"Note": {"Data": {"Key": None, "ParentKey": key,
                                                  "DateTime": d(-hh["note_days"], "14:30"),
                                                  "Text": hh["note"]}}})
        remember(manifest, "Note", created_key(ndata, "Note"), hh["note"][:50])
        if hh["call"]:
            ldata = call("Create", {"InteractionLog": {"Data": {
                "Key": None, "Subject": hh["call"].split(" : ")[0], "Description": hh["call"],
                "Type": phone, "StartDate": d(-hh["call_days"], "10:15"),
                "EndDate": d(-hh["call_days"], "10:24"), "User": MASTER, "AbEntryKey": key,
                "Direction": 2 if hh["kind"] == "prospect" else 1}}, "Compatibility": COMPAT})
            remember(manifest, "InteractionLog", created_key(ldata, "InteractionLog"), hh["call"][:50])
        print(f"  + {hh['name']} ({len(hh['contacts'])} membre(s))")

    # Every household here is new, so any note on it that is not ours was auto-logged
    # by this run. No time filter: this tenant stamps audit notes with Pacific
    # wall-clock time labelled Z (validated 2026-10-21).
    print("Sweeping audit notes ...")
    ours = {r["key"] for r in manifest["records"]}
    swept = 0
    for key in households:
        data = call("Read", {"Note": {"Scope": {"Fields": {"Key": 1}},
                                      "Criteria": {"SearchQuery": {"ParentKey": {"$EQ": key}}}}}, quiet=True)
        for note in data.get("Note", {}).get("Data", []) or []:
            if note["Key"] not in ours:
                call("Delete", {"Note": {"Data": {"Key": note["Key"]}}}, quiet=True)
                swept += 1
    print(f"  audit notes swept: {swept}")

    print("Read-back spot check (first 3 households) ...")
    for key in households[:3]:
        data = call("Read", {"AbEntry": {"Scope": {"Fields": {"Key": 1, "LastName": 1, SEGMENTATION: 1,
                                                              RECORD_TYPE: 1, LAST_CONTACTED: 1}},
                                         "Criteria": {"SearchQuery": {"Key": {"$EQ": key}}}},
                             "Compatibility": COMPAT})
        print("  ", json.dumps(data.get("AbEntry", {}).get("Data"), ensure_ascii=False))
    print(f"\nDone: {len(manifest['records'])} records. Manifest: {MANIFEST}")


def cleanup() -> None:
    if not os.path.exists(MANIFEST):
        sys.exit(f"No manifest at {MANIFEST} - nothing to clean.")
    with open(MANIFEST) as f:
        manifest = json.load(f)
    for rec in reversed(manifest.get("records", [])):
        data = call("Delete", {rec["kind"]: {"Data": {"Key": rec["key"]}}}, quiet=True)
        if data.get("Code", 0) != 0:
            print(f"  FAILED to delete {rec['kind']}: {rec['label']}")
    os.remove(MANIFEST)
    print(f"Removed {len(manifest.get('records', []))} records. Manifest removed.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--cleanup", action="store_true")
    args = ap.parse_args()
    if not PAT:
        sys.exit("Load the French token first: set -a; source fse-fr.env; set +a")

    book = build_book()
    if not (args.apply or args.cleanup):
        print("DRY RUN - nothing is written.\n")
        for hh in book:
            people = ", ".join("%s %s (%s)" % (c["first"], c["last"], c["birthdate"][:4]) for c in hh["contacts"])
            print("%-28s %-15s seg %s  KYC %s  contact -%dj | %s" % (
                hh["name"], hh["address"]["City"], hh["segmentation"], hh["next_kyc"],
                hh["last_contacted_days"], people))
        n = sum(1 + len(h["contacts"]) + 1 + (1 if h["call"] else 0) for h in book)
        print(f"\n{len(book)} households, {sum(len(h['contacts']) for h in book)} people, {n} records total.")
        return

    assert_tenant("fse-fr", call)
    if args.cleanup:
        cleanup()
        return
    if os.path.exists(MANIFEST):
        sys.exit(f"Manifest already exists ({MANIFEST}). Run --cleanup first.")
    seed(book)


if __name__ == "__main__":
    main()
