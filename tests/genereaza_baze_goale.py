# -*- coding: utf-8 -*-
"""Genereaza setul de baze de date RON GOALE (schema, 0 randuri) pentru release.
Include MEMBRII.db gol (necesar la pornire — la prima rulare aplicatia il
arhiveaza in MEMBRII.zip cu parola aleasa de user). Fara variante EUR."""
import os, sqlite3, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "release_baze_goale"
os.makedirs(OUT, exist_ok=True)

# Scheme canonice (identice cu tests/genereaza_baze_test.py). RON, fara MEMBRII/EUR.
SCHEME = {
    "MEMBRII.db": """
        CREATE TABLE MEMBRII (
            NR_FISA INTEGER PRIMARY KEY, NUM_PREN TEXT NOT NULL, DOMICILIUL TEXT,
            CALITATEA TEXT, DATA_INSCR TEXT, COTIZATIE_STANDARD REAL DEFAULT 10.00
        )""",
    "DEPCRED.db": """
        CREATE TABLE DEPCRED (
            NR_FISA INTEGER NOT NULL, LUNA INTEGER NOT NULL, ANUL INTEGER NOT NULL,
            DOBANDA REAL DEFAULT 0.0, IMPR_DEB REAL DEFAULT 0.0, IMPR_CRED REAL DEFAULT 0.0,
            IMPR_SOLD REAL DEFAULT 0.0, DEP_DEB REAL DEFAULT 0.0, DEP_CRED REAL DEFAULT 0.0,
            DEP_SOLD REAL DEFAULT 0.0, PRIMA INTEGER DEFAULT 0,
            PRIMARY KEY (NR_FISA, LUNA, ANUL)
        )""",
    "ACTIVI.db": """
        CREATE TABLE ACTIVI (
            NR_FISA INTEGER PRIMARY KEY, NUM_PREN TEXT, DEP_SOLD REAL, DIVIDEND REAL DEFAULT 0.0
        )""",
    "INACTIVI.db": """
        CREATE TABLE inactivi (
            nr_fisa INTEGER PRIMARY KEY, num_pren TEXT, lipsa_luni INTEGER
        )""",
    "LICHIDATI.db": """
        CREATE TABLE lichidati (
            nr_fisa INTEGER PRIMARY KEY, data_lichidare TEXT NOT NULL
        )""",
    "CHITANTE.db": """
        CREATE TABLE CHITANTE (
            STARTCH_PR INTEGER, STARTCH_AC INTEGER
        )""",
}

for nume, ddl in SCHEME.items():
    cale = os.path.join(OUT, nume)
    if os.path.exists(cale):
        os.unlink(cale)
    conn = sqlite3.connect(cale)
    try:
        conn.execute(ddl)
        conn.commit()
    finally:
        conn.close()
    print(f"  creat gol: {nume}")

print(f"OK - {len(SCHEME)} baze RON goale in '{OUT}' (incl. MEMBRII gol, fara EUR)")
