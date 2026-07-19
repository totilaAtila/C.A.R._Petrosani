#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifica_siguranta.py — PLASA DE SIGURANȚĂ a regulii de aur.

Compară un fișier restilizat cu versiunea originală (din git sau backup) și
ALARMEAZĂ dacă s-a schimbat CEVA în afara stilului. Rulează după fiecare fișier,
ÎNAINTE de commit. Dacă raportează linii roșii → NU face commit, verifică.

    python verifica_siguranta.py ui/sume_lunare.py

Compară implicit cu versiunea din `git show HEAD:<fisier>`. Alternativ:
    python verifica_siguranta.py ui/sume_lunare.py backup/sume_lunare.py

Ce e considerat "sigur" (modificări permise de redesign):
  - linii care conțin culori hex (#rrggbb), rgba(), qlineargradient
  - linii cu proprietăți QSS pure: border-radius, padding, margin, background,
    color, font-size, font-weight, border, min-height, max-height
  - linii în interiorul unui string de stil

Ce declanșează ALARMĂ ROȘIE (interzis de regula de aur):
  - modificări pe linii cu .connect( / .clicked / semnale
  - modificări pe def / class / return / import de LOGICĂ
  - modificări pe interogări SQL (SELECT/INSERT/UPDATE/DELETE/execute/cursor)
  - modificări pe setObjectName / objectName
  - modificări pe nume de funcții de calcul (format_number, sum, count, calcul,
    dobanda, dividend, sold, rata, conversie)
"""
import sys, subprocess, re, difflib

# Consola Windows e implicit cp1252 si nu poate afisa diacriticele/emoji-urile
# de mai jos -> UnicodeEncodeError la print, dupa ce analiza s-a facut deja.
# Fortam UTF-8 pe stdout/stderr. Nu afecteaza analiza, doar afisarea.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

STYLE_SAFE = re.compile(
    r'#[0-9a-fA-F]{3,8}\b|rgba?\(|qlineargradient|border-radius|padding|margin'
    r'|background|(?<!\w)color\s*:|font-size|font-weight|font-family|(?<!\w)border'
    r'|min-height|max-height|min-width|max-width|alternate-background|gridline'
    r'|setStyleSheet|"""|from ui\.palette|P\.|GRAD\.|RADIUS\.|FONT|btn_|card\(|table\(|input_field|header_bar',
    re.I)

DANGER = re.compile(
    r'\.connect\(|\.clicked|\.currentIndex|\.textChanged|\.valueChanged'
    r'|\bdef\b|\bclass\b|\breturn\b'
    r'|SELECT|INSERT|UPDATE|DELETE|\.execute|cursor|commit\(|sqlite'
    r'|setObjectName|objectName'
    r'|format_number|calcul|dobanda|dobânda|dividend|\bsold\b|\brata\b|\brată\b'
    r'|conversie|sum\(|count\(|round\(|Decimal',
    re.I)


def get_original(path, backup):
    if backup:
        with open(backup, encoding='utf-8') as f:
            return f.read().splitlines()
    try:
        out = subprocess.check_output(['git', 'show', f'HEAD:{path}'],
                                      stderr=subprocess.DEVNULL)
        return out.decode('utf-8').splitlines()
    except Exception:
        print(f"⚠  Nu pot obține versiunea git a {path}. Dă un backup ca al 2-lea argument.")
        sys.exit(2)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    path = sys.argv[1]
    backup = sys.argv[2] if len(sys.argv) > 2 else None
    with open(path, encoding='utf-8') as f:
        new = f.read().splitlines()
    old = get_original(path, backup)

    diff = list(difflib.unified_diff(old, new, lineterm='', n=0))
    changed = [l for l in diff if (l.startswith('+') or l.startswith('-'))
               and not l.startswith('+++') and not l.startswith('---')]

    alarms, safe = [], 0
    for line in changed:
        body = line[1:].strip()
        if not body:
            continue
        if DANGER.search(body) and not STYLE_SAFE.search(body):
            alarms.append(line)
        else:
            safe += 1

    print(f"\n=== Verificare siguranță: {path} ===")
    print(f"Linii schimbate: {len(changed)}  |  aparent-stil: {safe}  |  suspecte: {len(alarms)}")

    if alarms:
        print("\n🔴 ALARMĂ — linii schimbate care ating (posibil) LOGICA. NU face commit:")
        for a in alarms[:60]:
            print("   ", a)
        if len(alarms) > 60:
            print(f"    … și încă {len(alarms) - 60}")
        print("\nVerifică manual fiecare. Dacă e doar stil (fals pozitiv), ok. "
              "Dacă e semnal/SQL/calcul modificat → REVERT.")
        sys.exit(3)
    else:
        print("\n🟢 OK — toate modificările par a fi doar de stil. "
              "Rulează totuși aplicația și compară cifrele înainte de commit.")
        sys.exit(0)


if __name__ == '__main__':
    main()
