# dialog_styles.py
"""
Stiluri centralizate pentru toate dialogurile aplicației CAR Petroșani.
Versiune redesign "Glass Verde Rafinat".

CARACTERISTICI:
- Toate culorile vin din ui/palette.py — niciun hex literal în acest fișier
- Fundal dialog: P.PANEL_2 (neutru discret)
- Text principal: P.INK — contrast optim
- Fundal text: P.PANEL (alb curat) cu chenar P.LINE
- Butoane: neutre; butonul implicit (:default) e singurul accent verde
- Padding generos pentru lizibilitate maximă

REDESIGN: s-au schimbat exclusiv valorile de stil.
Structura, numele, funcțiile și comportamentul rămân identice.
"""

# REDESIGN: sursa unică de stil. Doar aspect — nicio logică atinsă.
from ui.palette import P, GRAD, RADIUS, FONT

GLOBAL_DIALOG_STYLESHEET = f"""
/* ==================== QMessageBox ==================== */
QMessageBox {{
    background-color: {P.PANEL_2};
    color: {P.INK};
    font-family: {FONT};
    font-size: 10pt;
    min-width: 420px;
}}

/* Zona de text principală - FUNDAL ALB CURAT */
QMessageBox QLabel#qt_msgbox_label {{
    background-color: {P.PANEL};
    color: {P.INK};
    padding: 14px 18px;
    border: 1px solid {P.LINE};
    border-radius: {RADIUS.SM};
    font-size: 10pt;
    margin: 4px;
}}

/* Label-uri secundare (titluri, informații suplimentare) */
QMessageBox QLabel {{
    background-color: transparent;
    color: {P.INK};
    padding: 6px;
}}

/* Butoane - stil validari.py */
QMessageBox QPushButton {{
    background-color: {P.PANEL};
    color: {P.MUTED};
    border: 1px solid {P.LINE};
    padding: 9px 26px;
    border-radius: {RADIUS.SM};
    font-family: 'Segoe UI';
    font-size: 10pt;
    font-weight: normal;
}}

QMessageBox QPushButton:hover {{
    background-color: {P.ACCENT_SOFT};
    border-color: {P.ACCENT_LINE};
}}

QMessageBox QPushButton:pressed {{
    background-color: {P.ACCENT_PRESS};
    border-color: {P.ACCENT};
}}

QMessageBox QPushButton:focus {{
    outline: none;
    border: 1px solid {P.ACCENT};
}}

QMessageBox QPushButton:default {{
    border: 1px solid {P.ACCENT_DEEP};
    background: {GRAD.ACCENT};
    color: {P.WHITE};
}}

/* ==================== QDialog ==================== */
QDialog {{
    background-color: {P.PANEL_2};
    color: {P.INK};
    font-family: {FONT};
    font-size: 10pt;
}}

/* Text din dialoguri custom */
QDialog QLabel {{
    background-color: {P.PANEL};
    color: {P.INK};
    padding: 12px 16px;
    border: 1px solid {P.LINE};
    border-radius: {RADIUS.SM};
}}

QDialog QPushButton {{
    background-color: {P.PANEL};
    color: {P.MUTED};
    border: 1px solid {P.LINE};
    padding: 9px 26px;
    border-radius: {RADIUS.SM};
    font-family: 'Segoe UI';
    font-size: 10pt;
    font-weight: normal;
}}

QDialog QPushButton:hover {{
    background-color: {P.ACCENT_SOFT};
}}

QDialog QPushButton:pressed {{
    background-color: {P.ACCENT_PRESS};
}}

QDialog QPushButton:focus {{
    outline: none;
    border: 1px solid {P.ACCENT};
}}

QDialog QPushButton:disabled {{
    background-color: {P.PANEL_2};
    color: {P.FAINT};
    border-color: {P.LINE};
}}

/* ==================== QInputDialog ==================== */
QInputDialog {{
    background-color: {P.PANEL_2};
    color: {P.INK};
    font-family: {FONT};
    font-size: 10pt;
}}

QInputDialog QLabel {{
    background-color: {P.PANEL};
    color: {P.INK};
    padding: 10px 14px;
    border: 1px solid {P.LINE};
    border-radius: {RADIUS.SM};
    margin: 4px;
}}

QInputDialog QLineEdit,
QInputDialog QSpinBox,
QInputDialog QComboBox {{
    background-color: {P.PANEL};
    color: {P.INK};
    border: 1px solid {P.LINE};
    border-radius: {RADIUS.SM};
    padding: 6px 10px;
    font-size: 10pt;
}}

QInputDialog QLineEdit:focus,
QInputDialog QSpinBox:focus,
QInputDialog QComboBox:focus {{
    border-color: {P.ACCENT};
}}

QInputDialog QPushButton {{
    background-color: {P.PANEL};
    color: {P.MUTED};
    border: 1px solid {P.LINE};
    padding: 9px 26px;
    border-radius: {RADIUS.SM};
    font-family: 'Segoe UI';
    font-size: 10pt;
    font-weight: normal;
}}

QInputDialog QPushButton:hover {{
    background-color: {P.ACCENT_SOFT};
}}

/* ==================== QFileDialog ==================== */
QFileDialog {{
    background-color: {P.PANEL_2};
    color: {P.INK};
}}

QFileDialog QPushButton {{
    background-color: {P.PANEL};
    color: {P.MUTED};
    border: 1px solid {P.LINE};
    padding: 7px 20px;
    border-radius: {RADIUS.SM};
    font-family: 'Segoe UI';
    font-size: 10pt;
    font-weight: normal;
}}

QFileDialog QPushButton:hover {{
    background-color: {P.ACCENT_SOFT};
}}

QFileDialog QPushButton:pressed {{
    background-color: {P.ACCENT_PRESS};
}}

/* ==================== QDialogButtonBox ==================== */
QDialogButtonBox QPushButton {{
    background-color: {P.PANEL};
    color: {P.MUTED};
    border: 1px solid {P.LINE};
    padding: 9px 26px;
    border-radius: {RADIUS.SM};
    font-family: 'Segoe UI';
    font-size: 10pt;
    font-weight: normal;
}}

QDialogButtonBox QPushButton:hover {{
    background-color: {P.ACCENT_SOFT};
}}

QDialogButtonBox QPushButton:pressed {{
    background-color: {P.ACCENT_PRESS};
}}
"""


def apply_global_dialog_styles(app):
    """
    Aplică stilurile centralizate pentru dialoguri cu consistență completă fundal-text.

    CARACTERISTICI VERSIUNE REDESIGN:
    - Fundal text alb curat cu chenar discret (P.PANEL / P.LINE)
    - Culoare text definită explicit (P.INK) pentru toate elementele
    - Butoane neutre cu hover verde deschis; butonul implicit = accent verde
    - Padding generos pentru lizibilitate maximă
    - Consistență vizuală 100% în toată aplicația

    Args:
        app: Instanța QApplication

    Returns:
        bool: True dacă aplicarea a avut succes
    """
    try:
        current_stylesheet = app.styleSheet()

        if current_stylesheet:
            app.setStyleSheet(current_stylesheet + "\n\n" + GLOBAL_DIALOG_STYLESHEET)
        else:
            app.setStyleSheet(GLOBAL_DIALOG_STYLESHEET)

        print("[OK] Stiluri globale aplicate: consistenta completa fundal-text")
        return True

    except Exception as e:
        print(f"[ERROR] Eroare aplicare stiluri: {e}")
        return False


def get_dialog_stylesheet():
    """Returnează stylesheet-ul pentru utilizare directă."""
    return GLOBAL_DIALOG_STYLESHEET
