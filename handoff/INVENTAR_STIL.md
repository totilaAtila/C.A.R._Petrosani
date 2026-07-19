# Inventar & audit stil — C.A.R. Petroșani

Hartă de lucru pentru redesign, generată din codul real (`main` @e51088d).
**230 apeluri `setStyleSheet` · ~1050 culori literale · ~30 fișiere.**

Scop: Claude Code nu explorează — urmează acest tabel. Pentru fiecare fișier
știe câte apeluri are, ce culori apar, la ce token din `palette.py` mapează,
și cât de riscant e (proximitatea de logică contabilă).

---

## A. DICȚIONAR DE CULORI  (literal găsit în cod → token paletă)

Acestea sunt TOATE familiile care reapar. Înlocuiește mecanic; sensul se
păstrează pentru că gruparea pe rol rămâne identică.

### Verde (pozitiv / succes / salvare / achitat)
`#28a745` `#27ae60` `#2ecc71` `#20c997` `#229954` `#186a3b` `#34ce57`
`#059669` `#047857` `#155724` `#2e7d32`  →  **`P.POSITIVE` / `P.ACCENT`**
(gradient verde → `GRAD.ACCENT`; fundal verde deschis `#d4edda #e8f5e8 #f8fff8` → `P.ACCENT_SOFT`)

### Albastru (informativ / primar vechi / refresh / neutru-acțiune)
`#3498db` `#2980b9` `#0078d4` `#005a9e` `#007bff` `#4a90e2` `#0056b3`
`#1565c0` `#1e3a8a` `#0ea5e9` `#0284c7` `#0d6efd` `#084298`  →  **`P.INFO`**
(fundal albastru deschis `#e8f1ff #cce5ff #e7f3ff #cfe2ff #d1ecf1` → `P.PANEL_2` sau fundal info dedicat)

### Roșu (pericol / ștergere / eroare / stop)
`#e74c3c` `#c0392b` `#dc3545` `#ee5a52` `#ff6b6b` `#ff7b7b` `#721c24`  →  **`P.DANGER`**
(fundal roșu deschis `#f8d7da #fff5f5 #ffebee #ffcdd2` → `P.DANGER_SOFT`)

### Portocaliu / chihlimbar (avertisment / atenție / doar-citire)
`#f39c12` `#e67e22` `#d35400` `#ffaa00` `#ff8c00` `#ffa500` `#a04000`
`#856404` `#e65100` `#E67E22`  →  **`P.WARNING`**
(fundal `#fff3cd #fdf6e3` → `P.WARNING_SOFT`)

### Mov (accente secundare — dividende, total general)
`#7c3aed` `#8e44ad` `#6a1b9a` `#4c0a9b` `#3e2c50`  →  **`P.INFO`** sau `P.NEUTRAL`
(recomandat: elimină movul, e outlier — folosește `P.ACCENT_DEEP` pentru „total")

### Text închis
`#2c3e50` `#34495e` `#495057` `#333333` `#37474f`  →  **`P.INK`** (principal) / **`P.MUTED`** (secundar)
Text terțiar / gri deschis `#6c757d` `#7f8c8d` `#666666`  →  **`P.FAINT`**

### Neutrale fundal / bordură / dezactivat
`#f8f9fa` `#ecf0f1` `#e9ecef` `#f0f0f0`  →  **`P.PANEL_2`**
`#ffffff`  →  **`P.PANEL`** / `P.WHITE`
`#dee2e6` `#bdc3c7` `#adb5bd` `#d0d0d0` `#e0e0e0`  →  **`P.LINE`**
`#95a5a6` `#7f8c8d` `#cccccc` `#d3d3d3` (butoane disabled)  →  fundal `#b9c6bf` din `btn_primary():disabled`

---

## B. INVENTAR PER FIȘIER  (ordine de lucru recomandată)

Legenda risc:
🟢 COSMETIC PUR — doar text/label, fără logică în jur. Sigur.
🟡 MEDIU — tabele/formulare; verifică vizual după.
🔴 CRITIC CONTABIL — fișier cu calcule; test obligatoriu pe copie DB, compară cifre.

| # | Fișier | ~setStyleSheet | Risc | Note de lucru |
|---|--------|----------------|------|----------------|
| — | **dialog_styles.py** | 2 (1 stylesheet global) | 🟢 | **ÎNCEPE AICI.** Un singur stylesheet global pentru TOATE dialogurile. O modificare aici armonizează zeci de dialoguri deodată. Paleta albastră `#e8f1ff #cce5ff #3399ff #0056b3` → verde/neutru. Efect de pârghie maxim. |
| 1 | statistici.py | 11 | 🟡 | ✅ **DEJA restilizat** (șablon în pachet). |
| 2 | vizualizare_lunara.py | 1 (bloc mare) | 🔴 | Tabel principal lunar. Folosește `table()`. Rând TOTAL → `P.ACCENT_SOFT`. Verifică totalurile după. |
| 3 | vizualizare_trimestriala.py | 1 | 🔴 | Idem, structură aproape identică. |
| 4 | vizualizare_anuala.py | 2 | 🔴 | Idem. Un `setStyleSheet` e comentat — ignoră-l. |
| 5 | sume_lunare.py | 15 + stylesheet combinat | 🔴🔴 | **CEL MAI CRITIC** (130KB, introducere plăți). `general_styles+header_styles+button_styles` la linia 1264. Butoane: `#28a745`→primary, `#17a2b8`→soft/info, `#6c757d`→secondary. Label status recalc (`#17a2b8`/`red`/`#ff6b6b`) — PĂSTREAZĂ roșu=eroare. Test intens pe copie DB. |
| 6 | generare_luna.py | 2 (blocuri mari) | 🔴🔴 | Generarea lunii — nucleul contabil. Doar aspect; NU atinge nimic în jurul SQL. Test pe copie. |
| 7 | dividende.py | 1 (bloc mare) | 🔴 | Calcule dividende. Doar stylesheet-ul de la linia 165. |
| 8 | imprumuturi_noi.py | 10 | 🟡 | Are helper `_get_button_style(color)` — **ideal**: schimbă doar cele 3 culori pasate: `#3498db`(refresh)→`P.INFO`, `#27ae60`(save)→`P.POSITIVE`, `#e74c3c`(delete)→`P.DANGER`. Tabel → `table()`. |
| 9 | listari.py | 4 | 🟡 | Tabel + 2 dialoguri (`get_dialog_stylesheet()` — vine din dialog_styles, deja acoperit). Input gri `#f0f0f0`→`P.PANEL_2`. |
| 10 | listariEUR.py | 4 | 🟡 | Geamăn cu listari.py — aplică identic. |
| 11 | adaugare_membru.py | ~15 | 🟡 | Secțiuni colorate (roșu/gri/verde = împrumut/date/depuneri). Păstrează codul de culoare pe secțiune, mapează la P.DANGER/P.NEUTRAL/P.POSITIVE. Buton salvare gradient verde → `btn_primary()`. |
| 12 | stergere_membru.py | ~11 | 🟡 | Structură identică cu adaugare_membru (secțiuni + header). |
| 13 | lichidare_membru.py | ~12 | 🟡 | Idem pattern secțiuni. |
| 14 | verificare_fise.py | ~10 | 🟡 | Idem secțiuni + tabel. |
| 15 | afisare_membri_lichidati.py | 1 (bloc) | 🟡 | Tabel albastru `#0078d4` + buton portocaliu. → `table()` + `P.WARNING`. |
| 16 | calculator.py | 1 (bloc mare) | 🟢 | Utilitar independent, fără DB. Paleta albastru/roșu/verde/portocaliu a tastelor → tokens. Sigur. |
| 17 | salvari.py | 3 | 🟡 | Backup DB — NU atinge logica de salvare, doar butoanele. |
| 18 | optimizare_index.py | 2 | 🟡 | Idem, doar aspect. |
| 19 | actualizare_membru.py | 3 | 🟢 | 3 frame-uri cu `border:1px solid black` → `P.LINE`. Trivial. |
| 20 | ~~adauga_membru.py~~ | — | — | **ȘTERS** (cod mort orfan, neimportat nicăieri). |
| 21 | modificare_membru.py | 2 | 🟢 | Idem. |
| 22 | despre.py | ~90 | 🟢 | **Volum mare dar risc zero** — doar text informativ/label-uri. Majoritatea sunt `color: #xxx` pe QLabel. Batch mecanic. Lasă-l spre final. |
| 23 | car_dbf_converter_widget.py | 2 | 🟢 | Utilitar conversie DBF. Paleta completă albastru/verde/roșu/portocaliu → tokens. |
| 24 | conversie_widget.py | 1 | 🔴 | Conversie RON→EUR — logică sensibilă. Doar variabila `style` de aspect; NU atinge ratele/calculele. |

### Fișiere fără stil relevant (ignoră)
`versiune.py`, `vizualizari.py`, `verificareIndex.py`, `validari.py` (folosește DIALOG_STYLESHEET global).

---

## C. PROTOCOL PENTRU FIECARE FIȘIER

1. `import` paleta sus: `from ui.palette import P, GRAD, RADIUS, FONT, btn_primary, btn_secondary, btn_soft, card, table, input_field, header_bar`
2. Înlocuiește culorile literale conform dicționarului (secțiunea A).
3. Înlocuiește blocurile de buton/tabel/dialog cu fabricile din paletă unde se potrivesc.
4. **NU** atinge: `objectName`, `.connect`, SQL, calcule, nume variabile, structura layout.
5. Rulează aplicația → deschide ecranul → 🔴 compară cifrele cu o lună cunoscută.
6. `git add <fișier> && git commit -m "UI: <fișier> temă rafinată (doar stil)"`
7. Dacă ceva e greșit: `git revert <hash>` — doar acel fișier.

**Ordinea de aur:** dialog_styles.py (pârghie) → statistici (gata) → cele 🟢 ușoare
(încredere) → 🟡 medii → 🔴 critice la final, cu cea mai mare atenție și test pe copie DB.
