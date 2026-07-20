<h1 align="center">C.A.R. Petroșani</h1>

<p align="center">
  <b>Aplicație desktop pentru gestiunea unei Case de Ajutor Reciproc (C.A.R.)</b><br>
  Membri &middot; cotizații &middot; împrumuturi &middot; dobânzi &middot; dividende &middot; chitanțe &middot; conversie definitivă RON&nbsp;→&nbsp;EUR
</p>

<p align="center">
  <a href="https://github.com/totilaAtila/C.A.R._Petrosani/releases/latest"><img alt="Descarcă" src="https://img.shields.io/badge/%E2%AC%87%20Desc%C4%83rc%C4%83%20aplica%C8%9Bia-Windows%20(.zip)-1f8a5b?style=for-the-badge"></a>
</p>

<p align="center">
  <img alt="Licență MIT" src="https://img.shields.io/badge/Licen%C8%9B%C4%83-MIT-blue">
  <img alt="Platformă" src="https://img.shields.io/badge/Platform%C4%83-Windows%2010%2F11-informational">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB">
  <img alt="Versiune" src="https://img.shields.io/badge/Versiune-3.2.0%20%C2%B7%20Glass%20Verde-1f8a5b">
</p>

---

## ⬇️ Descărcare

> **[➜ Descarcă ultima versiune pentru Windows (.zip)](https://github.com/totilaAtila/C.A.R._Petrosani/releases/latest)**

1. Descarcă arhiva `.zip` din pagina de [**Releases**](https://github.com/totilaAtila/C.A.R._Petrosani/releases/latest).
2. Dezarhiveaz-o într-un folder al tău (ex. `C:\CAR`).
3. Rulează **`CARpetrosani.exe`** din folder.

Nu ai nevoie de Python sau de alte instalări — **toate dependințele sunt incluse** în arhivă. La prima pornire, Windows SmartScreen poate afișa un avertisment pentru o aplicație nesemnată: apasă *„Informații suplimentare” → „Executare oricum”*.

---

## ⚠️ IMPORTANT — bazele de date livrate sunt **GOALE**

> **Arhiva conține baze de date RON complet GOALE (fără niciun membru).** Ele trebuie **populate** de tine, prin aplicație (adăugare membri, cotizații, împrumuturi, generare lună etc.). Este comportamentul intenționat — nicio dată reală nu este distribuită.
>
> - **Nu** este inclus fișierul `MEMBRII.zip`. La **prima rulare**, aplicația detectează absența lui și îți oferă crearea bazei de membri + setarea unei **parole** proprii (criptare AES‑256).
> - **Nu** sunt incluse bazele în EUR — ele se obțin ulterior, din aplicație, prin **conversia definitivă RON → EUR**.

---

## 📸 Capturi de ecran

| Statistici (tablou de bord) | Generare lună | Salvări / Backup |
|---|---|---|
| ![Statistici](docs/screenshots/statistici.png) | ![Generare lună](docs/screenshots/generare-luna.png) | ![Salvări](docs/screenshots/salvari.png) |

---

## ✨ Ce face aplicația

- **Membri** — adăugare, actualizare, ștergere, lichidare; istoric complet pe fișă.
- **Sume lunare** — cotizații (depuneri), retrageri din fond, împrumuturi, rate, cu recalcul automat al lunilor ulterioare.
- **Împrumuturi** — acordare, rate, sold, cu instrument ajutător de căutare.
- **Dobândă la stingere** — calculată o singură dată, la achitarea completă a împrumutului (rată configurabilă în ‰).
- **Dividende** — calcul anual pe baza soldurilor și transfer în Ianuarie anul următor.
- **Generare lună** — rostogolirea automată a soldurilor pentru o lună nouă, cu validări de integritate.
- **Vizualizări & listări** — situații lunare / trimestriale / anuale, verificare fișe, chitanțe PDF.
- **Export Excel** securizat (xlsxwriter) și **rapoarte PDF** (reportlab).
- **Sistem dual RON / EUR** — conversie definitivă la cursul fix, cu **arhivă RON doar‑citire** după conversie și comutare live RON/EUR în orice ecran.
- **Backup / restaurare** baze, verificare integritate, optimizare indexuri, conversie DBF.
- **Temă vizuală „Glass Verde Rafinat"** — interfață curată, consistentă, cu selector de teme.

---

## 🚀 Rulare din surse (pentru dezvoltatori)

```bash
git clone https://github.com/totilaAtila/C.A.R._Petrosani.git
cd C.A.R._Petrosani

# (recomandat) mediu virtual
python -m venv venv
venv\Scripts\activate            # Windows

pip install -r requirements.txt
python main.py
```

Necesită **Python 3.11+**. Bazele de date RON goale se pot regenera oricând:

```bash
python tests/genereaza_baze_goale.py        # baze RON goale, fara MEMBRII/EUR
```

---

## 🧪 Teste

Suită de teste automate (calcule financiare, precizie `Decimal`, securitate export):

```bash
pip install -r requirements-dev.txt
pytest -q                                   # 66 de teste
```

Detalii în [`tests/README_TESTS.md`](tests/README_TESTS.md).

---

## 🛠️ Tehnologii

`Python 3.11` · `PyQt5` · `SQLite` · `reportlab` (PDF) · `xlsxwriter` (Excel) · `pyzipper` (AES‑256) · `dbf` · `PyInstaller` (build).

---

## 🔒 Securitate & precizie

- **Criptare AES‑256** a bazei de membri (`pyzipper`), cu parolă aleasă de utilizator.
- **Export Excel prin `xlsxwriter`** (migrare de la openpyxl) — elimină CVE‑2023‑43810 (XXE) și CVE‑2024‑47204 (ReDoS).
- **Precizie financiară cu `Decimal`** peste tot — fără erori de rotunjire.

---

## 📄 Licență

Distribuit sub licența **MIT** — vezi [`LICENSE`](LICENSE).
