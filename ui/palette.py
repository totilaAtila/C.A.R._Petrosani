# -*- coding: utf-8 -*-
"""
palette.py — SURSA UNICĂ DE ADEVĂR pentru stilul aplicației C.A.R. Petroșani.
Redesign "Glass Verde Rafinat".

REGULĂ: niciun fișier UI nu mai scrie culori hex literale (#28a745, #17a2b8...).
Toate importă de aici:  from ui.palette import P, GRAD, RADIUS, btn_primary, ...

Acest fișier conține DOAR valori de stil. Nu are logică de business,
nu atinge baze de date, nu importă module de calcul. Modificarea lui
schimbă doar aspectul, niciodată rezultatele contabile.
"""

# ----------------------------------------------------------------------------
# 1. PALETA DE BAZĂ  (o singură familie, accent verde + neutrale slate)
# ----------------------------------------------------------------------------
class P:
    # Accent (verde) — folosit pentru acțiuni primare, activ, pozitiv
    ACCENT        = "#1f8a5b"   # verde principal
    ACCENT_DEEP   = "#14663f"   # verde închis (hover / gradient jos)
    ACCENT_SOFT   = "#e9f5ee"   # verde foarte deschis (fundal subtil)
    ACCENT_LINE   = "#bfe3ce"   # bordură verde discretă
    ACCENT_PRESS  = "#dceee4"   # verde pal, starea "apăsat"

    # Neutrale (slate verzui) — text, fundaluri, linii
    INK           = "#152219"   # text principal (aproape negru, cald)
    MUTED         = "#5c6b62"   # text secundar
    FAINT         = "#8a978f"   # text terțiar / etichete
    LINE          = "#e3e8ec"   # bordură standard
    LINE_SOFT     = "#eef2f5"   # bordură foarte discretă (rânduri tabel)
    PANEL         = "#ffffff"   # fundal card / suprafață
    PANEL_2       = "#f6f8fa"   # fundal secundar (header tabel, input)
    BG            = "#e9edf1"   # fundal aplicație

    # Semantice — păstrează sensul, dar armonizate cu accentul
    POSITIVE      = "#1f8a5b"   # verde (intrări, achitat)
    INFO          = "#2f7dc4"   # albastru calm (membri, informativ)
    WARNING       = "#c47d1e"   # chihlimbar (restanțe, atenție)
    DANGER        = "#c0473b"   # roșu cărămiziu (împrumuturi, ștergere)
    NEUTRAL       = "#6b7a72"   # gri-verzui (secundar)

    # Variante inchise ale semanticelor — pentru :hover / :pressed pe butoane
    # pline. Fara ele, fiecare fisier si-ar inventa propria nuanta si consistenta
    # s-ar pierde exact acolo unde se vede cel mai tare.
    INFO_DEEP     = "#245f96"
    WARNING_DEEP  = "#9a6117"
    DANGER_DEEP   = "#97372d"
    NEUTRAL_DEEP  = "#545f59"

    WARNING_SOFT  = "#fbf1df"
    WARNING_LINE  = "#ecd9b3"
    DANGER_SOFT   = "#f7e9e7"

    # Starea dezactivata — token propriu, ca sa NU se confunde cu NEUTRAL.
    # Un buton gri activ si unul dezactivat trebuie sa arate diferit; codul vechi
    # folosea aceeasi valoare (#95a5a6) pentru ambele.
    DISABLED      = "#b9c6bf"
    DISABLED_TEXT = "#eef2f0"

    WHITE         = "#ffffff"

# ----------------------------------------------------------------------------
# 2. GRADIENTURI  (folosite DISCRET — doar accent primar, titlu, elemente active)
#    Semi-transparența grea din vechea temă a fost eliminată intenționat.
# ----------------------------------------------------------------------------
class GRAD:
    # gradient verde pentru butoane primare / header / elemente active
    ACCENT = ("qlineargradient(x1:0, y1:0, x2:0, y2:1, "
              "stop:0 #24996a, stop:1 #14663f)")
    ACCENT_HOVER = ("qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                    "stop:0 #2aa876, stop:1 #17754a)")
    # fundal aplicație — foarte subtil, aproape plat
    APP_BG = ("qlineargradient(x1:0, y1:0, x2:0, y2:1, "
              "stop:0 #eef2f5, stop:1 #e6ebef)")

# ----------------------------------------------------------------------------
# 3. GEOMETRIE  (o singură scală — consistentă în toată aplicația)
# ----------------------------------------------------------------------------
class RADIUS:
    SM = "6px"
    MD = "9px"
    LG = "12px"
    PILL = "999px"

class SPACE:
    XS = "4px"
    SM = "8px"
    MD = "12px"
    LG = "16px"

FONT = "'Segoe UI', Arial, sans-serif"   # păstrează compatibilitatea diacriticelor

# ----------------------------------------------------------------------------
# 4. FABRICI DE STIL  (QSS gata de folosit — o singură definiție per tip)
# ----------------------------------------------------------------------------
def btn_primary():
    """Buton acțiune principală — verde, plin."""
    return f"""
        QPushButton {{
            background: {GRAD.ACCENT};
            color: {P.WHITE};
            border: none;
            border-radius: {RADIUS.MD};
            padding: 9px 16px;
            font-family: {FONT};
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover  {{ background: {GRAD.ACCENT_HOVER}; }}
        QPushButton:pressed{{ background: {P.ACCENT_DEEP}; }}
        QPushButton:disabled{{ background: {P.DISABLED}; color: {P.DISABLED_TEXT}; }}
    """

def btn_secondary():
    """Buton secundar — neutru, contur."""
    return f"""
        QPushButton {{
            background: {P.PANEL_2};
            color: {P.MUTED};
            border: 1px solid {P.LINE};
            border-radius: {RADIUS.MD};
            padding: 9px 16px;
            font-family: {FONT};
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover  {{ background: {P.LINE_SOFT}; color: {P.INK}; }}
        QPushButton:pressed{{ background: {P.BG}; }}
    """

def btn_soft(accent=None):
    """Buton terțiar — accent deschis (ex. 'Vezi tot', 'Export')."""
    a = accent or P.ACCENT_DEEP
    return f"""
        QPushButton {{
            background: {P.ACCENT_SOFT};
            color: {a};
            border: 1px solid {P.ACCENT_LINE};
            border-radius: {RADIUS.SM};
            padding: 7px 12px;
            font-family: {FONT};
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background: {P.ACCENT_PRESS}; }}
    """

def btn_solid(base, deep, selector="QPushButton"):
    """
    Buton plin intr-o culoare semantica (operator, avertisment, stergere...).
    Foloseste-l cu perechile din P: (P.INFO, P.INFO_DEEP), (P.DANGER, P.DANGER_DEEP),
    (P.WARNING, P.WARNING_DEEP), (P.NEUTRAL, P.NEUTRAL_DEEP).

    'selector' permite tintirea unui objectName fara a-l modifica, ex:
        btn_solid(P.DANGER, P.DANGER_DEEP, "QPushButton#operatorButton")
    """
    return f"""
        {selector} {{
            background-color: {base};
            color: {P.WHITE};
            border: 1px solid {deep};
            border-radius: {RADIUS.SM};
            font-weight: bold;
        }}
        {selector}:hover   {{ background-color: {deep}; }}
        {selector}:pressed {{ background-color: {deep}; border-color: {base}; }}
    """


def card(hover_accent=None):
    """Suprafață card — alb curat, bordură fină, colț consistent."""
    hover = f"QGroupBox:hover {{ border: 1px solid {hover_accent}; }}" if hover_accent else ""
    return f"""
        QGroupBox {{
            background: {P.PANEL};
            border: 1px solid {P.LINE};
            border-radius: {RADIUS.LG};
        }}
        {hover}
    """

def table():
    """
    Tabel financiar — dens, lizibil, cifre la dreapta prin delegat/align în cod.

    ATENȚIE, REGULĂ VERIFICATĂ EXPERIMENTAL:
    NU pune niciodată `color:` pe `QTableWidget::item`. O astfel de regulă
    ANULEAZĂ `item.setForeground(...)` pus din cod, iar aplicația folosește
    exact acest mecanism ca să scrie cu roșu 'NEACHITAT' în vizualizările
    lunare/trimestriale/anuale — semnalul după care se vede dintr-o privire
    cine nu și-a plătit rata sau cotizația.

    Măsurat prin randare efectivă, numărând pixelii roșii:
        fără stylesheet                  116 px roșii   textul e roșu
        color: pe QTableWidget::item       0 px roșii   ROȘUL DISPARE
        această fabrică (color pe widget) 103 px roșii  textul e roșu

    De aceea `color:` e setat aici pe QTableWidget, nu pe ::item.
    """
    return f"""
        QTableWidget, QTableView {{
            background: {P.PANEL};
            alternate-background-color: {P.PANEL_2};
            gridline-color: {P.LINE_SOFT};
            border: 1px solid {P.LINE};
            border-radius: {RADIUS.LG};
            font-family: {FONT};
            font-size: 12px;
            color: {P.INK};
        }}
        QHeaderView::section {{
            background: {P.PANEL_2};
            color: {P.FAINT};
            border: none;
            border-bottom: 1px solid {P.LINE};
            padding: 8px 12px;
            font-weight: bold;
            font-size: 11px;
        }}
        QTableWidget::item:selected, QTableView::item:selected {{
            background: {P.ACCENT_SOFT};
            color: {P.INK};
        }}
    """

def header_bar():
    """Bara de titlu a ecranului — verde, accent unic pe pagină."""
    return f"""
        QFrame {{
            background: {GRAD.ACCENT};
            border-radius: {RADIUS.LG};
        }}
    """

def input_field():
    return f"""
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background: {P.PANEL_2};
            border: 1px solid {P.LINE};
            border-radius: {RADIUS.MD};
            padding: 8px 11px;
            font-family: {FONT};
            font-size: 13px;
            color: {P.INK};
        }}
        QLineEdit:focus, QComboBox:focus,
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {P.ACCENT};
        }}
    """
