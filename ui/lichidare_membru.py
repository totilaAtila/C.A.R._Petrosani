# lichidare_membru.py
import os
import sqlite3
import sys
import logging
from datetime import datetime

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox,
    QApplication, QMainWindow, QFrame, QGridLayout, QLineEdit, QScrollArea,
    QTextEdit, QSizePolicy, QCompleter, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont, QColor

if getattr(sys, 'frozen', False):
    BASE_RESOURCE_PATH = os.path.dirname(sys.executable)
else:
    BASE_RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Definim caile catre bazele de date relative la directorul de resurse
DB_MEMBRII = os.path.join(BASE_RESOURCE_PATH, "MEMBRII.db")
DB_DEPCRED = os.path.join(BASE_RESOURCE_PATH, "DEPCRED.db")
DB_ACTIVI = os.path.join(BASE_RESOURCE_PATH, "ACTIVI.db")
DB_INACTIVI = os.path.join(BASE_RESOURCE_PATH, "INACTIVI.db")
DB_CHITANTE = os.path.join(BASE_RESOURCE_PATH, "CHITANTE.db")
DB_LICHIDATI = os.path.join(BASE_RESOURCE_PATH, "LICHIDATI.db")

# Gardian scriere: blocheaza modificarile pe RON dupa conversie (doar-citire).
from permisiuni import poate_scrie, MESAJ_READONLY

# REDESIGN: sursa unică de stil (ui/palette.py). Doar aspect — nicio logică atinsă.
from ui.palette import P, GRAD, RADIUS, FONT, btn_solid

# Importăm DOAR funcțiile de validare/dialog necesare
try:
    from ui.validari import afiseaza_eroare, CustomDialogYesNo, afiseaza_info
except ImportError as e:
    msg = ("EROARE CRITICĂ: Nu s-au putut importa modulele necesare "
           f"din ui.validari.\nDetalii: {e}")
    print(msg)
    app = QApplication.instance()
    if app: QMessageBox.critical(None, "Eroare Import", msg)


    def afiseaza_eroare(mesaj: str, parent=None):
        QMessageBox.critical(parent, "Eroare", mesaj)


    def afiseaza_info(mesaj: str, parent=None):
        QMessageBox.information(parent, "Informație", mesaj)


    class CustomDialogYesNo(QMessageBox):
        def __init__(self, title: str, message: str, icon_path: str = None, parent=None):
            super().__init__(parent)
            self.setWindowTitle(title)
            self.setText(message)
            self.setIcon(QMessageBox.Question)
            self.da_buton = self.addButton("Da", QMessageBox.YesRole)
            self.nu_buton = self.addButton("Nu", QMessageBox.NoRole)
            self.setDefaultButton(self.nu_buton)

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Clasa SyncedTextEdit copiată din șablon
class SyncedTextEdit(QTextEdit):
    """ QTextEdit cu scroll sincronizat. """

    def __init__(self, siblings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.siblings = siblings

    def wheelEvent(self, event):
        scrollbar = self.verticalScrollBar()
        can_scroll = scrollbar.minimum() < scrollbar.maximum()
        if not can_scroll:
            super().wheelEvent(event)
            return
        old_val = scrollbar.value()
        super().wheelEvent(event)
        new_val = scrollbar.value()
        if new_val != old_val:
            for te in self.siblings:
                if te is not self:
                    bar = te.verticalScrollBar()
                    if bar.value() != new_val:
                        bar.setValue(new_val)


# Clasa principală - NU mai moștenește din șablon
class LichidareMembruWidget(QWidget):
    """ Widget pentru lichidarea unui membru CAR cu design modern 3D. """

    def __init__(self, parent=None):
        self._deja_lichidat = False
        super().__init__(parent)
        self._verificare_activa = False
        self._edit_mode = False
        self._loaded_nr_fisa = None
        self._coloane_financiare_widgets = []
        self._coloane_financiare_layout_map = {}

        # Apelăm direct metodele modernizate
        self._init_ui()
        self._apply_styles()
        self._connect_signals()
        # Adăugăm configurarea specifică lichidării DUPĂ UI-ul de bază
        self._setup_lichidare_ui()
        self._set_form_editable(False)
        self.reset_form()

        if self.parent() is None or isinstance(self.parentWidget(), QMainWindow):
            try:
                self.window().setWindowTitle("Lichidare Membru CAR")
            except AttributeError:
                pass

    def _set_form_editable(self, editable: bool):
        """ Activează/dezactivează câmpurile formularului. """
        self.txt_adresa.setReadOnly(not editable)
        self.txt_calitate.setReadOnly(not editable)
        self.txt_data_insc.setReadOnly(not editable)
        for widget in self._coloane_financiare_widgets:
            widget.setReadOnly(not editable)

    # --- Metode UI modernizate cu efecte 3D ---
    def _init_ui(self):
        """ Inițializează interfața cu design modern 3D. """
        self.lbl_lichidat = QLabel("⚠ MEMBRU LICHIDAT")
        self.lbl_lichidat.setStyleSheet(f"""
            QLabel {{
                color: {P.DANGER};
                font-weight: bold;
                font-size: 12pt;
                padding: 8px;
                background: {P.DANGER_SOFT};
                border: 1px solid {P.DANGER};
                border-radius: {RADIUS.SM};
                margin: 5px;
            }}
        """)
        self.lbl_lichidat.setAlignment(Qt.AlignCenter)
        self.lbl_lichidat.setVisible(False)

        # Aplicăm efect de umbră la eticheta de avertisment
        self._apply_shadow_effect(self.lbl_lichidat)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        self.main_layout.addWidget(self.lbl_lichidat)

        self._setup_header_frame()
        self._setup_scroll_area()
        self._setup_actions_area()

    def _setup_header_frame(self):
        """ Creează header-ul cu design modern 3D. """
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        header_layout = QGridLayout(self.header_frame)
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.setSpacing(12)

        self.lbl_nume = QLabel("Nume Prenume:")
        self.txt_nume = QLineEdit()
        self.txt_nume.setPlaceholderText("Căutare după nume...")
        self.txt_nume.setToolTip("Introduceți primele litere...")

        self.lbl_nr_fisa = QLabel("Număr Fișă:")
        self.txt_nr_fisa = QLineEdit()
        self.txt_nr_fisa.setPlaceholderText("Căutare după fișă...")
        self.txt_nr_fisa.setToolTip("Introduceți numărul fișei...")

        self.lbl_adresa = QLabel("Adresa:")
        self.txt_adresa = QLineEdit()
        self.txt_adresa.setReadOnly(True)

        self.lbl_calitate = QLabel("Calitatea:")
        self.txt_calitate = QLineEdit()
        self.txt_calitate.setReadOnly(True)

        self.lbl_data_insc = QLabel("Data înscrierii:")
        self.txt_data_insc = QLineEdit()
        self.txt_data_insc.setReadOnly(True)

        # Buton modern cu efecte 3D
        self.reset_button = QPushButton("Golește formular")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setToolTip("Resetează formularul")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setMinimumHeight(35)

        # Aplicăm efectul de umbră la buton
        self._apply_shadow_effect(self.reset_button)

        header_layout.addWidget(self.lbl_nume, 0, 0)
        header_layout.addWidget(self.txt_nume, 0, 1)
        header_layout.addWidget(self.lbl_nr_fisa, 0, 2)
        header_layout.addWidget(self.txt_nr_fisa, 0, 3)
        header_layout.addWidget(self.lbl_adresa, 1, 0)
        header_layout.addWidget(self.txt_adresa, 1, 1)
        header_layout.addWidget(self.lbl_data_insc, 1, 2)
        header_layout.addWidget(self.txt_data_insc, 1, 3)
        header_layout.addWidget(self.lbl_calitate, 2, 0)
        header_layout.addWidget(self.txt_calitate, 2, 1)
        # Spacer pentru a împinge butonul la dreapta
        header_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 2, 2
        )
        header_layout.addWidget(self.reset_button, 2, 3)

        header_layout.setColumnStretch(1, 2)
        header_layout.setColumnStretch(3, 1)
        self.main_layout.addWidget(self.header_frame)

        self._update_completer_flag = True
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.txt_nume.setCompleter(self.completer)

    def _setup_scroll_area(self):
        """ Creează zona de scroll cu design modern. """
        scroll_container = QWidget()
        scroll_hbox = QHBoxLayout(scroll_container)
        scroll_hbox.setContentsMargins(0, 0, 0, 0)
        scroll_hbox.setSpacing(8)

        self.columns_frame = QFrame()
        self.columns_frame.setObjectName("columns_frame")
        self.columns_frame.setStyleSheet(
            "QFrame#columns_frame { border: none; background-color: transparent; padding: 0px; }")
        columns_layout = QHBoxLayout(self.columns_frame)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(8)

        # Secțiunile cu design modern 3D
        self.loan_section = self._create_financial_section_frame("Situație Împrumuturi", None, None, None)
        self.date_section = self._create_financial_section_frame("Dată", None, None, None)
        self.deposit_section = self._create_financial_section_frame("Situație Depuneri", None, None, None)

        self.loan_columns_layout = QHBoxLayout()
        self.loan_columns_layout.setContentsMargins(0, 0, 0, 0)
        self.loan_columns_layout.setSpacing(2)
        self.date_columns_layout = QHBoxLayout()
        self.date_columns_layout.setContentsMargins(0, 0, 0, 0)
        self.date_columns_layout.setSpacing(2)
        self.deposit_columns_layout = QHBoxLayout()
        self.deposit_columns_layout.setContentsMargins(0, 0, 0, 0)
        self.deposit_columns_layout.setSpacing(2)

        self.loan_section.layout().addLayout(self.loan_columns_layout)
        self.date_section.layout().addLayout(self.date_columns_layout)
        self.deposit_section.layout().addLayout(self.deposit_columns_layout)

        columns_layout.addWidget(self.loan_section, stretch=4)
        columns_layout.addWidget(self.date_section, stretch=1)
        columns_layout.addWidget(self.deposit_section, stretch=3)
        scroll_hbox.addWidget(self.columns_frame)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_container)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(250)
        self.main_layout.addWidget(self.scroll_area, stretch=1)

    def _create_financial_section_frame(self, title, border_color, bg_color, header_bg_color):
        """ Creează secțiuni moderne cu efecte 3D complete. """
        section = QFrame()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(8, 8, 8, 8)
        section_layout.setSpacing(6)

        # Design MODERN 3D cu gradienți îmbunătățiți
        if "Împrumuturi" in title:
            section.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {P.DANGER};
                    border-radius: {RADIUS.LG};
                    background: {P.DANGER_SOFT};
                }}
            """)
        elif "Depuneri" in title:
            section.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {P.ACCENT_LINE};
                    border-radius: {RADIUS.LG};
                    background: {P.ACCENT_SOFT};
                }}
            """)
        else:  # Dată
            section.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {P.LINE};
                    border-radius: {RADIUS.LG};
                    background: {P.PANEL_2};
                }}
            """)

        # Header cu stiluri hardcodate EXACT ca în celelalte module
        lbl_header = QLabel(title)
        lbl_header.setAlignment(Qt.AlignCenter)
        lbl_header.setMinimumHeight(38)

        # 🎨 STILURI SPECIFICE HARDCODATE pentru fiecare secțiune
        if "Împrumuturi" in title:
            lbl_header.setStyleSheet(f"""
                QLabel {{
                    background: {P.DANGER};
                    border: 1px solid {P.DANGER_DEEP};
                    border-radius: {RADIUS.SM};
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 11pt;
                    color: {P.WHITE};
                    margin-bottom: 6px;
                }}
            """)
        elif "Depuneri" in title:
            lbl_header.setStyleSheet(f"""
                QLabel {{
                    background: {P.ACCENT};
                    border: 1px solid {P.ACCENT_DEEP};
                    border-radius: {RADIUS.SM};
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 11pt;
                    color: {P.WHITE};
                    margin-bottom: 6px;
                }}
            """)
        else:  # Dată
            lbl_header.setStyleSheet(f"""
                QLabel {{
                    background: {P.NEUTRAL};
                    border: 1px solid {P.NEUTRAL_DEEP};
                    border-radius: {RADIUS.SM};
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 11pt;
                    color: {P.WHITE};
                    margin-bottom: 6px;
                }}
            """)

        section_layout.addWidget(lbl_header)

        # Aplicăm efectele de umbră
        self._apply_shadow_effect(section)
        self._apply_header_shadow_effect(lbl_header)

        return section

    def _apply_shadow_effect(self, widget):
        """ Aplică efectul de umbră 3D la un widget. """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 40))
        widget.setGraphicsEffect(shadow)

    def _apply_header_shadow_effect(self, header_widget):
        """ Aplică efectul de umbră 3D PREMIUM la headerele secțiunilor. """
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(10)
        header_shadow.setOffset(0, 3)
        header_shadow.setColor(QColor(0, 0, 0, 60))
        header_widget.setGraphicsEffect(header_shadow)

    def _setup_actions_area(self):
        """ Creează frame-ul pentru acțiuni. """
        self.actions_frame = QFrame()
        self.actions_layout = QHBoxLayout(self.actions_frame)
        self.actions_layout.setContentsMargins(0, 5, 0, 0)
        self.actions_layout.addStretch(1)
        self.actions_layout.addStretch(1)
        self.main_layout.addWidget(self.actions_frame)

    def _apply_styles(self):
        """ Aplică stilurile moderne cu efecte 3D. """
        general_styles = f"""
            /* fundal pe CLASA, nu pe 'QWidget' bare: altfel se propaga in
               QMessageBox-urile copil si suprascrie tema globala de dialog. */
            LichidareMembruWidget {{
                background: {GRAD.APP_BG};
            }}
            QWidget {{
                font-family: {FONT};
                font-size: 10pt;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none; background: {P.LINE_SOFT}; width: 12px;
                margin: 0; border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {P.ACCENT_LINE}; min-height: 20px;
                border-radius: 6px; margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {P.ACCENT}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none; background: none; height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none; background: {P.LINE_SOFT}; height: 12px;
                margin: 0; border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {P.ACCENT_LINE}; min-width: 20px;
                border-radius: 6px; margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: {P.ACCENT}; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none; background: none; width: 0px;
            }}
            QLineEdit {{
                background-color: {P.PANEL_2};
                border: 1px solid {P.LINE};
                border-radius: {RADIUS.MD};
                padding: 6px 10px;
                min-height: 23px;
                font-size: 10pt;
            }}
            QLineEdit:focus {{ border-color: {P.ACCENT}; }}
            QLineEdit:read-only {{
                background-color: {P.PANEL_2};
                color: {P.FAINT};
                border-color: {P.LINE};
            }}
            QLabel {{
                color: {P.MUTED};
                padding-bottom: 2px;
                font-weight: bold;
            }}
        """

        header_styles = f"""
            QFrame#header_frame {{
                background: {P.PANEL};
                border: 1px solid {P.LINE};
                border-radius: {RADIUS.LG};
                padding: 10px 15px;
            }}
            QFrame#header_frame QLabel {{
                font-weight: bold;
                padding-bottom: 0px;
                background: none;
                border: none;
                color: {P.MUTED};
            }}
        """

        reset_button_styles = (
            btn_solid(P.DANGER, P.DANGER_DEEP, "QPushButton#reset_button")
            + btn_solid(P.WARNING, P.WARNING_DEEP, "QPushButton#buton_lichideaza")
            + f"""
            QPushButton#reset_button {{
                font-size: 10pt; font-weight: bold; padding: 8px 16px; min-width: 140px;
            }}
            QPushButton#buton_lichideaza {{
                font-size: 10pt; font-weight: bold; padding: 8px 16px; min-width: 160px;
            }}
            QPushButton#buton_lichideaza:disabled {{
                background-color: {P.DISABLED};
                color: {P.DISABLED_TEXT};
                border-color: {P.DISABLED};
            }}
            """
        )

        self.setStyleSheet(general_styles + header_styles + reset_button_styles)
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        self.header_frame.setStyleSheet(header_styles)

    def _connect_signals(self):
        """ Conectează semnalele. """
        self.txt_nume.textChanged.connect(self._update_completer_model)
        self.completer.activated[str].connect(self._handle_name_selected)
        self.completer.highlighted.connect(lambda: setattr(self, '_update_completer_flag', False))
        self.txt_nume.editingFinished.connect(self._handle_name_finished)
        self.txt_nr_fisa.editingFinished.connect(self._handle_fisa_entered)
        self.reset_button.clicked.connect(self.reset_form)

    def _add_financial_column(self, section_layout, column_name, title, add_label=True, read_only=True):
        """ Creează coloană financiară cu design modern. """
        text_edit = SyncedTextEdit(siblings=self._coloane_financiare_widgets)
        text_edit.setReadOnly(read_only)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        text_edit.setFont(font)
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {P.LINE};
                border-top: none;
                border-radius: 0px;
                border-bottom-left-radius: {RADIUS.SM};
                border-bottom-right-radius: {RADIUS.SM};
                padding: 6px;
                background-color: {P.PANEL};
                color: {P.INK};
                selection-background-color: {P.ACCENT_SOFT};
            }}
            QTextEdit:read-only {{
                background-color: {P.PANEL_2};
                color: {P.FAINT};
            }}
            QTextEdit:focus {{
                border-color: {P.ACCENT};
                background-color: {P.PANEL};
            }}
        """)

        label = None
        layout = QVBoxLayout()
        layout.setSpacing(0)
        if add_label:
            label = QLabel(title)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedHeight(32)
            label.setStyleSheet(f"""
                QLabel {{
                    background: {P.PANEL_2};
                    border: 1px solid {P.LINE};
                    border-bottom: none;
                    border-top-left-radius: {RADIUS.SM};
                    border-top-right-radius: {RADIUS.SM};
                    padding: 6px;
                    font-weight: bold;
                    font-size: 9pt;
                    color: {P.MUTED};
                }}
            """)
            layout.addWidget(label)
        layout.addWidget(text_edit, stretch=1)

        section_layout.addLayout(layout)
        column_data = {"layout": layout, "label": label, "text_edit": text_edit}
        self._coloane_financiare_layout_map[column_name] = column_data
        self._coloane_financiare_widgets.append(text_edit)
        return column_data

    def showEvent(self, event):
        """ Setează focusul la afișare. """
        print(f"{self.__class__.__name__} afișat. Se setează focusul.")
        target = self.txt_nr_fisa if self.txt_nr_fisa.isEnabled() else self.txt_nume
        QtCore.QTimer.singleShot(0, lambda: target.setFocus())
        super(LichidareMembruWidget, self).showEvent(event)

    def hideEvent(self, event):
        """ Resetează la ascundere. """
        print(f"{self.__class__.__name__} ascuns. Se resetează formularul.")
        self.reset_form()
        super(LichidareMembruWidget, self).hideEvent(event)

    def _handle_name_selected(self, selected_name):
        """ Gestionează selectarea numelui. """
        print(f"Nume selectat din completer: {selected_name}")
        self._load_member_data(name=selected_name)

    def _handle_name_finished(self):
        """ Gestionează finalizarea editării numelui. """
        if not self._update_completer_flag:
            self._update_completer_flag = True
            return
        entered_name = self.txt_nume.text().strip()
        if not entered_name:
            return
        current_completion = self.completer.currentCompletion()
        if current_completion and current_completion.upper() == entered_name.upper():
            print(f"Nume confirmat prin Enter/Focus Lost: {current_completion}")
            self._load_member_data(name=current_completion)
        else:
            print(f"Nume introdus '{entered_name}' nu corespunde sugestiei '{current_completion}'. Ignorat.")
        self._update_completer_flag = True

    def _handle_fisa_entered(self):
        """ Gestionează introducerea nr. fișă. """
        nr_fisa_str = self.txt_nr_fisa.text().strip()
        if nr_fisa_str.isdigit():
            print(f"Nr. Fișă introdus: {nr_fisa_str}")
            self._load_member_data(nr_fisa=int(nr_fisa_str))
        elif nr_fisa_str:
            afiseaza_warning("Numărul fișei trebuie să fie numeric.", parent=self)
            self.txt_nr_fisa.selectAll()
            self.txt_nr_fisa.setFocus()

    def reincarca_valuta(self):
        """Re-afișează datele fișei curente în noua valută (bazele re-patchuite)."""
        if self._loaded_nr_fisa is not None:
            self._load_member_data(nr_fisa=self._loaded_nr_fisa)

    def _load_member_data(self, nr_fisa=None, name=None):
        """ Metodă centrală pentru încărcarea datelor unui membru. """
        if self._verificare_activa:
            return
        self._verificare_activa = True
        self._loaded_nr_fisa = None

        target_nr_fisa = nr_fisa
        target_name = name

        try:
            if target_nr_fisa is None and target_name:
                target_nr_fisa = self._get_nr_fisa_for_name(target_name)
                if not target_nr_fisa:
                    afiseaza_info(f"Membrul '{target_name}' nu a fost găsit.", parent=self)
                    self.reset_form()
                    return
                if self.txt_nume.text() != target_name:
                    self.txt_nume.setText(target_name)
                self.txt_nr_fisa.setText(str(target_nr_fisa))
                member_data_temp = self._get_member_data_from_membrii(target_nr_fisa)
            elif target_nr_fisa is not None:
                member_data_temp = self._get_member_data_from_membrii(target_nr_fisa)
                if not member_data_temp:
                    liquidation_date = self._check_if_liquidated(target_nr_fisa)
                    if liquidation_date:
                        afiseaza_info(f"Membrul cu fișa {target_nr_fisa} a fost lichidat la data {liquidation_date}.",
                                      parent=self)
                    else:
                        afiseaza_info(f"Fișa cu numărul {target_nr_fisa} nu există în baza de date.", parent=self)
                    self.reset_form()
                    return
                target_name = member_data_temp.get("NUM_PREN", "")
                self.txt_nume.setText(target_name)
                self.txt_nr_fisa.setText(str(target_nr_fisa))
            else:
                return

            liquidation_date = self._check_if_liquidated(target_nr_fisa)
            if liquidation_date:
                self._deja_lichidat = True
                afiseaza_info(
                    f"Membrul '{target_name}' (fișa {target_nr_fisa}) a fost lichidat la data {liquidation_date}.",
                    parent=self)
                self.txt_nume.setText(target_name)
                self.txt_nume.setEnabled(False)
                self.txt_nr_fisa.setText(str(target_nr_fisa))
                self.txt_nr_fisa.setEnabled(False)
                self._loaded_nr_fisa = target_nr_fisa
                self.txt_adresa.setText(member_data_temp.get("DOMICILIUL", ""))
                self.txt_calitate.setText(member_data_temp.get("CALITATEA", ""))
                self.txt_data_insc.setText(member_data_temp.get("DATA_INSCR", ""))
                self._set_form_editable(False)
                self._setup_module_actions()
                self._populate_financial_data(self._loaded_nr_fisa)
                if hasattr(self, 'lbl_lichidat'):
                    self.lbl_lichidat.setVisible(True)
                return

            self._loaded_nr_fisa = target_nr_fisa
            print(f"Încărcare date pentru fișa: {self._loaded_nr_fisa}, Nume: {target_name}")
            member_data = self._get_member_data_from_membrii(self._loaded_nr_fisa)
            if member_data:
                self.txt_adresa.setText(member_data.get("DOMICILIUL", ""))
                self.txt_calitate.setText(member_data.get("CALITATEA", ""))
                self.txt_data_insc.setText(member_data.get("DATA_INSCR", ""))
                self.txt_adresa.setToolTip(member_data.get("DOMICILIUL", ""))
                self.txt_calitate.setToolTip(member_data.get("CALITATEA", ""))
                self.txt_data_insc.setToolTip(member_data.get("DATA_INSCR", ""))
                self.txt_nr_fisa.setToolTip(str(self._loaded_nr_fisa))
            else:
                afiseaza_eroare(f"Datele pentru fișa {self._loaded_nr_fisa} nu au putut fi recuperate.", parent=self)
                self.reset_form()
                return

            self._populate_financial_data(self._loaded_nr_fisa)
            self._set_form_editable(False)
            self.txt_nume.setEnabled(False)
            self.txt_nr_fisa.setEnabled(False)
            self._setup_module_actions()
        except Exception as e:
            logging.error(f"Eroare în _load_member_data: {e}", exc_info=True)
            afiseaza_eroare(f"A apărut o eroare la încărcarea datelor:\n{str(e)}", parent=self)
            self.reset_form()
        finally:
            self._verificare_activa = False
            self._update_completer_flag = True

    def _populate_financial_data(self, nr_fisa):
        """ Încarcă datele financiare standard din DEPCRED. """
        print(f"Populare date financiare standard pentru fișa {nr_fisa}...")
        for widget in self._coloane_financiare_widgets:
            widget.clear()
        depcred_data = self._get_member_details(nr_fisa)
        if not depcred_data:
            print(f"Nu există intrări DEPCRED pentru fișa {nr_fisa}")
            return
        lines = {cd["text_edit"]: [] for cd in self._coloane_financiare_layout_map.values()}
        idx_to_col_name = {0: 'dobanda', 1: 'impr_deb', 2: 'impr_cred', 3: 'impr_sold', 6: 'dep_deb', 7: 'dep_cred',
                           8: 'dep_sold'}
        for row in depcred_data:
            for idx, col_name in idx_to_col_name.items():
                if col_name in self._coloane_financiare_layout_map:
                    widget = self._coloane_financiare_layout_map[col_name]["text_edit"]
                    lines[widget].append(f"{row[idx] or 0.0:.2f}")
            if 'luna_an' in self._coloane_financiare_layout_map:
                luna, anul = row[4], row[5]
                luna_an_val = f"{luna:02d}-{anul}" if luna and anul else "??-????"
                widget = self._coloane_financiare_layout_map['luna_an']["text_edit"]
                lines[widget].append(luna_an_val)
        for widget, line_list in lines.items():
            widget.setText("\n".join(line_list))
        for te in self._coloane_financiare_widgets:
            te.verticalScrollBar().setValue(te.verticalScrollBar().minimum())

    def _update_completer_model(self):
        """ Actualizează modelul pentru completer. """
        if not self._update_completer_flag:
            return

        prefix = self.txt_nume.text().strip()
        if len(prefix) < 2:
            self.completer.setModel(None)
            return

        try:
            conn = sqlite3.connect(DB_MEMBRII, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT num_pren FROM membrii WHERE num_pren LIKE ? COLLATE NOCASE ORDER BY num_pren",
                (prefix + "%",)
            )
            names = [row[0] for row in cursor.fetchall()]
            model = QStringListModel(names)
            self.completer.setModel(model)
            if names and self.txt_nume.hasFocus() and not self.completer.popup().isVisible():
                self.completer.complete()
        except Exception as e:
            print(f"Eroare completare nume: {e}")
        finally:
            if conn:
                conn.close()

    # --- Metode Statice DB ---
    @staticmethod
    def _get_names_starting_with(prefix):
        results = {}
        conn = None
        try:
            conn = sqlite3.connect(DB_MEMBRII, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT NR_FISA, NUM_PREN FROM membrii WHERE NUM_PREN LIKE ? COLLATE NOCASE ORDER BY NUM_PREN",
                (prefix + '%',))
            results = {row[1]: row[0] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            print(f"Eroare SQLite la _get_names_starting_with: {e}")
        finally:
            if conn:
                conn.close()
        return results

    @staticmethod
    def _get_nr_fisa_for_name(name):
        if not name:
            return None
        conn = None
        nr_fisa_result = None
        try:
            conn = sqlite3.connect(DB_MEMBRII, timeout=30.0)
            cur = conn.cursor()
            cur.execute("SELECT NR_FISA FROM membrii WHERE NUM_PREN = ? COLLATE NOCASE", (name,))
            row = cur.fetchone()
            if row:
                nr_fisa_result = row[0]
        except sqlite3.Error as e:
            print(f"Eroare SQLite la _get_nr_fisa_for_name: {e}")
        finally:
            if conn:
                conn.close()
        return nr_fisa_result

    @staticmethod
    def _get_member_data_from_membrii(nr_fisa):
        if not nr_fisa:
            return None
        conn = None
        member_data_result = None
        try:
            conn = sqlite3.connect(DB_MEMBRII, timeout=30.0)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT NR_FISA, NUM_PREN, CALITATEA, DOMICILIUL, DATA_INSCR FROM membrii WHERE NR_FISA = ?",
                        (nr_fisa,))
            row = cur.fetchone()
            if row:
                member_data_result = dict(row)
        except sqlite3.Error as e:
            print(f"Eroare SQLite la _get_member_data_from_membrii: {e}")
        finally:
            if conn:
                conn.close()
        return member_data_result

    @staticmethod
    def _get_member_details(nr_fisa):
        if not nr_fisa:
            return []
        data = []
        conn = None
        try:
            conn = sqlite3.connect(DB_DEPCRED, timeout=30.0)
            cur = conn.cursor()
            cur.execute(
                "SELECT DOBANDA, IMPR_DEB, IMPR_CRED, IMPR_SOLD, LUNA, ANUL, DEP_DEB, DEP_CRED, DEP_SOLD, PRIMA FROM depcred WHERE NR_FISA = ? ORDER BY ANUL DESC, LUNA DESC",
                (nr_fisa,))
            data = cur.fetchall()
        except sqlite3.Error as e:
            print(f"Eroare SQLite la _get_member_details: {e}")
        finally:
            if conn:
                conn.close()
        return data

    @staticmethod
    def _check_if_liquidated(nr_fisa):
        if not nr_fisa:
            return None
        conn = None
        liquidation_date = None
        try:
            conn = sqlite3.connect(DB_LICHIDATI)
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS lichidati (nr_fisa INTEGER PRIMARY KEY, data_lichidare TEXT NOT NULL)")
            cursor.execute("SELECT data_lichidare FROM lichidati WHERE nr_fisa = ?", (nr_fisa,))
            result = cursor.fetchone()
            if result:
                liquidation_date = result[0]
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la verificarea lichidării pt {nr_fisa}: {e}")
        except Exception as e:
            logging.error(f"Eroare generală la verificarea lichidării pt {nr_fisa}: {e}")
        finally:
            if conn:
                conn.close()
        return liquidation_date

    def reset_form(self):
        """ Resetează formularul la starea inițială. """
        self._deja_lichidat = False
        if hasattr(self, 'lbl_lichidat'):
            self.lbl_lichidat.setVisible(False)
        print(f"Resetare formular {self.__class__.__name__}...")
        self._loaded_nr_fisa = None
        self.txt_nume.clear()
        self.txt_adresa.clear()
        self.txt_calitate.clear()
        self.txt_data_insc.clear()
        self.txt_nr_fisa.clear()
        self.txt_nume.setToolTip("Introduceți primele litere...")
        self.txt_nr_fisa.setToolTip("Introduceți numărul fișei...")
        self.txt_adresa.setToolTip("")
        self.txt_calitate.setToolTip("")
        self.txt_data_insc.setToolTip("")
        for widget in self._coloane_financiare_widgets:
            widget.clear()
        self.completer.setModel(None)
        self._set_form_editable(False)
        self.txt_nume.setEnabled(True)
        self.txt_nr_fisa.setEnabled(True)
        self._setup_module_actions()
        self._update_completer_flag = True
        self._verificare_activa = False
        target_focus = self.txt_nr_fisa
        QtCore.QTimer.singleShot(0, lambda: target_focus.setFocus())

    # --- Metode Specifice Lichidării ---
    def _setup_lichidare_ui(self):
        """ Adaugă coloanele financiare specifice lichidării. """
        self._add_financial_column(self.loan_columns_layout, 'dobanda', 'Dobândă', read_only=True)
        self._add_financial_column(self.loan_columns_layout, 'impr_deb', 'Împrumut', read_only=True)
        self._add_financial_column(self.loan_columns_layout, 'impr_cred', 'Rată Achitată', read_only=True)
        self._add_financial_column(self.loan_columns_layout, 'impr_sold', 'Sold Împrumut', read_only=True)
        self._add_financial_column(self.date_columns_layout, 'luna_an', 'Luna-An', read_only=True)
        self._add_financial_column(self.deposit_columns_layout, 'dep_deb', 'Cotizație', read_only=True)
        self._add_financial_column(self.deposit_columns_layout, 'dep_cred', 'Retragere Fond', read_only=True)
        self._add_financial_column(self.deposit_columns_layout, 'dep_sold', 'Sold Depunere', read_only=True)
        for te in self._coloane_financiare_widgets:
            te.siblings = self._coloane_financiare_widgets

    def _setup_module_actions(self):
        """ Adaugă butoanele și controalele specifice lichidării. """
        # Curățăm întâi layout-ul de acțiuni
        while self.actions_layout.count() > 2:
            item = self.actions_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                item.layout().deleteLater()

        if self._loaded_nr_fisa is not None and not self._deja_lichidat:
            self.checkbox_resetare = QCheckBox("Setează soldurile finale (împrumut/depunere) la 0")
            self.checkbox_resetare.setChecked(True)
            self.checkbox_resetare.setStyleSheet(f"""
                QCheckBox {{
                    margin-left: 5px;
                    font-weight: bold;
                    color: {P.INK};
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {P.ACCENT};
                    border: 1px solid {P.ACCENT};
                    border-radius: 3px;
                }}
                QCheckBox::indicator:unchecked {{
                    background-color: {P.PANEL};
                    border: 1px solid {P.FAINT};
                    border-radius: 3px;
                }}
            """)

            self.buton_lichideaza = QPushButton("⚠️ Lichidează Membrul")
            self.buton_lichideaza.setObjectName("buton_lichideaza")
            self.buton_lichideaza.setMinimumHeight(35)
            self.buton_lichideaza.setCursor(Qt.PointingHandCursor)
            self.buton_lichideaza.clicked.connect(self._perform_lichidare)

            # Aplicăm efect de umbră la butonul de lichidare
            self._apply_shadow_effect(self.buton_lichideaza)

            h_layout = QHBoxLayout()
            h_layout.addStretch(1)
            h_layout.addWidget(self.checkbox_resetare)
            h_layout.addWidget(self.buton_lichideaza)
            h_layout.addStretch(1)
            self.actions_layout.insertLayout(1, h_layout)

    def _perform_lichidare(self):
        """ Logica executată la apăsarea butonului 'Lichidează Membrul'. """
        if not poate_scrie():
            QMessageBox.warning(self, "Mod doar-citire", MESAJ_READONLY)
            return
        if self._loaded_nr_fisa is None:
            afiseaza_eroare("Nu este selectat niciun membru pentru lichidare.", parent=self)
            return
        nr_fisa = self._loaded_nr_fisa
        nume = self.txt_nume.text()

        dialog = CustomDialogYesNo(
            title="⚠️ Confirmare Lichidare",
            message=(
                f"Sunteți sigur că doriți să marcați membrul:\n\n"
                f"📁 Fișa: {nr_fisa}\n"
                f"👤 Nume: {nume}\n\n"
                f"ca LICHIDAT?\n\n"
                f"Această acțiune va înregistra lichidarea și, opțional,\n"
                f"va seta soldurile finale la zero."
            ),
            parent=self
        )
        result = dialog.exec_()
        if dialog.clickedButton() == dialog.nu_buton:
            logging.info("Lichidare anulată.")
            return

        conn_dep = None
        conn_lich = None
        success = True
        error_msg = ""

        try:
            if self.checkbox_resetare.isChecked():
                logging.info(f"Resetare solduri pentru fișa {nr_fisa}...")
                conn_dep = sqlite3.connect(DB_DEPCRED)
                cursor_dep = conn_dep.cursor()
                cursor_dep.execute(
                    "SELECT luna, anul FROM depcred WHERE nr_fisa = ? ORDER BY anul DESC, luna DESC LIMIT 1",
                    (nr_fisa,))
                latest_period = cursor_dep.fetchone()
                if latest_period:
                    latest_luna, latest_anul = latest_period
                    cursor_dep.execute(
                        "UPDATE depcred SET impr_sold = 0, dep_sold = 0 WHERE nr_fisa = ? AND luna = ? AND anul = ?",
                        (nr_fisa, latest_luna, latest_anul))
                    logging.info(f"Solduri resetate pentru fișa {nr_fisa}, luna {latest_luna}-{latest_anul}.")
                    conn_dep.commit()
                    logging.info("Commit resetare solduri efectuat.")
                else:
                    logging.warning(f"Nu s-au găsit înregistrări DEPCRED pentru fișa {nr_fisa}.")

            logging.info(f"Adăugare fișă {nr_fisa} în LICHIDATI.db...")
            conn_lich = sqlite3.connect(DB_LICHIDATI)
            cursor_lich = conn_lich.cursor()
            cursor_lich.execute(
                "CREATE TABLE IF NOT EXISTS lichidati (nr_fisa INTEGER PRIMARY KEY, data_lichidare TEXT NOT NULL)")
            data_curenta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                cursor_lich.execute("INSERT INTO lichidati (nr_fisa, data_lichidare) VALUES (?, ?)",
                                    (nr_fisa, data_curenta))
                logging.info(f"Fișa {nr_fisa} inserată în lichidati.")
            except sqlite3.IntegrityError:
                cursor_lich.execute("UPDATE lichidati SET data_lichidare = ? WHERE nr_fisa = ?",
                                    (data_curenta, nr_fisa))
                logging.info(f"Fișa {nr_fisa} exista deja. Data actualizată.")
            conn_lich.commit()
            logging.info("Commit adăugare/actualizare lichidati efectuat.")
        except sqlite3.Error as e:
            success = False
            error_msg = f"Eroare SQLite: {e}"
            logging.error(f"EROARE SQLite în _perform_lichidare: {e}", exc_info=True)
        except Exception as e:
            success = False
            error_msg = f"Eroare neașteptată: {e}"
            logging.error(f"EROARE Generală în _perform_lichidare: {e}", exc_info=True)
        finally:
            if conn_dep:
                conn_dep.close()
            if conn_lich:
                conn_lich.close()

        if success:
            afiseaza_info(f"✅ Membrul {nume} (fișa {nr_fisa}) a fost marcat ca lichidat.", parent=self)
            self.reset_form()
        else:
            afiseaza_eroare(f"❌ Lichidarea nu a putut fi finalizată.\n{error_msg}", parent=self)


# =========================================
# Testare directă (dacă e necesar)
# =========================================
if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window.setWindowTitle("Test Lichidare Membru CAR - Design Modern 3D")
    main_window.setGeometry(100, 100, 1000, 700)

    widget = LichidareMembruWidget()
    main_window.setCentralWidget(widget)
    main_window.show()

    sys.exit(app.exec_())