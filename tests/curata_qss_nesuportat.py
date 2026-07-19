#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
curata_qss_nesuportat.py — găsește (și opțional elimină) proprietăți CSS pe care
Qt NU le suportă în QSS.

    python tests/curata_qss_nesuportat.py             # doar raportează
    python tests/curata_qss_nesuportat.py --scrie     # elimină efectiv

DE CE:
Qt implementează un subset din CSS. Proprietăți ca `box-shadow`, `text-shadow`,
`transform` sau `transition` sunt PARSATE, IGNORATE și raportate pe stderr ca
"Unknown property X" — o dată pentru fiecare widget stilizat. Rezultatul e o
consolă inundată și, mai important, un efect vizual pe care crezi că îl ai dar
nu îl ai. Umbrele și animațiile din codul acesta nu s-au randat niciodată.

Alternative reale în Qt, dacă vrei efectul:
  box-shadow / text-shadow  -> QGraphicsDropShadowEffect (în cod, nu în QSS)
  transform / transition    -> QPropertyAnimation pe geometrie
  opacity                   -> QGraphicsOpacityEffect sau setWindowOpacity

SIGURANȚĂ:
Elimină DOAR declarații QSS. Nu atinge cod Python: un `cursor` de bază de date
(`cursor = conn.cursor()`) nu se potrivește tiparului, care cere forma
`proprietate: valoare;`. Rulează întâi fără --scrie și citește raportul.
"""
import argparse
import io
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Proprietati CSS pe care Qt le ignora (lista din documentatia Qt Style Sheets)
NESUPORTATE = [
    "text-shadow", "box-shadow", "backdrop-filter", "filter",
    "transform", "transition", "animation",
    "cursor", "z-index", "overflow", "flex", "content",
]

# Linie care contine DOAR declaratia -> se sterge linia intreaga
TIPAR_LINIE = re.compile(
    r"^\s*(?:" + "|".join(NESUPORTATE) + r")\s*:[^;]*;\s*(?:/\*.*?\*/)?\s*$")
# Declaratie in interiorul unei linii mai lungi -> se scoate doar declaratia
TIPAR_INLINE = re.compile(
    r"\s*(?:" + "|".join(NESUPORTATE) + r")\s*:[^;]*;")

EXCLUSE = {".git", "__pycache__", "handoff", "tests", "build", "dist", "venv"}


def fisiere_python(radacina: Path):
    for cale in sorted(radacina.rglob("*.py")):
        if EXCLUSE & set(cale.relative_to(radacina).parts):
            continue
        yield cale


def proceseaza(cale: Path, scrie: bool):
    brut = cale.read_bytes()
    bom = brut.startswith(b"\xef\xbb\xbf")
    text = brut.decode("utf-8-sig")
    linii = text.split("\n")

    pastrate, gasite = [], []
    for nr, linie in enumerate(linii, 1):
        if TIPAR_LINIE.match(linie):
            gasite.append((nr, linie.strip(), "linie"))
            continue                      # se elimina complet
        curatata, n = TIPAR_INLINE.subn("", linie)
        if n:
            gasite.append((nr, linie.strip(), f"inline x{n}"))
            pastrate.append(curatata)
        else:
            pastrate.append(linie)

    if gasite and scrie:
        nou = "\n".join(pastrate)
        cale.write_bytes((b"\xef\xbb\xbf" if bom else b"") + nou.encode("utf-8"))
    return gasite


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    ap.add_argument("--scrie", action="store_true",
                    help="Elimina efectiv (implicit: doar raporteaza)")
    args = ap.parse_args()

    radacina = Path(args.dir).resolve() if args.dir else Path(__file__).resolve().parent.parent
    total, fisiere_atinse = 0, 0

    for cale in fisiere_python(radacina):
        gasite = proceseaza(cale, args.scrie)
        if not gasite:
            continue
        fisiere_atinse += 1
        total += len(gasite)
        rel = cale.relative_to(radacina)
        print(f"\n{rel}")
        for nr, continut, fel in gasite:
            taiat = continut if len(continut) <= 92 else continut[:89] + "..."
            print(f"   {nr:>5}  [{fel}]  {taiat}")

    print(f"\n{'-' * 70}")
    if total == 0:
        print("Nicio proprietate nesuportata. Consola ramane curata.")
        return 0
    verb = "eliminate" if args.scrie else "gasite"
    print(f"{total} declaratii {verb} in {fisiere_atinse} fisiere.")
    if not args.scrie:
        print("Ruleaza din nou cu --scrie pentru a le elimina.")
    else:
        print("Verifica acum: python handoff/verifica_siguranta.py <fisier>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
