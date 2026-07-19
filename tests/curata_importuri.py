#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
curata_importuri.py — elimină importurile nefolosite, conservator.

    python tests/curata_importuri.py            # doar raportează
    python tests/curata_importuri.py --scrie    # elimină efectiv

PRUDENȚĂ:
Un import se elimină DOAR dacă numele nu apare nicăieri altundeva în fișier —
nici în cod, nici în șiruri de caractere, nici în comentarii. Astfel, un import
folosit dinamic (getattr, eval, nume construit ca text) nu poate fi șters din
greșeală. Prețul e că unele importuri chiar nefolosite rămân pe loc; într-un cod
contabil, prudența e mai ieftină decât o regresie.

NU atinge:
  - importuri cu efecte secundare cunoscute (vezi PASTREAZA)
  - fișierele din PROTEJATE, unde câștigul nu justifică riscul
"""
import argparse
import ast
import io
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Importuri care se pastreaza chiar daca par nefolosite (efecte secundare)
PASTREAZA = {"sip", "pyqt5", "PyQt5", "matplotlib", "qtmodern"}

# Fisiere pe care nu le atingem deloc
PROTEJATE = {"palette.py", "conftest.py"}

EXCLUSE_DIR = {".git", "__pycache__", "handoff", "build", "dist", "venv", "eur_referinta"}


def analizeaza(cale: Path):
    """Returnează [(linie, nume, textul liniei)] pentru importuri sigur nefolosite."""
    src = io.open(cale, encoding="utf-8-sig", errors="replace").read()
    try:
        arbore = ast.parse(src)
    except SyntaxError:
        return [], src
    linii = src.split("\n")

    candidati = []
    for nod in ast.walk(arbore):
        if isinstance(nod, (ast.Import, ast.ImportFrom)):
            for alias in nod.names:
                if alias.name == "*":
                    continue
                nume = alias.asname or (alias.name.split(".")[0]
                                        if isinstance(nod, ast.Import) else alias.name)
                if nume in PASTREAZA:
                    continue
                candidati.append((nod.lineno, nume))

    # Textul fisierului FARA liniile de import — daca numele apare aici, il pastram.
    linii_import = {l for l, _ in candidati}
    rest = "\n".join(t for i, t in enumerate(linii, 1) if i not in linii_import)

    sigure = []
    for linie, nume in candidati:
        if re.search(r"\b" + re.escape(nume) + r"\b", rest):
            continue                      # apare undeva -> nu atingem
        sigure.append((linie, nume, linii[linie - 1]))
    return sigure, src


def elimina(cale: Path, sigure, src):
    """Șterge numele din liniile de import; linia dispare doar dacă rămâne goală."""
    linii = src.split("\n")
    pe_linie = {}
    for linie, nume, _ in sigure:
        pe_linie.setdefault(linie, []).append(nume)

    for linie, nume_list in pe_linie.items():
        t = linii[linie - 1]
        for nume in nume_list:
            t = re.sub(r"(?<![\w.])" + re.escape(nume) + r"\s*,\s*", "", t)
            t = re.sub(r",\s*" + re.escape(nume) + r"(?![\w.])", "", t)
            t = re.sub(r"^(\s*(?:from\s+\S+\s+)?import\s+)" + re.escape(nume) + r"\s*$",
                       "", t)
        # linie ramasa fara nimic de importat -> se sterge
        if re.match(r"^\s*(from\s+\S+\s+)?import\s*\(?\s*\)?\s*$", t) or not t.strip():
            linii[linie - 1] = None
        else:
            linii[linie - 1] = t

    rezultat = "\n".join(l for l in linii if l is not None)
    ast.parse(rezultat)        # nu scriem nimic care nu se compileaza
    return rezultat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    ap.add_argument("--scrie", action="store_true")
    args = ap.parse_args()
    radacina = Path(args.dir).resolve() if args.dir else Path(__file__).resolve().parent.parent

    total, fisiere = 0, 0
    for cale in sorted(radacina.rglob("*.py")):
        if EXCLUSE_DIR & set(cale.relative_to(radacina).parts):
            continue
        if cale.name in PROTEJATE:
            continue
        sigure, src = analizeaza(cale)
        if not sigure:
            continue
        fisiere += 1
        total += len(sigure)
        print(f"\n{cale.relative_to(radacina)}")
        for linie, nume, _ in sigure:
            print(f"   l.{linie:<5} {nume}")
        if args.scrie:
            cale.write_text(elimina(cale, sigure, src), encoding="utf-8")

    print(f"\n{'-' * 60}")
    print(f"{total} importuri {'eliminate' if args.scrie else 'nefolosite'} "
          f"in {fisiere} fisiere.")
    if not args.scrie:
        print("Ruleaza cu --scrie pentru a le elimina.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
