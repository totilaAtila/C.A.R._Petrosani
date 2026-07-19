#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostic_dimensiuni.py — află CARE widget impune dimensiunea minimă a ferestrei.

    python tests/diagnostic_dimensiuni.py

Rulează fără să deschidă ferestre (platforma Qt "offscreen").

DE CE:
Qt raportează la comutarea între module:
    QWindowsWindow::setGeometry: Unable to set geometry 1360x782 ...
    minimum size: 1344x782
Fereastra cere o înălțime minimă mai mare decât zona utilă a ecranului, deci
sistemul refuză, iar Qt reîncearcă la fiecare schimbare de modul.

Dimensiunea minimă a ferestrei = maximul minimelor copiilor. Scriptul
instanțiază fiecare widget și afișează minimul lui, ca să se vadă cine ridică
pragul — în loc să ghicim citind cod.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from PyQt5.QtWidgets import QApplication  # noqa: E402

# (etichetă, modul, clasă)
WIDGETURI = [
    ("Statistici",            "ui.statistici",              "StatisticiWidget"),
    ("Adaugare membru",       "ui.adaugare_membru",         "AdaugareMembruWidget"),
    ("Sume lunare",           "ui.sume_lunare",             "SumeLunareWidget"),
    ("Lichidare membru",      "ui.lichidare_membru",        "LichidareMembruWidget"),
    ("Stergere membru",       "ui.stergere_membru",         "StergereMembruWidget"),
    ("Dividende",             "ui.dividende",               "DividendeWidget"),
    ("Vizualizare lunara",    "ui.vizualizare_lunara",      "VizualizareLunaraWidget"),
    ("Vizualizare trim.",     "ui.vizualizare_trimestriala", "VizualizareTrimestrialaWidget"),
    ("Vizualizare anuala",    "ui.vizualizare_anuala",      "VizualizareAnualaWidget"),
    ("Verificare fise",       "ui.verificare_fise",         "VerificareFiseWidget"),
    ("Listari",               "ui.listari",                 "ListariWidget"),
    ("ListariEUR",            "ui.listariEUR",              "ListariEURWidget"),
    ("Generare luna",         "ui.generare_luna",           "GenerareLunaNouaWidget"),
    ("Calculator",            "ui.calculator",              "CalculatorWidget"),
    ("Despre / Versiune",     "ui.despre",                  "DespreWidget"),
    ("Salvari",               "ui.salvari",                 "OperatiuniSalvareWidget"),
    ("Optimizare index",      "ui.optimizare_index",        "OptimizareIndexWidget"),
    # Widget-uri din rădăcina proiectului, nu din ui/ — ușor de uitat la audit
    ("CAR DBF Converter",     "car_dbf_converter_widget",   "CARDBFConverterWidget"),
    ("Conversie RON->EUR",    "conversie_widget",           "ConversieWidget"),
]


def main():
    app = QApplication(sys.argv)

    ecran = app.primaryScreen()
    if ecran:
        g, d = ecran.geometry(), ecran.availableGeometry()
        print(f"Ecran: {g.width()}x{g.height()}  |  zona utila: {d.width()}x{d.height()}")
        limita = d.height()
    else:
        limita = 0
    print("Zona utila = ecran minus bara de activitati. Fereastra nu poate depasi asta.\n")

    print(f"{'Widget':<24}{'minimumSize':>14}{'minimumSizeHint':>18}   verdict")
    print("-" * 78)

    rezultate = []
    for eticheta, cale_modul, nume_clasa in WIDGETURI:
        try:
            modul = __import__(cale_modul, fromlist=[nume_clasa])
            clasa = getattr(modul, nume_clasa)
            w = clasa()
            mins = w.minimumSize()
            hint = w.minimumSizeHint()
            inaltime = max(mins.height(), hint.height())
            latime = max(mins.width(), hint.width())
            rezultate.append((eticheta, latime, inaltime))
            semn = ""
            if limita and inaltime > limita - 40:      # ~40px pentru chenarul ferestrei
                semn = "  <-- prea inalt"
            print(f"{eticheta:<24}{mins.width():>6}x{mins.height():<7}"
                  f"{hint.width():>9}x{hint.height():<8}{semn}")
            w.deleteLater()
        except Exception as e:
            print(f"{eticheta:<24}{'—':>14}{'—':>18}   nu a putut fi instantiat: {type(e).__name__}: {e}")

    if rezultate:
        print("-" * 78)
        cel_mai_lat = max(rezultate, key=lambda r: r[1])
        cel_mai_inalt = max(rezultate, key=lambda r: r[2])
        print(f"Cel mai lat  : {cel_mai_lat[0]} ({cel_mai_lat[1]} px)")
        print(f"Cel mai inalt: {cel_mai_inalt[0]} ({cel_mai_inalt[2]} px)")
        if limita and cel_mai_inalt[2] > limita - 40:
            print(f"\nAcesta e vinovatul: cere {cel_mai_inalt[2]} px inaltime, "
                  f"dar zona utila are {limita} px.")
            print("Fereastra nu poate cobori sub minimul copilului, deci Qt reincearca")
            print("la fiecare comutare de modul si scrie avertismentul.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
