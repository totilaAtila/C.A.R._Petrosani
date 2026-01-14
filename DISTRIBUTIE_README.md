# CARpetrosani - Ghid Distribuție Executabil

## 📦 Crearea Executabilului

### Prerequisite
- Python 3.11 sau mai nou
- PyInstaller (`pip install pyinstaller`)
- Toate dependințele instalate (`pip install -r requirements.txt`)

### Pași Build

**Windows:**
```bash
# Metodă 1: Folosește script-ul automat (RECOMANDAT)
build_windows.bat

# Metodă 2: Build manual cu PyInstaller
pyinstaller --clean --noconfirm CARpetrosani.spec
```

### Output

După build, vei găsi executabilul în:
```
dist/
└── CARpetrosani.exe    # Executabil standalone ~150-200MB
```

---

## 🚀 Pregătirea pentru Distribuție

### 1. Creare Arhivă de Protecție (OBLIGATORIU)

**IMPORTANT:** Înainte de prima rulare, utilizatorul TREBUIE să aibă arhiva `MEMBRII.zip` cu parolă!

**Opțiunea A - Creați arhiva manual:**
```bash
# 1. Copiați bazele de date în directorul aplicației:
#    - MEMBRII.db
#    - MEMBRIIEUR.db (dacă există)

# 2. Creați arhiva MEMBRII.zip cu parolă folosind 7-Zip, WinRAR sau similar:
#    - Selectați MEMBRII.db (și MEMBRIIEUR.db dacă există)
#    - Right-click → Add to archive
#    - Format: ZIP
#    - Encryption: AES-256
#    - Set password: [parola dorită]
#    - Save as: MEMBRII.zip

# 3. Ștergeți bazele de date originale de pe disc
#    (vor fi extrase automat la pornire cu parola)
```

**Opțiunea B - Lăsați aplicația să creeze arhiva:**
```bash
# 1. Copiați DOAR bazele de date în directorul aplicației
#    (FĂRĂ MEMBRII.zip)

# 2. Rulați aplicația - va detecta configurarea incompletă

# 3. Răspundeți "Yes" la dialogul "Doriți să creați arhiva acum?"

# 4. Introduceți parola dorită

# 5. Arhiva MEMBRII.zip va fi creată automat
```

### 2. Structura Directorului pentru Distribuție

Distribuiți următoarea structură:

```
CARpetrosani/
├── CARpetrosani.exe          # Executabilul principal
├── MEMBRII.zip               # Arhiva cu parolă (OBLIGATORIU)
├── fonts/                    # Fonturi (incluse în exe)
├── Icons/                    # Iconițe (incluse în exe)
└── README_UTILIZATOR.md      # Instrucțiuni pentru utilizator final
```

**NOTĂ:** Fonturile și iconițele sunt deja incluse în executabil - nu e nevoie să le distribuiți separat.

### 3. Instrucțiuni pentru Utilizatorul Final

Creați un fișier `README_UTILIZATOR.md` cu următorul conținut:

```markdown
# CARpetrosani - Ghid Utilizare

## Prima Pornire

1. Asigurați-vă că aveți fișierul **MEMBRII.zip** în același director cu aplicația
2. Dublu-click pe **CARpetrosani.exe**
3. Introduceți parola pentru deschiderea bazelor de date
4. Aplicația va porni cu datele decriptate

## La Închiderea Aplicației

1. Click pe X sau meniul Exit
2. Confirmați închiderea aplicației
3. Introduceți parola pentru arhivarea bazelor de date
4. Aplicația se închide și datele sunt criptate automat

## Securitate

⚠️ **IMPORTANT:**
- **Parola este obligatorie** la fiecare pornire și închidere
- **NU pierdeți parola** - nu există recovery fără backup!
- **Faceți backup regulat** la fișierul MEMBRII.zip
- **Bazele de date sunt șterse automat** de pe disc după închidere

## Recuperare Parolă Uitată

❌ **NU există funcție de recovery parolă!**

Soluții:
- Restaurați din backup (MEMBRII.zip cu parola cunoscută)
- Contactați administratorul pentru arhiva de backup

## Suport Tehnic

Pentru probleme sau întrebări, contactați dezvoltatorul.
```

---

## 🔒 Securitate și Protecție Date

### Fluxul de Securitate

**La pornire:**
1. ✅ Verificare baze de date expuse din crash-uri anterioare
2. ✅ Cleanup automat cu dialog de avertizare
3. ✅ Solicitare parolă pentru dezarhivare
4. ✅ Extragere baze de date din MEMBRII.zip
5. ✅ Pornire aplicație cu date active

**La închidere:**
1. ✅ Dialog confirmare închidere
2. ✅ Solicitare parolă pentru arhivare
3. ✅ Arhivare baze de date în MEMBRII.zip (suprascrie veche)
4. ✅ Ștergere automată baze de date de pe disc
5. ✅ Închidere aplicație cu date protejate

### Caracteristici Securitate

- **Criptare AES-256** prin arhivare ZIP cu parolă
- **Protecție race condition** - previne închidere în timpul operațiilor
- **Cleanup automat** - detectează și curăță date expuse din crash-uri
- **Validări obligatorii** - nu permite operații fără parolă corectă
- **3 încercări parolă** - aplicația se închide după 3 încercări greșite

---

## 📋 Checklist Distribuție

Înainte de a distribui executabilul, verificați:

- [ ] Build-ul s-a terminat cu succes (`dist/CARpetrosani.exe` există)
- [ ] Executabilul pornește fără erori
- [ ] Arhiva `MEMBRII.zip` există sau există instrucțiuni clare de creare
- [ ] Ați testat fluxul complet:
  - [ ] Pornire cu parolă
  - [ ] Operații în aplicație
  - [ ] Închidere cu arhivare
  - [ ] Re-pornire cu aceeași parolă
- [ ] Ați creat `README_UTILIZATOR.md` cu instrucțiuni
- [ ] Ați făcut backup la `MEMBRII.zip` cu parola cunoscută

---

## 🐛 Troubleshooting

### Executabilul nu pornește

**Simptom:** Dublu-click pe exe, nimic nu se întâmplă

**Soluții:**
1. Rulați din Command Prompt pentru a vedea erorile:
   ```bash
   cd C:\path\to\CARpetrosani
   CARpetrosani.exe
   ```
2. Verificați că toate DLL-urile necesare sunt prezente (Windows Defender poate bloca)
3. Verificați că antivirusul nu blochează executabilul

### Eroare "Arhivă lipsă"

**Simptom:** Dialog "Fișierul 'MEMBRII.zip' nu a fost găsit"

**Soluții:**
1. Verificați că `MEMBRII.zip` este în **același director** cu `CARpetrosani.exe`
2. Verificați că numele fișierului este exact `MEMBRII.zip` (nu `MEMBRII (1).zip`)
3. Creați arhiva conform instrucțiunilor de mai sus

### Eroare "Parolă incorectă"

**Simptom:** Dialog "Parolă incorectă" după introducere parolă

**Soluții:**
1. Verificați Caps Lock
2. Folosiți opțiunea "Arată parola" pentru a verifica ce introduceți
3. Dacă ați uitat parola, restaurați din backup cu parolă cunoscută

### Aplicația crapă la pornire

**Simptom:** Aplicația pornește dar se închide imediat

**Soluții:**
1. Rulați din Command Prompt pentru a vedea eroarea exactă
2. Verificați că toate bazele de date din arhivă sunt valide
3. Verificați logs-urile pentru erori

---

## 📞 Contact și Suport

Pentru probleme cu build-ul sau distribuția, contactați dezvoltatorul proiectului.

**Versiune document:** 1.0 (Ianuarie 2025)
**Compatibilitate:** Windows 10/11, macOS 10.15+
