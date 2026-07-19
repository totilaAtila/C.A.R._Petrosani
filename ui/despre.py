# -*- coding: utf-8 -*-
"""
Despre aplicația CAR Petroșani
Versiune modernizată - interfață profesională slick
Fără emoji, design clean, acordeon modern
"""

import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton,
    QHBoxLayout, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

# REDESIGN: sursa unică de stil. Doar aspect — nicio logică atinsă.
from ui.palette import P

# --- Configurare Cale Resurse ---
try:
    if getattr(sys, 'frozen', False):
        BASE_RESOURCE_PATH = os.path.dirname(sys.executable)
    else:
        current_script_path = os.path.abspath(__file__)
        ui_directory = os.path.dirname(current_script_path)
        BASE_RESOURCE_PATH = os.path.dirname(ui_directory)
except Exception as e:
    print(f"Eroare la configurarea căilor în despre.py: {e}")

# --- Date Aplicație ---
CURRENT_VERSION = "FINALA"

CHANGELOG = {
    "BETA2": [
        "Adăugare interfață pastelată modernă",
        "Modul de introducere membru nou complet funcțional",
        "Optimizări majore ale interfeței pentru redimensionare",
        "Implementare validări centralizate"
    ],
    "BETA3": [
        "Meniu 'Generare lună' cu opțiuni avansate (selectare, ștergere, suprascriere)",
        "Refactorizare module pentru performanță și claritate",
        "Buton 'Împrumut nou' cu estimare automată dobândă",
        "Statistici detaliate despre restanțe și lichidări în timp real",
        "Numerotare automată și export rapid chitanțe",
        "Manual interactiv extins cu descrieri detaliate"
    ],
    "BETA4": [
        "Corectare căi fonturi DejaVu pentru funcționare după împachetare",
        "Export Excel în module vizualizare",
        "Sortare date prin click pe antet coloane",
        "Fixare antet în timpul scrollului în Excel",
        "Uniformizare stil între module",
        "Dialog-uri stilizate cu efecte hover",
        "Marcare vizuală împrumuturi noi și achitate"
    ],
    "BETA5": [
        "Rezolvare erori critice procesare dividende ianuarie",
        "Îmbunătățire calcul dobândă lichidări anticipate",
        "Corectare afișare membri inactivi perioade extinse",
        "Optimizări performanță baze de date mari",
        "Corectare format date financiare în PDF",
        "Compatibilitate îmbunătățită Windows nou",
        "Validări suplimentare prevenire inconsistențe"
    ],
    "BETA6": [
        "Suport complet dividende la începutul anului",
        "Îmbunătățire calcul dobândă împrumuturi achitate la lichidare",
        "Corectare calcul total plată chitanțe",
        "Optimizare export Excel cu antet fix",
        "Corecție rată împrumut moștenită după lichidare",
        "Dialog-uri confirmare stilizate modern",
        "Uniformizare interfață module vizualizare"
    ],
    "BETA7": [
        "Configurare externă dobândă prin config_dobanda.json",
        "Sistem de recalculare automată solduri",
        "Îmbunătățire detecție împrumuturi noi",
        "Optimizare performanță module mari",
        "Calculator dobândă la zi pentru lichidări"
    ],
    "BETA8": [
        "Sistem avansat generare chitanțe PDF batch",
        "Dialog-uri non-blocking asincrone",
        "Deschidere PDF în thread separat",
        "Jurnal activitate cu font mărit la 9pt",
        "State machine pentru generare PDF",
        "Auto-recovery UI la probleme neașteptate",
        "Feedback continuu progres (la 10 chitanțe)",
        "Optimizare memorie și cleanup automat",
        "Calculator separat independent complet funcțional"
    ],
    "FINALA": [
        "Sistem dual-currency RON/EUR cu monkey patching",
        "Widget conversie definitivă RON→EUR conform UE",
        "Toggle currency în bara principală",
        "Protecție baze RON doar-citire",
        "Clonare automată baze EUR cu validare",
        "CAR DBF Converter pentru sisteme legacy",
        "Sistem de recalculare complete solduri",
        "Optimizare baze cu indexare automată",
        "20 teme profesionale moderne",
        "Interfață slick fără elemente decorative excesive"
    ],
    "ACTUALIZĂRI NOV-DEC 2025": [
        "Rezolvare BUG #1: Precizie financiară 100% - Eliminare erori rotunjire în generare_luna.py și dividende.py",
        "Rezolvare BUG #2: Protecție transfer dividende - Validare critică Ianuarie obligatorie",
        "Rezolvare BUG #3, #4, #5, #6: Critical bug fixes în multiple module",
        "Rezolvare BUG #5: Eroare SQL și optimizare logging împrumuturi active",
        "Fix validare număr fișă 0 în modul stergere_membru.py",
        "Eliminare referințe la câmpul inexistent BENEFICIU din tabelul ACTIVI",
        "Înlocuire bare except clauses cu exception handling specific",
        "Migrare openpyxl → xlsxwriter pentru securitate îmbunătățită (CVE-2023-43810, CVE-2024-47204)",
        "Adăugare suite completă de teste automată: test_conversie_widget, test_dividende, test_generare_luna, test_sume_lunare",
        "Configurare pytest.ini cu suport coverage și markers",
        "Adăugare requirements-dev.txt pentru dependențe dezvoltare",
        "Creare documentație BUGURI_IDENTIFICATE.md cu raport exhaustiv",
        "Adăugare Claude.md - Documentație contribuții AI și proces dezvoltare",
        "Adăugare README_TESTS.md - Ghid complet pentru rulare teste",
        "Implementare GitHub Actions workflows: CodeQL Analysis și Microsoft Defender",
        "Actualizare .gitignore pentru excludere baze de date și fișiere temporare",
        "Rezolvare conflicte Git merge în generare_luna.py",
        "Restaurare logging CAZ 1 și CAZ 2 pentru moștenire rată împrumut",
        "Corectare 3 buguri critice în sistemul de monkey patching",
        "Modernizare completă modul Despre - Ghid utilizare profesional",
        "Actualizare CARpetrosani.spec - Eliminare dependențe învechite",
        "Îmbunătățiri ISSUE #7, #8, #9: Calitate cod și best practices",
        "Fix dividende: Implementare paritate cu TypeScript și validare comprehensivă",
        "Eliminare auto-generare dividende în ianuarie din generare_luna.py",
        "Înlocuire BENEFICIU cu DIVIDEND conform schemei oficiale SQLite"
    ]
}

# Manual Utilizare - Structură Acordeon Modern
MANUAL_STRUCTURE = {
    "Actualizări": {
        "descriere": "Operațiuni de modificare și actualizare date membri",
        "submeniuri": {
            "Adăugare membru": {
                "descriere": "Înregistrarea unui membru nou în sistem cu validare completă a datelor",
                "functionalitati": [
                    "Introducere date identificare: nume, prenume, domiciliu",
                    "Atribuire automată număr fișă unic",
                    "Validare format CNP și verificare duplicat",
                    "Setare cotizație standard lunară",
                    "Înregistrare dată înscriere cu calendar",
                    "Salvare automată în MEMBRII.db și DEPCRED.db"
                ],
                "note": "Sistemul verifică automat dacă numărul de fișă există deja și previne duplicatele"
            },
            "Sume lunare": {
                "descriere": "Gestionarea tranzacțiilor lunare pentru fiecare membru cu calcule automate",
                "functionalitati": [
                    "Afișare istoric complet tranzacții membru",
                    "Adăugare/modificare tranzacții: împrumuturi, rate, cotizații, retrageri",
                    "Calcul automat solduri împrumuturi și depuneri",
                    "Buton 'Împrumut nou' cu calculator estimativ rate",
                    "Calculator dobândă la zi pentru lichidări complete",
                    "Detecție automată împrumuturi noi în tabel (marcaj vizual)",
                    "Recalculare automată solduri după modificări",
                    "Validări matematice stricte pentru conformitate"
                ],
                "note": "Modulul include protecții împotriva erorilor de introducere și recalculează automat toate soldurile impactate"
            },
            "Lichidare membru": {
                "descriere": "Procesarea lichidării complete a unui membru activ",
                "functionalitati": [
                    "Calcul automat sold final cu dobândă la zi",
                    "Generare automată chitanță lichidare PDF",
                    "Mutare automată membru din ACTIVI în LICHIDATI",
                    "Păstrare istoric complet în DEPCRED.db",
                    "Blocare prevenire lichidări duplicate",
                    "Validare matematică sold înainte de lichidare"
                ],
                "note": "Lichidarea este finală și nu poate fi anulată. Asigurați-vă că toate calculele sunt corecte"
            },
            "Ștergere membru": {
                "descriere": "Eliminarea definitivă a unui membru din toate bazele de date",
                "functionalitati": [
                    "Dialog confirmare dublă pentru siguranță",
                    "Ștergere din toate bazele: MEMBRII, DEPCRED, ACTIVI, INACTIVI",
                    "Verificare că membrul nu are sold activ",
                    "Jurnal complet al operației de ștergere",
                    "Opțiune anulare în orice moment"
                ],
                "note": "Operație IREVERSIBILĂ. Folosiți doar pentru corecții erori grave de introducere"
            },
            "Dividende": {
                "descriere": "Atribuirea dividendelor anuale la începutul fiecărui an pentru toți membrii activi",
                "functionalitati": [
                    "Selectare an pentru distribuire dividende",
                    "Calcul automat pe bază formula configurabilă",
                    "Aplicare automată la toți membrii activi",
                    "Validare că dividende nu au fost aplicate deja",
                    "Raportare sumă totală distribuită",
                    "Jurnal operații cu timestamp"
                ],
                "note": "Dividendele se aplică o singură dată pe an, de obicei în ianuarie"
            }
        }
    },
    "Vizualizări": {
        "descriere": "Rapoarte și analize detaliate situație financiară",
        "submeniuri": {
            "Situație lunară": {
                "descriere": "Raport detaliat pentru o lună specifică cu toate tranzacțiile",
                "functionalitati": [
                    "Selectare lună și an din calendar",
                    "Tabel complet: membru, împrumuturi, rate, cotizații, solduri",
                    "Totalizare automată pe coloane",
                    "Sortare date prin click pe antet",
                    "Export Excel cu formatare profesională",
                    "Filtrare opțională după criterii"
                ],
                "note": "Antetul rămâne fix la scroll pentru referință ușoară"
            },
            "Situație trimestrială": {
                "descriere": "Vizualizare agregată pe 3 luni consecutive",
                "functionalitati": [
                    "Selectare trimestru și an",
                    "Agregare automată date pe 3 luni",
                    "Calcul medii și totale trimestru",
                    "Export Excel cu subtotale",
                    "Comparații între luni din trimestru"
                ],
                "note": "Util pentru analize tendințe pe termen mediu"
            },
            "Situație anuală": {
                "descriere": "Raport complet pentru un an întreg cu toate operațiunile",
                "functionalitati": [
                    "Selectare an fiscal",
                    "Totalizare anuală toate categoriile",
                    "Statistici anuale: împrumuturi, rate, cotizații",
                    "Export Excel cu grafice automate",
                    "Comparație cu ani anteriori (opțional)"
                ],
                "note": "Esențial pentru raportări anuale și audit financiar"
            },
            "Verificare fișe": {
                "descriere": "Verificarea integrității și consistenței datelor pentru toți membrii",
                "functionalitati": [
                    "Scanare automată toate fișele membre",
                    "Detectare discrepanțe matematice solduri",
                    "Identificare înregistrări lipsa",
                    "Raport erori cu detalii localizare",
                    "Sugestii automate corecții",
                    "Export raport verificare"
                ],
                "note": "Recomandabil de rulat lunar pentru asigurarea calității datelor"
            },
            "Afișare membri inactivi": {
                "descriere": "Lista membrilor care nu au efectuat plăți de cotizație timp îndelungat",
                "functionalitati": [
                    "Configurare prag luni inactivitate",
                    "Listă automată membri inactivi cu detalii",
                    "Afișare ultimă lună plată cotizație",
                    "Calcul luni inactivitate pentru fiecare",
                    "Export listă pentru contactare"
                ],
                "note": "Util pentru menținerea bazei active de membri și recuperare restanțe"
            }
        }
    },
    "Listări": {
        "descriere": "Generare chitanțe și documente oficiale pentru plăți",
        "functionalitati": [
            "Selectare lună și an pentru listare",
            "Generare automată chitanțe PDF pentru toți membrii cu plăți",
            "Numerotare automată chitanțe secvențial",
            "Format profesional conform standarde contabile",
            "Salvare automată în director dedicat",
            "Deschidere directă PDF după generare",
            "Sistem batch processing pentru volume mari",
            "Progress bar în timp real cu feedback la fiecare 10 chitanțe",
            "Posibilitate de resetare numărul chitanței la 1 atunci când numărul de caractere depășește chenarul de tipărire"
        ],
        "note": "Sistemul funcționează în modul dual-currency (RON/EUR) automat conform monedei active"
    },
    "Generare lună": {
        "descriere": "Crearea automată lunii noi cu preluare solduri din luna anterioară",
        "functionalitati": [
            "Selectare lună și an nouă",
            "Verificare automată existență lună",
            "Preluare solduri finale din ultima lună existentă",
            "Aplicare cotizație standard la toți membrii activi",
            "Creare înregistrări pentru toți membrii activi",
            "Opțiuni: suprascriere, ștergere, anulare",
            "Validări matematice complete înainte de generare",
            "Raportare detaliere operațiuni efectuate"
        ],
        "note": "Operație complexă - verificați atent datele înainte de confirmare. Suportă suprascriere lună existentă cu confirmare"
    },
    "Salvări": {
        "descriere": "Operațiuni backup, restaurare și întreținere baze de date",
        "submeniuri": {
            "Backup Complet": {
                "descriere": "Creare copie siguranță toate bazele de date",
                "functionalitati": [
                    "Backup automat toate fișierele .db",
                    "Creare director timestamped în 'backup_db'",
                    "Verificare integritate după backup",
                    "Afișare mărime totală backup",
                    "Păstrare istoric backups pentru restaurări",
                    "Deschidere automată folder backup în Explorer"
                ],
                "note": "Recomandabil înainte de operațiuni majore sau la finalul fiecărei luni"
            },
            "Restaurare": {
                "descriere": "Recuperare date din backup anterior",
                "functionalitati": [
                    "Selectare folder backup dorit",
                    "Previzualizare conținut backup",
                    "Restaurare selectivă sau completă",
                    "Confirmare dublă înainte de suprascriere",
                    "Verificare integritate după restaurare",
                    "Backup automat înainte de restaurare"
                ],
                "note": "ATENȚIE: Restaurarea suprascrie datele curente. Verificați data backup-ului atent"
            },
            "Ștergere An": {
                "descriere": "Eliminare definitivă date pentru un an complet",
                "functionalitati": [
                    "Selectare an pentru ștergere",
                    "Afișare statistici an (nr înregistrări, membri afectați)",
                    "Confirmare multiplă pentru siguranță",
                    "Backup automat obligatoriu înainte de ștergere",
                    "Ștergere recursivă toate lunile anului",
                    "Raport detaliat operațiuni efectuate"
                ],
                "note": "IREVERSIBIL fără backup. Folosiți doar pentru arhivare ani vechi conform politici legale"
            },
            "Verifică Integritatea": {
                "descriere": "Verificare PRAGMA integrity_check pe toate bazele",
                "functionalitati": [
                    "Scanare automată toate fișierele .db",
                    "PRAGMA integrity_check pentru fiecare DB",
                    "Detectare corupții sau inconsistențe",
                    "Raport detaliat probleme găsite",
                    "Sugestii remediere automată",
                    "Export raport verificare"
                ],
                "note": "Rulați periodic sau după crash sistem pentru asigurarea sănătății bazelor"
            }
        }
    },
    "Optimizare baze": {
        "descriere": "Optimizare și întreținere performanță baze de date",
        "functionalitati": [
            "VACUUM: Recuperare spațiu nefolosit și defragmentare",
            "ANALYZE: Actualizare statistici pentru optimizer query",
            "REINDEX: Reconstruire indexi pentru performanță maximă",
            "Creare indexi automatici pe coloane critice (NR_FISA, LUNA, ANUL)",
            "Verificare integritate referințe între tabele",
            "Raportare mărime înainte/după optimizare",
            "Progress indicator în timp real",
            "Backup automat recomandat înainte de operație"
        ],
        "note": "Recomandabil lunar sau după operațiuni majore cu volume mari. Îmbunătățește semnificativ viteza query-urilor și reduce dimensiunea fișierelor"
    },
    "Conversie RON→EUR": {
        "descriere": "Aplicarea conversiei definitive RON→EUR pentru tranziția la moneda euro",
        "stari_sistem": {
            "Perioada 1 - Pre-conversie": {
                "descriere": "Funcționare normală doar cu RON",
                "comportament": [
                    "Toggle currency INACTIV (doar RON vizibil)",
                    "Toate modulele funcționează normal cu RON",
                    "Baze originale: DEPCRED.db, MEMBRII.db, activi.db, INACTIVI.db, LICHIDATI.db",
                    "Butonul Conversie ACTIV și vizibil în meniu"
                ]
            },
            "Perioada 2 - Post-conversie": {
                "descriere": "Sistem dual-currency cu toggle RON/EUR",
                "comportament": [
                    "Toggle currency ACTIV (implicit pornește pe EUR)",
                    "Baze clonate EUR: DEPCREDEUR.db, MEMBRIIEUR.db, activiEUR.db, INACTIVIEUR.db, LICHIDATIEUR.db",
                    "Modul EUR: Citire și scriere complete în bazele EUR",
                    "Modul RON: DOAR CITIRE pentru protecție date istorice",
                    "Butonul Conversie DISPARE din meniu (conversie deja aplicată), apare anunț: Sistem în EUR",
                    "Monkey patching activ: redirectare automată apeluri DB"
                ]
            }
        },
        "proces_conversie": {
            "descriere": "Proces automat clonare și conversie conform regulilor UE",
            "etape": [
                "1. Validare schemă și integritate date toate bazele (DEPCRED, MEMBRII, ACTIVI, INACTIVI, LICHIDATI)",
                "2. Validare comprehensivă consistență membri între baze",
                "3. Obținere lock-uri exclusive pe toate bazele pentru evitare corupții",
                "4. Clonare fizică toate cele 5 baze de date cu verificare",
                "5. Conversie DEPCRED.db: toate sumele RON→EUR cu rotunjire ROUND_HALF_UP",
                "6. Conversie MEMBRII.db: cotizații standard RON→EUR",
                "7. Conversie activi.db: solduri, dividende, beneficii RON→EUR",
                "8. Clonare directă INACTIVI.db și LICHIDATI.db (fără conversie)",
                "9. Validare matematică finală: suma_totală_EUR = suma_totală_RON / curs",
                "10. Salvare configurație conversie cu timestamp și curs aplicat"
            ],
            "validari_ue": [
                "Rotunjire obligatorie ROUND_HALF_UP (conform Regulamentul CE 1103/97)",
                "Precizie 2 zecimale pentru toate sumele EUR",
                "Toleranță maximă 0.01 EUR diferență la validare finală",
                "Verificare consistență sumă totală pre și post conversie",
                "Raportare detaliate discrepanțe dacă depășesc toleranța"
            ]
        },
        "monkey_patching": {
            "descriere": "Sistem de redirectare automată apeluri către baze de date corecte",
            "mecanism": [
                "La pornire aplicație: detectare automată stare conversie",
                "Patching dinamic toate modulele UI încărcate în sys.modules",
                "Înlocuire automată căi: DEPCRED.db → DEPCREDEUR.db, etc.",
                "La toggle currency: re-patching automat și reload widget activ",
                "Protecție scriere: validare permisiuni înainte de orice operație write",
                "Mesaje informative utilizator când operații blocate în modul doar-citire"
            ],
            "avantaje": [
                "Zero modificări cod modulelor existente",
                "Compatibilitate completă înapoi cu perioada pre-conversie",
                "Comutare instant între RON și EUR fără restart",
                "Protecție automată date istorice RON",
                "Transparență completă pentru modulele business logic"
            ]
        },
        "note": "Operație IREVERSIBILĂ după aplicare. Creați backup complet OBLIGATORIU înainte. Verificați cursul RON/EUR atent - acesta va fi fix pentru toată istoria aplicației"
    },
    "CAR DBF Converter": {
        "descriere": "Utilitar conversie unidirecțională SQLite DB --> DBF pentru compatibilitate sistemul anterior Visual FoxPro",
        "functionalitati": [
            "Conversie SQLite → DBF: pentru export către sisteme vechi Visual FoxPro",
            "Sistem 'amprentă digitală' pentru tracking versiuni și modificări",
            "Validare automată structură și consistență date",
            "Support multiple tabele simultan",
            "Progress indicator pentru operațiuni mari",
            "Verificare integritate post-conversie",
            "Backup automat înainte de conversii"
        ],
        "proces_conversie": [
            "Pasul 1: Verificare fișiere sursa - detectare automată fișiere disponibile",
            "Pasul 2: Creare amprentă digitală - snapshot metadata pentru tracking",
            "Pasul 3: Conversie propriu-zisă cu validări stricte",
            "Pasul 4: Lansare Visual FoxPro pentru reindexare (opțional, doar Windows)"
        ],
        "note": "Modul opțional - disponibil doar dacă fișierul car_dbf_converter_widget.py este prezent. Util pentru migrare date sau integrare cu software legacy existent"
    },
    "Selector temă": {
        "descriere": "Personalizare interfață cu 20 teme profesionale moderne",
        "categorii": {
            "Profesional": [
                "Pure Black - negru complet pentru OLED",
                "Dark Gray - gri închis profesional",
                "Charcoal - cărbune elegant",
                "Steel Blue - albastru oțel modern"
            ],
            "Corporate": [
                "Navy Blue - albastru marin corporate",
                "Business Gray - gri business clasic",
                "Corporate Blue - albastru corporatist",
                "Executive Dark - întuneric executive"
            ],
            "Vibrant": [
                "Ocean Blue - albastru ocean vibrant",
                "Forest Green - verde pădure natural",
                "Purple Night - violet noapte profund",
                "Ruby Red - roșu rubin elegant"
            ],
            "Neutral": [
                "Warm Gray - gri cald neutru",
                "Cool Slate - ardezie rece profesional",
                "Beige Professional - bej profesional cald",
                "Taupe Modern - taupe modern sofisticat"
            ]
        },
        "functionalitati": [
            "Previzualizare live la hover pe temă",
            "Aplicare instant fără restart",
            "Salvare automată preferință temă",
            "Filtrare teme după categorie",
            "Design consistent pe toate modulele"
        ],
        "note": "Tema se aplică imediat la toate componentele aplicației pentru experiență vizuală unitară"
    },
    "Calcule": {
        "descriere": "Calculator științific separat pentru calcule financiare și matematice",
        "functionalitati": [
            "Fereastră independentă 450x350px",
            "Operații de bază: +, -, *, /",
            "Funcții științifice: √ (radical), x² (pătrat), 1/x (reciprocă)",
            "Funcții speciale: % (procente), ± (schimbare semn)",
            "Operații în lanț complexe (ex: 2+3*4=20)",
            "Repetare automată ultimă operație prin apăsare repetată '='",
            "Control complet tastatură: cifre, operatori, Enter (=), Esc (Clear), Backspace",
            "Istoric complet sesiune cu timestamp",
            "Export istoric în fișier text",
            "Gestionare erori: împărțire la zero, overflow, radical negativ",
            "Butoane color-coded: albastru (=), roșu (operatori), portocaliu (științifice)",
            "Layout 70% calcul, 30% istoric pentru eficiență"
        ],
        "utilizare": [
            "Deschidere: Click buton 'Calcule' din bara principală",
            "Rămâne deschis și funcțional pe toată durata sesiunii",
            "Se închide automat la închiderea aplicației principale",
            "Perfect pentru calcule dobândă, rate, procente în paralel cu lucrul în CAR"
        ],
        "note": "Calculator complet independent - nu interferează cu aplicația principală și permite multitasking eficient"
    },
    "Versiune": {
        "descriere": "Informații aplicație, istoric versiuni și manual utilizare complet",
        "sectiuni": [
            "Informații versiune curentă cu număr și dată",
            "Istoric complet schimbări de la BETA2 la FINALA",
            "Manual detaliat toate meniurile și submeniurile",
            "Explicații funcționalități noi (monkey patching, dual-currency)",
            "Ghid rapid operațiuni frecvente",
            "Informații tehnice sistem dual-currency"
        ],
        "note": "Documentație completă actualizată la zi cu toate funcționalitățile aplicației"
    }
}


# ---------------------------------------------------------------------------
# GHID_STRUCTURE — conținutul filei "Ghid Utilizare".
#
# Folosește ACELEAȘI chei ca MANUAL_STRUCTURE (descriere / submeniuri /
# functionalitati / note), ca să fie randat de același cod, în același acordeon.
# Diferența e de ton: manualul descrie CE face fiecare modul, ghidul explică
# CUM se face, pas cu pas, pentru cineva fără cunoștințe tehnice.
#
# ATENȚIE — text duplicat: aceleași informații există și în README.md
# (secțiunile "Utilizare" și "Troubleshooting"). Dacă modifici una, actualizeaz-o
# și pe cealaltă. Comenzile de shell și SQL din README au fost intenționat lăsate
# afară: ghidul se adresează utilizatorului, nu administratorului.
# ---------------------------------------------------------------------------
GHID_STRUCTURE = {
    "1. Primii pași": {
        "descriere": "Ce se întâmplă când porniți aplicația și ce vedeți pe ecran",
        "functionalitati": [
            "Aplicația cere parola pentru dezarhivarea bazelor de date protejate",
            "Se încarcă automat tema salvată de la ultima utilizare",
            "Se verifică dacă a fost făcută conversia la EUR",
            "Se deschide fereastra principală: meniul lateral în stânga, conținutul în dreapta",
            "Ecranul de pornire este <b>Statistici</b>, cu situația lunii curente"
        ],
        "note": "La închiderea aplicației, bazele de date sunt rearhivate automat cu parolă. "
                "Nu închideți aplicația forțat din Task Manager — datele rămân neprotejate pe disc."
    },
    "2. Navigare în aplicație": {
        "descriere": "Cum ajungeți rapid la ce vă trebuie",
        "submeniuri": {
            "Meniul lateral": {
                "descriere": "Coloana din stânga, cu toate modulele aplicației",
                "functionalitati": [
                    "Click pe un buton deschide modulul respectiv",
                    "Modulele cu mai multe opțiuni deschid un submeniu",
                    "Butonul <b>⬅ Ieșire Meniu</b> vă întoarce la Statistici",
                    "Indicatorul de jos arată dacă aveți drept de scriere sau doar de citire"
                ]
            },
            "Scurtături de tastatură": {
                "descriere": "Mai rapid decât mouse-ul, pentru operațiunile zilnice",
                "functionalitati": [
                    "<b>Alt+A</b> — Actualizări (adăugare membru, sume lunare)",
                    "<b>Alt+V</b> — Vizualizări (situații lunare, trimestriale, anuale)",
                    "<b>Alt+L</b> — Listări (chitanțe PDF)",
                    "<b>Alt+S</b> — Salvări (backup și restaurare)",
                    "<b>Alt+G</b> — Generare lună nouă",
                    "<b>Alt+T</b> — Selector temă",
                    "<b>Ctrl+Alt+R</b> — Conversie RON→EUR",
                    "Lista completă se află în fila <b>Scurtături</b>"
                ]
            },
            "Comutarea RON / EUR": {
                "descriere": "Butoanele din partea de jos a meniului lateral",
                "functionalitati": [
                    "Disponibilă doar după ce conversia a fost efectuată",
                    "Comutarea e instantanee, fără repornirea aplicației",
                    "Ecranele se reîncarcă automat cu datele monedei alese"
                ]
            }
        }
    },
    "3. Operațiuni comune": {
        "descriere": "Cele mai frecvente activități, pas cu pas",
        "submeniuri": {
            "Adăugare membru nou": {
                "descriere": "Actualizări (Alt+A) → Adăugare membru",
                "functionalitati": [
                    "Completați datele: nume, prenume, domiciliu, calitatea",
                    "Numărul de fișă este atribuit automat și verificat împotriva duplicatelor",
                    "Stabiliți cotizația standard lunară",
                    "Alegeți data înscrierii din calendar",
                    "Click pe <b>Salvare</b> — membrul intră în MEMBRII.db și DEPCRED.db"
                ]
            },
            "Introducere plăți lunare": {
                "descriere": "Actualizări (Alt+A) → Sume lunare",
                "functionalitati": [
                    "Căutați membrul după numărul de fișă sau după nume",
                    "Introduceți datele lunii: cotizație, rată împrumut, împrumut nou, retrageri",
                    "Soldurile se recalculează automat după fiecare modificare",
                    "Click pe <b>Salvare</b> pentru a înregistra tranzacția"
                ],
                "note": "Dacă modificați o lună din trecut, toate lunile următoare se recalculează. "
                        "Verificați soldul final după o astfel de modificare."
            },
            "Generare lună nouă": {
                "descriere": "Generare lună (Alt+G)",
                "functionalitati": [
                    "Alegeți luna și anul de generat",
                    "Soldurile sunt preluate automat din luna anterioară",
                    "Rata de împrumut se moștenește din luna precedentă",
                    "Cotizația standard se aplică tuturor membrilor activi",
                    "Membrii lichidați sunt excluși automat",
                    "Dobânda se calculează pentru împrumuturile care se sting în această lună"
                ],
                "note": "Membrii fără înregistrare în luna anterioară sunt săriți și raportați. "
                        "Verificați lista de omisiuni la finalul generării."
            },
            "Generare chitanțe PDF": {
                "descriere": "Listări (Alt+L)",
                "functionalitati": [
                    "Alegeți luna și anul pentru care tipăriți chitanțele",
                    "Setați numărul primei chitanțe (de exemplu 1001)",
                    "Configurați câte chitanțe intră pe pagină (între 5 și 15, implicit 10)",
                    "Click pe <b>Preview</b> și verificați totalurile afișate",
                    "Click pe <b>Tipărește PDF</b> — fișierul se salvează ca chitante_LUNA_AN.pdf",
                    "PDF-ul se deschide automat la final"
                ],
                "note": "Numerotarea continuă de la ultima tipărire, memorată în CHITANTE.db. "
                        "Dacă numărul a crescut nejustificat, folosiți butonul Reset."
            },
            "Vizualizare rapoarte": {
                "descriere": "Vizualizări (Alt+V)",
                "functionalitati": [
                    "Alegeți tipul: situație lunară, trimestrială sau anuală",
                    "Selectați perioada dorită",
                    "Se afișează toate tranzacțiile și soldurile perioadei",
                    "Datele pot fi exportate în Excel"
                ]
            }
        }
    },
    "4. Conversie RON → EUR": {
        "descriere": "Operațiune IREVERSIBILĂ. Se face o singură dată, la trecerea la euro.",
        "submeniuri": {
            "Înainte de conversie": {
                "descriere": "Pregătirea, obligatorie",
                "functionalitati": [
                    "Faceți un backup complet: Salvări (Alt+S) → Backup Complet",
                    "Verificați că backup-ul s-a creat și conține toate bazele",
                    "Copiați backup-ul pe un dispozitiv extern"
                ],
                "note": "Conversia NU poate fi anulată. Backup-ul este singura cale de întoarcere."
            },
            "Efectuarea conversiei": {
                "descriere": "Conversie RON→EUR (Ctrl+Alt+R)",
                "functionalitati": [
                    "Verificați cursul de schimb afișat",
                    "Confirmați în dialogul de avertizare",
                    "Se creează baze noi, cu sufixul EUR: MEMBRIIEUR.db, DEPCREDEUR.db și celelalte",
                    "Bazele originale în lei rămân neatinse"
                ]
            },
            "După conversie": {
                "descriere": "Ce se schimbă în funcționarea zilnică",
                "functionalitati": [
                    "<b>Modul EUR</b> — citire și scriere, toate operațiunile permise",
                    "<b>Modul RON</b> — doar citire, pentru consultarea istoricului",
                    "Comutarea între monede se face din meniul lateral, fără repornire"
                ]
            }
        }
    },
    "5. Backup și siguranța datelor": {
        "descriere": "Cum vă protejați datele și cum le recuperați",
        "submeniuri": {
            "Crearea unui backup": {
                "descriere": "Salvări (Alt+S) → Backup Complet",
                "functionalitati": [
                    "Se creează automat un director cu data curentă, în folderul backup_db",
                    "Toate bazele de date sunt copiate acolo",
                    "Folderul se deschide singur la final, ca să puteți verifica"
                ]
            },
            "Restaurarea din backup": {
                "descriere": "Salvări (Alt+S) → Restaurare",
                "functionalitati": [
                    "Alegeți folderul de backup din care restaurați",
                    "Datele curente sunt salvate automat înainte de restaurare",
                    "După restaurare, aplicația trebuie repornită"
                ]
            },
            "Recomandări": {
                "descriere": "Obiceiuri care previn pierderea datelor",
                "functionalitati": [
                    "Faceți backup lunar și înainte de orice operațiune majoră",
                    "Păstrați cel puțin o copie pe un dispozitiv extern",
                    "Verificați periodic integritatea: Salvări → Verifică Integritatea"
                ],
                "note": "Un backup pe care nu l-ați verificat niciodată nu este un backup."
            }
        }
    },
    "6. Rezolvare probleme comune": {
        "descriere": "Ce puteți verifica singur, înainte de a cere ajutor",
        "submeniuri": {
            "Aplicația nu pornește": {
                "functionalitati": [
                    "Verificați că bazele de date se află în directorul aplicației",
                    "Verificați că nu ați introdus greșit parola de dezarhivare",
                    "Dacă problema persistă, contactați administratorul"
                ]
            },
            "Nu pot modifica datele": {
                "functionalitati": [
                    "Verificați indicatorul de permisiuni din meniul lateral",
                    "Dacă scrie <b>Doar Citire</b>, sunteți probabil în modul RON după conversie",
                    "Comutați pe EUR pentru a putea modifica"
                ]
            },
            "Comutarea RON/EUR nu funcționează": {
                "functionalitati": [
                    "Bazele EUR lipsesc — conversia nu a fost făcută sau a eșuat",
                    "Fișierul dual_currency.json lipsește sau e deteriorat",
                    "Contactați administratorul: ambele cazuri cer verificare tehnică"
                ]
            },
            "Chitanțele nu au diacritice": {
                "functionalitati": [
                    "Lipsesc fonturile Arial.ttf și DejaVuSans-Bold.ttf",
                    "Ele trebuie să existe atât în folderul fonts, cât și în rădăcina aplicației",
                    "Contactați administratorul pentru copierea lor"
                ]
            },
            "Numărul chitanței a devenit prea mare": {
                "functionalitati": [
                    "Apăsați <b>Reset</b> în modulul Listări",
                    "Confirmați resetarea la 1, sau introduceți manual un număr potrivit",
                    "Numărul nou se memorează automat"
                ]
            },
            "Erori la generarea lunii noi": {
                "functionalitati": [
                    "Verificați că luna anterioară a fost generată complet",
                    "Membrii fără înregistrare în luna anterioară sunt săriți — e normal pentru cei noi",
                    "Citiți lista de omisiuni afișată la finalul generării"
                ]
            },
            "Tema nu se salvează": {
                "functionalitati": [
                    "Fișierul car_settings.json nu poate fi scris",
                    "Cel mai des e o problemă de permisiuni pe director",
                    "Contactați administratorul"
                ]
            }
        }
    }
}


class AccordionSection(QWidget):
    """Secțiune acordeon modernă slick - stil profesional clean"""

    def __init__(self, title, content_widget, parent=None):
        super().__init__(parent)
        self.content_widget = content_widget
        self.is_expanded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header clickable
        self.header = QPushButton(f"▶  {title}")
        self.header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.header.setStyleSheet(f"""
            QPushButton {{
                background: {P.PANEL_2};
                border: 1px solid {P.LINE};
                border-radius: 6px;
                padding: 12px 16px;
                text-align: left;
                color: {P.INK};
            }}
            QPushButton:hover {{
                background: {P.PANEL_2};
                border-color: {P.LINE};
            }}
            QPushButton:pressed {{
                background: {P.LINE};
            }}
        """)
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.clicked.connect(self.toggle)
        layout.addWidget(self.header)

        # Container pentru conținut
        self.content_container = QFrame()
        self.content_container.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-top: none;
                border-radius: 0 0 6px 6px;
                padding: 16px;
            }}
        """)
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.addWidget(content_widget)
        self.content_container.setMaximumHeight(0)
        self.content_container.setVisible(False)
        layout.addWidget(self.content_container)

        # Animație pentru expand/collapse
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

    def toggle(self):
        """Toggle expand/collapse cu animație"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Expandează secțiunea"""
        self.is_expanded = True
        self.header.setText(self.header.text().replace("▶", "▼"))

        # Calculează înălțimea necesară
        self.content_widget.adjustSize()
        target_height = self.content_widget.sizeHint().height() + 32

        self.animation.setStartValue(0)
        self.animation.setEndValue(target_height)
        self.content_container.setVisible(True)
        self.animation.start()

    def collapse(self):
        """Colapsează secțiunea"""
        self.is_expanded = False
        self.header.setText(self.header.text().replace("▼", "▶"))

        self.animation.setStartValue(self.content_container.maximumHeight())
        self.animation.setEndValue(0)
        self.animation.finished.connect(lambda: self.content_container.setVisible(False))
        self.animation.start()


class DespreWidget(QDialog):
    """Dialog Despre - Design profesional modern slick"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CAR Petroșani - Informații Aplicație")
        self.setMinimumSize(900, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header compact profesional
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {P.INK}, stop:1 {P.INFO});
                border-radius: 8px;
                padding: 16px;
            }}
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(20)

        # Titlu
        title_label = QLabel("CAR Petroșani")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)

        # Versiune
        version_label = QLabel(f"Versiunea {CURRENT_VERSION}")
        version_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        version_label.setStyleSheet(f"color: {P.PANEL_2};")
        header_layout.addWidget(version_label)

        header_layout.addStretch()

        main_layout.addWidget(header_frame)

        # Tab-uri principale
        tabs_frame = QFrame()
        tabs_layout = QHBoxLayout(tabs_frame)
        tabs_layout.setSpacing(10)

        self.btn_ghid = self._create_tab_button("Ghid Utilizare")
        self.btn_manual = self._create_tab_button("Manual Tehnic")
        self.btn_changelog = self._create_tab_button("Istoric Versiuni")
        self.btn_tech = self._create_tab_button("Info Tehnice")
        self.btn_shortcut = self._create_tab_button("Scurtături Tastatură")

        self.btn_ghid.clicked.connect(lambda: self._switch_tab(0))
        self.btn_manual.clicked.connect(lambda: self._switch_tab(1))
        self.btn_changelog.clicked.connect(lambda: self._switch_tab(2))
        self.btn_tech.clicked.connect(lambda: self._switch_tab(3))
        self.btn_shortcut.clicked.connect(lambda: self._switch_tab(4))

        tabs_layout.addWidget(self.btn_ghid)
        tabs_layout.addWidget(self.btn_manual)
        tabs_layout.addWidget(self.btn_changelog)
        tabs_layout.addWidget(self.btn_tech)
        tabs_layout.addWidget(self.btn_shortcut)

        tabs_layout.addStretch()

        main_layout.addWidget(tabs_frame)

        # Scroll area pentru conținut
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {P.LINE};
                border-radius: 6px;
                background: white;
            }}
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)

        # Buton închidere
        close_btn = QPushButton("Închide")
        close_btn.setFont(QFont("Segoe UI", 10))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {P.INFO};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {P.INFO};
            }}
        """)
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(150)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        main_layout.addLayout(close_layout)

        # Încarcă tab implicit
        self._switch_tab(0)

    def _create_tab_button(self, text):
        """Creează buton tab modern"""
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {P.PANEL_2};
                border: 1px solid {P.LINE};
                border-radius: 6px;
                padding: 10px 20px;
                color: {P.MUTED};
            }}
            QPushButton:hover {{
                background: {P.PANEL_2};
            }}
            QPushButton:checked {{
                background: {P.INFO};
                color: white;
                border-color: {P.INFO};
            }}
        """)
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def _switch_tab(self, tab_index):
        """Comută între tab-uri"""
        # Resetează toate butoanele
        self.btn_ghid.setChecked(False)
        self.btn_manual.setChecked(False)
        self.btn_changelog.setChecked(False)
        self.btn_tech.setChecked(False)
        self.btn_shortcut.setChecked(False)

        # Curăță layout-ul
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Încarcă conținutul corespunzător
        if tab_index == 0:
            self.btn_ghid.setChecked(True)
            self._load_ghid_utilizare()
        elif tab_index == 1:
            self.btn_manual.setChecked(True)
            self._load_manual()
        elif tab_index == 2:
            self.btn_changelog.setChecked(True)
            self._load_changelog()
        elif tab_index == 3:
            self.btn_tech.setChecked(True)
            self._load_tech_info()
        elif tab_index == 4:
            self.btn_shortcut.setChecked(True)
            self._load_shortcuts()

    def _load_ghid_utilizare(self):
        """Încarcă ghidul de utilizare pentru utilizatori non-tehnici"""
        intro_label = QLabel(
            "<b>Ghid de Utilizare CAR Petroșani</b><br>"
            "Ghid pas cu pas pentru utilizarea aplicației, destinat utilizatorilor "
            "care nu au cunoștințe tehnice. Click pe orice secțiune pentru a o deschide."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet(f"padding: 10px; background: {P.ACCENT_SOFT}; border-radius: 6px; color: {P.POSITIVE};")
        self.content_layout.addWidget(intro_label)

        # Aceeași randare ca la Manual Tehnic: acordeon, o secțiune per subiect.
        for sectiune_nume, sectiune_date in GHID_STRUCTURE.items():
            section_widget = self._create_menu_section_widget(sectiune_nume, sectiune_date)
            accordion = AccordionSection(sectiune_nume, section_widget)
            self.content_layout.addWidget(accordion)

        # Contact și Suport
        support_frame = QFrame()
        support_frame.setStyleSheet(f"""
            QFrame {{
                background: {P.PANEL_2};
                border: 1px solid {P.LINE};
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
            }}
        """)
        support_layout = QVBoxLayout(support_frame)

        support_label = QLabel(
            "<b>Suport și Documentație:</b><br>"
            "Pentru întrebări sau probleme, consultați <b>Manual Tehnic</b> sau accesați repository-ul GitHub:<br>"
            f"<a href='https://github.com/totilaAtila/C.A.R._Petrosani' style='color: {P.INFO};'>"
            "https://github.com/totilaAtila/C.A.R._Petrosani</a>"
        )
        support_label.setWordWrap(True)
        support_label.setTextFormat(Qt.RichText)
        support_label.setOpenExternalLinks(True)
        support_label.setStyleSheet(f"color: {P.INFO}; font-size: 10pt;")
        support_layout.addWidget(support_label)
        self.content_layout.addWidget(support_frame)

        self.content_layout.addStretch()

    def _create_section_frame(self, title):
        """Creează un frame pentru o secțiune cu titlu"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        layout = QVBoxLayout(frame)

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {P.INK}; margin-bottom: 8px;")
        layout.addWidget(title_label)

        return frame

    def _load_shortcuts(self):
        """Încarcă lista completă de scurtături tastatură"""
        intro_label = QLabel(
            "<b>Scurtături Tastatură</b><br>"
            "Lista completă a combinațiilor de taste pentru acces rapid la funcționalități."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet(f"padding: 10px; background: {P.WARNING_SOFT}; border-radius: 6px; color: {P.WARNING};")
        self.content_layout.addWidget(intro_label)

        # Secțiunea Meniu Principal
        main_menu_frame = QFrame()
        main_menu_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        main_menu_layout = QVBoxLayout(main_menu_frame)

        main_menu_title = QLabel("<b>Scurtături Meniu Principal</b>")
        main_menu_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        main_menu_title.setStyleSheet(f"color: {P.INK};")
        main_menu_layout.addWidget(main_menu_title)

        shortcuts_main = f"""
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: {P.PANEL_2};'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE}; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE};'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+A</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide meniul <b>Actualizări</b></td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+V</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide meniul <b>Vizualizări</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+L</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Listări</b> chitanțe</td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+S</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide meniul <b>Salvări</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+I</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Împrumuturi Noi</b></td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+G</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Generare lună</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+O</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Optimizare baze</b></td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+T</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Selector temă</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+R</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Versiune</b> (acest dialog)</td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+Q</kbd></td>
                <td style='padding: 8px;'>Închide aplicația (<b>Ieșire</b>)</td>
            </tr>
        </table>
        """
        shortcuts_label = QLabel(shortcuts_main)
        shortcuts_label.setWordWrap(True)
        shortcuts_label.setTextFormat(Qt.RichText)
        shortcuts_label.setStyleSheet(f"color: {P.MUTED};")
        main_menu_layout.addWidget(shortcuts_label)

        self.content_layout.addWidget(main_menu_frame)

        # Secțiunea Scurtături Avansate
        advanced_frame = QFrame()
        advanced_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        advanced_layout = QVBoxLayout(advanced_frame)

        advanced_title = QLabel("<b>Scurtături Avansate</b>")
        advanced_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        advanced_title.setStyleSheet(f"color: {P.INK};")
        advanced_layout.addWidget(advanced_title)

        shortcuts_advanced = f"""
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: {P.PANEL_2};'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE}; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE};'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Ctrl+Alt+C</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Calculator</b> independent</td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Ctrl+Alt+D</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>CAR DBF Converter</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Ctrl+Alt+R</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Conversie RON→EUR</b></td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>F12</kbd></td>
                <td style='padding: 8px;'>Comută rapid către <b>Împrumuturi Noi</b> (dacă fereastră deja deschisă)</td>
            </tr>
        </table>
        """
        shortcuts_advanced_label = QLabel(shortcuts_advanced)
        shortcuts_advanced_label.setWordWrap(True)
        shortcuts_advanced_label.setTextFormat(Qt.RichText)
        shortcuts_advanced_label.setStyleSheet(f"color: {P.MUTED};")
        advanced_layout.addWidget(shortcuts_advanced_label)

        self.content_layout.addWidget(advanced_frame)

        # Secțiunea Modul Sume Lunare
        sume_frame = QFrame()
        sume_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        sume_layout = QVBoxLayout(sume_frame)

        sume_title = QLabel("<b>Scurtături Modul Sume Lunare</b>")
        sume_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        sume_title.setStyleSheet(f"color: {P.INK};")
        sume_layout.addWidget(sume_title)

        shortcuts_sume = f"""
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: {P.PANEL_2};'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE}; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE};'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Escape</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Reset/Anulare</b> - Golește formularul și istoricul</td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>F1</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Modifică Tranzacție</b> - Deschide dialog pentru modificarea ultimei luni înregistrate</td>
            </tr>
            <tr>
                <td style='padding: 8px;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>F5</kbd></td>
                <td style='padding: 8px;'><b>Calculează Dobândă la Zi</b> - Pentru achitare anticipată împrumut</td>
            </tr>
        </table>
        """
        shortcuts_sume_label = QLabel(shortcuts_sume)
        shortcuts_sume_label.setWordWrap(True)
        shortcuts_sume_label.setTextFormat(Qt.RichText)
        shortcuts_sume_label.setStyleSheet(f"color: {P.MUTED};")
        sume_layout.addWidget(shortcuts_sume_label)

        self.content_layout.addWidget(sume_frame)

        # Secțiunea Calculator
        calc_frame = QFrame()
        calc_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        calc_layout = QVBoxLayout(calc_frame)

        calc_title = QLabel("<b>Scurtături Calculator</b>")
        calc_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        calc_title.setStyleSheet(f"color: {P.INK};")
        calc_layout.addWidget(calc_title)

        shortcuts_calc = f"""
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: {P.PANEL_2};'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE}; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid {P.LINE};'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>0-9, .</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Introducere <b>cifre și punct zecimal</b></td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>+, -, *, /</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Introducere <b>operatori matematici</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Enter / =</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Calculează rezultatul</b></td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Escape / C</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Clear</b> - Șterge tot conținutul</td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Backspace</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Șterge ultimul caracter</b></td>
            </tr>
            <tr style='background: {P.PANEL_2};'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Delete</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Clear Entry</b> - Șterge intrarea curentă</td>
            </tr>
            <tr>
                <td style='padding: 8px;'><kbd style='background: {P.PANEL_2}; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>%</kbd></td>
                <td style='padding: 8px;'><b>Calcul procent</b></td>
            </tr>
        </table>
        """
        shortcuts_calc_label = QLabel(shortcuts_calc)
        shortcuts_calc_label.setWordWrap(True)
        shortcuts_calc_label.setTextFormat(Qt.RichText)
        shortcuts_calc_label.setStyleSheet(f"color: {P.MUTED};")
        calc_layout.addWidget(shortcuts_calc_label)

        self.content_layout.addWidget(calc_frame)

        # Notă finală
        note_frame = QFrame()
        note_frame.setStyleSheet(f"""
            QFrame {{
                background: {P.PANEL_2};
                border: 1px solid {P.PANEL_2};
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
            }}
        """)
        note_layout = QVBoxLayout(note_frame)

        note_label = QLabel(
            "<b>Notă:</b> Toate scurtăturile funcționează indiferent de fereastra activă în cadrul aplicației. "
            "Scurtăturile cu <kbd style='background: #fff; padding: 2px 6px; border-radius: 3px;'>Alt</kbd> sunt pentru accesul rapid la meniuri, "
            "iar cele cu <kbd style='background: #fff; padding: 2px 6px; border-radius: 3px;'>Ctrl+Alt</kbd> pentru funcționalități avansate. "
            "Scurtăturile din module specifice (Sume Lunare, Calculator) funcționează doar când modulul respectiv este activ."
        )
        note_label.setWordWrap(True)
        note_label.setTextFormat(Qt.RichText)
        note_label.setStyleSheet(f"color: {P.INFO}; font-size: 9pt;")
        note_layout.addWidget(note_label)

        self.content_layout.addWidget(note_frame)

        self.content_layout.addStretch()

    def _load_manual(self):
        """Încarcă manualul de utilizare cu acordeon"""
        intro_label = QLabel(
            "<b>Manual Complet de Utilizare</b><br>"
            "Ghid detaliat pentru toate funcționalitățile aplicației CAR Petroșani. "
            "Click pe orice secțiune pentru a vedea detaliile."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet(f"padding: 10px; background: {P.PANEL_2}; border-radius: 6px; color: {P.INFO};")
        self.content_layout.addWidget(intro_label)

        # Creează secțiuni acordeon pentru fiecare meniu
        for menu_name, menu_data in MANUAL_STRUCTURE.items():
            section_widget = self._create_menu_section_widget(menu_name, menu_data)
            accordion = AccordionSection(menu_name, section_widget)
            self.content_layout.addWidget(accordion)

        self.content_layout.addStretch()

    def _create_menu_section_widget(self, menu_name, menu_data):
        """Creează widget pentru secțiune meniu"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Descriere generală
        if 'descriere' in menu_data:
            desc_label = QLabel(f"<b>Descriere:</b> {menu_data['descriere']}")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"color: {P.MUTED}; padding: 8px; background: {P.PANEL_2}; border-radius: 4px;")
            layout.addWidget(desc_label)

        # Submeniuri (dacă există)
        if 'submeniuri' in menu_data:
            for submenu_name, submenu_data in menu_data['submeniuri'].items():
                submenu_frame = QFrame()
                submenu_frame.setStyleSheet(f"""
                    QFrame {{
                        background: white;
                        border-left: 3px solid {P.INFO};
                        padding: 12px;
                        margin: 4px 0;
                    }}
                """)
                submenu_layout = QVBoxLayout(submenu_frame)

                # Titlu submeniu
                title = QLabel(f"<b>{submenu_name}</b>")
                title.setFont(QFont("Segoe UI", 10, QFont.Bold))
                title.setStyleSheet(f"color: {P.INK};")
                submenu_layout.addWidget(title)

                # Descriere submeniu
                if 'descriere' in submenu_data:
                    desc = QLabel(submenu_data['descriere'])
                    desc.setWordWrap(True)
                    desc.setStyleSheet(f"color: {P.FAINT}; margin-left: 10px;")
                    submenu_layout.addWidget(desc)

                # Funcționalități
                if 'functionalitati' in submenu_data:
                    func_text = "<ul style='margin: 5px 0 5px 20px;'>"
                    for func in submenu_data['functionalitati']:
                        func_text += f"<li>{func}</li>"
                    func_text += "</ul>"
                    func_label = QLabel(func_text)
                    func_label.setWordWrap(True)
                    func_label.setTextFormat(Qt.RichText)
                    func_label.setStyleSheet(f"color: {P.MUTED}; margin-left: 10px;")
                    submenu_layout.addWidget(func_label)

                # Note
                if 'note' in submenu_data:
                    note_label = QLabel(f"<b>Notă:</b> {submenu_data['note']}")
                    note_label.setWordWrap(True)
                    note_label.setStyleSheet(f"""
                        color: {P.WARNING};
                        background: {P.WARNING_SOFT};
                        padding: 8px;
                        border-radius: 4px;
                        border-left: 3px solid {P.WARNING};
                        margin: 8px 0 0 10px;
                    """)
                    submenu_layout.addWidget(note_label)

                layout.addWidget(submenu_frame)

        # Funcționalități directe (fără submeniuri)
        elif 'functionalitati' in menu_data:
            func_text = "<ul style='margin: 5px 0 5px 20px;'>"
            for func in menu_data['functionalitati']:
                func_text += f"<li>{func}</li>"
            func_text += "</ul>"
            func_label = QLabel(func_text)
            func_label.setWordWrap(True)
            func_label.setTextFormat(Qt.RichText)
            func_label.setStyleSheet(f"color: {P.MUTED}; padding: 8px;")
            layout.addWidget(func_label)

        # Stări sistem (pentru Conversie)
        if 'stari_sistem' in menu_data:
            for stare_name, stare_data in menu_data['stari_sistem'].items():
                stare_frame = QFrame()
                stare_frame.setStyleSheet(f"""
                    QFrame {{
                        background: {P.PANEL_2};
                        border: 2px solid {P.LINE};
                        border-radius: 6px;
                        padding: 12px;
                        margin: 8px 0;
                    }}
                """)
                stare_layout = QVBoxLayout(stare_frame)

                stare_title = QLabel(f"<b>{stare_name}</b>")
                stare_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
                stare_title.setStyleSheet(f"color: {P.INFO};")
                stare_layout.addWidget(stare_title)

                if 'descriere' in stare_data:
                    stare_desc = QLabel(stare_data['descriere'])
                    stare_desc.setWordWrap(True)
                    stare_desc.setStyleSheet(f"color: {P.FAINT}; margin-left: 10px;")
                    stare_layout.addWidget(stare_desc)

                if 'comportament' in stare_data:
                    comp_text = "<ul style='margin: 5px 0 5px 20px;'>"
                    for comp in stare_data['comportament']:
                        comp_text += f"<li>{comp}</li>"
                    comp_text += "</ul>"
                    comp_label = QLabel(comp_text)
                    comp_label.setWordWrap(True)
                    comp_label.setTextFormat(Qt.RichText)
                    comp_label.setStyleSheet(f"color: {P.MUTED}; margin-left: 10px;")
                    stare_layout.addWidget(comp_label)

                layout.addWidget(stare_frame)

        # Proces conversie (pentru Conversie)
        if 'proces_conversie' in menu_data:
            proces_data = menu_data['proces_conversie']
            proces_frame = QFrame()
            proces_frame.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 2px solid {P.POSITIVE};
                    border-radius: 6px;
                    padding: 12px;
                    margin: 8px 0;
                }}
            """)
            proces_layout = QVBoxLayout(proces_frame)

            proces_title = QLabel("<b>Procesul de Conversie Automată</b>")
            proces_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            proces_title.setStyleSheet(f"color: {P.POSITIVE};")
            proces_layout.addWidget(proces_title)

            if 'descriere' in proces_data:
                proces_desc = QLabel(proces_data['descriere'])
                proces_desc.setWordWrap(True)
                proces_desc.setStyleSheet(f"color: {P.FAINT}; margin-left: 10px;")
                proces_layout.addWidget(proces_desc)

            if 'etape' in proces_data:
                etape_text = "<ol style='margin: 5px 0 5px 20px;'>"
                for etapa in proces_data['etape']:
                    etape_text += f"<li>{etapa}</li>"
                etape_text += "</ol>"
                etape_label = QLabel(etape_text)
                etape_label.setWordWrap(True)
                etape_label.setTextFormat(Qt.RichText)
                etape_label.setStyleSheet(f"color: {P.MUTED}; margin-left: 10px;")
                proces_layout.addWidget(etape_label)

            if 'validari_ue' in proces_data:
                val_title = QLabel("<b>Validări Conformitate UE:</b>")
                val_title.setStyleSheet(f"color: {P.INFO}; margin: 8px 0 4px 10px;")
                proces_layout.addWidget(val_title)

                val_text = "<ul style='margin: 5px 0 5px 20px;'>"
                for val in proces_data['validari_ue']:
                    val_text += f"<li>{val}</li>"
                val_text += "</ul>"
                val_label = QLabel(val_text)
                val_label.setWordWrap(True)
                val_label.setTextFormat(Qt.RichText)
                val_label.setStyleSheet(f"color: {P.INFO}; margin-left: 10px;")
                proces_layout.addWidget(val_label)

            layout.addWidget(proces_frame)

        # Monkey patching (pentru Conversie)
        if 'monkey_patching' in menu_data:
            mp_data = menu_data['monkey_patching']
            mp_frame = QFrame()
            mp_frame.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 2px solid {P.ACCENT_DEEP};
                    border-radius: 6px;
                    padding: 12px;
                    margin: 8px 0;
                }}
            """)
            mp_layout = QVBoxLayout(mp_frame)

            mp_title = QLabel("<b>Sistem Monkey Patching</b>")
            mp_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            mp_title.setStyleSheet(f"color: {P.ACCENT_DEEP};")
            mp_layout.addWidget(mp_title)

            if 'descriere' in mp_data:
                mp_desc = QLabel(mp_data['descriere'])
                mp_desc.setWordWrap(True)
                mp_desc.setStyleSheet(f"color: {P.FAINT}; margin-left: 10px;")
                mp_layout.addWidget(mp_desc)

            if 'mecanism' in mp_data:
                mec_text = "<ul style='margin: 5px 0 5px 20px;'>"
                for mec in mp_data['mecanism']:
                    mec_text += f"<li>{mec}</li>"
                mec_text += "</ul>"
                mec_label = QLabel(mec_text)
                mec_label.setWordWrap(True)
                mec_label.setTextFormat(Qt.RichText)
                mec_label.setStyleSheet(f"color: {P.MUTED}; margin-left: 10px;")
                mp_layout.addWidget(mec_label)

            if 'avantaje' in mp_data:
                av_title = QLabel("<b>Avantaje:</b>")
                av_title.setStyleSheet(f"color: {P.POSITIVE}; margin: 8px 0 4px 10px;")
                mp_layout.addWidget(av_title)

                av_text = "<ul style='margin: 5px 0 5px 20px;'>"
                for av in mp_data['avantaje']:
                    av_text += f"<li>{av}</li>"
                av_text += "</ul>"
                av_label = QLabel(av_text)
                av_label.setWordWrap(True)
                av_label.setTextFormat(Qt.RichText)
                av_label.setStyleSheet(f"color: {P.POSITIVE}; margin-left: 10px;")
                mp_layout.addWidget(av_label)

            layout.addWidget(mp_frame)

        # Categorii (pentru Selector temă)
        if 'categorii' in menu_data:
            for cat_name, cat_themes in menu_data['categorii'].items():
                cat_label = QLabel(f"<b>{cat_name}:</b> {', '.join(cat_themes)}")
                cat_label.setWordWrap(True)
                cat_label.setStyleSheet(f"color: {P.MUTED}; padding: 6px; margin-left: 10px;")
                layout.addWidget(cat_label)

        # Note finale
        if 'note' in menu_data:
            note_label = QLabel(f"<b>Important:</b> {menu_data['note']}")
            note_label.setWordWrap(True)
            note_label.setStyleSheet(f"""
                color: {P.DANGER};
                background: {P.DANGER_SOFT};
                padding: 10px;
                border-radius: 4px;
                border-left: 4px solid {P.DANGER};
                margin-top: 10px;
            """)
            layout.addWidget(note_label)

        # Utilizare (pentru Calcule)
        if 'utilizare' in menu_data:
            util_text = "<b>Utilizare:</b><ul style='margin: 5px 0 5px 20px;'>"
            for util in menu_data['utilizare']:
                util_text += f"<li>{util}</li>"
            util_text += "</ul>"
            util_label = QLabel(util_text)
            util_label.setWordWrap(True)
            util_label.setTextFormat(Qt.RichText)
            util_label.setStyleSheet(f"color: {P.MUTED}; padding: 8px; background: {P.PANEL_2}; border-radius: 4px;")
            layout.addWidget(util_label)

        # Secțiuni (pentru Versiune)
        if 'sectiuni' in menu_data:
            sect_text = "<ul style='margin: 5px 0 5px 20px;'>"
            for sect in menu_data['sectiuni']:
                sect_text += f"<li>{sect}</li>"
            sect_text += "</ul>"
            sect_label = QLabel(sect_text)
            sect_label.setWordWrap(True)
            sect_label.setTextFormat(Qt.RichText)
            sect_label.setStyleSheet(f"color: {P.MUTED}; padding: 8px;")
            layout.addWidget(sect_label)

        return widget

    def _load_changelog(self):
        """Încarcă istoricul versiunilor"""
        intro_label = QLabel(
            "<b>Istoric Versiuni</b><br>"
            "Evoluția aplicației CAR Petroșani de la prima versiune BETA la versiunea finală."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet(f"padding: 10px; background: {P.ACCENT_SOFT}; border-radius: 6px; color: {P.POSITIVE};")
        self.content_layout.addWidget(intro_label)

        for version, changes in reversed(list(CHANGELOG.items())):
            version_frame = QFrame()

            if version == "FINALA":
                version_frame.setStyleSheet(f"""
                    QFrame {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {P.WARNING_SOFT}, stop:1 {P.WARNING_SOFT});
                        border: 2px solid {P.WARNING};
                        border-radius: 8px;
                        padding: 16px;
                        margin: 8px 0;
                    }}
                """)
            elif version == CURRENT_VERSION:
                version_frame.setStyleSheet(f"""
                    QFrame {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {P.PANEL_2}, stop:1 {P.PANEL_2});
                        border: 2px solid {P.INFO};
                        border-radius: 8px;
                        padding: 16px;
                        margin: 8px 0;
                    }}
                """)
            else:
                version_frame.setStyleSheet(f"""
                    QFrame {{
                        background: white;
                        border: 1px solid {P.LINE};
                        border-radius: 8px;
                        padding: 16px;
                        margin: 8px 0;
                    }}
                """)

            version_layout = QVBoxLayout(version_frame)

            # Header versiune
            if version == "FINALA":
                version_label = QLabel(f"<b>{version}</b>")
                version_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
                version_label.setStyleSheet(f"color: {P.WARNING};")
            elif version == CURRENT_VERSION:
                version_label = QLabel(f"<b>Versiunea {version}</b> - CURENT")
                version_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                version_label.setStyleSheet(f"color: {P.INFO};")
            else:
                version_label = QLabel(f"<b>Versiunea {version}</b>")
                version_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                version_label.setStyleSheet(f"color: {P.INK};")

            version_layout.addWidget(version_label)

            # Lista îmbunătățiri
            changes_text = "<ul style='margin: 8px 0 0 20px; line-height: 1.6;'>"
            for change in changes:
                changes_text += f"<li>{change}</li>"
            changes_text += "</ul>"

            changes_label = QLabel(changes_text)
            changes_label.setWordWrap(True)
            changes_label.setTextFormat(Qt.RichText)
            changes_label.setStyleSheet(f"color: {P.MUTED}; font-size: 9pt;")
            version_layout.addWidget(changes_label)

            self.content_layout.addWidget(version_frame)

        self.content_layout.addStretch()

    def _load_tech_info(self):
        """Încarcă informații tehnice sistem"""
        intro_label = QLabel(
            "<b>Informații Tehnice</b><br>"
            "Detalii despre arhitectura și tehnologiile utilizate în aplicația CAR Petroșani."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet(f"padding: 10px; background: {P.ACCENT_SOFT}; border-radius: 6px; color: {P.ACCENT_DEEP};")
        self.content_layout.addWidget(intro_label)

        # Informații generale
        general_frame = QFrame()
        general_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        general_layout = QVBoxLayout(general_frame)

        general_title = QLabel("<b>Tehnologii Utilizate</b>")
        general_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        general_title.setStyleSheet(f"color: {P.INK};")
        general_layout.addWidget(general_title)

        tech_info = """
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>Limbaj:</b> Python 3.x</li>
            <li><b>Framework UI:</b> PyQt5 pentru interfață grafică modernă</li>
            <li><b>Baze de date:</b> SQLite3 pentru persistență date</li>
            <li><b>Export:</b> ReportLab pentru generare PDF, xlsxwriter pentru Excel</li>
            <li><b>Arhitectură:</b> MVC cu separare logică business și prezentare</li>
            <li><b>Conversie monedă:</b> Decimal pentru precizie matematică conform UE</li>
        </ul>
        """
        tech_label = QLabel(tech_info)
        tech_label.setWordWrap(True)
        tech_label.setTextFormat(Qt.RichText)
        tech_label.setStyleSheet(f"color: {P.MUTED};")
        general_layout.addWidget(tech_label)

        # Link GitHub
        github_label = QLabel(
            "<b>Repository GitHub:</b><br>"
            f"<a href='https://github.com/totilaAtila/C.A.R._Petrosani' style='color: {P.INFO};'>"
            "https://github.com/totilaAtila/C.A.R._Petrosani</a>"
        )
        github_label.setWordWrap(True)
        github_label.setTextFormat(Qt.RichText)
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet(f"padding: 10px; background: {P.PANEL_2}; border-radius: 6px; color: {P.MUTED}; margin-top: 10px;")
        general_layout.addWidget(github_label)

        self.content_layout.addWidget(general_frame)

        # Arhitectură dual-currency
        dual_frame = QFrame()
        dual_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        dual_layout = QVBoxLayout(dual_frame)

        dual_title = QLabel("<b>Arhitectură Dual-Currency (RON/EUR)</b>")
        dual_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        dual_title.setStyleSheet(f"color: {P.INK};")
        dual_layout.addWidget(dual_title)

        dual_info = """
        <b>Componente principale:</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>currency_logic.py:</b> Management stare conversie și validare permisiuni</li>
            <li><b>conversie_widget.py:</b> Widget aplicare conversie definitivă cu validări UE</li>
            <li><b>currency_toggle_widget.py:</b> Control toggle RON/EUR în bara principală</li>
            <li><b>main_ui.py (monkey patching):</b> Redirectare automată apeluri DB către baze corecte</li>
        </ul>

        <b>Strategia de protecție date:</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li>Bazele originale RON rămân intacte ca audit trail</li>
            <li>Conversie creează clone complete cu sufix EUR</li>
            <li>Modul RON post-conversie: DOAR CITIRE (protecție scriere)</li>
            <li>Modul EUR: Citire și scriere complete funcționale</li>
            <li>Toggle instant între moduri fără restart aplicație</li>
        </ul>

        <b>Validări matematice:</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li>ROUND_HALF_UP conform Regulamentul CE 1103/97</li>
            <li>Precizie 2 zecimale toate sumele EUR</li>
            <li>Toleranță maximă ±0.01 EUR la validare finală</li>
            <li>Verificare consistență sumă totală pre și post conversie</li>
        </ul>
        """
        dual_label = QLabel(dual_info)
        dual_label.setWordWrap(True)
        dual_label.setTextFormat(Qt.RichText)
        dual_label.setStyleSheet(f"color: {P.MUTED};")
        dual_layout.addWidget(dual_label)

        self.content_layout.addWidget(dual_frame)

        # Baze de date
        db_frame = QFrame()
        db_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {P.LINE};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        db_layout = QVBoxLayout(db_frame)

        db_title = QLabel("<b>Structură Baze de Date</b>")
        db_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        db_title.setStyleSheet(f"color: {P.INK};")
        db_layout.addWidget(db_title)

        db_info = """
        <b>Baze principale (RON + EUR post-conversie):</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>DEPCRED.db / DEPCREDEUR.db:</b> Tranzacții lunare - împrumuturi, rate, cotizații, solduri</li>
            <li><b>MEMBRII.db / MEMBRIIEUR.db:</b> Date identificare membri și cotizații standard</li>
            <li><b>activi.db / activiEUR.db:</b> Membri activi cu solduri depuneri, dividende, beneficii</li>
            <li><b>INACTIVI.db / INACTIVIEUR.db:</b> Membri inactivi și număr luni fără plată</li>
            <li><b>LICHIDATI.db / LICHIDATIEUR.db:</b> Istoric lichidări cu date finalizare</li>
        </ul>

        <b>Baze auxiliare (comune ambelor monede):</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>CHITANTE.db:</b> Numerotare secvențială chitanțe generate</li>
            <li><b>config_dobanda.json:</b> Rată dobândă configurabilă extern</li>
            <li><b>conversie_config.json:</b> Cursul RON/EUR și directorul bazelor de date</li>
            <li><b>dual_currency.json:</b> Status conversie (cheia <i>conversie_aplicata</i>)</li>
        </ul>
        """
        db_label = QLabel(db_info)
        db_label.setWordWrap(True)
        db_label.setTextFormat(Qt.RichText)
        db_label.setStyleSheet(f"color: {P.MUTED};")
        db_layout.addWidget(db_label)

        self.content_layout.addWidget(db_frame)

        self.content_layout.addStretch()


def test_despre_widget():
    """Funcție test pentru rulare standalone"""
    app = QApplication(sys.argv)
    dialog = DespreWidget()
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_despre_widget()