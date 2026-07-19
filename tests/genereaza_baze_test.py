#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
genereaza_baze_test.py — construiește setul COMPLET de baze de date de TEST
pentru C.A.R. Petroșani, cu date deterministe și valori verificabile.

    python tests/genereaza_baze_test.py            # scrie in radacina proiectului
    python tests/genereaza_baze_test.py --dir X    # scrie in alt director
    python tests/genereaza_baze_test.py --force    # suprascrie baze existente

DE CE EXISTĂ:
Redesign-ul UI cere, după fiecare fișier, verificarea că cifrele au rămas
identice. Fără un set de date cunoscut, "compară cifrele" nu e executabil.
Acest script produce baze reproductibile (seed fix) + fișa de valori așteptate
(VALORI_ASTEPTATE.md), astfel încât verificarea devine mecanică.

SIGURANȚĂ:
- Refuză să suprascrie baze existente fără --force (ca să nu atingi date reale).
- Fișierele .db generate sunt în .gitignore — nu ajung niciodată pe GitHub.
- Nu importă și nu atinge niciun modul al aplicației. Doar sqlite3 + stdlib.

MODEL CONTABIL (identic cu ui/generare_luna.py):
    impr_sold[M] = impr_sold[M-1] + impr_deb[M] - impr_cred[M]   (0 daca <= 0.005)
    dep_sold[M]  = dep_sold[M-1]  + dep_deb[M]  - dep_cred[M]
    rata mostenita[M] = impr_cred[M-1], dar 0 daca impr_deb[M-1] > 0 sau lipsa rand
    dobanda la stingere = SUM(impr_sold > 0, de la ultima luna cu impr_deb>0
                              pana la luna sursa inclusiv) * 0.004, ROUND_HALF_UP
"""
import argparse
import random
import sqlite3
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# Consola Windows e implicit cp1252 si nu poate afisa diacriticele de mai jos.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# --------------------------------------------------------------------------
# PARAMETRI  (schimbarea lor schimba datele — actualizeaza si VALORI_ASTEPTATE.md
#            rerurland scriptul, care o rescrie automat)
# --------------------------------------------------------------------------
SEED = 20260719
CURS_EUR_RON = Decimal("4.9665")      # din conversie_config.json
RATA_DOBANDA = Decimal("0.004")       # din config_dobanda.json
PERIOADA_START = (2023, 1)
PERIOADA_FINAL = (2025, 11)           # 12/2025 se lasa liber: il genereaza aplicatia
NR_MEMBRI = 200

CENT = Decimal("0.01")


def q(d: Decimal) -> Decimal:
    """Rotunjire contabila la 2 zecimale, HALF_UP (ca in aplicatie)."""
    return Decimal(d).quantize(CENT, rounding=ROUND_HALF_UP)


def f(d: Decimal) -> float:
    """Decimal -> float pentru stocare in coloane REAL."""
    return float(q(d))


def luni_intre(start, final):
    """Lista de (an, luna) inclusiv, in ordine cronologica."""
    (a0, l0), (a1, l1) = start, final
    out = []
    a, l = a0, l0
    while (a, l) <= (a1, l1):
        out.append((a, l))
        l += 1
        if l > 12:
            l, a = 1, a + 1
    return out


LUNI = luni_intre(PERIOADA_START, PERIOADA_FINAL)
PERIOADA_ULTIMA = LUNI[-1]

# --------------------------------------------------------------------------
# PROFILE DE MEMBRI  (intervale de nr_fisa alese ca sa fie usor de gasit in UI)
# --------------------------------------------------------------------------
PROFILE = [
    ("NORMAL",            1, 120, "Depuneri regulate; ~60% au avut imprumut."),
    ("ZECIMALE",        121, 140, "Cotizatii si rate cu banuti — stres pe rotunjire."),
    ("LUNI_LIPSA",      141, 155, "2-4 luni fara inregistrare — 'Lipsa date sursa'."),
    ("FARA_TRANZACTII", 156, 165, "In MEMBRII, zero randuri in DEPCRED."),
    ("ACHITARE_DEC",    166, 180, "Imprumut care se stinge la generarea lui 12/2025."),
    ("LICHIDATI",       181, 190, "Au istoric, dar sunt in LICHIDATI.db (exclusi)."),
    ("INACTIVI",        191, 200, "In INACTIVI.db cu lipsa_luni."),
]

PRENUME = ["Ion", "Maria", "Ana", "Dan", "Elena", "Mihai", "Carmen", "Victor",
           "Ioana", "Andrei", "Gabriela", "Radu", "Simona", "Cristian", "Adriana",
           "Florin", "Lucia", "Bogdan", "Raluca", "Sorin"]
NUME = ["Popescu", "Ionescu", "Georgescu", "Vasilescu", "Dumitrescu", "Radu",
        "Popa", "Stan", "Marin", "Pavel", "Constantin", "Munteanu", "Barbu",
        "Nistor", "Cojocaru", "Ardelean", "Toma", "Sandu", "Lazar", "Oprea"]
STRAZI = ["Str. Libertatii", "Str. 1 Decembrie", "Bd. Republicii", "Str. Minerilor",
          "Str. Aviatorilor", "Str. Garii", "Str. Unirii", "Aleea Florilor"]
CALITATI = ["Inginer", "Contabil", "Muncitor", "Tehnician", "Economist",
            "Sofer", "Functionar", "Secretar", "Administrator", "Pensionar"]


def profil_pentru(fisa):
    for nume, lo, hi, _ in PROFILE:
        if lo <= fisa <= hi:
            return nume
    return "NORMAL"


# --------------------------------------------------------------------------
# GENERARE MEMBRI
# --------------------------------------------------------------------------
def genereaza_membri(rnd):
    membri = []
    for fisa in range(1, NR_MEMBRI + 1):
        prof = profil_pentru(fisa)
        nume = f"{rnd.choice(NUME)} {rnd.choice(PRENUME)}"
        domiciliu = f"{rnd.choice(STRAZI)} {rnd.randint(1, 180)}"
        calitate = rnd.choice(CALITATI)
        an_inscr = rnd.choice([2018, 2019, 2020, 2021, 2022])
        data_inscr = f"{an_inscr}-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}"

        if prof == "ZECIMALE":
            cotizatie = q(Decimal(rnd.randint(1237, 4783)) / 100)   # ex. 23.71
        else:
            cotizatie = q(Decimal(rnd.choice([10, 15, 20, 25, 30, 40, 50])))

        membri.append({
            "fisa": fisa, "nume": nume, "domiciliu": domiciliu,
            "calitate": calitate, "data_inscr": data_inscr,
            "cotizatie": cotizatie, "profil": prof,
        })
    return membri


# --------------------------------------------------------------------------
# GENERARE ISTORIC DEPCRED  (respecta recurentele din generare_luna.py)
# --------------------------------------------------------------------------
def genereaza_istoric(membri, rnd):
    """
    Returneaza: randuri DEPCRED + plan-ul de imprumuturi (pentru raport).
    Fiecare rand: dict cu cheile coloanelor DEPCRED.
    """
    randuri = []
    plan = {}

    for m in membri:
        fisa, prof = m["fisa"], m["profil"]
        if prof == "FARA_TRANZACTII":
            plan[fisa] = {"imprumuturi": [], "luni_lipsa": []}
            continue

        # --- luni fara inregistrare (doar profilul LUNI_LIPSA) ---
        luni_lipsa = []
        if prof == "LUNI_LIPSA":
            idx = sorted(rnd.sample(range(3, len(LUNI) - 2), rnd.randint(2, 4)))
            luni_lipsa = [LUNI[i] for i in idx]

        # --- planificare imprumut ---
        imprumuturi = []          # (index_luna, suma, rata)
        if prof == "ACHITARE_DEC":
            # Imprumut calibrat: soldul la 11/2025 <= rata, deci se stinge la
            # generarea lui 12/2025 si declanseaza calculul de dobanda.
            nr_rate = rnd.randint(8, 16)
            rata = q(Decimal(rnd.choice([150, 200, 250, 300, 350, 400])))
            suma = q(rata * nr_rate)
            idx_start = len(LUNI) - 1 - nr_rate      # ultima rata cade in 11/2025
            if idx_start < 1:
                idx_start = 1
            imprumuturi.append((idx_start, suma, rata))
        elif prof in ("NORMAL", "ZECIMALE", "LUNI_LIPSA"):
            if rnd.random() < 0.60:
                idx_start = rnd.randint(1, len(LUNI) - 6)
                nr_rate = rnd.randint(6, 30)
                if prof == "ZECIMALE":
                    rata = q(Decimal(rnd.randint(8333, 41667)) / 100)
                else:
                    rata = q(Decimal(rnd.choice([100, 150, 200, 250, 300, 500])))
                suma = q(rata * nr_rate)
                imprumuturi.append((idx_start, suma, rata))
        elif prof == "LICHIDATI":
            if rnd.random() < 0.5:
                idx_start = rnd.randint(1, 12)
                rata = q(Decimal(rnd.choice([100, 200, 300])))
                imprumuturi.append((idx_start, q(rata * rnd.randint(4, 10)), rata))

        plan[fisa] = {"imprumuturi": imprumuturi, "luni_lipsa": luni_lipsa}

        # --- simulare luna cu luna ---
        dep_sold = Decimal("0.00")
        impr_sold = Decimal("0.00")
        rata_curenta = Decimal("0.00")
        avut_rand_anterior = False
        impr_deb_anterior = Decimal("0.00")

        # INACTIVI: se opresc din activitate la un moment dat
        idx_stop = len(LUNI)
        if prof == "INACTIVI":
            idx_stop = len(LUNI) - rnd.randint(3, 10)

        for idx, (an, luna) in enumerate(LUNI):
            if idx >= idx_stop:
                break
            if (an, luna) in luni_lipsa:
                avut_rand_anterior = False
                impr_deb_anterior = Decimal("0.00")
                continue

            impr_deb = Decimal("0.00")
            for (i_start, suma, rata) in imprumuturi:
                if idx == i_start:
                    impr_deb = suma
                    rata_curenta = rata

            # rata efectiv platita luna asta (regula de mostenire)
            if impr_deb > 0:
                impr_cred = Decimal("0.00")          # luna in care se acorda
            elif not avut_rand_anterior:
                impr_cred = Decimal("0.00")          # fara luna sursa
            elif impr_deb_anterior > 0:
                impr_cred = Decimal("0.00")          # luna imediat dupa acordare
            else:
                impr_cred = min(impr_sold, rata_curenta) if impr_sold > Decimal("0.005") \
                    else Decimal("0.00")

            dep_deb = m["cotizatie"]
            dep_cred = Decimal("0.00")
            # retrageri ocazionale (profil NORMAL)
            if prof == "NORMAL" and rnd.random() < 0.02 and dep_sold > Decimal("300"):
                dep_cred = q(Decimal(rnd.randint(50, 250)))

            impr_sold_nou = impr_sold + impr_deb - impr_cred
            impr_sold = Decimal("0.00") if impr_sold_nou <= Decimal("0.005") else impr_sold_nou
            dep_sold = dep_sold + dep_deb - dep_cred

            # dobanda la stingere, calculata ca in aplicatie
            dobanda = Decimal("0.00")
            if impr_cred > 0 and impr_sold == Decimal("0.00"):
                dobanda = calc_dobanda(randuri, fisa, (an, luna))

            randuri.append({
                "NR_FISA": fisa, "LUNA": luna, "ANUL": an,
                "DOBANDA": dobanda, "IMPR_DEB": impr_deb, "IMPR_CRED": impr_cred,
                "IMPR_SOLD": impr_sold, "DEP_DEB": dep_deb, "DEP_CRED": dep_cred,
                "DEP_SOLD": dep_sold,
                "PRIMA": 1 if (an, luna) == PERIOADA_ULTIMA else 0,
            })
            avut_rand_anterior = True
            impr_deb_anterior = impr_deb

    return randuri, plan


def calc_dobanda(randuri, fisa, pana_la):
    """
    Reproduce exact calculul din generare_luna.py:
    suma soldurilor pozitive, de la ultima luna cu impr_deb>0 pana la luna
    SURSA (adica luna anterioara celei in care soldul devine 0), * 0.004.
    """
    ale_mele = [r for r in randuri if r["NR_FISA"] == fisa]
    if not ale_mele:
        return Decimal("0.00")
    p_sursa = (pana_la[0] * 100 + pana_la[1]) - 1
    # luna sursa = ultima inregistrare strict anterioara
    anterioare = [r for r in ale_mele if r["ANUL"] * 100 + r["LUNA"] <= p_sursa]
    if not anterioare:
        return Decimal("0.00")
    p_sursa_real = max(r["ANUL"] * 100 + r["LUNA"] for r in anterioare)
    cu_deb = [r["ANUL"] * 100 + r["LUNA"] for r in anterioare if r["IMPR_DEB"] > 0]
    if not cu_deb:
        return Decimal("0.00")
    p_start = max(cu_deb)
    suma = sum((r["IMPR_SOLD"] for r in ale_mele
                if p_start <= r["ANUL"] * 100 + r["LUNA"] <= p_sursa_real
                and r["IMPR_SOLD"] > 0), Decimal("0.00"))
    return q(suma * RATA_DOBANDA) if suma > 0 else Decimal("0.00")


# --------------------------------------------------------------------------
# PREVIZIUNE: ce trebuie sa produca aplicatia la Generare Luna 12/2025
# --------------------------------------------------------------------------
def prevede_generare_decembrie(membri, randuri, lichidati_set):
    """
    Simuleaza generarea lui 12/2025 exact dupa regulile din generare_luna.py.
    Rezultatul intra in VALORI_ASTEPTATE.md si e ce trebuie sa vezi in aplicatie.
    """
    sursa = {(r["NR_FISA"]): None for r in randuri}
    ultima = {}
    for r in randuri:
        if (r["ANUL"], r["LUNA"]) == PERIOADA_ULTIMA:
            ultima[r["NR_FISA"]] = r

    cot = {m["fisa"]: m["cotizatie"] for m in membri}
    generate, dobanzi, total_dobanda = 0, [], Decimal("0.00")
    omisi_lipsa_sursa = 0
    total_dep_sold = Decimal("0.00")

    for m in membri:
        fisa = m["fisa"]
        if fisa in lichidati_set:
            continue
        r = ultima.get(fisa)
        if r is None:
            omisi_lipsa_sursa += 1
            continue

        impr_sold_sursa = r["IMPR_SOLD"]
        dep_sold_sursa = r["DEP_SOLD"]

        # rata mostenita
        if r["IMPR_DEB"] > 0:
            rata = Decimal("0.00")
        else:
            rata = r["IMPR_CRED"]

        if impr_sold_sursa <= Decimal("0.005"):
            impr_cred = Decimal("0.00")
        else:
            impr_cred = min(impr_sold_sursa, rata)

        impr_sold_nou = impr_sold_sursa - impr_cred
        impr_sold_nou = Decimal("0.00") if impr_sold_nou <= Decimal("0.005") else impr_sold_nou
        dep_sold_nou = dep_sold_sursa + cot[fisa]

        dob = Decimal("0.00")
        if impr_sold_sursa > Decimal("0.005") and impr_sold_nou == Decimal("0.00"):
            dob = calc_dobanda(randuri, fisa, (2025, 12))
            if dob > 0:
                dobanzi.append((fisa, m["nume"], dob))
                total_dobanda += dob

        generate += 1
        total_dep_sold += dep_sold_nou

    _ = sursa
    return {
        "generate": generate,
        "omisi_lipsa_sursa": omisi_lipsa_sursa,
        "nr_dobanzi": len(dobanzi),
        "total_dobanda": total_dobanda,
        "dobanzi": sorted(dobanzi),
        "total_dep_sold": total_dep_sold,
    }


# --------------------------------------------------------------------------
# SCRIERE BAZE DE DATE
# --------------------------------------------------------------------------
SCHEME = {
    "MEMBRII": ("MEMBRII", """
        CREATE TABLE MEMBRII (
            NR_FISA INTEGER PRIMARY KEY,
            NUM_PREN TEXT NOT NULL,
            DOMICILIUL TEXT,
            CALITATEA TEXT,
            DATA_INSCR TEXT,
            COTIZATIE_STANDARD REAL DEFAULT 10.00
        )"""),
    # ATENTIE: exact 11 coloane, fara 'id'. ui/imprumuturi_noi.py:1234 face
    # INSERT INTO depcred VALUES (?x11) — pozitional. O coloana in plus il rupe.
    "DEPCRED": ("DEPCRED", """
        CREATE TABLE DEPCRED (
            NR_FISA INTEGER NOT NULL,
            LUNA INTEGER NOT NULL,
            ANUL INTEGER NOT NULL,
            DOBANDA REAL DEFAULT 0.0,
            IMPR_DEB REAL DEFAULT 0.0,
            IMPR_CRED REAL DEFAULT 0.0,
            IMPR_SOLD REAL DEFAULT 0.0,
            DEP_DEB REAL DEFAULT 0.0,
            DEP_CRED REAL DEFAULT 0.0,
            DEP_SOLD REAL DEFAULT 0.0,
            PRIMA INTEGER DEFAULT 0,
            PRIMARY KEY (NR_FISA, LUNA, ANUL)
        )"""),
    "ACTIVI": ("ACTIVI", """
        CREATE TABLE ACTIVI (
            NR_FISA INTEGER PRIMARY KEY,
            NUM_PREN TEXT,
            DEP_SOLD REAL,
            DIVIDEND REAL DEFAULT 0.0
        )"""),
    "INACTIVI": ("inactivi", """
        CREATE TABLE inactivi (
            nr_fisa INTEGER PRIMARY KEY,
            num_pren TEXT,
            lipsa_luni INTEGER
        )"""),
    "LICHIDATI": ("lichidati", """
        CREATE TABLE lichidati (
            nr_fisa INTEGER PRIMARY KEY,
            data_lichidare TEXT NOT NULL
        )"""),
    "CHITANTE": ("CHITANTE", """
        CREATE TABLE CHITANTE (
            STARTCH_PR INTEGER,
            STARTCH_AC INTEGER
        )"""),
}


def scrie_db(cale: Path, cheie: str, randuri, coloane):
    tabel, ddl = SCHEME[cheie]
    if cale.exists():
        cale.unlink()
    conn = sqlite3.connect(cale)
    try:
        conn.execute(ddl)
        if randuri:
            ph = ", ".join("?" * len(coloane))
            conn.executemany(
                f"INSERT INTO {tabel} ({', '.join(coloane)}) VALUES ({ph})", randuri)
        conn.commit()
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description="Genereaza bazele de date de test.")
    ap.add_argument("--dir", default=None, help="Directorul tinta (implicit: radacina proiectului)")
    ap.add_argument("--force", action="store_true", help="Suprascrie baze existente")
    ap.add_argument("--fara-eur", action="store_true", dest="fara_eur",
                    help="Nu scrie bazele EUR in radacina; le pune in tests/eur_referinta/. "
                         "Foloseste asta cand vrei sa testezi conversia RON->EUR din "
                         "aplicatie: radacina ramane curata, iar setul de referinta "
                         "serveste la compararea rezultatului conversiei.")
    args = ap.parse_args()

    baza = Path(args.dir).resolve() if args.dir else Path(__file__).resolve().parent.parent
    baza.mkdir(parents=True, exist_ok=True)

    toate = ["MEMBRII.db", "DEPCRED.db", "ACTIVI.db", "INACTIVI.db", "LICHIDATI.db",
             "CHITANTE.db", "MEMBRIIEUR.db", "DEPCREDEUR.db", "activiEUR.db",
             "INACTIVIEUR.db", "LICHIDATIEUR.db"]
    existente = [n for n in toate if (baza / n).exists()]
    if existente and not args.force:
        print("STOP — exista deja baze de date in directorul tinta:")
        for n in existente:
            print(f"   {baza / n}")
        print("\nDaca sunt baze de PRODUCTIE, muta-le intai in alta parte.")
        print("Daca sunt tot baze de test, ruleaza din nou cu --force.")
        return 2

    rnd = random.Random(SEED)
    membri = genereaza_membri(rnd)
    randuri, plan = genereaza_istoric(membri, rnd)

    # --- LICHIDATI / INACTIVI ---
    lichidati = [(m["fisa"], f"2025-{rnd.randint(1, 11):02d}-{rnd.randint(1, 28):02d}")
                 for m in membri if m["profil"] == "LICHIDATI"]
    lichidati_set = {fisa for fisa, _ in lichidati}
    inactivi = [(m["fisa"], m["nume"], rnd.randint(3, 10))
                for m in membri if m["profil"] == "INACTIVI"]

    # --- ACTIVI: soldul din Decembrie 2024 (an inchis), fara lichidati ---
    dec24 = {r["NR_FISA"]: r for r in randuri if (r["ANUL"], r["LUNA"]) == (2024, 12)}
    nume_dupa_fisa = {m["fisa"]: m["nume"] for m in membri}
    activi = [(fisa, nume_dupa_fisa[fisa], f(r["DEP_SOLD"]), 0.0)
              for fisa, r in sorted(dec24.items()) if fisa not in lichidati_set]

    # ---------------- scriere RON ----------------
    scrie_db(baza / "MEMBRII.db", "MEMBRII",
             [(m["fisa"], m["nume"], m["domiciliu"], m["calitate"],
               m["data_inscr"], f(m["cotizatie"])) for m in membri],
             ["NR_FISA", "NUM_PREN", "DOMICILIUL", "CALITATEA", "DATA_INSCR",
              "COTIZATIE_STANDARD"])

    col_dep = ["NR_FISA", "LUNA", "ANUL", "DOBANDA", "IMPR_DEB", "IMPR_CRED",
               "IMPR_SOLD", "DEP_DEB", "DEP_CRED", "DEP_SOLD", "PRIMA"]
    scrie_db(baza / "DEPCRED.db", "DEPCRED",
             [tuple(r[c] if c in ("NR_FISA", "LUNA", "ANUL", "PRIMA") else f(r[c])
                    for c in col_dep) for r in randuri], col_dep)

    scrie_db(baza / "ACTIVI.db", "ACTIVI", activi,
             ["NR_FISA", "NUM_PREN", "DEP_SOLD", "DIVIDEND"])
    scrie_db(baza / "INACTIVI.db", "INACTIVI", inactivi,
             ["nr_fisa", "num_pren", "lipsa_luni"])
    scrie_db(baza / "LICHIDATI.db", "LICHIDATI", lichidati,
             ["nr_fisa", "data_lichidare"])
    scrie_db(baza / "CHITANTE.db", "CHITANTE", [(1000, 1000)],
             ["STARTCH_PR", "STARTCH_AC"])

    # ---------------- scriere EUR ----------------
    # Cu --fara-eur, bazele EUR NU ajung in radacina: aplicatia trebuie sa le
    # creeze ea, prin Conversie RON->EUR. Setul generat aici ramane in
    # tests/eur_referinta/ ca REZULTAT ASTEPTAT al acelei conversii.
    baza_eur = (Path(__file__).resolve().parent / "eur_referinta") if args.fara_eur else baza
    baza_eur.mkdir(parents=True, exist_ok=True)

    def eur(v):
        return f(Decimal(str(v)) / CURS_EUR_RON)

    scrie_db(baza_eur / "MEMBRIIEUR.db", "MEMBRII",
             [(m["fisa"], m["nume"], m["domiciliu"], m["calitate"],
               m["data_inscr"], eur(f(m["cotizatie"]))) for m in membri],
             ["NR_FISA", "NUM_PREN", "DOMICILIUL", "CALITATEA", "DATA_INSCR",
              "COTIZATIE_STANDARD"])
    scrie_db(baza_eur / "DEPCREDEUR.db", "DEPCRED",
             [tuple(r[c] if c in ("NR_FISA", "LUNA", "ANUL", "PRIMA") else eur(f(r[c]))
                    for c in col_dep) for r in randuri], col_dep)
    scrie_db(baza_eur / "activiEUR.db", "ACTIVI",
             [(a[0], a[1], eur(a[2]), eur(a[3])) for a in activi],
             ["NR_FISA", "NUM_PREN", "DEP_SOLD", "DIVIDEND"])
    scrie_db(baza_eur / "INACTIVIEUR.db", "INACTIVI", inactivi,
             ["nr_fisa", "num_pren", "lipsa_luni"])
    scrie_db(baza_eur / "LICHIDATIEUR.db", "LICHIDATI", lichidati,
             ["nr_fisa", "data_lichidare"])

    # ---------------- fisa de valori asteptate ----------------
    previziune = prevede_generare_decembrie(membri, randuri, lichidati_set)
    scrie_raport(baza, membri, randuri, plan, lichidati, inactivi, activi, previziune)

    print(f"OK — 11 baze de date scrise in {baza}")
    print(f"   membri: {len(membri)}   randuri DEPCRED: {len(randuri)}")
    print(f"   lichidati: {len(lichidati)}   inactivi: {len(inactivi)}   activi: {len(activi)}")
    print(f"   fisa de valori: {Path(__file__).parent / 'VALORI_ASTEPTATE.md'}")
    return 0


# --------------------------------------------------------------------------
# RAPORT — VALORI_ASTEPTATE.md
# --------------------------------------------------------------------------
def scrie_raport(baza, membri, randuri, plan, lichidati, inactivi, activi, prev):
    out = Path(__file__).resolve().parent / "VALORI_ASTEPTATE.md"

    def s(col, filtru=None):
        return q(sum((r[col] for r in randuri if (filtru is None or filtru(r))),
                     Decimal("0.00")))

    ani = sorted({r["ANUL"] for r in randuri})
    L = []
    A = L.append
    A("# Valori așteptate — baze de date de test")
    A("")
    A("Generat automat de `tests/genereaza_baze_test.py`. **Nu edita manual** —")
    A("rulează scriptul din nou dacă schimbi parametrii.")
    A("")
    A(f"- Seed: `{SEED}` (date identice la fiecare rulare)")
    A(f"- Perioadă: {PERIOADA_START[1]:02d}/{PERIOADA_START[0]} → "
      f"{PERIOADA_FINAL[1]:02d}/{PERIOADA_FINAL[0]}")
    A(f"- Curs EUR: `{CURS_EUR_RON}` · Rată dobândă la stingere: `{RATA_DOBANDA}`")
    A("")
    A("> **La ce folosește:** după fiecare fișier restilizat, deschizi ecranul")
    A("> corespunzător și compari cu tabelele de mai jos. Orice diferență")
    A("> înseamnă că redesign-ul a atins logica → `git revert`.")
    A("")
    A("---")
    A("")
    A("## 1. Totaluri generale")
    A("")
    A("| Indicator | Valoare |")
    A("|---|---:|")
    A(f"| Membri în MEMBRII | {len(membri)} |")
    A(f"| Înregistrări DEPCRED | {len(randuri)} |")
    A(f"| Membri lichidați | {len(lichidati)} |")
    A(f"| Membri inactivi | {len(inactivi)} |")
    A(f"| Rânduri ACTIVI (sold 12/2024) | {len(activi)} |")
    A(f"| Total depuneri (DEP_DEB, toată perioada) | {s('DEP_DEB'):,.2f} |")
    A(f"| Total retrageri (DEP_CRED) | {s('DEP_CRED'):,.2f} |")
    A(f"| Total împrumuturi acordate (IMPR_DEB) | {s('IMPR_DEB'):,.2f} |")
    A(f"| Total rate încasate (IMPR_CRED) | {s('IMPR_CRED'):,.2f} |")
    A(f"| Total dobânzi istorice (DOBANDA) | {s('DOBANDA'):,.2f} |")
    A("")
    A("## 2. Solduri la finalul fiecărui an")
    A("")
    A("| An | Luna | Membri cu rând | Total DEP_SOLD | Total IMPR_SOLD |")
    A("|---|---|---:|---:|---:|")
    for an in ani:
        luni_an = sorted({r["LUNA"] for r in randuri if r["ANUL"] == an})
        lu = luni_an[-1]
        sel = [r for r in randuri if r["ANUL"] == an and r["LUNA"] == lu]
        A(f"| {an} | {lu:02d} | {len(sel)} | "
          f"{q(sum((r['DEP_SOLD'] for r in sel), Decimal('0'))):,.2f} | "
          f"{q(sum((r['IMPR_SOLD'] for r in sel), Decimal('0'))):,.2f} |")
    A("")
    A("## 3. Totaluri lunare 2025 (ecranul Vizualizare Lunară)")
    A("")
    A("| Luna | Rânduri | DEP_DEB | DEP_SOLD | IMPR_CRED | IMPR_SOLD |")
    A("|---|---:|---:|---:|---:|---:|")
    for lu in sorted({r["LUNA"] for r in randuri if r["ANUL"] == 2025}):
        sel = [r for r in randuri if r["ANUL"] == 2025 and r["LUNA"] == lu]
        A(f"| {lu:02d}/2025 | {len(sel)} | "
          f"{q(sum((r['DEP_DEB'] for r in sel), Decimal('0'))):,.2f} | "
          f"{q(sum((r['DEP_SOLD'] for r in sel), Decimal('0'))):,.2f} | "
          f"{q(sum((r['IMPR_CRED'] for r in sel), Decimal('0'))):,.2f} | "
          f"{q(sum((r['IMPR_SOLD'] for r in sel), Decimal('0'))):,.2f} |")
    A("")
    A("## 4. Profile de membri (unde găsești fiecare caz)")
    A("")
    A("| Interval fișe | Profil | Ce testează |")
    A("|---|---|---|")
    for nume, lo, hi, desc in PROFILE:
        A(f"| {lo}–{hi} | `{nume}` | {desc} |")
    A("")
    A("## 5. Fișe de control (verificabile la mână)")
    A("")
    A("Ultima lună înregistrată pentru câțiva membri. Deschide fișa în aplicație")
    A("și compară exact aceste cifre.")
    A("")
    A("| Fișa | Nume | Cotizație | DEP_SOLD 11/2025 | IMPR_SOLD 11/2025 | IMPR_CRED 11/2025 |")
    A("|---:|---|---:|---:|---:|---:|")
    ultima = {r["NR_FISA"]: r for r in randuri if (r["ANUL"], r["LUNA"]) == PERIOADA_ULTIMA}
    cot = {m["fisa"]: m["cotizatie"] for m in membri}
    nm = {m["fisa"]: m["nume"] for m in membri}
    for fisa in [1, 2, 3, 50, 121, 122, 166, 167, 168]:
        r = ultima.get(fisa)
        if r:
            A(f"| {fisa} | {nm[fisa]} | {cot[fisa]:,.2f} | {r['DEP_SOLD']:,.2f} | "
              f"{r['IMPR_SOLD']:,.2f} | {r['IMPR_CRED']:,.2f} |")
    A("")
    A("## 6. Test cheie — Generare Lună 12/2025")
    A("")
    A("Luna 12/2025 e lăsată **negenerată** intenționat. Rulează *Generare Lună*")
    A("în aplicație pentru 12/2025; rezultatul trebuie să fie exact:")
    A("")
    A("| Indicator | Valoare așteptată |")
    A("|---|---:|")
    A(f"| Înregistrări generate | {prev['generate']} |")
    A(f"| Membri omiși (lipsă date sursă) | {prev['omisi_lipsa_sursa']} |")
    A(f"| Număr dobânzi calculate | {prev['nr_dobanzi']} |")
    A(f"| Total dobânzi | {prev['total_dobanda']:,.2f} |")
    A(f"| Total DEP_SOLD după generare | {prev['total_dep_sold']:,.2f} |")
    A("")
    if prev["dobanzi"]:
        A("Dobânzile, pe fișe:")
        A("")
        A("| Fișa | Nume | Dobândă |")
        A("|---:|---|---:|")
        for fisa, nume, d in prev["dobanzi"]:
            A(f"| {fisa} | {nume} | {d:,.2f} |")
        A("")
    A("## 7. Regenerare")
    A("")
    A("```bash")
    A("python tests/genereaza_baze_test.py --force")
    A("python tests/verifica_valori_asteptate.py")
    A("```")
    A("")

    out.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
