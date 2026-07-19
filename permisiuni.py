# -*- coding: utf-8 -*-
"""
permisiuni.py — gardian central pentru permisiunile de SCRIERE în funcție de
starea monedei (RON/EUR).

De ce există:
    După conversia definitivă RON->EUR, bazele RON devin ISTORICE (doar-citire).
    În starea `post_conversion_ron` (toggle pe RON după conversie),
    `CurrencyLogic.can_write_data()` întoarce False. Modulele care modifică
    datele financiare (INSERT/UPDATE/DELETE în DEPCRED/MEMBRII/ACTIVI) apelează
    `poate_scrie()` ÎNAINTE de scriere și refuză cu mesaj dacă suntem în această
    stare. Vizualizarea (citirea) rămâne permisă în toate stările.

    Dezactivarea butoanelor de meniu NU e suficientă: un ecran deschis pe EUR și
    apoi comutat pe RON rămâne funcțional. De aceea blocarea se face la momentul
    scrierii, nu la nivel de navigare.

Cablare:
    CARApp (main_ui.py) înregistrează instanța LIVE de CurrencyLogic la pornire
    prin `set_currency_logic(...)`. Verificarea citește mereu starea curentă (nu
    o copie), deci reflectă corect toggle-ul RON/EUR fără repornire.

Fără înregistrare (ex. rularea standalone a unui widget în test), `poate_scrie()`
întoarce True — echivalent cu starea normală pre-conversie (readwrite).

NOTĂ: nu blochează CHITANTE.db (contoare de tipărire, bază neconvertită) — doar
scrierile în datele financiare, conform deciziei de proiectare.
"""

_currency_logic = None


def set_currency_logic(currency_logic):
    """Înregistrează instanța live de CurrencyLogic (apelat o dată de CARApp)."""
    global _currency_logic
    _currency_logic = currency_logic


def poate_scrie():
    """
    True dacă scrierea în datele financiare e permisă în starea curentă.
    False doar în `post_conversion_ron` (RON după conversie = doar-citire).
    """
    if _currency_logic is None:
        # Nefixat (test standalone al unui widget) -> comportament pre-conversie.
        return True
    try:
        return _currency_logic.can_write_data()
    except Exception:
        # get_current_permission() e logică pură; dacă totuși eșuează, nu blocăm
        # comportamentul normal (pre-conversia e readwrite).
        return True


MESAJ_READONLY = (
    "Mod doar-citire.\n\n"
    "După conversia în EUR, bazele de date RON sunt istorice și nu pot fi "
    "modificate. Comutați la EUR pentru operațiuni de scriere."
)
