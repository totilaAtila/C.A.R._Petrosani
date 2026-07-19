# Handoff redesign UI — C.A.R. Petroșani → Claude Code

Pachet pentru implementarea temei **„Glass Verde Rafinat"** în aplicația PyQt5,
în siguranță, pe un branch separat. Direcția vizuală e validată (mockup aprobat).

---

## ⚠️ REGULA DE AUR (citește prima dată, respect-o la fiecare fișier)

> **Se modifică EXCLUSIV conținutul string-urilor de stil** (`setStyleSheet`,
> valori de culoare, `border-radius`, `padding`, gradient).
>
> **NU se atinge, sub nicio formă:**
> - numele de variabile, clase, `objectName`, `setObjectName`
> - semnalele și sloturile (`.clicked.connect(...)`, `.currentIndexChanged`, etc.)
> - interogările SQL, accesul la baze de date, calculele (`format_number_ro`,
>   `_sum_from_depcred`, orice `_count_*`, logica de dobândă/dividende/conversie)
> - structura layout-urilor (ce widget e adăugat unde) dacă nu e strict necesar
> - fișierele de logic/business din afara folderului `ui/` de prezentare
>
> **Test obligatoriu după FIECARE fișier:** pornește aplicația, deschide ecranul
> modificat, și compară cifrele cu o situație lunară cunoscută. Cifrele trebuie
> să fie **identice**. Dacă diferă orice sold → revert imediat acel commit.

O culoare greșită produce doar un widget urât — niciodată un sold greșit,
**cât timp regula de aur e respectată.**

---

## Pasul 0 — Clonare și branch (o singură dată)

Repo-ul este doar pe GitHub, trebuie clonat local:

```bash
cd C:\Users\totil\PycharmProjects\
git clone https://github.com/totilaAtila/C.A.R._Petrosani.git
cd C.A.R._Petrosani

# branch dedicat — main (producția) rămâne neatins
git checkout -b redesign-ui-glass-verde
```

Revenire la producție oricând:
```bash
git checkout main
```

---

## Pasul 1 — Adaugă sursa unică de stil

Copiază `handoff/ui/palette.py` din acest pachet în `ui/palette.py` al repo-ului.
Este un fișier NOU, nu suprascrie nimic. Conține doar valori de stil
(culori, gradienturi, radius) și fabrici QSS (`btn_primary()`, `card()`,
`table()`, `header_bar()`, etc.).

```bash
git add ui/palette.py
git commit -m "UI: palette.py — sursa unică de culoare (redesign, doar stil)"
```

---

## Pasul 2 — Șablonul de referință: statistici.py

`handoff/ui/statistici.py` este fișierul real, deja restilizat, ca **exemplu
de urmat**. Compară-l cu originalul (`git diff`) — vei vedea că **doar
string-urile de stil s-au schimbat**:

- glass semi-transparent greu → carduri albe curate, bordură fină `P.LINE`
- header albastru → verde accent (`GRAD.ACCENT`) — unicul accent tare pe pagină
- progress bar cu gradient dublu → verde plat, colț consistent
- fundal albastru → neutru subtil (`GRAD.APP_BG`)
- tooltip → slate-verde din paletă

Culorile semantice ale cardurilor (albastru = membri, verde = depuneri,
roșu = împrumuturi) sunt **păstrate** ca argumente — opțional pot fi mapate
mai târziu la `P.INFO / P.POSITIVE / P.DANGER / P.WARNING` pentru armonie
completă, dar nu e necesar pentru funcționare.

```bash
# copiază handoff/ui/statistici.py peste ui/statistici.py
git add ui/statistici.py
git commit -m "UI: statistici.py — temă rafinată (doar stil)"
# RULEAZĂ aplicația, deschide Statistici, verifică cifrele
```

---

## Pasul 3 — Restul fișierelor, unul câte unul

Aplică același tipar în fiecare fișier `ui/*.py` care are `setStyleSheet`.
Ordine recomandată (cele mai vizibile întâi):

1. `ui/sume_lunare.py`  — tabel + dialog (înlocuiește `#28a745`, `#17a2b8`,
   `#6c757d`, `#dc3545` cu `btn_primary/secondary/soft` și `table()`)
2. `ui/vizualizare_lunara.py` — tabel (`table()`, rând TOTAL cu `P.ACCENT_SOFT`)
3. `ui/dividende.py`
4. `ui/vizualizare_*.py` (trimestrială, anuală)
5. dialoguri (`dialog_styles.py`, `adauga_membru.py`, `actualizare_membru.py`, …)
6. `ui/listari*.py`

Pentru fiecare fișier, tiparul de înlocuire:

| Vechi (hard-codat)                          | Nou (din paletă)                    |
|---------------------------------------------|-------------------------------------|
| `#28a745`, verde Bootstrap                  | `P.ACCENT` / `btn_primary()`        |
| `#17a2b8`, `#007bff` info                   | `P.INFO` / `btn_soft()`             |
| `#6c757d` gri buton                         | `btn_secondary()`                   |
| `#dc3545` roșu                              | `P.DANGER`                          |
| `#f39c12` portocaliu                        | `P.WARNING`                         |
| `qlineargradient(... rgba alb 0.5 ...)`     | `P.PANEL` (fundal plat)             |
| `border-radius: 8px/10px/6px` (amestecat)   | `RADIUS.MD` / `RADIUS.LG`           |
| tabel fără stil coerent                     | `table()`                           |

Un commit per fișier + test după fiecare. Astfel orice problemă se izolează
și se revocă individual (`git revert <hash>`).

**Înainte de FIECARE commit — rulează plasa de siguranță automată:**
```bash
python handoff/verifica_siguranta.py ui/<fișier>
```
Compară fișierul cu versiunea git și alarmează dacă s-a schimbat orice în afara
stilului (semnale `.connect`, SQL, calcule, `objectName`). 🔴 alarmă → **NU face
commit**, verifică fiecare linie. 🟢 → rulează aplicația, compară cifrele, apoi commit.

---

## Pasul 4 — Meniul lateral (deja făcut)

`main_ui.py` are deja tema nouă „🌿 Glass Verde Rafinat" (index 21), setată
implicită. Fișierul modificat e în acest pachet dacă e nevoie. Nimic de făcut
în plus, decât `git add main_ui.py` pe branch.

---

## Recomandări de siguranță suplimentare

- **Testează pe o COPIE a bazelor de date** (`*.db`), nu pe cele de producție,
  până ai încredere completă.
- Ține un checklist de verificare: pentru 2-3 membri cunoscuți, notează
  soldurile înainte și după — trebuie identice.
- Nu combina redesign-ul cu alte modificări funcționale în același commit.
- La final, când tot branch-ul e testat: `git checkout main && git merge redesign-ui-glass-verde`.

---

## Ce e în pachet

```
handoff/
├─ HANDOFF_REDESIGN.md      ← acest document
└─ ui/
   ├─ palette.py            ← FIȘIER NOU — sursa unică de stil
   └─ statistici.py         ← ȘABLON restilizat (diff = doar stil)
```

Mockup-ul vizual complet (referință de aspect): `Redesign CAR Petrosani.dc.html`.
