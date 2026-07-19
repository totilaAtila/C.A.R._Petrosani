# Pachet handoff — Redesign C.A.R. Petroșani

Tot ce-i trebuie lui Claude Code (pe PC) ca să implementeze redesign-ul
**în siguranță**, pe un branch, fără să atingă logica contabilă.

## Ordinea de citire

1. **HANDOFF_REDESIGN.md** — START. Regula de aur, pașii git (clonare→branch→commit),
   protocolul per fișier. Citește prima dată.
2. **verifica_siguranta.py** — plasa de siguranță. Rulează după FIECARE fișier,
   înainte de commit: alarmează dacă s-a atins ceva în afara stilului.
3. **INVENTAR_STIL.md** — harta de lucru: dicționar culori→tokens, tabel per fișier
   cu nivel de risc (🟢🟡🔴) și ordinea recomandată.
4. **DESIGN_SYSTEM.md** — catalogul de piese (butoane, tabele, carduri, inputuri).
   Asigură CONSISTENȚA: fiecare ecran folosește aceleași piese; layout-ul rămâne 1:1.
5. **ui/palette.py** — fișier NOU, sursa unică de culoare + fabrici QSS.
6. **ui/statistici.py** — șablon deja restilizat (exemplu de urmat; diff = doar stil).

## Cele două straturi (ține minte)

- **Sistem (palette.py + DESIGN_SYSTEM.md)** = identic peste tot → consistență.
- **Layout fiecărui ecran** = păstrat 1:1 → niciun câmp/coloană/buton șters.

Redesign = îmbrăcăm widget-urile existente în piesele sistemului. Atât.

## Prompt sugerat pentru Claude Code

> Clonează repo-ul, fă branch `redesign-ui-glass-verde`. Urmează
> `handoff/HANDOFF_REDESIGN.md` și `handoff/INVENTAR_STIL.md` în ordinea
> recomandată. Folosește piesele din `handoff/DESIGN_SYSTEM.md` și tokenii din
> `ui/palette.py` — nu scrie culori de mână. `ui/statistici.py` e șablonul.
> Respectă REGULA DE AUR: doar string-uri de stil, niciodată semnale/SQL/calcule/
> objectName/layout. După fiecare fișier rulează
> `python handoff/verifica_siguranta.py ui/<fișier>`, apoi pornește aplicația și
> compară cifrele pe o COPIE a bazei de date. Un commit per fișier.

## Referință vizuală
`Redesign CAR Petrosani.dc.html` (în rădăcina proiectului) — mockup-ul aprobat.
Arată *limbajul vizual*, NU conținutul ecranelor (acela se păstrează integral).
