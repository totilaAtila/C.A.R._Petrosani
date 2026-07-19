#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifica_valori_asteptate.py — verifică bazele de test generate.

    python tests/verifica_valori_asteptate.py
    python tests/verifica_valori_asteptate.py --dir X

Nu se uită la aspect. Verifică doar că datele sunt COERENTE contabil și că
structura e cea pe care o așteaptă aplicația. Rulează-l:
  - o dată după generare (confirmă că setul e valid)
  - oricând bănuiești că aplicația a scris ceva greșit în baze

Ce verifică:
  1. Structura fiecărei baze == DatabaseSchemaValidator.EXPECTED_SCHEMAS
  2. DEPCRED are EXACT 11 coloane (ui/imprumuturi_noi.py face INSERT pozițional)
  3. Recurența soldurilor, membru cu membru, lună cu lună:
        dep_sold[M]  == dep_sold[M-1]  + dep_deb[M]  - dep_cred[M]
        impr_sold[M] == impr_sold[M-1] + impr_deb[M] - impr_cred[M]
  4. Niciun sold de împrumut negativ
  5. Nicio rată mai mare decât soldul rămas
  6. Integritate referențială: fiecare NR_FISA din DEPCRED există în MEMBRII
  7. Bazele EUR == bazele RON împărțite la curs (±1 ban)
"""
import argparse
import sqlite3
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# Consola Windows e implicit cp1252 si nu poate afisa diacriticele de mai jos.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CENT = Decimal("0.01")
TOL = Decimal("0.011")          # o rotunjire de un ban
CURS_EUR_RON = Decimal("4.9665")

SCHEME_ASTEPTATE = {
    "MEMBRII.db": ("MEMBRII", ["NR_FISA", "NUM_PREN", "DOMICILIUL", "CALITATEA",
                               "DATA_INSCR", "COTIZATIE_STANDARD"]),
    "DEPCRED.db": ("DEPCRED", ["NR_FISA", "LUNA", "ANUL", "DOBANDA", "IMPR_DEB",
                               "IMPR_CRED", "IMPR_SOLD", "DEP_DEB", "DEP_CRED",
                               "DEP_SOLD", "PRIMA"]),
    "ACTIVI.db": ("ACTIVI", ["NR_FISA", "NUM_PREN", "DEP_SOLD", "DIVIDEND"]),
    "INACTIVI.db": ("inactivi", ["nr_fisa", "num_pren", "lipsa_luni"]),
    "LICHIDATI.db": ("lichidati", ["nr_fisa", "data_lichidare"]),
    "CHITANTE.db": ("CHITANTE", ["STARTCH_PR", "STARTCH_AC"]),
}

PERECHI_EUR = [
    ("MEMBRII.db", "MEMBRIIEUR.db", "MEMBRII", "NR_FISA", ["COTIZATIE_STANDARD"]),
    ("DEPCRED.db", "DEPCREDEUR.db", "DEPCRED", "NR_FISA, ANUL, LUNA",
     ["DOBANDA", "IMPR_DEB", "IMPR_CRED", "IMPR_SOLD", "DEP_DEB", "DEP_CRED", "DEP_SOLD"]),
    ("ACTIVI.db", "activiEUR.db", "ACTIVI", "NR_FISA", ["DEP_SOLD", "DIVIDEND"]),
]


def d(v) -> Decimal:
    return Decimal(str(v if v is not None else 0)).quantize(CENT, rounding=ROUND_HALF_UP)


class Raport:
    def __init__(self):
        self.erori = []
        self.note = []

    def eroare(self, msg):
        self.erori.append(msg)

    def nota(self, msg):
        self.note.append(msg)

    @property
    def ok(self):
        return not self.erori


def coloane(conn, tabel):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({tabel})")]


def exista_reala(cale: Path) -> bool:
    """
    Fișier prezent ȘI nevid.

    ATENȚIE: sqlite3.connect(cale) CREEAZĂ fișierul dacă lipsește. Fără această
    verificare, simpla rulare a acestui script fabrica baze goale pe disc — iar
    security_manager le-ar fi raportat apoi drept 'baze neprotejate detectate'.
    Verificăm întotdeauna existența înainte de a deschide o conexiune.
    """
    return cale.exists() and cale.stat().st_size > 0


def verifica_structura(baza: Path, rap: Raport):
    for fisier, (tabel, cols_asteptate) in SCHEME_ASTEPTATE.items():
        cale = baza / fisier
        if not exista_reala(cale):
            lipsa = "lipsește" if not cale.exists() else "este gol (0 octeți)"
            rap.eroare(f"[structura] {fisier} {lipsa}"
                       + (" — probabil e în MEMBRII.zip; porniți aplicația pentru extragere"
                          if fisier.startswith("MEMBRII") else ""))
            continue
        with sqlite3.connect(cale) as conn:
            cols = coloane(conn, tabel)
            if not cols:
                rap.eroare(f"[structura] {fisier}: tabelul '{tabel}' nu există")
                continue
            lipsa = [c for c in cols_asteptate if c.upper() not in [x.upper() for x in cols]]
            if lipsa:
                rap.eroare(f"[structura] {fisier}.{tabel}: coloane lipsă {lipsa}")

    # verificarea critica: DEPCRED trebuie sa aiba fix 11 coloane
    cale = baza / "DEPCRED.db"
    if exista_reala(cale):
        with sqlite3.connect(cale) as conn:
            n = len(coloane(conn, "DEPCRED"))
        if n != 11:
            rap.eroare(
                f"[structura] DEPCRED are {n} coloane, nu 11. "
                f"ui/imprumuturi_noi.py:1234 face 'INSERT INTO depcred VALUES (?x11)' "
                f"— pozițional. Cu alt număr de coloane, acordarea unui împrumut "
                f"nou scrie pe coloane greșite sau crapă.")
        else:
            rap.nota("DEPCRED are exact 11 coloane (INSERT pozițional e sigur)")


def verifica_recurente(baza: Path, rap: Raport):
    cale = baza / "DEPCRED.db"
    if not exista_reala(cale):
        return
    with sqlite3.connect(cale) as conn:
        randuri = conn.execute(
            "SELECT NR_FISA, ANUL, LUNA, IMPR_DEB, IMPR_CRED, IMPR_SOLD,"
            " DEP_DEB, DEP_CRED, DEP_SOLD FROM DEPCRED"
            " ORDER BY NR_FISA, ANUL, LUNA").fetchall()

    pe_fisa = defaultdict(list)
    for r in randuri:
        pe_fisa[r[0]].append(r)

    erori_dep = erori_impr = negative = rate_prea_mari = 0
    for fisa, lista in pe_fisa.items():
        dep_ant = impr_ant = Decimal("0.00")
        prima_luna = True
        for (_, an, luna, i_deb, i_cred, i_sold, d_deb, d_cred, d_sold) in lista:
            i_deb, i_cred, i_sold = d(i_deb), d(i_cred), d(i_sold)
            d_deb, d_cred, d_sold = d(d_deb), d(d_cred), d(d_sold)

            if i_sold < Decimal("0.00"):
                negative += 1
                rap.eroare(f"[sold negativ] fișa {fisa} {luna:02d}/{an}: IMPR_SOLD={i_sold}")

            if not prima_luna:
                asteptat_dep = dep_ant + d_deb - d_cred
                if abs(asteptat_dep - d_sold) > TOL:
                    erori_dep += 1
                    if erori_dep <= 5:
                        rap.eroare(f"[dep_sold] fișa {fisa} {luna:02d}/{an}: "
                                   f"așteptat {asteptat_dep}, găsit {d_sold}")
                asteptat_impr = impr_ant + i_deb - i_cred
                if asteptat_impr <= Decimal("0.005"):
                    asteptat_impr = Decimal("0.00")
                if abs(asteptat_impr - i_sold) > TOL:
                    erori_impr += 1
                    if erori_impr <= 5:
                        rap.eroare(f"[impr_sold] fișa {fisa} {luna:02d}/{an}: "
                                   f"așteptat {asteptat_impr}, găsit {i_sold}")
                if i_cred > impr_ant + i_deb + TOL:
                    rate_prea_mari += 1
                    if rate_prea_mari <= 5:
                        rap.eroare(f"[rată > sold] fișa {fisa} {luna:02d}/{an}: "
                                   f"IMPR_CRED={i_cred}, disponibil={impr_ant + i_deb}")

            dep_ant, impr_ant = d_sold, i_sold
            prima_luna = False

    rap.nota(f"recurențe verificate pe {len(pe_fisa)} membri, {len(randuri)} rânduri")
    if not (erori_dep or erori_impr or negative or rate_prea_mari):
        rap.nota("toate soldurile se leagă lună de lună")


def verifica_prima(baza: Path, rap: Raport):
    """
    PRIMA e un boolean care marchează LUNA ACTIVĂ (cea mai recentă generată).
    generare_luna.py resetează prima=0 pe tot, apoi inserează luna nouă cu prima=1.
    Deci: o singură perioadă poate avea prima=1, și trebuie să fie ultima.
    """
    cale = baza / "DEPCRED.db"
    if not exista_reala(cale):
        return
    with sqlite3.connect(cale) as c:
        active = c.execute(
            "SELECT ANUL, LUNA, COUNT(*) FROM DEPCRED WHERE PRIMA=1"
            " GROUP BY ANUL, LUNA ORDER BY ANUL, LUNA").fetchall()
        ultima = c.execute(
            "SELECT ANUL, LUNA FROM DEPCRED ORDER BY ANUL DESC, LUNA DESC LIMIT 1").fetchone()
        alte_valori = c.execute(
            "SELECT DISTINCT PRIMA FROM DEPCRED WHERE PRIMA NOT IN (0,1)").fetchall()

    if alte_valori:
        rap.eroare(f"[prima] PRIMA e boolean, dar există valori {[v[0] for v in alte_valori]}")
    if not active:
        rap.eroare("[prima] nicio lună marcată ca activă (PRIMA=1)")
        return
    if len(active) > 1:
        rap.eroare(f"[prima] {len(active)} luni marcate active simultan: "
                   f"{[(a, l) for a, l, _ in active]} — poate fi doar una")
        return
    an, luna, nr = active[0]
    if (an, luna) != tuple(ultima):
        rap.eroare(f"[prima] luna activă e {luna:02d}/{an}, dar ultima lună din bază "
                   f"e {ultima[1]:02d}/{ultima[0]}")
    else:
        rap.nota(f"luna activă: {luna:02d}/{an} ({nr} rânduri cu PRIMA=1), "
                 f"restul pe 0")


def verifica_integritate(baza: Path, rap: Raport):
    m, dp = baza / "MEMBRII.db", baza / "DEPCRED.db"
    if not (exista_reala(m) and exista_reala(dp)):
        return
    with sqlite3.connect(m) as c:
        fise_membrii = {r[0] for r in c.execute("SELECT NR_FISA FROM MEMBRII")}
    with sqlite3.connect(dp) as c:
        fise_depcred = {r[0] for r in c.execute("SELECT DISTINCT NR_FISA FROM DEPCRED")}

    orfani = sorted(fise_depcred - fise_membrii)
    if orfani:
        rap.eroare(f"[integritate] {len(orfani)} fișe în DEPCRED fără membru: {orfani[:10]}")
    fara_activitate = sorted(fise_membrii - fise_depcred)
    rap.nota(f"membri: {len(fise_membrii)} · cu activitate: {len(fise_depcred)} · "
             f"fără nicio tranzacție: {len(fara_activitate)} (intenționat, profil FARA_TRANZACTII)")


def verifica_eur(baza: Path, rap: Raport):
    for f_ron, f_eur, tabel, chei, cols in PERECHI_EUR:
        c_ron, c_eur = baza / f_ron, baza / f_eur
        # Cu --fara-eur, setul EUR sta in tests/eur_referinta, ca sa lase radacina
        # libera pentru conversia facuta de aplicatie. Il cautam si acolo.
        if not exista_reala(c_eur):
            alternativ = Path(__file__).resolve().parent / "eur_referinta" / f_eur
            if exista_reala(alternativ):
                c_eur = alternativ
        if not (exista_reala(c_ron) and exista_reala(c_eur)):
            unde = []
            if not exista_reala(c_ron):
                unde.append(f_ron)
            if not exista_reala(c_eur):
                unde.append(f_eur)
            rap.nota(f"[eur] sarit: lipsesc {', '.join(unde)} "
                     f"(normal inainte de conversie)")
            continue
        sel = f"SELECT {chei}, {', '.join(cols)} FROM {tabel} ORDER BY {chei}"
        with sqlite3.connect(c_ron) as a, sqlite3.connect(c_eur) as b:
            ron = a.execute(sel).fetchall()
            eur = b.execute(sel).fetchall()
        if len(ron) != len(eur):
            rap.eroare(f"[eur] {f_eur}: {len(eur)} rânduri vs {len(ron)} în {f_ron}")
            continue
        nr_chei = len(chei.split(","))
        gresite = 0
        for r_ron, r_eur in zip(ron, eur):
            for i in range(nr_chei, len(r_ron)):
                asteptat = (Decimal(str(r_ron[i] or 0)) / CURS_EUR_RON).quantize(
                    CENT, rounding=ROUND_HALF_UP)
                if abs(asteptat - d(r_eur[i])) > TOL:
                    gresite += 1
                    if gresite <= 3:
                        rap.eroare(f"[eur] {f_eur} {r_ron[:nr_chei]} col{i}: "
                                   f"așteptat {asteptat}, găsit {d(r_eur[i])}")
        if not gresite:
            rap.nota(f"{f_eur}: conversie corectă pe {len(eur)} rânduri")


def rezumat(baza: Path):
    print("\n--- Cifre de referință (compară cu ecranele aplicației) ---")
    with sqlite3.connect(baza / "DEPCRED.db") as c:
        for an, luna in [(2023, 12), (2024, 12), (2025, 11)]:
            row = c.execute(
                "SELECT COUNT(*), COALESCE(SUM(DEP_SOLD),0), COALESCE(SUM(IMPR_SOLD),0)"
                " FROM DEPCRED WHERE ANUL=? AND LUNA=?", (an, luna)).fetchone()
            print(f"  {luna:02d}/{an}: {row[0]:>4} rânduri · "
                  f"DEP_SOLD {row[1]:>14,.2f} · IMPR_SOLD {row[2]:>12,.2f}")
        tot = c.execute("SELECT COALESCE(SUM(DOBANDA),0) FROM DEPCRED").fetchone()[0]
        print(f"  Total dobânzi istorice: {tot:,.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    args = ap.parse_args()
    baza = Path(args.dir).resolve() if args.dir else Path(__file__).resolve().parent.parent

    rap = Raport()
    verifica_structura(baza, rap)
    verifica_recurente(baza, rap)
    verifica_prima(baza, rap)
    verifica_integritate(baza, rap)
    verifica_eur(baza, rap)

    print(f"=== Verificare baze de test: {baza} ===")
    for n in rap.note:
        print(f"  OK  {n}")
    if rap.erori:
        print(f"\n  {len(rap.erori)} PROBLEME:")
        for e in rap.erori[:40]:
            print(f"      {e}")
        if len(rap.erori) > 40:
            print(f"      ... și încă {len(rap.erori) - 40}")
        return 1

    print("\n  TOATE VERIFICĂRILE AU TRECUT")
    rezumat(baza)
    return 0


if __name__ == "__main__":
    sys.exit(main())
