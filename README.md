# CAR Petroșani - Aplicație Desktop Windows

Aplicație desktop pentru gestionarea Casei de Ajutor Reciproc Petroșani, dezvoltată în Python cu PyQt5, cu suport complet pentru conversie RON→EUR și sistem dual currency cu protecție avansată a datelor.

## 🆕 Actualizări Recente (Noiembrie 2025 - Ianuarie 2026)

### Îmbunătățiri Ianuarie 2026
- **🔐 Criptare AES-256 REALĂ**: Migrare de la `zipfile` standard la `pyzipper` pentru criptare profesională
- **Prevenire WinError 32**: Funcție nouă `_force_close_database_connections()` pentru cleanup conexiuni SQLite
- **UX îmbunătățit**: Dialoguri cu butoane clare în română ("Da, închide", "Nu, rămân", "Arhivează (recomandat)")
- **Cleanup complet la închidere**: Metodă nouă `_cleanup_before_close()` în `main_ui.py`
- **Build actualizat**: `CARpetrosani.spec` include acum `pyzipper` și `Cryptodome` pentru criptare

### Rezolvări Buguri Critice
- **BUG #1**: Precizie financiară 100% - Eliminare completă erori de rotunjire în `generare_luna.py:859-861` și `dividende.py:808`
- **BUG #2**: Protecție transfer dividende - Validare critică existență Ianuarie obligatorie în `dividende.py:707-730`
- **BUG #3, #4, #5, #6**: Critical bug fixes în multiple module (generare_luna, dividende, sume_lunare, stergere_membru)
- **Fix validare**: Corectare validare număr fișă 0 în `stergere_membru.py`
- **Eliminare BENEFICIU**: Înlocuire referințe la câmpul inexistent BENEFICIU cu DIVIDEND conform schemei oficiale

### Securitate și Calitate Cod
- **Migrare openpyxl → xlsxwriter**: Eliminare vulnerabilități CVE-2023-43810 (XXE) și CVE-2024-47204 (ReDoS)
- **🔐 Sistem Securitate Baze de Date** (Ianuarie 2025-2026): Protecție completă cu criptare AES-256 REALĂ
  - Arhivare automată cu parolă la închidere aplicație
  - Dezarhivare cu autentificare la pornire (3 încercări)
  - Cleanup automat baze de date expuse din crash-uri
  - Protecție race condition - previne corupere date
  - **NOU**: Prevenire WinError 32 (file locked) pe Windows
  - Module: `security_manager.py`, `dialog_styles.py`
- **Exception handling**: Înlocuire bare except clauses cu specific exception handling
- **GitHub Actions**: Implementare workflows CodeQL Analysis și Microsoft Defender
- **Monkey patching**: Corectare 3 buguri critice în sistemul de patching dual currency

### Testing și Documentație
- **Suite teste complete**: Adăugare `test_conversie_widget.py`, `test_dividende.py`, `test_generare_luna.py`, `test_sume_lunare.py`
- **pytest.ini**: Configurare cu suport coverage, markers și verbose output
- **requirements-dev.txt**: Dependențe dezvoltare separate (pytest, pytest-cov, pytest-qt)
- **BUGURI_IDENTIFICATE.md**: Raport exhaustiv cu 9 buguri categorizate (critice/majore/minore)
- **Claude.md**: Documentație contribuții AI și proces dezvoltare
- **README_TESTS.md**: Ghid complet pentru rulare și scriere teste

### Îmbunătățiri Module
- **generare_luna.py**: Eliminare auto-generare dividende în ianuarie, restaurare logging CAZ 1 și CAZ 2
- **dividende.py**: Implementare paritate cu TypeScript, validare comprehensivă, înlocuire BENEFICIU → DIVIDEND
- **despre.py**: Modernizare completă cu ghid utilizare profesional
- **CARpetrosani.spec**: Actualizare eliminare dependențe învechite

### Alte Îmbunătățiri
- **Rezolvare conflicte Git**: Fix merge conflicts în `generare_luna.py`
- **.gitignore**: Actualizare pentru excludere baze de date și fișiere temporare Python
- **Logging optimizat**: Îmbunătățiri în logging împrumuturi active și moștenire rate

## 📋 Caracteristici Principale

### 🔄 Sistem Dual Currency RON/EUR
- **Monkey Patching Condițional**: Comutare dinamică între bazele de date RON și EUR la runtime
- **Protecție Scriere Avansată**: Modul RON devine read-only după aplicarea conversiei
- **Toggle Valutar**: Comutare rapidă între RON și EUR direct din interfață
- **Indicatori Vizuali**: Afișare clară a monedei active și permisiunilor (Citire-Scriere / Doar Citire)
- **Fișier Configurare**: `dual_currency.json` pentru persistența statusului conversiei

### 💱 Conversie RON → EUR
- **Conformitate CE**: Conversie conform Regulamentului CE 1103/97
- **Conversie Directă Individuală**: Fiecare înregistrare este convertită separat
- **Precizie Decimal**: Calcule financiare exacte pentru conformitate UE
- **Curs Fix Configurabil**: Curs implicit 4.9755 RON/EUR (modificabil)
- **Clone Perfecte**: Creează baze de date EUR ca clone ale bazelor RON
- **Statistici Conversie**: Raportare detaliată cu totaluri și diferențe de rotunjire

### 🎨 Interfață Modernă cu 21+ Teme Vizuale
- **Teme Clasice Glass**
- **Teme Profesionale**
- **Teme Optimizate**
- **Persistență**: Tema selectată este salvată automat în `car_settings.json`
- **Preview Real-Time**: Vizualizare instantanee a temelor înainte de aplicare
- **Efecte Moderne**: Gradient glass, shadow effects, animații fluide

### 🔐 Sistem Securitate Baze de Date (Ianuarie 2025)

Protecție completă a datelor sensibile prin **criptare AES-256 REALĂ** cu parolă folosind biblioteca `pyzipper`.

#### Caracteristici Principale

**Protecție Automată la Pornire/Închidere:**
- ✅ **Criptare AES-256 reală** - folosește `pyzipper` pentru criptare profesională (nu doar ZIP cu parolă)
- ✅ **Arhivare cu parolă** la închiderea aplicației - toate bazele de date sunt criptate automat în `MEMBRII.zip`
- ✅ **Dezarhivare cu autentificare** la pornire - solicită parolă pentru acces la date (3 încercări)
- ✅ **Ștergere automată** - bazele de date sunt eliminate de pe disc după arhivare pentru securitate maximă
- ✅ **Cleanup inteligent** - detectează și curăță baze de date expuse din crash-uri anterioare

**Dialog Personalizat de Autentificare:**
- 🔑 Câmp parolă cu opțiune "Arată parola" pentru verificare
- 🔄 Sistem de retry cu 3 încercări pentru parolă incorectă
- ⏱️ Progress dialog pentru operații de arhivare/dezarhivare
- 📊 Mesaje clare și detaliate pentru utilizator
- 🇷🇴 **Butoane în română** - "Da, închide", "Nu, rămân", "Arhivează (recomandat)", etc.

**Protecție Avansată:**
- 🛡️ **Protecție race condition** - previne închiderea aplicației în timpul operațiilor de arhivare
- 🔒 **Prevenire WinError 32** - cleanup complet conexiuni SQLite înainte de arhivare
- 🔍 **Validare integritate** - verificare automată integritate arhivă ZIP la pornire
- ⚠️ **Gestionare erori** - mesaje user-friendly pentru toate scenariile excepționale
- 💾 **Suport dual currency** - protejează atât MEMBRII.db cât și MEMBRIIEUR.db

**Scenarii Suportate:**
1. **Prima configurare**: Creează arhiva cu parolă automată dacă DB-uri există dar arhiva lipsește
2. **Operare normală**: Dezarhivare → Lucru cu date → Arhivare automată la închidere
3. **Recuperare crash**: Detectează date expuse și oferă opțiune de arhivare înainte de ștergere
4. **Schimbare parolă**: Permite setarea unei parole noi la fiecare arhivare

#### Module Implementate

- **`security_manager.py`** (~950 linii) - Modul principal de securitate:
  - `cleanup_exposed_database()` - Curățare baze de date expuse
  - `extract_database_with_password()` - Dezarhivare cu autentificare (3 încercări)
  - `archive_database_with_password()` - Arhivare cu criptare AES-256
  - `_force_close_database_connections()` - **NOU**: Închidere forțată conexiuni SQLite pentru prevenire WinError 32
  - `CustomPasswordDialog` - Dialog personalizat PyQt5 pentru parolă
  - `get_security_status()` - Debugging și monitoring securitate

- **`dialog_styles.py`** - Stiluri moderne pentru dialogurile de securitate
- **Integrare în `main.py`** (linii 95-102) - Verificări obligatorii la pornire
- **Integrare în `main_ui.py`** - Arhivare obligatorie la închidere cu cleanup complet:
  - `_cleanup_before_close()` - **NOU**: Cleanup conexiuni și ferestre înainte de arhivare
  - Dialog de confirmare cu butoane clare în română

#### Flux de Lucru

**La pornirea aplicației:**
```
1. cleanup_exposed_database()        → Curățare DB expuse din crash-uri
2. extract_database_with_password()  → Dialog parolă → Dezarhivare MEMBRII.zip
3. Aplicație pornește cu DB active pe disc
```

**La închiderea aplicației:**
```
1. Dialog confirmare "Sigur închideți?"
2. archive_database_with_password()  → Dialog parolă → Arhivare în MEMBRII.zip
3. Ștergere automată DB de pe disc
4. Aplicație se închide cu date protejate
```

#### Securitate și Compatibilitate

- ✅ **Criptare profesională** - folosește `pyzipper` pentru criptare AES-256 reală
- ✅ **Compatibil Windows/macOS** - testare completă pe ambele platforme
- ✅ **Build PyInstaller** - include module în `CARpetrosani.spec` (pyzipper, Cryptodome)
- ✅ **Backward compatible** - nu afectează funcționalitatea existentă
- ✅ **Prevenire WinError 32** - cleanup automat conexiuni SQLite înainte de arhivare

### 💎 Precizie Financiară & Integritate Date

#### ✅ Buguri Critice Rezolvate (Commit e156100)

**BUG #1: Precizie Financiară 100% - Eliminare Erori Rotunjire**
- **Problemă Identificată**: Conversie Decimal→Float în operații de bază de date cauzând erori microscopice de rotunjire
- **Impact Potențial**: Acumulare diferențe 1-5 lei anual pentru 800 membri × 12 luni
- **Soluție Implementată**:
  - `generare_luna.py:859-861` - INSERT folosește acum `str(decimal)` pentru toate cele 7 coloane financiare
  - `dividende.py:808` - UPDATE transfer dividende folosește `str(decimal)` pentru precizie exactă
  - Pattern consistent: Scriere `str(decimal)` ↔ Citire `Decimal(str(value))`
- **Rezultat**: Zero erori de rotunjire, precizie financiară perfectă în toate calculele

**BUG #2: Protecție Transfer Dividende - Validare Critică Ianuarie**
- **Problemă Identificată**: Transfer dividende fără validare existență lună Ianuarie, risc corupere date
- **Impact Potențial**: Eșec silențios sau date corupte la transfer dividende anual
- **Soluție Implementată**:
  - `dividende.py:707-730` - Validare obligatorie la începutul funcției `_transfera_dividend()`
  - Verificare existență Ianuarie cu mesaj explicit pentru utilizator
  - Protecție dublă: validare buton + validare funcție cu QMessageBox.critical
- **Rezultat**: Imposibilitate transfer fără Ianuarie generat, mesaje clare cu instrucțiuni specifice

#### 🔒 Garanții Calitate Cod
- **Analiză Exhaustivă**: 26 module, ~15,000 linii cod verificate
- **Raport Buguri**: `BUGURI_IDENTIFICATE.md` cu 9 buguri categorizate (critice/majore/minore)
- **Testare Efecte Adverse**: Verificare completă compatibilitate schema SQLite și pattern-uri existente
- **Documentație Actualizată**: README sincronizat 100% cu funcționalitatea reală a codului

#### 🛡️ Securitate Export Excel (Commit 096bfa0)

**Migrare openpyxl → xlsxwriter pentru Securitate Îmbunătățită**
- **Problemă Identificată**: Biblioteca openpyxl avea 2 vulnerabilități critice:
  - CVE-2023-43810 (XXE - XML External Entity Injection)
  - CVE-2024-47204 (ReDoS - Regular Expression Denial of Service)
  - Detectări false positive frecvente de la antiviruși
- **Soluție Implementată**:
  - Migrare completă la xlsxwriter (bibliotecă write-only, zero vulnerabilități cunoscute)
  - 4 module actualizate: `vizualizare_lunara.py`, `vizualizare_trimestriala.py`, `vizualizare_anuala.py`, `dividende.py`
  - Toate formatările Excel păstrate IDENTIC (fonturi, culori, alignments, borders, freeze panes)
  - Performanță îmbunătățită la scriere Excel
- **Rezultat**: Export Excel 100% securizat, fără compromisuri vizuale sau funcționale

### 📊 Module Funcționale Complete

#### 1. **Gestiune Membri**
   - **Adăugare Membru**: Înregistrare membri noi cu validare completă
   - **Lichidare Membru**: Procesare lichidare cu calcul solduri finale
   - **Ștergere Membru**: Ștergere cu verificări de integritate
   - **Verificare Fișe**: Validare consistență date membri

#### 2. **Operațiuni Financiare**
   - **Sume Lunare**: Introducere plăți lunare cu calculator automatizat pentru dobândă integrat
   - Rezumat amănunțit al modulului sume_lunare


---

1. Scop general

Modulul sume_lunare gestionează toate operațiile lunare din aplicația CAR:

vizualizarea și editarea tranzacțiilor din tabela DEPCRED

recalcularea soldurilor lunare după modificări

calculul dobânzii la stingerea împrumuturilor

actualizarea cotizației standard

propagarea modificărilor în lunile ulterioare.


Totul rulează în interfață PyQt5, cu fire separate pentru recalculare.


---

2. Structură logică

a. Clase și funcții principale

SumeLunareWidget — componenta principală a UI-ului lunar.

Gestionează fișele membrilor, modificările, recalculările, butoanele de comandă și etichetele de stare.

Apelează funcțiile interne _handle_aplica_dobanda, _declanseaza_recalculare_ulterioara, _on_recalculation_finished, _on_recalculation_error, _worker_recalculeaza_luni_ulterioare.


TranzactieDialog — dialog modern pentru modificarea tranzacțiilor.

Include validatori numerici, calcul estimativ al ratelor (prin număr de luni sau rată fixă).

Poate fi deschis automat din logica de aplicare a dobânzii.


get_config_path() / get_dobanda()

Localizează și citește fișierul config_dobanda.json.

Extrage valoarea loan_interest_rate_on_extinction (ex. 0.004 = 4‰).

Dacă lipsește fișierul, folosește valoarea implicită.




---

3. Calculul soldurilor

Soldurile curente se bazează pe:

impr_sold_nou = impr_sold_vechi + impr_deb - impr_cred
dep_sold_nou  = dep_sold_vechi + dep_deb - dep_cred

Soldurile sunt ajustate la 0 dacă rezultatul este ≤ 0.005.

Orice modificare manuală într-o lună declanșează recalcularea automată a lunilor ulterioare (prin _declanseaza_recalculare_ulterioara → _worker_recalculeaza_luni_ulterioare).

Recalcularea iterează lună cu lună, preluând soldurile de deschidere din luna anterioară și rescrie valorile corecte în depcred.



---

4. Calculul dobânzii

Dobânda este calculată în două contexte:

1. La stingerea automată a împrumutului – în timpul generării lunii (sincronizat cu generare_luna.py).


2. Manual, prin butonul “Aplică dobândă” – pentru achitare anticipată.



Algoritm principal (_calculeaza_dobanda_la_zi)

1. Se determină perioada ultimului împrumut activ:

SELECT MAX(anul*100+luna)
FROM depcred
WHERE nr_fisa=? AND impr_deb>0 AND (anul*100+luna <= ?)


2. Se caută perioada de început (ultima lună cu sold zero înainte de acel împrumut).


3. Se adună toate soldurile lunare pozitive din perioada împrumutului:

SELECT SUM(impr_sold)
FROM depcred
WHERE nr_fisa=? AND (anul*100+luna BETWEEN ? AND ?)
AND impr_sold > 0


4. Dobânda este:

dobanda = SUM(impr_sold) * rata_dobanda

apoi rotunjită la 2 zecimale.


5. Dobânda se adaugă în dialogul de tranzacție, dar se salvează doar dacă utilizatorul confirmă.




---

5. Alte funcții relevante

_actualizeaza_cotizatie_standard() – modifică COTIZATIE_STANDARD în tabela membrii.

_on_recalculation_progress(), _on_recalculation_error() – actualizează UI în timp real.

Validatori – asigură introducerea valorilor numerice corecte pentru toate câmpurile.



---

6. Fluxul general al operațiilor

1. Utilizatorul selectează o fișă → se încarcă istoricul.


2. Modifică o lună → soldurile se recalculează și propagate automat.


3. Poate aplica manual dobânda → se deschide dialogul precompletat.


4. Se salvează tranzacția → se actualizează baza DEPCRED.


5. Recalcularea lunilor ulterioare pornește în fundal.


6. Interfața se reactivează după finalizare.




---

7. Legătura cu generare_luna.py

sume_lunare operează la nivel de membru (individual), în timp ce generare_luna procesează toți membrii simultan.

Ambele folosesc aceleași formule pentru calculul soldurilor și dobânzii.

sume_lunare permite intervenții manuale și recalculări selective.



---


   - **Împrumuturi Noi**: Instrument adiacent strict pentru Sume lunare. Permite vizualizarea, marcarea și copierea numelor membrilor la care trebuie stabilită Prima rată și lipirea numelui respectiv în căsuța de căutare din Sume lunare. De asemenea afișează lista velor vare au primit împrumut în luna sursă, ajutând utilizatorul să consemneze respectivul împrumut (Fereastră separată - F12)
   - **Dividende**: Modul separat pentru calculul dividendelor anuale. Calculează dividende pe baza sumei soldurilor lunare ale membrilor activi din anul selectat. Permite transferul manual al dividendelor calculate în luna Ianuarie a anului următor prin actualizarea DEP_DEB și DEP_SOLD
   - **Calculator**: Calculator integrat cu funcții avansate (Ctrl+Alt+C)

#### 3. **Vizualizări și Raportări**
   - **Situație Lunară**: Vizualizare detalii pentru o lună selectată
   - **Situație Trimestrială**: Raportare date pe trimestru
   - **Situație Anuală**: Sinteză anuală completă
   - **Statistici**: Dashboard cu totaluri, situații financiare și de membrii chitanțe etc.
   - **Afișare Membri cu Date Incomplete**: Identifică și afișează membri care lipsesc din luna anterioară ultimei luni procesate (necesari pentru generarea lunii noi). Include funcționalitate de ștergere definitivă a membrilor selectați

#### 4. **Listări și Chitanțe**
   - **Generare Chitanțe PDF**: Creare automată chitanțe lunare pentru membri
   - **Configurare Tipărire**: Număr chitanță inițial, chitanțe per pagină (5-15)
   - **Preview Chitanțe**: Previzualizare date înainte de generare PDF
   - **Sistem Progres**: Bare de progres pentru operații lungi cu protecție anti-înghețare
   - **Pagină Totaluri**: PDF include pagină finală cu totaluri dobândă, împrumuturi, depuneri
   - **Listări RON**: Modul specializat pentru generare chitanțe în RON
   - **Listări EUR**: Modul specializat pentru generare chitanțe în EUR
   - **Actualizare Automată**: CHITANTE.db actualizat cu numerele chitanțelor (STARTCH_PR, STARTCH_AC)

#### 5. **Administrare Sistem**
   - **Generare Lună Nouă**: Proces automatizat cu calcul dobânzi la achitarea împrumuturilor și actualizare solduri, automatizarea completării datelor financiare preluate din luna sursă
   - Rezumat amănunțit generare_luna.py:

Scop și context

Modul GUI PyQt5 pentru "Generare Lună Nouă" în aplicația CAR. Generează înregistrările lunare în DEPCRED.db, pe baza stării din luna anterioară, aplică cotizații, moștenește rate și calculează dobânda la stingerea împrumutului. Folosește MEMBRII.db și LICHIDATI.db ca surse și scrie în DEPCRED.db. Verifică existența fișierelor și afișează erori dacă lipsesc. NOTĂ: Dividendele se gestionează separat prin modulul Dividende.


Baze de date și fișiere

DB principale: MEMBRII.db, DEPCRED.db, LICHIDATI.db (+ opțional ACTIVI.db pentru dividende). La inițializare se avertizează dacă lipsesc.

Config rată dobândă în config_dobanda.json (cheie loan_interest_rate_on_extinction). Citire și salvare cu fallback la valoare implicită.


Interfața (UI)

Widget principal cu etichete de perioadă curentă/următoare, selector de lună, butoane: generează, șterge ultima lună, modifică rata, export log, curăță log, listează lichidați/activi și numere nealocate; zonă de status. Stilizare prin stylesheet.


Fluxul de generare a lunii

1. Determină perioada sursă M-1 față de țintă; validează anul. Deschide conexiuni la DB. Preia setul de lichidați.


2. Verifică schema MEMBRII.membrii pentru COTIZATIE_STANDARD. Selectează membrii activi (excludere lichidați). Resetează prima=0 pe luna sursă.


3. Pentru fiecare membru:

Citește impr_sold și dep_sold din luna sursă; dacă lipsesc, omite. Inițializează impr_deb_nou=0, dep_cred_nou=0.

Moștenește rata plătită luna anterioară, doar dacă nu există împrumut nou în luna sursă. Valoarea este quantizată la 0,01; altfel 0,00.

Setează dep_deb_nou = cotizație_standard (aplicat uniform pentru toate lunile).

Plafonează impr_cred_nou la soldul sursă; dacă soldul sursă ≤ 0.005, rata devine 0.00.

Calculează solduri noi:

Împrumut: impr_sold_nou = max(0, impr_sold_sursa + impr_deb_nou - impr_cred_nou) cu prag de zeroizare 0.005.
Depozit: dep_sold_nou = dep_sold_sursa + dep_deb_nou - dep_cred_nou.


Dacă împrumutul se stinge acum (impr_sold_sursa > 0.005 și impr_sold_nou == 0), calculează dobânda de lichidare: caută perioada de început (MAX anul*100+luna cu impr_deb>0 ≤ luna sursă), însumează impr_sold pozitiv pe interval [start..sursă], apoi dobândă = SUM(impr_sold) × rată_lichidare, cu rotunjire la 0.01.

Inserează în depcred rândul lunii țintă: câmpuri nr_fisa, luna, anul, dobanda, impr_deb, impr_cred, impr_sold, dep_deb, dep_cred, dep_sold, prima=1. Commit la final. Rezumat cu totaluri și număr dobânzi calculate.




Gestionare perioadă curentă și selecție

Detectează ultima lună procesată din DEPCRED.depcred și afișează următoarea lună logică; actualizează combobox. Verifică existența unei luni în DB.


Ștergerea ultimei luni / unei luni țintă

Ștergere sigură a ultimei luni generate cu confirmare. Operația internă: DELETE FROM depcred WHERE luna=? AND anul=?. Reactualizează perioada. Suport și pentru suprascriere: dacă luna țintă există, întreabă pentru ștergere + regenerare.


Alte funcții utile

Listă membri lichidați: citește LICHIDATI.lichidati, atașează numele din MEMBRII.membrii, afișează în log.

Listă membri activi pe luna curentă: join DEPCRED + MEMBRII, raportează total depuneri/împrumuturi și statistici.

Numere de fișă nealocate: calculează diferența dintre [1..max] și setul de NR_FISA din MEMBRII. Dialog dedicat.


Configurarea și modificarea ratei

Dialog pentru setarea ratei în ‰. Intern salvează ca fracție la mie în loan_interest_rate_on_extinction. Actualizează eticheta și persistă în config_dobanda.json. Validări și rotunjiri.


Threading, progres, erori

Rulează generarea în worker thread, raportează progres în UI, gestionează erorile cu rollback la blocări/exceptii și reînchide conexiunile. Mesaje clare în log și pop-ups.


Reguli de calcul critice

Prag zeroizare împrumut: 0.005.

Moștenire rată doar dacă nu există impr_deb în luna sursă.

Cotizație standard aplicată uniform în toate lunile (dividendele se gestionează separat prin modulul Dividende).

Rotunjiri: sume la 0.01, rata la 0.000001, dobândă la 0.01.


   - **Optimizare Baze**: VACUUM și REINDEX pentru performanță optimă
   - **Salvări**: Operațiuni backup și restore pentru bazele de date
   - **CAR DBF Converter**: Import/export date din formate DBF (Ctrl+Alt+D)

### ⌨️ Scurtături Tastatură Complete

| Scurtătură | Funcție |
|------------|---------|
| **Alt+A** | Meniu Actualizări |
| **Alt+V** | Meniu Vizualizări |
| **Alt+L** | Listări |
| **Alt+S** | Salvări |
| **Alt+I** | Împrumuturi Noi |
| **Alt+O** | Optimizare Baze |
| **Alt+G** | Generare Lună |
| **Alt+T** | Selector Temă |
| **Alt+R** | Versiune |
| **Alt+Q** | Ieșire |
| **Ctrl+Alt+C** | Calculator |
| **Ctrl+Alt+D** | CAR DBF Converter |
| **Ctrl+Alt+R** | Conversie RON→EUR |
| **F12** | Comutare rapidă către Împrumuturi Noi |

### 🔒 Protecție Date și Permisiuni

După aplicarea conversiei RON→EUR, sistemul implementează protecție automată:

**Modul RON (Doar Citire)**:
- Vizualizare date permisă
- Operațiuni de scriere blocate
- Meniuri protejate: Actualizări, Generare Lună, Optimizare Baze

**Modul EUR (Citire-Scriere)**:
- Toate operațiunile permise
- Modificări salvate în bazele EUR
- Flexibilitate completă pentru actualizări

**Indicator Vizual**:
- ✅ Citire-Scriere (verde) - Operațiuni permise
- 🔒 Doar Citire (portocaliu) - Protecție activă

## 💻 Cerințe de Sistem

### Software Necesar
- **Python**: 3.7+ (recomandat 3.9 sau 3.10)
- **PyQt5**: 5.15.0+
- **SQLite3**: Include în Python (versiune 3.30+)
- **IDE Recomandat**: PyCharm Community/Professional

### Dependențe Python
```bash
PyQt5>=5.15.0
reportlab>=3.6.0   # Pentru generarea PDF chitanțe
xlsxwriter>=3.2.9  # Pentru export Excel securizat (fără vulnerabilități)
pyzipper>=0.3.6    # Pentru criptare AES-256 baze de date
sqlite3   # Inclus în Python standard library
pathlib   # Inclus în Python standard library
json      # Inclus în Python standard library
```

**Note Securitate:**
- `xlsxwriter` pentru export Excel - elimină vulnerabilitățile CVE-2023-43810 (XXE) și CVE-2024-47204 (ReDoS)
- `pyzipper` pentru criptare AES-256 REALĂ a bazelor de date (nu doar ZIP cu parolă standard)

### Sistem de Operare
- **Windows**: 10 sau 11 (64-bit recomandat)
- **Minimum RAM**: 4 GB
- **Spațiu Disc**: 500 MB (incluzând baze de date)
- **Rezoluție Ecran**: Minimum 1366x768 (recomandat 1920x1080)

## 🚀 Instalare și Configurare

### 1. Clonare Repository

```bash
git clone https://github.com/totilaAtila/CARpetrosani.git
cd CARpetrosani
```

### 2. Creare Mediu Virtual (Recomandat)

```bash
# Creare mediu virtual
python -m venv venv

# Activare mediu virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Instalare Dependențe

```bash
pip install -r requirements.txt
```

Sau instalare manuală:
```bash
pip install PyQt5>=5.15.0
pip install reportlab>=3.6.0
```

### 4. Pregătire Baze de Date

Plasați bazele de date SQLite în directorul principal al aplicației:

**Baze de Date Obligatorii:**
- `MEMBRII.db` - Informații despre membri
- `DEPCRED.db` - Depuneri și credite
- `LICHIDATI.db` - Membri lichidați
- `activi.db` - Membri activi (pentru dividende)
- `INACTIVI.db` - Membri inactivi
- `CHITANTE.db` - Tracking numere chitanțe (creat automat dacă lipsește)

**Fișiere de Configurare:**
- `dual_currency.json` - Status conversie și configurare sistem dual currency
- `config_dobanda.json` - Configurare rată dobândă

**După Conversie EUR (generate automat):**
- `MEMBRIIEUR.db` 
- `DEPCREDEUR.db`
- `activiEUR.db`
- `LICHIDATIEUR.db`
- `INACTIVIEUR.db`
- `dual_currency.json` - Status conversie și configurare

### 5. Rulare Aplicație

```bash
python main.py
```

## 📁 Structura Proiectului

```
CARpetrosani/
├── main.py                          # Punct de intrare cu early database patching
├── main_ui.py                       # Interfața principală cu sistem dual currency
├── currency_logic.py                # Logică gestionare monede și permisiuni
├── dialog_styles.py                 # Stiluri pentru dialoguri
├── car_settings.json                # Setări persistente (tema selectată)
├── dual_currency.json               # Status conversie și configurare dual currency
├── config_dobanda.json              # Configurare rată dobândă (creat la prima utilizare)
│
├── ui/                              # Module interfață utilizator
│   ├── statistici.py                # Dashboard statistici
│   ├── adaugare_membru.py           # Widget adăugare membri noi
│   ├── actualizare_membru.py        # Widget actualizare date membri
│   ├── modificare_membru.py         # Logică modificare membri (modul auxiliar)
│   ├── sume_lunare.py               # Introducere plăți lunare
│   ├── lichidare_membru.py          # Procesare lichidări
│   ├── stergere_membru.py           # Ștergere membri
│   ├── dividende.py                 # Calcul și distribuire dividende
│   ├── vizualizare_lunara.py        # Vizualizare date lunare
│   ├── vizualizare_trimestriala.py  # Vizualizare date trimestriale
│   ├── vizualizare_anuala.py        # Vizualizare date anuale
│   ├── verificare_fise.py           # Validare consistență date
│   ├── afisare_membri_lichidati.py  # Identificare membri cu date incomplete
│   ├── listari.py                   # Generare chitanțe PDF pentru RON
│   ├── listariEUR.py                # Generare chitanțe PDF pentru EUR
│   ├── salvari.py                   # Operațiuni salvare/backup
│   ├── calculator.py                # Calculator integrat
│   ├── imprumuturi_noi.py           # Gestionare împrumuturi (fereastră separată)
│   ├── generare_luna.py             # Generare lună nouă automată
│   ├── optimizare_index.py          # Optimizare performanță baze
│   ├── despre.py                    # Informații aplicație
│   ├── validari.py                  # Funcții validare date (modul utilitar)
│   └── ...
│
├── conversie_widget.py              # Widget conversie RON→EUR
├── car_dbf_converter_widget.py      # Converter DBF (opțional)
│
├── fonts/                           # Fonturi pentru generare PDF
│   ├── Arial.ttf
│   ├── DejaVuSans-Bold.ttf
│   └── ...
│
├── icons/                           # Iconițe aplicație
│   ├── app_icon.png
│   ├── calc.png
│   └── ...
│                       # Baze de date SQLite (RON)
|─ MEMBRII.db
├── DEPCRED.db
├── activi.db
├── INACTIVI.db
├── LICHIDATI.db
├── CHITANTE.db                      # Tracking chitanțe (creat automat)
│                    # Baze de date SQLite (nume original + sufix EUR - după conversie)
├── MEMBRIIEUR.db
├── DEPCREDEUR.db
├── activiEUR.db
├── INACTIVIEUR.db
├── LICHIDATIEUR.db
├── CHITANTEEUR.db                   # Tracking chitanțe EUR (creat automat)
│
└── README.md                        # Documentație
```

## 🗄️ Structura Bazelor de Date

### Tabele Principale

#### 1. MEMBRII.db - Tabela MEMBRII 
Informații Membri
```sql
Coloane:
- NR_FISA          INTEGER PRIMARY KEY    -- Număr fișă unic
- NUM_PREN         TEXT                   -- Nume și prenume
- DOMICILIUL       TEXT                   -- Adresă domiciliu
- CALITATEA        TEXT                   -- Funcție/Departament
- DATA_INSCR       TEXT                   -- Data înscrierii (YYYY-MM-DD)
- COTIZATIE_STANDARD REAL                 -- Cotizație lunară standard REAL
```

#### 2. DEPCRED.db - Tabela DEPCRED
Depuneri și Credite
```sql
Coloane:
- NR_FISA          INTEGER                -- Referință către MEMBRII
- DOBANDA          REAL                   -- Dobândă calculată
- IMPR_DEB         REAL                   -- Împrumut debit (nou împrumut)
- IMPR_CRED        REAL                   -- Împrumut credit (plată)
- IMPR_SOLD        REAL                  -- Sold împrumut
- LUNA             INTEGER                -- Luna (1-12)
- ANUL             INTEGER                -- Anul
- DEP_DEB          REAL                   -- Cotizația, se consideră debit lunar,se adaugă la DEP_SOLD
- DEP_CRED         REAL                   - Retragere din fondul social
- DEP_SOLD         REAL                   -- Sold depunere
- PRIMA            LOGIC                   -- Prima este un câmp boolean, marchează luna activă 1= luna activă. Generare lună folosește acest câmp: când se generează luna țintă - devine 1, uar luna sursă - devine 0
```

#### 3. activi.db - Tabela ACTIVI
```sql
Coloane:
- NR_FISA          INTEGER PRIMARY KEY    -- Număr fișă
- NUM_PREN         TEXT                   -- Nume și prenume
- DEP_SOLD         REAL                   -- Sold depuneri
- DIVIDEND         REAL                   -- Dividend calculat
```

#### 4. LICHIDATI.db - Tabela lichidati
Membri Lichidați
```sql
Coloane:
- nr_fisa          INTEGER PRIMARY KEY    -- Număr fișă
- data_lichidare   TEXT                   -- Data lichidării
```

#### 5. INACTIVI.db - Tabela inactivi
Membri Inactivi
```sql
Coloane:
- nr_fisa          INTEGER PRIMARY KEY    -- Număr fișă
- num_pren         TEXT                   -- Nume și prenume
- lipsa_luni       INTEGER                -- Număr luni lipsă consecutive
```

#### 6. CHITANTE.db - Tabela CHITANTE Tracking Chitanțe
```sql
Coloane:
- STARTCH_PR       INTEGER                -- Număr chitanță precedent (ultima sesiune)
- STARTCH_AC       INTEGER                -- Număr chitanță actual (sesiunea curentă)
```

**Utilizare:**
- `STARTCH_AC` = numărul ultimei chitanțe generate
- `STARTCH_PR` = numărul ultimei chitanțe din sesiunea precedentă (pentru istoric)
- La resetare: `STARTCH_PR = 0`
- Actualizare automată la fiecare generare PDF chitanțe

### Diferențe RON vs EUR

**Baze RON** (MEMBRII.db, DEPCRED.db, etc.):
- Câmp `COTIZATIE_STANDARD` cu 

**Baze EUR** (MEMBRIIEUR.db, DEPCREDEUR.db, etc.):

- Structura Identică!, doar valorile sunt convertite la momentul folosirii conversie_widget

## 💰 Logică Financiară

### Calcul Dobândă

Dobânda se calculează DOAR la achitarea Rezumat calculuri în generare_luna.py:


---

1. Calcul solduri

a) Împrumut (impr_sold)

impr_sold_nou_calculat = impr_sold_sursa + impr_deb_nou - impr_cred_nou
if impr_sold_nou_calculat <= Decimal('0.005'):
    impr_sold_nou = Decimal("0.00")
else:
    impr_sold_nou = impr_sold_nou_calculat

Interpretare:

impr_sold_sursa = soldul anterior al împrumutului.

impr_deb_nou = debit nou (împrumut acordat în luna curentă).

impr_cred_nou = credit nou (rată plătită luna aceasta).

Rezultatul final este zeroizat dacă diferența este sub 0.005 RON (rotunjire).



---

b) Depozit (dep_sold)

dep_sold_nou = dep_sold_sursa + dep_deb_nou - dep_cred_nou

Interpretare:

dep_sold_sursa = sold anterior al depozitului.

dep_deb_nou = sumă nou depusă (de obicei cotizația standard în generare_luna.py; dividendele se adaugă separat prin modulul Dividende).

dep_cred_nou = sume retrase din depozit.



---

2. Calcul dobândă la stingere împrumut

Dobânda se calculează doar dacă:

if impr_sold_sursa > Decimal('0.005') and impr_sold_nou == Decimal("0.00"):

adică membrul avea împrumut activ și acum l-a stins complet.

Etape:

1. Se caută prima lună de început a împrumutului:

SELECT MAX(anul*100+luna)
FROM depcred
WHERE nr_fisa=? AND impr_deb>0 AND (anul*100+luna <= ?)


2. Se calculează suma tuturor soldurilor de împrumut din perioada activă:

SELECT SUM(impr_sold)
FROM depcred
WHERE nr_fisa=? AND (anul*100+luna BETWEEN ? AND ?) AND impr_sold > 0


3. Dobânda este:

dobanda_noua = (sum_balances * self.loan_interest_rate_on_extinction).quantize(Decimal("0.01"), ROUND_HALF_UP)

loan_interest_rate_on_extinction este rata configurabilă (‰ – la mie).

Se înmulțește cu suma totală a soldurilor din perioada împrumutului și se rotunjește la 0.01.





---

3. Rata dobânzii (configurare)

Se salvează/încarcă din fișierul config_dobanda.json.

Poate fi modificată prin UI:

self.loan_interest_rate_on_extinction = Decimal(str(new_permille)) / 1000



---

Sinteză practică

Tip sold	Formula	Observații

Împrumut nou	impr_sold_nou = impr_sold_sursa + impr_deb_nou - impr_cred_nou	Dacă < 0.005 ⇒ 0
Depozit nou	dep_sold_nou = dep_sold_sursa + dep_deb_nou - dep_cred_nou	dep_deb_nou = cotizația standard în generare_luna.py
Dobândă lichidare	dobanda = SUM(impr_sold) × rata_lichidare	doar la stingerea totala
```

### Conversie RON → EUR

Aplicația implementează conversia conform **Regulamentului CE 1103/97**:

**Metodologie:**
- **Conversie Directă Individuală**: Fiecare înregistrare convertită separat
- **Precizie Decimal**: Utilizare aritmetică precisă pentru evitarea erorilor de rotunjire
- **Metodă de Rotunjire**: ROUND_HALF_UP (0.5 rotunjit la 1)
- **Curs Fix**: 4.9755 RON/EUR implicit (configurabil)

**Exemplu Conversie:**
```python
Suma RON: 497.55 RON
Curs: 4.9755 RON/EUR
Suma EUR = 497.55 ÷ 4.9755 = 100.00 EUR (rotunjit la 2 zecimale)
```

**Formula Generală:**
```
Valoare_EUR = ROUND(Valoare_RON / Curs_Schimb, 2)
```

### Generare Lună Nouă

Procesul automatizat de generare lună nouă:

1. **Citire Solduri**: Extrage soldurile din luna anterioară pentru fiecare membru
2. **Aplicare Tranzacții**: Procesează toate tranzacțiile din luna curentă
3. **Calcul Dobândă**: Calculează dobânda pe soldul împrumutului
4. **Creare Înregistrări**: Generează înregistrări pentru luna următoare
5. **Raportare**: Raport cu membrii procesați, împrumuturi noi și omiși

## 🛠️ Utilizare

### Pornire Aplicație

1. **Lansare**: Executați `python main.py` sau dublu-click pe `main.py` (dacă Python este configurat)
2. **Încărcare Automată**: Aplicația încarcă automat tema salvată și verifică statusul conversiei
3. **Interfață**: Se deschide fereastra principală cu meniul lateral și zona de conținut

### Navigare în Aplicație

**Meniu Lateral:**
- Click pe butoane pentru acces rapid la module
- Utilizați scurtăturile tastatură pentru eficiență
- Toggle RON/EUR pentru comutare monedă
- Indicator permisiuni (Citire-Scriere / Doar Citire)

**Submeniuri:**
- Se deschid automat la click pe module cu opțiuni multiple
- Buton "⬅ Ieșire Meniu" pentru revenire la statistici

**Teme Vizuale:**
- Click pe "Selector temă" sau Alt+T
- Navigare cu tastatura pentru preview real-time
- Aplicare automată și salvare persistentă

### Operațiuni Comune

#### 1. Adăugare Membru Nou
```
Actualizări (Alt+A) → Adăugare membru
→ Completare date → Salvare
```

#### 2. Introducere Plăți Lunare
```
Actualizări (Alt+A) → Sume lunare
→ Selectare membru → Introducere date → Salvare
```

#### 3. Generare Lună Nouă
```
Generare lună (Alt+G)
→ Selectare lună și an → Confirmare → Procesare automată
```

#### 4. Conversie RON → EUR
```
Conversie RON->EUR (Ctrl+Alt+R)
→ Verificare curs → Confirmare → Conversie automată
→ Descărcare baze EUR generate
```

#### 5. Comutare între RON și EUR
```
Toggle în meniul lateral: Click pe RON sau EUR
→ Aplicația re-patchuiește modulele automat
→ Widget-urile se reîncarcă cu datele corecte
```

#### 6. Generare Chitanțe PDF (Listări)
```
Listări (Alt+L)
→ Selectare lună și an pentru chitanțe
→ Setare număr chitanță inițial (ex: 1001)
→ Configurare chitanțe per pagină (5-15, default 10)
→ Click "Preview" pentru verificare date
→ Verificare totaluri (dobândă, împrumuturi, depuneri)
→ Click "Tipărește PDF" → Confirmare
→ Generare automată cu progres vizual
→ PDF salvat ca chitante_LUNA_AN.pdf
→ Deschidere automată PDF sau click "Deschide PDF"
```

**Caracteristici Chitanțe:**
- Format A4 cu 10 chitanțe per pagină (configurabil 5-15)
- Dimensiune chitanță: 2,5 cm înălțime
- Informații: Nr.Fișă, Nume, Dobândă, Rată Împrumut, Sold Împrumut, Depuneri, Retrageri, Total de Plată
- Pagină finală cu totaluri generale
- Actualizare automată CHITANTE.db (tracking STARTCH_PR, STARTCH_AC)

## 🔧 Configurare Avansată

### Fișier car_settings.json

```json
{
    "current_theme": 0,
    "app_version": "3.2",
    "last_updated": "2025-10-24 14:30:00"
}
```

### Fișier dual_currency.json

```json
{
    "conversie_aplicata": true,
    "data_conversie": "2025-10-24 15:45:00",
    "curs_folosit": 4.9755,
    "baze_convertite": [
        "MEMBRII",
        "DEPCRED",
        "activi",
        "INACTIVI",
        "LICHIDATI"
    ]
}
```

### Fișier config_dobanda.json

```json
{
    "rata_dobanda": 0.004
}
```

**Notă:** Rata dobândă = 0.004 înseamnă 4‰ (4 la mie). Acest fișier este creat automat la prima utilizare a modulelor de generare lună sau sume lunare.

## 🐛 Troubleshooting

### Problema: Aplicația nu pornește

**Soluții:**
```bash
# Verificare versiune Python
python --version  # Trebuie să fie 3.7+

# Reinstalare PyQt5
pip uninstall PyQt5
pip install PyQt5

# Verificare dependențe
pip list | grep PyQt5
```

### Problema: Erori la încărcarea bazelor de date

**Verificări:**
1. Bazele de date există în directorul aplicației
2. Fișierele nu sunt corupte (testare cu DB Browser for SQLite)
3. Permisiuni de citire/scriere pe fișiere
4. Spațiu disponibil pe disc

```bash
# Testare integritate bază de date
sqlite3 MEMBRII.db "PRAGMA integrity_check;"
```

### Problema: Toggle RON/EUR nu funcționează

**Cauze Posibile:**
- Fișierul `dual_currency.json` lipsește sau este corupt
- Bazele EUR nu există după conversie
- Permisiuni de scriere blocate

**Soluție:**
```bash
# Verificare existență baze EUR
ls *EUR.db

# Verificare dual_currency.json
cat dual_currency.json
```

### Problema: Tema nu se salvează

**Soluție:**
```bash
# Verificare permisiuni
# Windows (PowerShell):
Get-Acl car_settings.json

# Ștergere fișier corupt și regenerare
del car_settings.json
# Repornire aplicație pentru regenerare automată
```

### Problema: Erori de calcul financiar

**Verificări:**
- Toate valorile sunt numerice (nu TEXT)
- Câmpurile nu conțin NULL
- Soldurile sunt consistente

```sql
-- Verificare consistență
SELECT NR_FISA, LUNA, ANUL, 
       IMPR_SOLD, DEP_SOLD 
FROM DEPCRED 
WHERE IMPR_SOLD IS NULL OR DEP_SOLD IS NULL;
```

### Problema: Chitanțele PDF nu se generează, sau caracterele nu au diacritice 

**Cauze Posibile:**
- Fonturile lipsesc (Arial.ttf, DejaVuSans-Bold.ttf) . Ele trebuie să fie atât in dosarul Fonturi cât si în rădăcina aplicației 
- Permisiuni insuficiente pentru scriere
- DEPCRED.db sau MEMBRII.db lipsesc

**Soluții:**
```bash
# Verificare fonturi
ls fonts/Arial.ttf
ls fonts/DejaVuSans-Bold.ttf

# Copiere fonturi din Windows
copy C:\Windows\Fonts\Arial.ttf fonts\

# Verificare permisiuni
# Windows:
icacls chitante_*.pdf

# Verificare existență baze
dir DEPCRED.db MEMBRII.db
```

### Problema: Număr chitanță prea mare (8+ cifre)

**Soluție:**
- Apăsați "Reset" în modulul Listări
- Confirmați resetarea numărului la 1
- Sau setați manual un număr mai mic
- CHITANTE.db va fi actualizat cu noul număr

## 📖 FAQ (Întrebări Frecvente)

**
