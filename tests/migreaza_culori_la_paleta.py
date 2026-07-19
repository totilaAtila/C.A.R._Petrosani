#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migreaza_culori_la_paleta.py — înlocuiește culorile hex literale din string-urile
de stil cu tokeni din ui/palette.py, mecanic și verificabil.

    python tests/migreaza_culori_la_paleta.py ui/despre.py           # raport
    python tests/migreaza_culori_la_paleta.py ui/despre.py --scrie   # aplică

CUM FUNCȚIONEAZĂ
Găsește, prin AST, fiecare literal string care conține culori hex. Îl transformă
în f-string (acoladele QSS se dublează) și înlocuiește fiecare hex cu tokenul
corespunzător din dicționarul de mai jos — cel din handoff/INVENTAR_STIL.md.

DE CE E SIGUR
După transformare, fiecare f-string nou e EVALUAT și rezultatul comparat cu
originalul în care s-au substituit direct valorile paletei. Dacă cele două nu
coincid caracter cu caracter, fișierul NU se scrie. Astfel, o acoladă greșită
sau un string stricat sunt imposibil de ratat: verificarea e o dovadă, nu o
inspecție vizuală.

Atinge exclusiv literali string care conțin culori. Nu se apropie de cod.
"""
import argparse
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from ui.palette import P, GRAD, RADIUS  # noqa: E402

# ---------------------------------------------------------------------------
# DICTIONARUL DE CULORI  (handoff/INVENTAR_STIL.md, sectiunea A)
# hex literal gasit in cod -> numele tokenului din palette.P
# ---------------------------------------------------------------------------
MAPARE = {}


def _adauga(token, *hexuri):
    for h in hexuri:
        MAPARE[h.lower()] = token


# Neutrale — fundal, suprafete
_adauga("PANEL_2", "#f8f9fa", "#ecf0f1", "#e9ecef", "#f0f0f0", "#eeeeee")
_adauga("PANEL", "#ffffff")
# Borduri
_adauga("LINE", "#dee2e6", "#bdc3c7", "#adb5bd", "#d0d0d0", "#e0e0e0", "#d5dbdb")
# Text
_adauga("INK", "#2c3e50", "#34495e", "#333333", "#37474f")
_adauga("MUTED", "#495057")
_adauga("FAINT", "#6c757d", "#7f8c8d", "#666666")
# Albastru informativ
_adauga("NEUTRAL", "#95a5a6")
_adauga("INFO", "#3498db", "#2980b9", "#0078d4", "#005a9e", "#007bff", "#4a90e2",
        "#0056b3", "#1565c0", "#1e3a8a", "#0ea5e9", "#0284c7", "#0d6efd",
        "#084298", "#004085", "#0c5460", "#2196f3")
# Fundaluri albastre deschise -> neutru (INVENTAR: devin PANEL_2)
_adauga("PANEL_2", "#e8f1ff", "#cce5ff", "#e7f3ff", "#cfe2ff", "#d1ecf1",
        "#e3f2fd", "#bbdefb", "#bee5eb", "#9ec5fe", "#e8f4f8", "#e8f4fd")
# Verde pozitiv
_adauga("POSITIVE", "#28a745", "#27ae60", "#2ecc71", "#20c997", "#229954",
        "#186a3b", "#34ce57", "#059669", "#047857", "#155724", "#2e7d32")
_adauga("ACCENT_SOFT", "#d4edda", "#e8f5e8", "#f8fff8", "#e8f5e9")
# Rosu pericol
_adauga("DANGER", "#e74c3c", "#c0392b", "#dc3545", "#ee5a52", "#ff6b6b",
        "#ff7b7b", "#721c24")
_adauga("DANGER_SOFT", "#f8d7da", "#fff5f5", "#ffebee", "#ffcdd2")
# Chihlimbar / avertisment
_adauga("WARNING", "#f39c12", "#e67e22", "#d35400", "#ffaa00", "#ff8c00",
        "#ffa500", "#a04000", "#856404", "#e65100", "#ffc107", "#ff9800")
_adauga("WARNING_SOFT", "#fff3cd", "#fdf6e3", "#fff8e1", "#ffecb3")
# Mov — outlier, INVENTAR recomanda eliminarea lui
_adauga("ACCENT_DEEP", "#7c3aed", "#8e44ad", "#6a1b9a", "#4c0a9b", "#3e2c50",
        "#6610f2")
_adauga("ACCENT_SOFT", "#f3e5f5")

TIPAR_HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
NAMESPACE = {"P": P, "GRAD": GRAD, "RADIUS": RADIUS}


def literali_cu_culori(arbore, sursa_linii):
    """Returnează literalii string care conțin culori hex, cu pozițiile lor."""
    gasiti = []
    for nod in ast.walk(arbore):
        if not isinstance(nod, ast.Constant) or not isinstance(nod.value, str):
            continue
        if not TIPAR_HEX.search(nod.value):
            continue
        if nod.end_lineno is None:
            continue
        gasiti.append(nod)
    # de la coada spre cap, ca inlocuirile sa nu mute pozitiile urmatoare
    gasiti.sort(key=lambda n: (n.lineno, n.col_offset), reverse=True)
    return gasiti


def segment(sursa_linii, nod):
    if nod.lineno == nod.end_lineno:
        return sursa_linii[nod.lineno - 1][nod.col_offset:nod.end_col_offset]
    bucati = [sursa_linii[nod.lineno - 1][nod.col_offset:]]
    bucati += sursa_linii[nod.lineno:nod.end_lineno - 1]
    bucati.append(sursa_linii[nod.end_lineno - 1][:nod.end_col_offset])
    return "\n".join(bucati)


def construieste_fstring(brut, valoare):
    """Din literalul sursă construiește varianta f-string cu tokeni."""
    m = re.match(r"^([rbuRBU]*)('''|\"\"\"|'|\")", brut)
    if not m:
        return None, None
    prefix, ghilimele = m.group(1), m.group(2)
    if "f" in prefix.lower():
        return None, None                     # deja f-string, nu atingem
    corp = brut[len(prefix) + len(ghilimele): -len(ghilimele)]

    corp_nou = corp.replace("{", "{{").replace("}", "}}")

    necunoscute = set()

    def inlocuieste(m):
        h = m.group(0).lower()
        token = MAPARE.get(h)
        if token is None:
            necunoscute.add(h)
            return m.group(0)
        return "{P." + token + "}"

    corp_nou = TIPAR_HEX.sub(inlocuieste, corp_nou)
    nou = f"f{prefix}{ghilimele}{corp_nou}{ghilimele}"

    # ---- DOVADA: f-string-ul evaluat == originalul cu valorile paletei ----
    try:
        randat = eval(nou, {"__builtins__": {}}, NAMESPACE)
    except Exception as e:
        return None, f"f-string invalid: {e}"

    asteptat = TIPAR_HEX.sub(
        lambda m: getattr(P, MAPARE[m.group(0).lower()]) if m.group(0).lower() in MAPARE
        else m.group(0), valoare)

    if randat != asteptat:
        return None, "randarea difera de original (transformare nesigura)"
    return nou, (f"culori nemapate: {sorted(necunoscute)}" if necunoscute else None)


def proceseaza(cale: Path, scrie: bool):
    sursa = cale.read_text(encoding="utf-8-sig")
    linii = sursa.split("\n")
    arbore = ast.parse(sursa)
    noduri = literali_cu_culori(arbore, linii)

    schimbate, sarite, avertismente = 0, 0, []
    for nod in noduri:
        brut = segment(linii, nod)
        nou, nota = construieste_fstring(brut, nod.value)
        if nou is None:
            sarite += 1
            if nota:
                avertismente.append(f"  linia {nod.lineno}: {nota}")
            continue
        if nota:
            avertismente.append(f"  linia {nod.lineno}: {nota}")

        if nod.lineno == nod.end_lineno:
            l = linii[nod.lineno - 1]
            linii[nod.lineno - 1] = l[:nod.col_offset] + nou + l[nod.end_col_offset:]
        else:
            cap = linii[nod.lineno - 1][:nod.col_offset]
            coada = linii[nod.end_lineno - 1][nod.end_col_offset:]
            linii[nod.lineno - 1:nod.end_lineno] = (cap + nou + coada).split("\n")
        schimbate += 1

    rezultat = "\n".join(linii)
    ast.parse(rezultat)          # nu scriem nimic care nu se compileaza

    if scrie and schimbate:
        cale.write_text(rezultat, encoding="utf-8")

    return schimbate, sarite, avertismente


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fisier")
    ap.add_argument("--scrie", action="store_true")
    args = ap.parse_args()

    cale = Path(args.fisier).resolve()
    schimbate, sarite, avertismente = proceseaza(cale, args.scrie)

    print(f"=== {cale.name} ===")
    print(f"  literali de stil transformati : {schimbate}")
    print(f"  sariti (deja f-string / neconvertibili): {sarite}")
    for a in avertismente[:30]:
        print(a)
    if len(avertismente) > 30:
        print(f"  ... si inca {len(avertismente) - 30}")

    ramase = TIPAR_HEX.findall(cale.read_text(encoding="utf-8-sig"))
    print(f"  culori hex ramase in fisier   : {len(set(ramase))} distincte")
    if ramase:
        print(f"    {sorted(set(h.lower() for h in ramase))}")
    if not args.scrie:
        print("\n  (dry-run — ruleaza cu --scrie pentru a aplica)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
