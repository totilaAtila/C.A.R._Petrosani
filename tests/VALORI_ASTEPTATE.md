# Valori așteptate — baze de date de test

Generat automat de `tests/genereaza_baze_test.py`. **Nu edita manual** —
rulează scriptul din nou dacă schimbi parametrii.

- Seed: `20260719` (date identice la fiecare rulare)
- Perioadă: 01/2023 → 11/2025
- Curs EUR: `4.9665` · Rată dobândă la stingere: `0.004`

> **La ce folosește:** după fiecare fișier restilizat, deschizi ecranul
> corespunzător și compari cu tabelele de mai jos. Orice diferență
> înseamnă că redesign-ul a atins logica → `git revert`.

---

## 1. Totaluri generale

| Indicator | Valoare |
|---|---:|
| Membri în MEMBRII | 200 |
| Înregistrări DEPCRED | 6531 |
| Membri lichidați | 10 |
| Membri inactivi | 10 |
| Rânduri ACTIVI (sold 12/2024) | 177 |
| Total depuneri (DEP_DEB, toată perioada) | 175,369.15 |
| Total retrageri (DEP_CRED) | 4,873.00 |
| Total împrumuturi acordate (IMPR_DEB) | 496,997.63 |
| Total rate încasate (IMPR_CRED) | 375,732.07 |
| Total dobânzi istorice (DOBANDA) | 6,537.25 |

## 2. Solduri la finalul fiecărui an

| An | Luna | Membri cu rând | Total DEP_SOLD | Total IMPR_SOLD |
|---|---|---:|---:|---:|
| 2023 | 12 | 188 | 60,036.28 | 122,821.26 |
| 2024 | 12 | 187 | 119,037.56 | 219,004.41 |
| 2025 | 11 | 180 | 161,671.15 | 121,265.56 |

## 3. Totaluri lunare 2025 (ecranul Vizualizare Lunară)

| Luna | Rânduri | DEP_DEB | DEP_SOLD | IMPR_CRED | IMPR_SOLD |
|---|---:|---:|---:|---:|---:|
| 01/2025 | 187 | 5,030.69 | 122,812.25 | 16,304.42 | 227,987.39 |
| 02/2025 | 187 | 5,010.69 | 127,122.94 | 17,077.03 | 231,389.40 |
| 03/2025 | 186 | 4,985.69 | 131,392.63 | 19,542.13 | 221,810.22 |
| 04/2025 | 181 | 4,825.69 | 131,842.32 | 18,980.71 | 226,979.51 |
| 05/2025 | 182 | 4,840.69 | 136,444.01 | 18,448.24 | 222,368.47 |
| 06/2025 | 181 | 4,810.69 | 140,214.70 | 20,198.24 | 216,570.23 |
| 07/2025 | 178 | 4,700.69 | 141,391.39 | 20,270.72 | 191,999.51 |
| 08/2025 | 180 | 4,790.69 | 148,314.08 | 19,296.17 | 177,003.34 |
| 09/2025 | 180 | 4,790.69 | 152,996.77 | 19,896.17 | 157,107.17 |
| 10/2025 | 180 | 4,790.69 | 157,358.46 | 18,196.17 | 138,911.00 |
| 11/2025 | 180 | 4,790.69 | 161,671.15 | 17,645.44 | 121,265.56 |

## 4. Profile de membri (unde găsești fiecare caz)

| Interval fișe | Profil | Ce testează |
|---|---|---|
| 1–120 | `NORMAL` | Depuneri regulate; ~60% au avut imprumut. |
| 121–140 | `ZECIMALE` | Cotizatii si rate cu banuti — stres pe rotunjire. |
| 141–155 | `LUNI_LIPSA` | 2-4 luni fara inregistrare — 'Lipsa date sursa'. |
| 156–165 | `FARA_TRANZACTII` | In MEMBRII, zero randuri in DEPCRED. |
| 166–180 | `ACHITARE_DEC` | Imprumut care se stinge la generarea lui 12/2025. |
| 181–190 | `LICHIDATI` | Au istoric, dar sunt in LICHIDATI.db (exclusi). |
| 191–200 | `INACTIVI` | In INACTIVI.db cu lipsa_luni. |

## 5. Fișe de control (verificabile la mână)

Ultima lună înregistrată pentru câțiva membri. Deschide fișa în aplicație
și compară exact aceste cifre.

| Fișa | Nume | Cotizație | DEP_SOLD 11/2025 | IMPR_SOLD 11/2025 | IMPR_CRED 11/2025 |
|---:|---|---:|---:|---:|---:|
| 1 | Pavel Bogdan | 25.00 | 875.00 | 0.00 | 0.00 |
| 2 | Constantin Elena | 15.00 | 525.00 | 0.00 | 0.00 |
| 3 | Ionescu Maria | 40.00 | 1,304.00 | 0.00 | 0.00 |
| 50 | Munteanu Carmen | 20.00 | 700.00 | 0.00 | 0.00 |
| 121 | Popa Ion | 32.71 | 1,144.85 | 0.00 | 0.00 |
| 122 | Toma Carmen | 38.68 | 1,353.80 | 0.00 | 0.00 |
| 166 | Constantin Dan | 30.00 | 1,050.00 | 300.00 | 300.00 |
| 167 | Ardelean Victor | 10.00 | 350.00 | 200.00 | 200.00 |
| 168 | Oprea Cristian | 20.00 | 700.00 | 150.00 | 150.00 |

## 6. Test cheie — Generare Lună 12/2025

Luna 12/2025 e lăsată **negenerată** intenționat. Rulează *Generare Lună*
în aplicație pentru 12/2025; rezultatul trebuie să fie exact:

| Indicator | Valoare așteptată |
|---|---:|
| Înregistrări generate | 170 |
| Membri omiși (lipsă date sursă) | 20 |
| Număr dobânzi calculate | 18 |
| Total dobânzi | 1,919.40 |
| Total DEP_SOLD după generare | 156,381.84 |

Dobânzile, pe fișe:

| Fișa | Nume | Dobândă |
|---:|---|---:|
| 30 | Barbu Dan | 167.20 |
| 48 | Radu Radu | 35.00 |
| 146 | Nistor Radu | 87.00 |
| 166 | Constantin Dan | 92.40 |
| 167 | Ardelean Victor | 95.20 |
| 168 | Oprea Cristian | 46.20 |
| 169 | Oprea Radu | 119.00 |
| 170 | Cojocaru Lucia | 108.00 |
| 171 | Vasilescu Carmen | 216.00 |
| 172 | Constantin Victor | 144.00 |
| 173 | Vasilescu Radu | 95.20 |
| 174 | Popescu Lucia | 32.40 |
| 175 | Oprea Adriana | 189.00 |
| 176 | Nistor Ana | 182.40 |
| 177 | Vasilescu Bogdan | 91.20 |
| 178 | Popescu Lucia | 35.20 |
| 179 | Pavel Sorin | 121.60 |
| 180 | Radu Adriana | 62.40 |

## 7. Regenerare

```bash
python tests/genereaza_baze_test.py --force
python tests/verifica_valori_asteptate.py
```
