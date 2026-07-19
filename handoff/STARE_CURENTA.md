# Stare curentă — redesign C.A.R. Petroșani

Scris la finalul unei sesiuni lungi de lucru, ca să nu se piardă raționamentul
din spatele celor 30 de commit-uri. Cine reia — om sau asistent — citește întâi
acest document, apoi `CONVENTII_VIZUALE.md`.

**Branch:** `redesign-ui-glass-verde` · **`main` neatins** · nimic nu a fost
împins pe GitHub. 30 de commit-uri locale.

---

## 1. Ce e gata (12 fișiere)

Criteriu obiectiv: **zero culori hex literale rămase în fișier.**

| Fișier | Notă |
|---|---|
| `ui/palette.py` | sursa unică. Extinsă pe parcurs (vezi §4) |
| `dialog_styles.py` | pârghia: stilizează global toate dialogurile |
| `ui/statistici.py` | șablonul din pachet. Culorile cardurilor KPI rămân argumente, nu stil |
| `ui/calculator.py` | |
| `ui/despre.py` | 86 de literali migrați automat. Ghidul restructurat ca acordeón |
| `ui/actualizare_membru.py` | |
| `ui/adauga_membru.py` | |
| `ui/modificare_membru.py` | |
| `ui/imprumuturi_noi.py` | |
| `ui/listari.py` | |
| `ui/listariEUR.py` | |
| `ui/vizualizare_lunara/trimestriala/anuala.py` | 3 culori lăsate intenționat — vezi `CONVENTII_VIZUALE.md` |
| `main_ui.py` | tema nouă adăugată; restul fișierului nu e încă migrat |

## 2. Ce a mai rămas (11 fișiere)

În ordinea recomandată. Cifra e numărul de culori distincte rămase.

**Grupul „secțiuni colorate"** — același tipar, se învață o dată:
`adaugare_membru` (32) · `stergere_membru` (34) · `lichidare_membru` (35) ·
`verificare_fise` (30)

**Independente, mai ușoare:**
`optimizare_index` (17) · `salvari` (16) · `afisare_membri_lichidati` (14) ·
`car_dbf_converter_widget` (17) · `main_ui` (35, parțial făcut)

**🔴 Critice — la final, câte unul, cu test pe date după fiecare:**
`dividende` (19) · `generare_luna` (26) · `sume_lunare` (40)

> `dividende.py` conține culori din lista protejată, folosite în exportul Excel.
> Vezi `CONVENTII_VIZUALE.md` §3 înainte de a-l atinge.

---

## 3. Cum se lucrează un fișier

```bash
# 1. migrare mecanică a culorilor (dry-run întâi, mereu)
python tests/migreaza_culori_la_paleta.py ui/<fisier>.py
python tests/migreaza_culori_la_paleta.py ui/<fisier>.py --scrie

# 2. adaugă importul paletei — ATENȚIE la importuri cu continuare pe linia
#    următoare (`\`); validează sintaxa ÎNAINTE de a scrie fișierul

# 3. plasa de siguranță
python handoff/verifica_siguranta.py ui/<fisier>.py

# 4. suita de teste
set QT_QPA_PLATFORM=offscreen
python -m pytest -q

# 5. pornește aplicația, compară cifrele cu tests/VALORI_ASTEPTATE.md

# 6. un commit per fișier
```

### Ce face fiecare unealtă

| Unealtă | Rol |
|---|---|
| `handoff/verifica_siguranta.py` | compară cu `HEAD`, alarmează dacă s-a atins logică. **Rulează-l ÎNAINTE de commit** — după commit dă mereu verde fals |
| `tests/migreaza_culori_la_paleta.py` | migrează culorile prin AST. Evaluează fiecare f-string rezultat și îl compară cu originalul; dacă nu coincid, **nu scrie deloc** |
| `tests/curata_qss_nesuportat.py` | găsește proprietăți CSS pe care Qt le ignoră (`box-shadow`, `transform`...) |
| `tests/curata_importuri.py` | importuri nefolosite, cu verificare conservatoare |
| `tests/diagnostic_dimensiuni.py` | instanțiază fiecare widget și raportează minimele — pentru „Unable to set geometry" |
| `tests/genereaza_baze_test.py` | 200 membri, 2023–2025, date deterministe. `--fara-eur` lasă rădăcina liberă pentru testul de conversie |
| `tests/verifica_valori_asteptate.py` | verifică coerența contabilă a bazelor generate |

### Alarme false cunoscute

`verifica_siguranta.py` semnalează corect, dar are trei false pozitive recurente:
`QFrame#calculatorFrame` (conține „calcul"), `::item:selected` (conține „select"),
și comentariile care conțin aceste cuvinte. Verifică manual, apoi continuă.

---

## 4. Ce s-a adăugat în paletă pe parcurs

Toate adăugările sunt **aditive** — niciun token existent nu a fost modificat.

- `ACCENT_PRESS` — nuanța „apăsat", era scrisă de mână în două locuri
- `INFO_DEEP` / `WARNING_DEEP` / `DANGER_DEEP` / `NEUTRAL_DEEP` — pentru hover pe
  butoane pline; fără ele fiecare fișier își inventa propria nuanță
- `DISABLED` / `DISABLED_TEXT` — codul vechi folosea aceeași culoare pentru un
  buton dezactivat și pentru unul activ gri
- `btn_solid(base, deep, selector)` — fabrică pentru butoane semantice pline
- **`class STARE`** — culori pentru TEXTUL de stare din tabel. Vezi §5

---

## 5. Regula care contează cel mai mult

Detaliată în `CONVENTII_VIZUALE.md`. Pe scurt:

> Înainte de a înlocui o culoare, întreabă **cine o citește**. Dacă răspunsul e
> „utilizatorul, ca să afle ceva ce nu scrie în text" — nu e stil, e conținut.

Semnele: se aplică *condiționat* pe date · se aplică *pe element*, nu în
stylesheet · apare și în **PDF sau Excel** · se schimbă la rulare.

Capcana concretă, măsurată: `QTableWidget::item { color: ... }` **anulează**
`item.setForeground(...)`. Aplicația scrie `NEACHITAT` cu roșu exact așa.
Fără eroare, fără avertisment — doar text negru în loc de roșu.

---

## 6. Bug-uri preexistente găsite (nu sunt de la redesign)

Reparate:

- **`DB_ACTIVI` nu era patchuit la EUR.** Cheia din mapare era `"activi.db"`,
  modulele definesc `"ACTIVI.db"`. Zece module scriau în baza RON în timp ce
  aplicația afișa EUR. Dividendele s-ar fi calculat din solduri în lei.
- **Generare Preview conversie crăpa mereu** — format numeric aplicat pe
  string-uri. Butonul „APLICĂ CONVERSIE" nu se activa niciodată.
- HiDPI setat după `QApplication` (ignorat), `Unable to set geometry` la fiecare
  comutare de modul, text tăiat pe butoane la focus.

**Rămase, de discutat separat:**

- **51 de locuri** folosesc `with sqlite3.connect(...)`, care gestionează
  tranzacția dar **nu închide conexiunea**. De aceea `security_manager` are
  nevoie de `_force_close_database_connections()`. Reparate doar cele 8 din
  `verifica_valori_asteptate.py`.
  **Atenție:** `contextlib.closing` închide dar NU face commit — o înlocuire
  mecanică ar pierde datele în cele 12 blocuri care scriu. Vezi commit `beaba6b`.
- `imprumuturi_noi.py` cade la construcție pe platforma `offscreen` (preexistent).

---

## 7. Testare

- **66 de teste** trec (`pytest`). Acoperă `generare_luna`, `dividende`,
  `conversie_widget`, `sume_lunare` — exact modulele critice rămase.
- Bazele de test: 200 membri, 6.531 înregistrări. Cifrele de comparat sunt în
  `tests/VALORI_ASTEPTATE.md`.
- Testul cheie: luna 12/2025 e lăsată **negenerată** intenționat. După
  restilizarea lui `generare_luna.py`, rulează *Generare Lună* pe 12/2025 —
  trebuie să iasă exact 170 înregistrări, 18 dobânzi, total **1.919,40**.
- Setul EUR de referință e în `tests/eur_referinta/`, pentru compararea
  rezultatului conversiei.

---

## 8. Când totul e gata

```bash
python -m pytest -q                    # 66 trecute
python tests/verifica_valori_asteptate.py
# construiește exe-ul, testează pe o COPIE a bazelor
git checkout main && git merge redesign-ui-glass-verde
```
