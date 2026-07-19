# Design System — catalog de componente C.A.R. Petroșani

Piesele reutilizabile ale redesign-ului. Fiecare ecran se construiește DIN aceste
piese — nu inventează stiluri noi. Aceasta e sursa consistenței: 24 de ecrane
diferite arată ca o singură aplicație pentru că toate folosesc aceleași piese.

> **Layout-ul fiecărui ecran rămâne 1:1.** Redesign = îmbrăcăm widget-urile
> existente în aceste piese. NU se șterge, NU se ascunde, NU se mută niciun câmp,
> buton sau coloană. Un ecran cu 15 câmpuri rămâne cu 15 câmpuri.

---

## 1. BUTOANE  (din palette.py)

| Piesă | Când | Fabrică |
|-------|------|---------|
| Primar | acțiunea principală a ecranului (Salvează, Generează, Adaugă) — **max 1-2 pe ecran** | `btn_primary()` |
| Secundar | acțiuni neutre (Anulează, Închide, Înapoi) | `btn_secondary()` |
| Soft/accent | acțiuni terțiare frecvente (Vezi tot, Export, Reîmprospătează) | `btn_soft()` |
| Pericol | ștergere/lichidare ireversibilă | `btn_secondary()` + culoare `P.DANGER` pe text/bordură; plin roșu doar la confirmarea finală |

**Regula de sens prin culoare (păstrată din codul actual):**
refresh/info = `P.INFO` · salvare/pozitiv = `P.POSITIVE` · ștergere = `P.DANGER` ·
atenție = `P.WARNING`. Redesign-ul **nu schimbă ce culoare = ce sens**, doar nuanța.

---

## 2. TABELE  (piesa cu cel mai mare impact — fabrica `table()`)

Aceeași înfățișare pentru TOATE tabelele (sume lunare, vizualizări, listări, verificări):
- antet `P.PANEL_2`, text `P.FAINT` uppercase mic, o singură linie de jos
- rânduri zebra discrete (`alternate-background-color`)
- **numerele aliniate la DREAPTA**, cifre tabulare (setează în cod: `item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)` pe coloanele numerice)
- selecție = `P.ACCENT_SOFT`, nu albastru de sistem
- rând TOTAL/sumar = fundal `P.ACCENT_SOFT`, text `P.ACCENT_DEEP` bold, linie sus 2px

**Important:** toate coloanele existente rămân. Dacă „Sume Lunare" are 15 coloane,
toate cele 15 rămân — se schimbă doar stilul antetului, alinierea și rândul de total.

---

## 3. CARDURI / SECȚIUNI  (`card()`)
Suprafață albă, bordură `P.LINE`, colț `RADIUS.LG`. Pentru formularele cu secțiuni
colorate (adaugare/stergere/lichidare membru): păstrează codul pe secțiune
(împrumut=roșu, date=neutru, depuneri=verde) dar folosește tokenii soft
(`P.DANGER_SOFT`, `P.PANEL_2`, `P.ACCENT_SOFT`) în loc de culori saturate.

## 4. HEADER DE ECRAN  (`header_bar()`)
Banda de titlu sus = verde accent (`GRAD.ACCENT`), text alb. **Unicul accent tare
pe pagină** — restul rămâne calm, ca ochiul să știe unde e titlul.

## 5. INPUTURI  (`input_field()`)
QLineEdit/QComboBox/QSpin: fundal `P.PANEL_2`, bordură `P.LINE`, la focus bordură
`P.ACCENT`. Aceeași înălțime și radius peste tot.

## 6. BADGE-URI DE STARE  (accente rare, deci imposibil de ratat)
- Permisiuni: ✅ Citire-Scriere = `P.ACCENT_SOFT`/`P.ACCENT_DEEP` · 🔒 Doar Citire = `P.WARNING_SOFT`/`P.WARNING`
- Toggle RON/EUR: segment activ = `GRAD.ACCENT` alb, inactiv = transparent
- Status recalcul (sume_lunare): succes `P.POSITIVE` · în lucru `P.INFO` · eroare `P.DANGER` — **păstrează roșu=eroare**

---

## 7. MAPARE ECRAN → PIESE  (ce aplică fiecare, fără să inventeze)

| Ecran | Piese folosite | Ce se PĂSTREAZĂ obligatoriu |
|-------|----------------|------------------------------|
| Statistici | card, header_bar | toate cardurile KPI + culorile lor semantice |
| Sume Lunare | table, btn_primary/secondary/soft, input, dialog | **TOATE cele ~15 câmpuri/coloane**, toate butoanele, label recalcul |
| Vizualizări (×3) | table, btn_soft (export), header_bar | toate coloanele + rândul TOTAL |
| Dividende | table, card, btn_primary | formula/coloanele de calcul |
| Adăugare/Ștergere/Lichidare membru | card (secțiuni), input, btn_primary/danger | toate secțiunile + toate câmpurile |
| Împrumuturi noi | table, `_get_button_style` (3 culori→tokens) | logica helperului, doar culorile pasate |
| Listări / ListăriEUR | table, dialog_styles (global) | toate opțiunile de listare |
| Calculator | butoane grid (tokens) | layout tastelor identic |
| Despre | doar `color:` pe label-uri | tot textul |
| Conversie / DBF converter | input, btn_primary, badge | **ratele și calculele — INTACTE** |

---

## 8. PRINCIPIUL DE VERIFICARE A CONSISTENȚEI
După ce un ecran e gata, întreabă: „butonul primar de aici arată identic cu cel din
alt ecran? tabelul are același antet? inputul are același focus verde?" Dacă da —
consistența e atinsă. Dacă un ecran arată diferit, înseamnă că cineva a scris stil
„de mână" în loc să folosească fabrica din `palette.py`. Aia e greșeala de evitat.
