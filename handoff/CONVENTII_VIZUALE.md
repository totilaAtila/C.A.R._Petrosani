# Convenții vizuale — ce NU se schimbă la redesign

Acest document lipsea din pachetul de handoff, și lipsa lui s-a simțit.

`INVENTAR_STIL.md` spune ce culoare devine ce token. Nu spune însă care culori
**poartă informație** și de aceea nu au voie să devină nimic. Diferența nu se
vede grepuind după `#rrggbb`: arată la fel în cod, dar una e decor și cealaltă e
semnal pe care utilizatorul îl citește dintr-o privire.

Scris după ce două astfel de convenții au fost descoperite din întâmplare —
una semnalată de utilizator, alta găsită verificând prima.

---

## 1. Codul de culoare al textului din tabel

Se aplică prin `item.setForeground(QBrush(QColor(...)))`, direct pe element.
**Nu e stil, e conținut.** Un membru cu restanță se vede fără să citești cifrele.

| Marcaj | Culoare | Înseamnă | Unde |
|---|---|---|---|
| `NEACHITAT` | roșu | sold > 0 dar plata lunii = 0 | `vizualizare_lunara/trimestriala/anuala`, 6 locuri |
| *(planificat)* `ACHITAT` | verde | rata plătită integral | — |
| *(planificat)* împrumut nou | albastru | împrumut acordat în luna curentă | — |
| *(planificat)* `!NOU` | chihlimbar | marcaj de element nou | — |

Pentru cele planificate există deja tokenii `STARE.*` din `ui/palette.py`.
**Nu folosi `P.DANGER` / `P.POSITIVE` / `P.INFO` / `P.WARNING` ca text**: sunt
culori de umplere, gândite cu text alb peste, și cad sub pragul de lizibilitate
pe rândurile deschise ale tabelului. Contrastele măsurate sunt în `palette.py`.

### Capcana care șterge acest cod, în tăcere

O regulă `QTableWidget::item { color: ... }` **anulează** `setForeground`.
Una pusă pe widget, nu. Măsurat prin randare, numărând pixelii roșii:

```
fără stylesheet                     116 px roșii
color: pe QTableWidget::item          0 px roșii   ← semnalul dispare
fabrica table() (color pe widget)   103 px roșii
```

Nicio eroare, niciun avertisment. Doar text negru în loc de roșu.
De aceea `table()` din paletă pune `color:` pe widget.

---

## 2. Alternanța pe grupuri de membri

```python
bg_color = "#e8f4ff" if (group % 2 == 0) else "#fff5e6"
```

Cele două nuanțe alternează la fiecare **schimbare de membru**, nu la fiecare
rând. Ele arată unde se termină fișa unuia și începe a altuia. Mapate amândouă
la același neutru, distincția dispare complet.

`#dce8ff` este fundalul antetului, din aceeași familie.

**Toate trei sunt în lista `PROTEJATE` din `tests/migreaza_culori_la_paleta.py`**
și nu se înlocuiesc niciodată.

---

## 3. Același cod, trei canale de ieșire

Convențiile de mai sus nu trăiesc doar pe ecran. Aceleași culori apar în:

| Canal | Mecanism | Fișiere |
|---|---|---|
| Ecran | `QColor` / `QBrush` pe element | `vizualizare_*` |
| PDF tipărit | `reportlab.HexColor` | `vizualizare_*` |
| Excel exportat | `xlsxwriter add_format(bg_color=...)` | `vizualizare_*`, `dividende.py` |

O schimbare pe ecran care nu se face și în celelalte două rupe corespondența
dintre ce vede utilizatorul și ce tipărește. Iar o schimbare făcută în toate
trei modifică aspectul documentelor față de cele deja arhivate.

Decizie luată: **rămân neatinse pe toate canalele.**

---

## 4. Eticheta de status a recalculării (`sume_lunare.py`)

`lbl_recalc_status` își schimbă culoarea după stare, din cod:

| Culoare | Stare |
|---|---|
| `#17a2b8` | recalculare în desfășurare |
| `red` | eroare |
| `#ff6b6b` | eroare / avertisment |

`INVENTAR_STIL.md` avertizează explicit: **păstrează roșu = eroare.**
Nuanța poate fi armonizată; sensul, nu.

---

## 5. Regula generală, extrasă din cele de mai sus

> Înainte de a înlocui o culoare, întreabă: **cine o citește?**
>
> Dacă răspunsul e „utilizatorul, ca să afle ceva ce nu scrie în text" —
> atunci nu e stil, e conținut, și nu intră în redesign.

Semnele că o culoare poartă informație:

- e aplicată **condiționat**, în funcție de date (`if ... else`)
- e aplicată **pe element**, nu în stylesheet
- apare și în **PDF sau Excel**, nu doar pe ecran
- alternează sau se schimbă la rulare

Oricare dintre acestea e motiv de oprire și întrebare.
