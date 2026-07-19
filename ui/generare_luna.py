# generare_luna.py
"""
Modul pentru generarea lunilor noi într-o aplicație CAR (Casa de Ajutor Reciproc).
Include gestionarea cotizațiilor standard, a ratelor de împrumut moștenite din luna
anterioară și funcționalități adiacente.
"""

import sys
import sqlite3
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import os

# Importuri PyQt5
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QTextEdit, QApplication, QInputDialog, QComboBox, QDialog,
    QDialogButtonBox, QListWidget, QListWidgetItem, QAbstractItemView,
    QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QMetaObject, Q_ARG, QObject, pyqtSignal
from typing import Optional, Callable
from pathlib import Path
from utils import afiseaza_warning, afiseaza_eroare, afiseaza_info, afiseaza_intrebare
from permisiuni import poate_scrie, MESAJ_READONLY  # gardian scriere post-conversie RON
import json


# Import utilitare
try:
    from utils import attach_qt_logger, run_task_in_background, WorkerSignals
except ImportError as import_err:
    logging.error(f"Eroare import utils: {import_err} - se folosește fallback.")


    class WorkerSignals(QObject):
        """Semnale disponibile de la un worker thread."""
        finished = pyqtSignal()
        error = pyqtSignal(tuple)
        progress = pyqtSignal(str)


    def run_task_in_background(*args, **kwargs):
        """Fallback simplu pentru threading."""
        parent = args[0] if args else kwargs.get('parent_widget')
        if parent and isinstance(parent, QWidget):
            QMessageBox.critical(
                parent, "Eroare Configurare",
                "Modulul 'utils.py' lipsește sau e incomplet! Threading indisponibil."
            )
        raise RuntimeError("Threading indisponibil")

# --- Constante Globale ---
if getattr(sys, 'frozen', False):
    BASE_PATH = Path(sys.executable).parent
else:
    BASE_PATH = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
)

logging.info(f"Resurse încărcate din: {BASE_PATH}")

DB_MEMBRII = BASE_PATH / "MEMBRII.db"
DB_DEPCRED = BASE_PATH / "DEPCRED.db"
DB_LICHIDATI = BASE_PATH / "LICHIDATI.db"
DB_ACTIVI = BASE_PATH / "ACTIVI.db"
DB_INACTIVI = BASE_PATH / "INACTIVI.db"

for db_path in (DB_MEMBRII, DB_DEPCRED, DB_LICHIDATI):
    if not db_path.exists():
        logging.warning(f"Fișier DB lipsă: {db_path}")

MONTH_NAMES = {
    1: "Ianuarie", 2: "Februarie", 3: "Martie", 4: "Aprilie",
    5: "Mai", 6: "Iunie", 7: "Iulie", 8: "August",
    9: "Septembrie", 10: "Octombrie", 11: "Noiembrie", 12: "Decembrie"
}


class NealocateDialog(QDialog):
    """Dialog pentru afișarea numerelor de fișă nealocate."""

    def __init__(self, numere_nealocate, min_fisa, max_fisa, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Numere de Fișă Nealocate")
        self.setMinimumSize(450, 550)
        self.setStyleSheet("""
            QDialog { background-color: #eef2f7; }
            QLabel { font-size: 10pt; padding-bottom: 5px; }
            QListWidget { border: 1px solid #cccccc; border-radius: 3px; background-color: white; font-size: 10pt; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #d0e0f0; color: black; }
            QPushButton { padding: 6px 12px; border-radius: 4px; background-color: #e0e0e0;
                          border: 1px solid #adadad; font-weight: bold; min-width: 80px; }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        layout = QVBoxLayout(self)
        info_text = (f"Intervalul numerelor de fișă verificate: <b>{min_fisa} - {max_fisa}</b><br>"
                     f"Numere de fișă nealocate găsite în acest interval: <b>{len(numere_nealocate)}</b>")
        self.lbl_info = QLabel(info_text)
        layout.addWidget(self.lbl_info)
        self.list_widget = QListWidget()
        if numere_nealocate:
            self.list_widget.addItems([str(n) for n in numere_nealocate])
        else:
            item = QListWidgetItem("Nu s-au găsit numere nealocate.")
            item.setForeground(Qt.gray)
            self.list_widget.addItem(item)
            self.list_widget.setEnabled(False)
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.list_widget)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        layout.addWidget(self.button_box)


class GenerareLunaNouaWidget(QWidget):
    """Widget principal pentru generarea lunilor noi și funcții asociate."""

    # Semnale worker disponibile
    worker_signals = WorkerSignals()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generare Lună Nouă CAR")

        # Variabile de stare
        self._current_month = 0
        self._current_year = 0
        self._target_month = 0
        self._target_year = 0
        self._is_running = False
        self.loan_interest_rate_on_extinction = Decimal("0.004")
        self._load_interest_rate_config()
        self._dbs_missing = []

        # Construim UI și conectăm logger-ul
        self._check_essential_dbs()
        self._init_ui()
        try:
            attach_qt_logger(self.status_text)
        except Exception as e:
            logging.error(f"Eroare la atașarea logger-ului Qt: {e}")
        self._apply_styles()
        self._connect_signals()
        # Starea inițială
        if not self._dbs_missing:
            self._load_current_period()
        else:
            # Afișare eroare DB lipsă
            missing_dbs_str = ", ".join(self._dbs_missing)
            self.current_period_label.setText(f"Ultima lună: EROARE (Lipsă DB: {missing_dbs_str})")
            self.next_period_label.setText("Se va genera: -")
            self.status_text.setPlaceholderText(
                f"Eroare: Bazele de date {missing_dbs_str} nu au fost găsite în {BASE_PATH}!"
            )
            self._set_buttons_enabled_state(False)
            # Afișăm mesajul critic după ce UI-ul e gata (folosind QTimer)
            QTimer.singleShot(0, lambda: afiseaza_eroare(
                f"Următoarele baze de date esențiale nu au fost găsite:\n"
                f"- {missing_dbs_str}\n\n"
                f"Verificați dacă fișierele există în:\n{BASE_PATH}\n\n"
                "Funcționalitatea este limitată.",
                self
            ))

    def _check_essential_dbs(self):
        """Verifică existența fișierelor DB esențiale."""
        self._dbs_missing = []
        all_ok = True
        for db_path in (DB_MEMBRII, DB_DEPCRED, DB_LICHIDATI):
            if not os.path.exists(db_path):
                db_name = os.path.basename(db_path)
                self._dbs_missing.append(db_name)
                logging.error(f"Baza de date LIPSA: {db_path}")
                all_ok = False
        return all_ok


    def _load_interest_rate_config(self):
        """Încarcă rata dobânzii din fișierul de configurare."""
        config_path = os.path.join(BASE_PATH, "config_dobanda.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if 'loan_interest_rate_on_extinction' in config:
                        rate = Decimal(str(config['loan_interest_rate_on_extinction']))
                        self.loan_interest_rate_on_extinction = rate
                        logging.info(f"Rată dobândă încărcată din config: {rate}")
                        return True
        except (json.JSONDecodeError, IOError, KeyError, InvalidOperation) as e:
            logging.error(f"Eroare la încărcarea configurației dobânzii: {e}")
        return False

    def _save_interest_rate_config(self):
        """Salvează rata dobânzii în fișierul de configurare."""
        config_path = os.path.join(BASE_PATH, "config_dobanda.json")
        try:
            config = {'loan_interest_rate_on_extinction': str(self.loan_interest_rate_on_extinction)}
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            logging.info(f"Rată dobândă salvată în config: {self.loan_interest_rate_on_extinction}")
            return True
        except (IOError, TypeError) as e:
            logging.error(f"Eroare la salvarea configurației dobânzii: {e}")
            return False

    def _get_inherited_loan_rate(self, cursor_d, nr_fisa, source_period_val):
        """
        Preia rata de împrumut plătită (impr_cred) de membru exact în luna anterioară.

        BUG #6 FIX: Logică clarificată pentru moștenire rată împrumut:

        Cazuri tratate:
        1. Nu există date în luna anterioară → rata = 0.00 (membru nou sau reîntors după lichidare)
        2. Există împrumut nou (impr_deb > 0) → rata = 0.00 (împrumut proaspăt contractat)
        3. Există date dar fără împrumut nou → moștenește rata din luna anterioară

        Notă: Membrii lichidați sunt excluși complet din generare (vezi BUG #5),
        deci acest caz nu ar trebui să apară. Totuși, dacă un membru e re-activat
        (șters din LICHIDATI.db), va fi tratat ca membru nou (caz 1).
        """
        source_year = source_period_val // 100
        source_month = source_period_val % 100
        rate_paid = Decimal("0.00")

        try:
            # Extrage datele din luna anterioară
            cursor_d.execute(
                "SELECT impr_deb, impr_cred, impr_sold FROM depcred WHERE nr_fisa = ? AND anul = ? AND luna = ?",
                (nr_fisa, source_year, source_month)
            )
            result = cursor_d.fetchone()

            if not result:
                # CAZ 1: Nu există date în luna anterioară
                # Poate fi membru nou SAU membru re-activat după lichidare
                logging.info(
                    f"ℹ️ INFO: Membru fără istoric în luna {source_month:02d}-{source_year} pentru fișa {nr_fisa}. "
                    f"Posibil membru nou sau re-activat după lichidare. Rata inițializată la 0.00."
                )
                return rate_paid  # Returnează 0.00

            # Verificăm dacă există împrumut nou în luna anterioară
            impr_deb = Decimal(str(result[0] or '0.00'))
            impr_sold_anterior = Decimal(str(result[2] or '0.00'))

            if impr_deb > Decimal('0.00'):
                # CAZ 2: Împrumut nou contractat în luna anterioară
                # Rata se inițializează la 0 pentru că e un împrumut proaspăt
                logging.info(
                    f"ℹ️ INFO: Împrumut nou ({impr_deb:.2f}) în luna {source_month:02d}-{source_year} pentru fișa {nr_fisa}. "
                    f"Rata inițializată la 0.00 (împrumut proaspăt contractat)."
                )
                return Decimal("0.00")

            # CAZ 3: Moștenire normală - preia rata din luna anterioară
            if result[1] is not None:
                try:
                    rate_paid = Decimal(str(result[1] or '0.00')).quantize(Decimal("0.01"), ROUND_HALF_UP)
                    # Afișăm doar rate > 0 pentru a urmări împrumuturi active
                    if rate_paid > Decimal("0.00"):
                        logging.info(
                            f"ℹ️ INFO: Rată moștenită pentru fișa {nr_fisa}: {rate_paid:.2f} "
                            f"(sold anterior: {impr_sold_anterior:.2f})"
                        )
                except InvalidOperation:
                    logging.warning(
                        f"⚠️ ATENȚIE: Valoare impr_cred ('{result[1]}') invalidă în luna sursă {source_month:02d}-{source_year} "
                        f"pt fișa {nr_fisa}. Se va folosi 0.00."
                    )
                    rate_paid = Decimal("0.00")
        except sqlite3.Error as e_sql:
            logging.error(f"Eroare SQLite extragere rată plătită sursă pt fișa {nr_fisa}: {e_sql}", exc_info=True)
            rate_paid = Decimal("0.00")
        except Exception as e:
            logging.error(f"Eroare generală extragere rată plătită sursă pt fișa {nr_fisa}: {e}", exc_info=True)
            rate_paid = Decimal("0.00")

        return rate_paid

    # --- Metodele UI, Semnale, Handlers ---

    def _init_ui(self):
        """Inițializează componentele interfeței grafice."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Layout butoane extra (sus)
        extra_buttons_layout = QHBoxLayout()
        extra_buttons_layout.setSpacing(6)
        self.btn_update_inactivi = QPushButton("Numere de fișă nealocate")
        self.btn_afiseaza_inactivi = QPushButton("Afișează membri lichidați")
        self.btn_afiseaza_activi = QPushButton("Afișează membri activi")
        self.btn_export_log = QPushButton("Exportă rezumat")
        self.btn_clear_log = QPushButton("Șterge log")
        extra_buttons_layout.addWidget(self.btn_update_inactivi)
        extra_buttons_layout.addWidget(self.btn_afiseaza_inactivi)
        extra_buttons_layout.addWidget(self.btn_afiseaza_activi)
        extra_buttons_layout.addStretch()
        extra_buttons_layout.addWidget(self.btn_export_log)
        extra_buttons_layout.addWidget(self.btn_clear_log)
        layout.addLayout(extra_buttons_layout)

        # Layout informații perioadă
        info_layout = QHBoxLayout()
        self.current_period_label = QLabel("Ultima lună: Necunoscută")
        self.current_period_label.setObjectName("lblCurrentPeriod")
        self.next_period_label = QLabel("Următoarea lună (implicit): Necunoscută")
        self.next_period_label.setObjectName("lblNextPeriod")
        self.current_rate_label = QLabel(
            f"Rata dobândă lichidare: {self.loan_interest_rate_on_extinction * 1000:.1f} ‰")
        self.current_rate_label.setObjectName("lblCurrentRate")
        info_layout.addWidget(self.current_period_label)
        info_layout.addStretch()
        info_layout.addWidget(self.next_period_label)
        info_layout.addStretch()
        info_layout.addWidget(self.current_rate_label)
        layout.addLayout(info_layout)

        # Layout acțiuni principale
        action_layout = QHBoxLayout()
        self.lblSelectMonth = QLabel("Selectați luna pentru acțiune:")
        self.lblSelectMonth.setObjectName("lblSelectMonthForAction")
        action_layout.addWidget(self.lblSelectMonth)

        self.month_selector = QComboBox()
        self.month_selector.setObjectName("cmbMonthSelector")
        for i in range(1, 13):
            self.month_selector.addItem(f"{i:02d} - {MONTH_NAMES.get(i, 'N/A')}", userData=i)

        self.generate_button = QPushButton("Generează Lună Selectată")
        self.btn_delete_month = QPushButton("Șterge Lună Selectată")  # Buton redenumit
        self.modify_rate_button = QPushButton("Modifică Rata Dobândă")

        action_layout.addWidget(self.month_selector)
        action_layout.addWidget(self.generate_button)
        action_layout.addWidget(self.btn_delete_month)  # Buton adăugat
        action_layout.addStretch()
        action_layout.addWidget(self.modify_rate_button)
        layout.addLayout(action_layout)

        # Zona de status/log
        self.status_text = QTextEdit()
        self.status_text.setObjectName("txtStatusLog")
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText("Selectați luna și apăsați butonul de generare sau ștergere...")
        layout.addWidget(self.status_text, 1)

        # Setăm starea inițială a butoanelor
        self._set_buttons_enabled_state(not self._dbs_missing)

    def _apply_styles(self):
        """Aplică stiluri CSS și setează objectName-uri pentru stilizare."""
        self.setStyleSheet("""
            /* ... (CSS complet aici, inclusiv stilul pentru #btnDeleteSelectedMonth) ... */
            QWidget { background-color: #f0f4f8; font-family: Arial, sans-serif; font-size: 10pt; }
            QLabel { color: #333333; padding-bottom: 1px; }
            QLabel#lblCurrentPeriod, QLabel#lblNextPeriod, QLabel#lblCurrentRate { font-weight: bold; }
            QTextEdit#txtStatusLog { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 4px; padding: 6px;
                                     font-family: Consolas, monospace; font-size: 9pt; color: #333; }
            QComboBox#cmbMonthSelector { border: 1px solid #cccccc; border-radius: 4px; padding: 5px; min-height: 24px; background-color: white; }
            QComboBox#cmbMonthSelector::drop-down { border: none; }
            /* QComboBox#cmbMonthSelector::down-arrow { image: url(down_arrow.png); width: 14px; height: 14px; } */
            QComboBox#cmbMonthSelector:disabled { background-color: #f0f0f0; color: #888888; }
            QPushButton { padding: 6px 12px; border-radius: 4px; min-height: 30px; font-weight: bold;
                          border: 1px solid #adadad; background-color: #e0e0e0; color: #333; }
            QPushButton:hover { background-color: #d0d0d0; }
            QPushButton:pressed { background-color: #c0c0c0; }
            QPushButton:!enabled { background-color: #e0e0e0; border-color: #c0c0c0; color: #888888; }
            QPushButton#generate_button { background-color: #28a745; color: white; border-color: #1e7e34; }
            QPushButton#generate_button:hover { background-color: #218838; }
            QPushButton#generate_button:pressed { background-color: #1e7e34; }
            QPushButton#modify_rate_button { background-color: #ffc107; color: black; border-color: #d39e00; }
            QPushButton#modify_rate_button:hover { background-color: #e0a800; }
            QPushButton#modify_rate_button:pressed { background-color: #d39e00; }
            QPushButton#btnDeleteSelectedMonth { background-color: #dc3545; color: white; border-color: #bd2130; }
            QPushButton#btnDeleteSelectedMonth:hover { background-color: #c82333; }
            QPushButton#btnDeleteSelectedMonth:pressed { background-color: #bd2130; }
            QPushButton#btnDeleteSelectedMonth:!enabled { background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }
            QPushButton#btn_update_inactivi, QPushButton#btn_afiseaza_inactivi, QPushButton#btn_afiseaza_activi,
            QPushButton#btn_export_log, QPushButton#btn_clear_log {
                background-color: #6c757d; color: white; border-color: #5a6268; padding: 4px 8px;
                font-size: 9pt; min-height: 28px; font-weight: normal;
            }
            QPushButton#btn_update_inactivi:hover, QPushButton#btn_afiseaza_inactivi:hover, QPushButton#btn_afiseaza_activi:hover,
            QPushButton#btn_export_log:hover, QPushButton#btn_clear_log:hover { background-color: #5a6268; }
        """)  # Adăugați stilurile lipsă dacă e necesar
        # Setăm objectName aici, folosite de CSS și potențial de findChild
        self.generate_button.setObjectName("generate_button")
        self.modify_rate_button.setObjectName("modify_rate_button")
        self.btn_delete_month.setObjectName("btnDeleteSelectedMonth")  # NOU
        self.btn_update_inactivi.setObjectName("btn_update_inactivi")
        self.btn_afiseaza_inactivi.setObjectName("btn_afiseaza_inactivi")
        self.btn_afiseaza_activi.setObjectName("btn_afiseaza_activi")
        self.btn_export_log.setObjectName("btn_export_log")
        self.btn_clear_log.setObjectName("btn_clear_log")

    def _set_buttons_enabled_state(self, enabled: bool):
        """Setează starea activat/dezactivat pentru controalele principale."""
        is_period_loaded = self._current_month > 0 and self._current_year > 0
        # Activăm butoanele doar dacă starea generală 'enabled' e True ȘI avem o perioadă validă
        effective_enabled = enabled and is_period_loaded

        self.generate_button.setEnabled(effective_enabled)
        self.month_selector.setEnabled(enabled)  # Selectorul e activ mereu dacă UI e activ
        self.modify_rate_button.setEnabled(effective_enabled)
        self.btn_delete_month.setEnabled(effective_enabled)  # Butonul ștergere e activ doar dacă avem ce șterge

        # Butoanele extra depind doar de starea generală 'enabled'
        self.btn_update_inactivi.setEnabled(enabled)
        self.btn_afiseaza_inactivi.setEnabled(enabled)
        self.btn_afiseaza_activi.setEnabled(enabled)
        self.btn_export_log.setEnabled(enabled)
        self.btn_clear_log.setEnabled(True)  # Șterge log mereu activ

    def _connect_signals(self):
        """Conectează semnalele widget-urilor la slot-uri."""
        # Butoane extra
        self.btn_export_log.clicked.connect(self._export_log)
        self.btn_clear_log.clicked.connect(self.status_text.clear)
        self.btn_afiseaza_inactivi.clicked.connect(self.afiseaza_membri_lichidati)
        self.btn_update_inactivi.clicked.connect(self.afiseaza_numere_nealocate)
        self.btn_afiseaza_activi.clicked.connect(self._afiseaza_activi)

        # Acțiuni principale
        self.generate_button.clicked.connect(self._handle_generate_selected_month)
        self.modify_rate_button.clicked.connect(self._modify_loan_rate_on_extinction)
        self.month_selector.currentIndexChanged.connect(self._update_target_year_display)
        # !!! NOU: Conectare buton ștergere !!!
        self.btn_delete_month.clicked.connect(self._handle_delete_last_month)  # Folosim handlerul sigur

    # --- Handlers și Sloturi ---

    # !!! NOU: Handler pentru butonul de ștergere (varianta sigură) !!!
    def _handle_delete_last_month(self):
        """Gestionează acțiunea de ștergere a ULTIMEI luni generate."""
        if not poate_scrie():
            afiseaza_warning(MESAJ_READONLY, parent=self)
            return
        if self._is_running:
            afiseaza_warning("Un proces este deja în curs. Așteptați finalizarea.", self)
            return

        if not (self._current_month > 0 and self._current_year > 0):
            afiseaza_eroare("Nu este încărcată nicio lună procesată pentru a putea șterge.", self)
            return

        # Identificăm ultima lună generată din starea curentă
        month_to_delete = self._current_month
        year_to_delete = self._current_year

        # (Opțional: verificăm dacă selecția curentă din combobox corespunde, doar pentru a informa)
        selected_index = self.month_selector.currentIndex()
        selected_month_data = self.month_selector.itemData(selected_index) if selected_index >= 0 else None
        # Aici ar trebui o logică mai bună de a calcula anul potențial selectat, dar
        # pentru scopul de a șterge DOAR ultima lună, este suficient să informăm dacă selecția diferă.
        # Ignorăm selecția pt acțiunea efectivă, dar putem informa utilizatorul.
        # ... (codul de avertizare dacă selected_month_data != month_to_delete poate fi adăugat aici) ...

        # Verificăm dacă ultima lună chiar există (sanity check)
        if not self._check_month_exists(month_to_delete, year_to_delete):
            afiseaza_eroare(f"Eroare internă: Ultima lună ({month_to_delete:02d}-{year_to_delete}) nu a fost găsită.",
                            self)
            return

        # Confirmare critică
        confirm_msg = (
            f"Sunteți ABSOLUT sigur că doriți să ștergeți TOATE înregistrările "
            f"pentru ultima lună generată ({month_to_delete:02d}-{year_to_delete}) "
            f"din DEPCRED.db?\n\n"
            f"!!! ACEASTĂ ACȚIUNE ESTE IREVERSIBILĂ !!!"
        )
        if not afiseaza_intrebare(
                confirm_msg,
                titlu="Confirmare Ștergere Ultima Lună",
                parent=self,
                buton_default=QMessageBox.No
        ):
            self.status_text.append(f"ℹ️ Ștergerea lunii {month_to_delete:02d}-{year_to_delete} a fost anulată.")
            return

        # Executăm ștergerea
        self.status_text.append(f"⏳ Se șterg datele pentru luna {month_to_delete:02d}-{year_to_delete}...")
        QApplication.processEvents()
        self.setCursor(Qt.WaitCursor)
        # Salvăm starea butoanelor înainte de a le dezactiva
        # Ar fi mai bine să folosim o variabilă self._is_running deja existentă
        self._is_running = True  # Marcăm că o operație e în curs
        self._set_buttons_enabled_state(False)  # Dezactivăm conform stării _is_running / _current_month

        # Folosim funcția existentă
        deleted_ok = self._delete_month_data(month_to_delete, year_to_delete)

        self._is_running = False  # Resetăm flag-ul
        self.setCursor(Qt.ArrowCursor)

        if deleted_ok:
            self.status_text.append(f"✅ Datele lunii {month_to_delete:02d}-{year_to_delete} șterse.")
            self.status_text.append("ℹ️ Reîncărcare perioadă curentă...")
            QApplication.processEvents()
            self._load_current_period()  # Actualizează starea și implicit butoanele
            self.status_text.append("✅ Perioada curentă actualizată.")
        else:
            self.status_text.append(f"⛔ Ștergerea lunii {month_to_delete:02d}-{year_to_delete} a eșuat.")
            self._load_current_period()  # Reîncărcăm oricum starea pt consistență

    def _update_target_year_display(self):
        """Actualizează afișarea anului țintă când luna selectată se schimbă."""
        if self._current_month == 0 or self._current_year == 0:
            return  # Nu avem date despre perioada curentă

        selected_index = self.month_selector.currentIndex()
        if selected_index < 0:
            return

        selected_month = self.month_selector.itemData(selected_index)

        # Calculăm anul bazat pe luna selectată
        if selected_month == 1 and self._current_month == 12:
            target_year = self._current_year + 1
        else:
            target_year = self._current_year

        self.next_period_label.setText(f"Următoarea lună (selectată): {selected_month:02d}-{target_year}")

    # --- Handler pentru butonul principal de Generare ---
    # (Rămâne similar, dar trebuie să gestioneze _target_year corect)
    def _handle_generate_selected_month(self):
        """Gestionează acțiunea de generare a lunii selectate."""
        if not poate_scrie():
            afiseaza_warning(MESAJ_READONLY, parent=self)
            return
        if self._is_running:
            afiseaza_warning("Un proces de generare este deja în curs.", self)
            return

        if self._dbs_missing:
            afiseaza_eroare(f"Lipsesc baze de date esențiale: {', '.join(self._dbs_missing)}.", self)
            return

        if self._current_year == 0 or self._current_month == 0:
            # Asta înseamnă că _load_current_period a eșuat sau DB e gol la început
            # Încercăm să inițializăm dacă e cazul? Sau afișăm eroare.
            afiseaza_warning("Perioada curentă (ultima lună procesată) nu este clară. Verificați baza de date DEPCRED.",
                             self)
            # Am putea încerca aici: self._initialize_period_first_run() și apoi self._load_current_period()
            # Dar e mai sigur să cerem verificare manuală.
            return

        selected_index = self.month_selector.currentIndex()
        if selected_index < 0:
            afiseaza_warning("Vă rugăm selectați o lună pentru generare.", self)
            return
        self._target_month = self.month_selector.itemData(selected_index)

        # Calculăm anul țintă CORECT pe baza ultimei luni PROCESATE (_current...)
        # și a lunii selectate (_target_month)
        if self._target_month == 1 and self._current_month == 12:
            # Trecerea de la Decembrie la Ianuarie
            self._target_year = self._current_year + 1
        elif self._target_month == self._current_month + 1:
            # Luna imediat următoare în același an
            self._target_year = self._current_year
        # Cazuri speciale sau de eroare
        elif self._target_month == self._current_month and self._current_year > 0:
            # Același an, aceeași lună - nu ar trebui să generăm
            afiseaza_eroare(
                f"Luna {self._target_month:02d}-{self._current_year} pare să fie deja ultima lună procesată.", self)
            return
        else:
            # Orice altă selecție (lună mult mai mare, lună mai mică etc.) este invalidă pt generare normală
            afiseaza_eroare(
                f"Selecție invalidă. Puteți genera doar luna imediat următoare ultimei luni procesate ({self._current_month:02d}-{self._current_year}).\n"
                f"Următoarea lună logică este {(self._current_month % 12) + 1:02d}-"
                f"{self._current_year if self._current_month != 12 else self._current_year + 1}.", self)
            return

        logging.info(f"Generare solicitată pentru: {self._target_month:02d}-{self._target_year}")

        # Verificăm dacă luna țintă există deja
        month_exists = self._check_month_exists(self._target_month, self._target_year)
        if month_exists:
            if afiseaza_intrebare(
                    f"Datele pentru luna {self._target_month:02d}-{self._target_year} există deja în DEPCRED.db.\n"
                    "Doriți să le ștergeți și să le regenerați?",
                    titlu="Confirmare Suprascriere",
                    parent=self,
                    buton_default=QMessageBox.No
            ):
                # Folosim funcția de ștergere existentă
                self.status_text.append(
                    f"Se șterg datele existente pentru {self._target_month:02d}-{self._target_year}...")
                QApplication.processEvents()
                deleted = self._delete_month_data(self._target_month, self._target_year)
                if not deleted:
                    afiseaza_eroare("Ștergerea datelor existente a eșuat. Regenerarea a fost anulată.", self)
                    return
                self.status_text.append("Date existente șterse.")
            else:
                self.status_text.append("Generare anulată de utilizator.")
                return

        # Pornim generarea în thread separat
        self._is_running = True
        self._set_buttons_enabled_state(False)
        self.setCursor(Qt.WaitCursor)
        self.status_text.clear()
        self.status_text.append(
            f"⏳ Se generează luna {MONTH_NAMES.get(self._target_month, '')} "
            f"({self._target_month:02d}-{self._target_year})..."
        )
        QApplication.processEvents()

        # Lansăm task-ul în background
        run_task_in_background(
            self,  # parent_widget
            self._run_month_end_logic_for_target,  # funcția corectă
            self._target_month,  # arg1: luna țintă
            self._target_year,  # arg2: anul țintă
            on_progress=self._on_generation_progress,  # callback original
            on_finish=self._on_generation_finished,  # callback original
            on_error=self._on_generation_error  # callback original
        )

    # --- Sloturi pentru semnale Worker ---
    def _on_generation_progress(self, message):
        """Actualizează UI-ul cu mesaje de progres din thread."""
        # Asigură-te că actualizarea se face în thread-ul UI
        # QMetaObject.invokeMethod poate fi folosit aici dacă rulează în alt thread
        # Dar dacă semnalul e conectat corect, Qt ar trebui să se ocupe.
        # Verificare suplimentară:
        if self and self.status_text and self.status_text.isVisible():
            try:
                # Append este thread-safe în multe cazuri, dar invokeMethod e mai sigur
                QMetaObject.invokeMethod(self.status_text, "append", Qt.QueuedConnection, Q_ARG(str, message))
            except Exception as e:
                logging.error(f"Eroare la invokeMethod pentru status_text.append: {e}")

    def _on_generation_finished(self):
        """Acțiuni la finalizarea cu succes a generării."""
        logging.info("Generare terminată cu succes (semnal finished primit).")
        if self and hasattr(self, 'isVisible') and self.isVisible():
            self._generation_cleanup()
            # Reîncarcă perioada curentă după generare
            self._load_current_period()
            afiseaza_info("Generarea lunii noi s-a terminat cu succes!", self)
        else:
            logging.warning("Widget-ul nu mai există sau nu e vizibil la finalizarea generării.")

    def _on_generation_error(self, error_tuple):
        """Acțiuni la apariția unei erori în timpul generării."""
        try:
            exctype, value, tb_str = error_tuple
            error_message = f"{exctype.__name__}: {value}"
            logging.error(f"Eroare în worker thread: {error_message}\n{tb_str}")
            if self and hasattr(self, 'isVisible') and self.isVisible():
                self._generation_cleanup()
                # Reîncărcăm starea chiar dacă a fost eroare, pt consistență
                self._load_current_period()
                afiseaza_eroare(
                    f"A apărut o eroare în timpul generării:\n\n{error_message}\n\nConsultați log-ul (generare_luna.log dacă e configurat) pentru detalii.",
                    self)
            else:
                logging.warning("Widget-ul nu mai există/vizibil la raportarea erorii.")
        except Exception as e:
            logging.error(f"Eroare în handler-ul _on_generation_error: {e}", exc_info=True)

    def _generation_cleanup(self):
        """Curăță starea după finalizarea (cu succes sau eroare) a generării."""
        self._is_running = False
        self.setCursor(Qt.ArrowCursor)
        # Starea butoanelor va fi setată de _load_current_period care e apelat după
        # self._set_buttons_enabled_state(not self._dbs_missing) # Se poate seta și aici
        logging.info("Interfața a fost reactivată după generare.")

    def _run_month_end_logic_for_target(
            self,
            target_month: int,
            target_year: int,
            *,
            progress_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Logica principală de generare a lunii noi (rulează în thread).
        Include cotizație standard, rată împrumut moștenită din luna anterioară
        și calcul dobândă la stingere împrumut.
        """
        def report_progress(message: str, is_detailed: bool = False) -> None:
            """
            Raportează progresul prin callback și log.
            Param is_detailed: Dacă True, mesajul este trimis doar la logging, nu și în UI
            """
            logging.info(message)
            if progress_callback and not is_detailed:
                try:
                    # Abordare simplă și directă pentru emiterea semnalului
                    progress_callback(message)
                except Exception as e:
                    logging.error(f"Eroare la emiterea progresului: {e}", exc_info=True)

        # --- Calcul perioadă sursă ---------------------------------------------
        source_month = target_month - 1 if target_month > 1 else 12
        source_year = target_year if target_month > 1 else target_year - 1
        source_period_val = source_year * 100 + source_month

        if source_year <= 0:
            err = f"Anul sursă ({source_year}) invalid pentru {target_month:02d}-{target_year}."
            report_progress(f"⛔ EROARE FATALĂ: {err}")
            logging.critical(err)
            raise ValueError(err)

        report_progress(
            f"--- Generare pentru {target_month:02d}-{target_year} "
            f"(Sursa: {source_month:02d}-{source_year}) ---"
        )

        conn_m, conn_d, conn_l = None, None, None
        generati, dobanda_calculata_total, nr_dobanzi_calculate = 0, Decimal("0.00"), 0
        total_sold_impr_nou, total_sold_dep_nou = Decimal("0.00"), Decimal("0.00")
        membri_activi_count, membri_omis_lipsa_sursa, membri_omis_eroare_calcul = 0, 0, 0

        try:
            # --- Deschidere conexiuni DB ---------------------------------------
            report_progress(f"📂 CITIRE din: {os.path.basename(DB_MEMBRII)}, {os.path.basename(DB_LICHIDATI)}")
            report_progress(f"📝 SCRIERE în: {os.path.basename(DB_DEPCRED)}")
            conn_m = sqlite3.connect(f"file:{DB_MEMBRII}?mode=ro", uri=True, timeout=30.0)
            conn_d = sqlite3.connect(DB_DEPCRED, timeout=30.0)  # Read-write
            conn_l = sqlite3.connect(f"file:{DB_LICHIDATI}?mode=ro", uri=True, timeout=30.0)
            cursor_m, cursor_d, cursor_l = conn_m.cursor(), conn_d.cursor(), conn_l.cursor()
            report_progress("✅ Conexiuni DB deschise.", is_detailed=True)

            # --- Preluare Lichidați ---
            report_progress("ℹ️ Preluare lichidați...", is_detailed=True)
            lichidati_set = set()
            try:
                cursor_l.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lichidati'")
                if cursor_l.fetchone():
                    cursor_l.execute("SELECT nr_fisa FROM lichidati")
                    lichidati_set = {row[0] for row in cursor_l.fetchall()}
                else:
                    logging.warning("Tabela 'lichidati' nu există în LICHIDATI.db.")
            except sqlite3.Error as e:
                report_progress(f"⚠️ Eroare citire lichidați: {e}. Se continuă fără.")
                logging.error("Eroare SQLite LICHIDATI.db", exc_info=True)
            report_progress(f"✅ Găsit {len(lichidati_set)} membri lichidați.")

            # --- Preluare membri activi & cotizații standard -------------------
            report_progress("ℹ️ Preluare membri activi și cotizații standard...", is_detailed=True)
            cursor_m.execute("PRAGMA table_info(membrii)")
            cols = [info[1].lower() for info in cursor_m.fetchall()]
            if 'cotizatie_standard' not in cols:
                msg = "EROARE FATALĂ: Coloana 'COTIZATIE_STANDARD' lipsește din 'membrii'!"
                report_progress(f"⛔ {msg}")
                raise sqlite3.OperationalError(msg)

            query = "SELECT nr_fisa, NUM_PREN, COTIZATIE_STANDARD FROM membrii WHERE nr_fisa IS NOT NULL"

            cursor_m.execute(query)
            membri_activi = []

            for row in cursor_m.fetchall():
                nr = row[0]
                if nr not in lichidati_set:
                    nume_pren = row[1]
                    cot_standard = row[2]
                    nume = nume_pren.strip() if nume_pren else "N/A"
                    try:
                        cotizatie = Decimal(str(cot_standard or '0.00')).quantize(Decimal("0.01"), ROUND_HALF_UP)
                    except InvalidOperation:
                        report_progress(
                            f"⚠️ 'COTIZATIE_STANDARD' invalidă pt {nr} ({nume}): '{cot_standard}'. Folosit 0.00.",
                            is_detailed=True
                        )
                        cotizatie = Decimal("0.00")


                    membri_activi.append((nr, nume, cotizatie))

            membri_activi_count = len(membri_activi)
            report_progress(f"✅ Identificat {membri_activi_count} membri activi.")
            if membri_activi_count == 0:
                report_progress("⚠️ Nu există membri activi.")
                return

            # --- Actualizare 'prima=0' Luna Sursă ---
            report_progress(f"ℹ️ Resetez flag 'prima' pentru luna anterioară: {source_month:02d}-{source_year}")
            cursor_d.execute("UPDATE depcred SET prima = 0 WHERE luna = ? AND anul = ?", (source_month, source_year))
            affected_rows = cursor_d.rowcount
            conn_d.commit()
            report_progress(f"✅ Reset 'prima=0' pentru {affected_rows} înregistrări.", is_detailed=True)

            # --- Procesare Membri ---
            report_progress(f"📊 Începe procesarea celor {membri_activi_count} membri...")
            for i, (nr_fisa, nume, cotizatie_standard) in enumerate(membri_activi):
                if (i + 1) % 25 == 0:
                    report_progress(f"... procesat {i + 1}/{membri_activi_count} membri")

                dobanda_noua = Decimal("0.00")  # Resetăm dobânda
                try:
                    # 1. Preluare solduri sursă
                    cursor_d.execute("SELECT impr_sold, dep_sold FROM depcred WHERE nr_fisa = ? AND luna = ?"
                                     " AND anul = ?", (nr_fisa, source_month, source_year))
                    row_source = cursor_d.fetchone()
                    if not row_source:
                        membri_omis_lipsa_sursa += 1
                        report_progress(f"⚠️ Lipsă date sursă in perioada: {source_period_val} pentru numarul de fisa: {nr_fisa}.", is_detailed=True)
                        continue

                    impr_sold_sursa = Decimal(str(row_source[0] or '0.00'))
                    dep_sold_sursa = Decimal(str(row_source[1] or '0.00'))


                    # 2. Inițializare valorile noi și preluare moșteniri
                    impr_deb_nou = Decimal("0.00")  # Resetăm, se ia din sume lunare
                    dep_cred_nou = Decimal("0.00")  # Resetăm, se ia din sume lunare

                    # Preluare rată și inițializare cotizație
                    impr_cred_nou = self._get_inherited_loan_rate(cursor_d, nr_fisa, source_period_val)
                    dep_deb_nou = cotizatie_standard

                    # Ajustăm plata să nu depășească soldul
                    if impr_sold_sursa <= Decimal("0.005"):
                        impr_cred_nou = Decimal("0.00")
                    else:
                        impr_cred_nou = min(impr_sold_sursa, impr_cred_nou)

                    # 3. Calcul solduri noi
                    impr_sold_nou_calculat = impr_sold_sursa + impr_deb_nou - impr_cred_nou
                    if impr_sold_nou_calculat <= Decimal('0.005'):
                        impr_sold_nou = Decimal("0.00")
                    else:
                        impr_sold_nou = impr_sold_nou_calculat
                    dep_sold_nou = dep_sold_sursa + dep_deb_nou - dep_cred_nou

                    # 4. Calcul dobândă la stingere (dacă e cazul)
                    if impr_sold_sursa > Decimal('0.005') and impr_sold_nou == Decimal("0.00"):
                        report_progress(f"📝 Fișa {nr_fisa} ({nume}): Împrumut achitat! Calculez dobânda...")

                        # Găsește MAX perioada <= luna sursă unde impr_deb > 0
                        cursor_d.execute(
                            "SELECT MAX(anul*100+luna) FROM depcred WHERE nr_fisa=? "
                            "AND impr_deb>0 AND (anul*100+luna <= ?)",
                            (nr_fisa, source_period_val)  # Folosim luna sursă (M-1) ca limită superioară
                        )
                        start_period_res = cursor_d.fetchone()
                        if start_period_res and start_period_res[0] is not None:
                            start_period_val = start_period_res[0]
                            start_year, start_month = divmod(start_period_val, 100)

                            # Suma de la start_period_val PÂNĂ LA source_period_val (inclusiv)
                            end_sum_period = source_period_val  # Suma include luna sursă M-1
                            cursor_d.execute(
                                "SELECT SUM(impr_sold) FROM depcred WHERE nr_fisa=? "
                                "AND (anul*100+luna BETWEEN ? AND ?) "
                                "AND impr_sold > 0",  # Doar solduri pozitive
                                (nr_fisa, start_period_val, end_sum_period)
                            )
                            sum_balances_result = cursor_d.fetchone()
                            sum_balances = Decimal(str(sum_balances_result[0] or '0.00'))

                            if sum_balances > 0:
                                dobanda_noua = (sum_balances * self.loan_interest_rate_on_extinction
                                                ).quantize(Decimal("0.01"), ROUND_HALF_UP)
                                dobanda_calculata_total += dobanda_noua
                                nr_dobanzi_calculate += 1
                                report_progress(
                                    f"💸 Fișa {nr_fisa} ({nume}): Dobândă calculată = {dobanda_noua:.2f}  "
                                    f"(Suma sold: {sum_balances:.2f}, perioada: {start_month:02d}-{start_year} → {source_month:02d}-{source_year})"
                                )
                        else:
                            report_progress(
                                f"⚠️ Fișa {nr_fisa}: Nu s-a putut stabili perioada împrumutului. Dobânda=0.",
                                is_detailed=True)

                    # 5. Inserare înregistrare nouă pentru luna țintă
                    insert_query = ("INSERT INTO depcred (nr_fisa, luna, anul, dobanda, impr_deb, impr_cred, impr_sold,"
                                    " dep_deb, dep_cred, dep_sold, prima) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)")
                    insert_params = (nr_fisa, target_month, target_year,
                                     str(dobanda_noua), str(impr_deb_nou), str(impr_cred_nou),
                                     str(impr_sold_nou), str(dep_deb_nou), str(dep_cred_nou),
                                     str(dep_sold_nou))
                    cursor_d.execute(insert_query, insert_params)
                    generati += 1
                    total_sold_dep_nou += dep_sold_nou
                    total_sold_impr_nou += impr_sold_nou

                    # Afișăm un rezumat pentru membrii care nu au stins un împrumut
                    if not (impr_sold_sursa > Decimal('0.005') and impr_sold_nou == Decimal("0.00")):
                        # Afișăm detalii pentru primii 10 membri și apoi la fiecare 50 (pentru a nu încărca UI-ul)
                        if i < 10 or i % 50 == 0:
                            report_progress(
                                f"👤 Fișa {nr_fisa} ({nume}): Cotizație={dep_deb_nou:.2f}, "
                                f"Împr.Sold={impr_sold_nou:.2f}, Dep.Sold={dep_sold_nou:.2f}"
                            )

                except (sqlite3.Error, InvalidOperation, TypeError, ValueError) as e_mem:
                    report_progress(f"⛔ Eroare la procesarea {nr_fisa} ({nume}): {e_mem}", is_detailed=True)
                    logging.error(f"Eroare procesare membru {nr_fisa}", exc_info=True)
                    membri_omis_eroare_calcul += 1

            # --- Finalizare și Rezumat ---
            report_progress("📝 Salvare date în baza de date...")
            conn_d.commit()
            report_progress("✅ Date salvate cu succes!")

            # BUG #5 FIX: Validare post-generare - verifică că niciun membru lichid nu a fost inclus greșit
            report_progress("🔍 Validare post-generare: verificare membri lichidați...", is_detailed=True)
            try:
                # Folosim lichidati_set în loc de subquery SQL pentru a evita eroarea "no such table"
                if lichidati_set:
                    placeholders = ','.join('?' * len(lichidati_set))
                    cursor_d.execute(f"""
                        SELECT COUNT(*) FROM depcred
                        WHERE nr_fisa IN ({placeholders})
                        AND luna = ? AND anul = ?
                    """, tuple(lichidati_set) + (target_month, target_year))
                    membri_lichidati_gresit = cursor_d.fetchone()[0]
                else:
                    membri_lichidati_gresit = 0

                if membri_lichidati_gresit > 0:
                    # AVERTIZARE CRITICĂ - membri lichidați au fost incluși greșit!
                    report_progress(f"⚠️ AVERTIZARE: {membri_lichidati_gresit} membri lichidați au fost incluși greșit în luna {target_month:02d}-{target_year}!")
                    logging.warning(f"BUG #5: {membri_lichidati_gresit} membri lichidați incluși greșit în luna generată")

                    # Afișează lista membrilor lichidați incluși greșit
                    cursor_d.execute(f"""
                        SELECT d.nr_fisa, m.NUM_PREN
                        FROM depcred d
                        LEFT JOIN membrii m ON d.nr_fisa = m.nr_fisa
                        WHERE d.nr_fisa IN ({placeholders})
                        AND d.luna = ? AND d.anul = ?
                    """, tuple(lichidati_set) + (target_month, target_year))
                    membri_gresit = cursor_d.fetchall()

                    for nr_fisa, nume in membri_gresit:
                        report_progress(f"  - Fișa {nr_fisa}: {nume or 'N/A'} (LICHID AT, NU AR TREBUI INCLUS)", is_detailed=True)

                    # Opțional: șterge automat aceste înregistrări greșite
                    report_progress("🔧 Curățare automată: șterg înregistrările greșite...", is_detailed=True)
                    cursor_d.execute(f"""
                        DELETE FROM depcred
                        WHERE nr_fisa IN ({placeholders})
                        AND luna = ? AND anul = ?
                    """, tuple(lichidati_set) + (target_month, target_year))
                    sterse = cursor_d.rowcount
                    conn_d.commit()
                    report_progress(f"✅ {sterse} înregistrări greșite șterse pentru membri lichidați")
                    generati -= sterse  # Ajustează numărul de înregistrări generate
                else:
                    report_progress("✅ Validare OK: Niciun membru lichid at inclus greșit", is_detailed=True)
            except sqlite3.Error as e_valid:
                report_progress(f"⚠️ Eroare validare post-generare: {e_valid}", is_detailed=True)
                logging.error("Eroare validare post-generare BUG #5", exc_info=True)

            summary = [f" Membri activi procesați: {membri_activi_count}",
                       f" Înregistrări generate: {generati}",
                       f" Omiși (lipsă date sursă): {membri_omis_lipsa_sursa}",
                       f" Omiși (eroare): {membri_omis_eroare_calcul}",
                       f" Sold final împrumuturi: {total_sold_impr_nou:.2f}",
                       f" Sold final depuneri: {total_sold_dep_nou:.2f}",
                       f" Total Dobânzi: {nr_dobanzi_calculate} ({dobanda_calculata_total:.2f} )"]
            report_progress("\n=== REZUMAT GENERARE ===")
            report_progress(f"📅 Luna generată: {target_month:02d}-{target_year}")
            for line in summary:
                report_progress(line)
            report_progress("=== GENERARE FINALIZATĂ CU SUCCES ===")
            return True

        except sqlite3.OperationalError as e_op:
            if "database is locked" in str(e_op).lower():
                report_progress(f"⛔ EROARE FATALĂ: Baza de date DEPCRED blocată!")
                logging.error("DB Locked", exc_info=True)
                if conn_d:
                    conn_d.rollback()
                raise RuntimeError("Baza de date DEPCRED blocată.") from e_op
            else:
                report_progress(f"⛔ EROARE OPERAȚIONALĂ DB: {e_op}. Rollback.")
                logging.error("Eroare Op SQLite", exc_info=True)
            if conn_d:
                conn_d.rollback()
                raise
        except Exception as e_fatal:
            report_progress(f"⛔ EROARE FATALĂ: {e_fatal}. Rollback.")
            logging.error("Eroare fatală worker", exc_info=True)
            if conn_d:
                conn_d.rollback()
                raise
        finally:
            # Închidere conexiuni DB
            if conn_m: conn_m.close()
            if conn_d: conn_d.close()
            if conn_l: conn_l.close()
            report_progress("🔒 Conexiuni DB închise.", is_detailed=True)

    def _load_current_period(self) -> None:
        """Încarcă ultima lună și an procesate din DEPCRED.db."""
        logging.info("DEBUG: Entering _load_current_period...")
        conn = None
        try:
            if not os.path.exists(DB_DEPCRED):
                logging.error(f"DB_DEPCRED ({DB_DEPCRED}) lipsă.")
                self._current_month, self._current_year = 0, 0
                self.current_period_label.setText("Ultima lună: Eroare (DB Lipsă)")
                self.next_period_label.setText("Următoarea lună: -")
                self._dbs_missing.append(os.path.basename(DB_DEPCRED))
                self._set_buttons_enabled_state(False)
                return

            db_path_abs = os.path.abspath(DB_DEPCRED)
            conn = sqlite3.connect(f"file:{db_path_abs}?mode=ro", uri=True, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT anul, luna FROM depcred "
                "ORDER BY anul DESC, luna DESC LIMIT 1"
            )
            result = cursor.fetchone()

            if result and all(val is not None for val in result):
                self._current_year, self._current_month = map(int, result)
                self.current_period_label.setText(
                    f"Ultima lună: {self._current_month:02d}-{self._current_year}"
                )
                next_m, next_y = (
                    (1, self._current_year + 1)
                    if self._current_month == 12 else
                    (self._current_month + 1, self._current_year)
                )
                self.next_period_label.setText(
                    f"Următoarea lună (logică): {next_m:02d}-{next_y}"
                )
                self._update_month_selector(select_month=next_m)
            else:
                logging.warning("DEPCRED: Tabela goală sau perioadă invalidă.")
                self._current_month, self._current_year = 0, 0
                self.current_period_label.setText("Ultima lună: Nicio lună procesată")
                self.next_period_label.setText("Următoarea lună: -")
                self._update_month_selector()
        except sqlite3.Error as e:
            logging.error(f"SQLite Error in _load_current_period: {e}", exc_info=True)
            afiseaza_eroare("Nu s-a putut determina ultima lună procesată. Verificați că baza de date DEPCRED.db există și conține date.", self)
        finally:
            if conn:
                conn.close()
                logging.info("DEBUG: DB Connection closed in _load_current_period.")
            self._set_buttons_enabled_state(not self._dbs_missing)

    def _update_month_selector(self, select_month: Optional[int] = None) -> None:
        """Actualizează luna selectată în ComboBox."""
        current_selection = self.month_selector.currentData()
        month_to_set = select_month if select_month is not None else current_selection
        if 1 <= (month_to_set or 0) <= 12:
            idx = self.month_selector.findData(month_to_set)
            self.month_selector.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            self.month_selector.setCurrentIndex(0)

    def _check_month_exists(self, month: int, year: int) -> bool:
        """Verifică dacă există date pentru o lună/an specific în DEPCRED.db."""
        if not os.path.exists(DB_DEPCRED):
            return False
        conn = None
        try:
            conn = sqlite3.connect(f"file:{DB_DEPCRED}?mode=ro", uri=True, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM depcred WHERE luna = ? AND anul = ? LIMIT 1",
                (month, year)
            )
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la verificare lună {month}-{year}: {e}", exc_info=True)
            afiseaza_eroare("Nu s-a putut verifica dacă luna există în baza de date. Verificați că DEPCRED.db este accesibilă.", self)
            return False
        finally:
            if conn:
                conn.close()

    def _delete_month_data(self, month: int, year: int) -> bool:
        """Șterge toate datele pentru o lună/an specific din DEPCRED.db."""
        if not os.path.exists(DB_DEPCRED):
            afiseaza_eroare(f"Baza de date {os.path.basename(DB_DEPCRED)} nu a fost găsită!", self)
            return False
        conn = None
        try:
            conn = sqlite3.connect(DB_DEPCRED)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM depcred WHERE luna = ? AND anul = ?", (month, year)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la ștergere {month}-{year}: {e}", exc_info=True)
            afiseaza_eroare(f"Eroare DB la ștergerea datelor lunii {month:02d}-{year}:\n{e}", self)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def _modify_loan_rate_on_extinction(self) -> None:
        """Modifică rata dobânzii aplicată la lichidarea împrumutului."""
        current_permille = (
                self.loan_interest_rate_on_extinction * 1000
        ).quantize(Decimal("0.1"), ROUND_HALF_UP)
        new_permille, ok = QInputDialog.getDouble(
            self,
            "Modifică Rata Dobândă Stingere",
            "Introduceți noua rată (‰):",
            float(current_permille),
            0.0,
            1000.0,
            1
        )
        if ok:
            try:
                new_rate = (
                        Decimal(str(new_permille)) / 1000
                ).quantize(Decimal("0.000001"), ROUND_HALF_UP)
                if new_rate < 0:
                    raise ValueError("Rata nu poate fi negativă.")
                self.loan_interest_rate_on_extinction = new_rate

                # Salvăm noua rată în fișierul de configurare
                if self._save_interest_rate_config():
                    display = (new_rate * 1000).quantize(Decimal("0.1"))
                    self.current_rate_label.setText(f"Rata lichidare: {display} ‰")
                    afiseaza_info(f"Rata a fost setată la {display} ‰ și salvată.", self)
                else:
                    display = (new_rate * 1000).quantize(Decimal("0.1"))
                    self.current_rate_label.setText(f"Rata lichidare: {display} ‰")
                    afiseaza_warning(
                        f"Rata a fost setată la {display} ‰, dar nu a putut fi salvată în fișierul de configurare.",
                        self)
            except (InvalidOperation, ValueError) as e:
                afiseaza_warning(f"Valoare rată invalidă: {new_permille}", self)

    def afiseaza_membri_lichidati(self) -> None:
        """Afișează în log lista membrilor din LICHIDATI.db."""
        self.status_text.clear()
        self.status_text.append("--- Membri Lichidați ---")
        if not os.path.exists(DB_LICHIDATI):
            afiseaza_eroare(f"Baza de date {os.path.basename(DB_LICHIDATI)} lipsește!", self)
            return

        conn_l = None
        conn_m = None  # Adăugăm o conexiune separată pentru MEMBRII.db
        try:
            # Deschidem LICHIDATI.db
            conn_l = sqlite3.connect(f"file:{DB_LICHIDATI}?mode=ro", uri=True)
            cursor_l = conn_l.cursor()

            # Verificăm dacă tabela lichidati există
            cursor_l.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='lichidati'"
            )
            if not cursor_l.fetchone():
                self.status_text.append("Tabela 'lichidati' lipsește.")
                return

            # Obținem nr_fisa și data_lichidare din tabela lichidati
            cursor_l.execute("SELECT nr_fisa, data_lichidare FROM lichidati ORDER BY nr_fisa")
            lichidati_data = cursor_l.fetchall()

            if not lichidati_data:
                self.status_text.append("Nu există membri lichidați în baza de date.")
                return

            # Deschidem MEMBRII.db pentru a obține numele
            conn_m = sqlite3.connect(f"file:{DB_MEMBRII}?mode=ro", uri=True)
            cursor_m = conn_m.cursor()

            # Procesăm datele și afișăm
            self.status_text.append(f"Total membri lichidați: {len(lichidati_data)}")

            # Construim rezultatul final cu nume (dacă există)
            lichidati_complet = []
            for idx, (nr_fisa, data_lichidare) in enumerate(lichidati_data, 1):
                # Căutăm numele în MEMBRII.db
                cursor_m.execute("SELECT NUM_PREN FROM membrii WHERE nr_fisa = ?", (nr_fisa,))
                nume_row = cursor_m.fetchone()
                nume = nume_row[0] if nume_row else "Nume negăsit"

                # Formatăm data de lichidare
                data_formatata = data_lichidare if data_lichidare else "N/A"

                # Adăugăm la lista completă
                lichidati_complet.append((nr_fisa, nume, data_formatata))

                # Afișăm în log (limitat la primii 100)
                if idx <= 100:
                    self.status_text.append(f"{idx}. Fișa {nr_fisa}: {nume} (Lichidare: {data_formatata})")

            # Afișăm mesaj dacă sunt mai mulți de 100
            if len(lichidati_data) > 100:
                self.status_text.append(
                    f"... și încă {len(lichidati_data) - 100} membri lichidați (afișați primii 100)")

        except sqlite3.Error as e:
            self.status_text.append(f"Eroare citire LICHIDATI.db: {e}")
            logging.error(f"Eroare la afișarea lichidaților: {e}", exc_info=True)
        finally:
            if conn_l:
                conn_l.close()
            if conn_m:
                conn_m.close()

    def _afiseaza_activi(self) -> None:
        """Afișează în log lista membrilor activi din ultima lună."""
        from decimal import Decimal

        self.status_text.clear()
        if self._current_month == 0:
            afiseaza_warning("Perioada curentă necunoscută.", self)
            return

        # Header
        self.status_text.append(
            f"--- Membri Activi (luna {self._current_month:02d}-{self._current_year}) ---"
        )

        conn_d = None
        try:
            # Deschidem DEPCRED și atașăm MEMBRII
            conn_d = sqlite3.connect(f"file:{DB_DEPCRED}?mode=ro", uri=True)
            cursor_d = conn_d.cursor()
            cursor_d.execute(f"ATTACH DATABASE '{DB_MEMBRII}' AS membrii_db")

            # Preluăm toți membrii din luna curentă
            cursor_d.execute(
                "SELECT d.nr_fisa, membrii_db.membrii.NUM_PREN, d.dep_sold, d.impr_sold "
                "FROM depcred d "
                "LEFT JOIN membrii_db.membrii ON d.nr_fisa = membrii_db.membrii.nr_fisa "
                "WHERE d.luna = ? AND d.anul = ? "
                "ORDER BY d.nr_fisa",
                (self._current_month, self._current_year)
            )
            membri = cursor_d.fetchall()

            if not membri:
                self.status_text.append(
                    f"Nu s-au găsit membri activi pentru luna {self._current_month:02d}-{self._current_year}."
                )
                return

            # Total membri (toți)
            self.status_text.append(f"Total membri activi: {len(membri)}")

            # 1. Calculăm total depuneri și total împrumuturi
            total_depuneri = Decimal("0.00")
            total_imprumuturi = Decimal("0.00")

            # 2. Construim setul de membri cu sold de împrumut > 0 (unici)
            membri_acti = {
                nr_fisa
                for nr_fisa, _, _, impr_sold in membri
                if Decimal(str(impr_sold or "0.00")) > Decimal("0")
            }
            total_membri_cu_impr = len(membri_acti)

            # 3. Afișăm detalii pentru primii 100
            for idx, (nr_fisa, nume, dep_sold, impr_sold) in enumerate(membri[:100], start=1):
                nume_formatat = nume.strip() if nume else "N/A"
                dep_sold_dec = Decimal(str(dep_sold or "0.00"))
                impr_sold_dec = Decimal(str(impr_sold or "0.00"))

                total_depuneri += dep_sold_dec
                total_imprumuturi += impr_sold_dec

                self.status_text.append(
                    f"{idx}. Fișa {nr_fisa}: {nume_formatat} "
                    f"(Depuneri: {dep_sold_dec:.2f}, Împrumut: {impr_sold_dec:.2f})"
                )

            if len(membri) > 100:
                self.status_text.append(
                    f"... și încă {len(membri) - 100} membri activi (afișați primii 100)"
                )

            # 4. Afișăm statistici finale
            self.status_text.append("\n=== Statistici ===")
            self.status_text.append(f"Total membri: {len(membri)}")
            self.status_text.append(f"Membri cu împrumuturi active: {total_membri_cu_impr}")
            self.status_text.append(f"Total depuneri: {total_depuneri:.2f} ")
            self.status_text.append(f"Total împrumuturi: {total_imprumuturi:.2f} ")

        except sqlite3.Error as e:
            self.status_text.append(f"Eroare citire membri activi: {e}")
            logging.error(f"Eroare la afișarea membrilor activi: {e}", exc_info=True)
        finally:
            if conn_d:
                conn_d.close()

    def afiseaza_numere_nealocate(self):
        """Caută și afișează numerele de fișă nealocate într-un dialog."""
        sender_button = self.sender()
        original_text = ""
        button_to_disable = self.btn_update_inactivi
        if button_to_disable:
            original_text = button_to_disable.text()
            button_to_disable.setEnabled(False)
            button_to_disable.setText("Se caută...")
            QApplication.processEvents()

        if not os.path.exists(DB_MEMBRII):
            afiseaza_eroare(f"Baza de date {os.path.basename(DB_MEMBRII)} nu a fost găsită!", self)
            if button_to_disable:
                button_to_disable.setEnabled(True)
                button_to_disable.setText(original_text)
            return

        conn_m = None
        try:
            logging.info("Preluare numere de fișă alocate din MEMBRII.db...")
            self.status_text.setText("Se caută numerele de fișă nealocate...")
            QApplication.processEvents()

            conn_m = sqlite3.connect(f"file:{DB_MEMBRII}?mode=ro", uri=True)
            cursor = conn_m.cursor()
            # Preluăm distinct numerele de fișă valide (întregi > 0)
            cursor.execute(
                "SELECT DISTINCT NR_FISA FROM MEMBRII WHERE NR_FISA IS NOT NULL AND TYPEOF(NR_FISA) = 'integer' AND NR_FISA > 0")
            numere_alocate = {row[0] for row in cursor.fetchall()}
            conn_m.close()  # Închidem devreme
            conn_m = None

            if not numere_alocate:
                afiseaza_info("Nu s-au găsit numere de fișă valide alocate în MEMBRII.db.", self)
                self.status_text.clear()
                if button_to_disable:
                    button_to_disable.setEnabled(True)
                    button_to_disable.setText(original_text)
                return

            # Găsim intervalul și numerele lipsă
            min_fisa_alloc = min(numere_alocate)  # Minimul alocat
            max_fisa_alloc = max(numere_alocate)  # Maximul alocat
            # Definim intervalul relevant (de la 1 la maximul găsit)
            interval_complet = set(range(1, max_fisa_alloc + 1))
            nealocate_set = interval_complet - numere_alocate
            nealocate_list = sorted(list(nealocate_set))

            logging.info(f"Găsit {len(nealocate_list)} numere nealocate în intervalul 1 - {max_fisa_alloc}.")
            self.status_text.setText(f"Verificare finalizată. Găsit {len(nealocate_list)} numere nealocate.")

            # Afișăm dialogul
            dialog = NealocateDialog(nealocate_list, 1, max_fisa_alloc, self)
            dialog.exec_()

        except sqlite3.Error as e_sql:
            error_msg = f"Eroare SQLite la căutarea nealocatelor: {e_sql}"
            self.status_text.setText("Eroare DB.")
            logging.error(error_msg, exc_info=True)
            afiseaza_eroare(f"Eroare la citirea din {os.path.basename(DB_MEMBRII)}:\n{e_sql}", self)
        except Exception as e_gen:
            error_msg = f"Eroare neașteptată la căutarea nealocatelor: {e_gen}"
            self.status_text.setText("Eroare.")
            logging.error(error_msg, exc_info=True)
            afiseaza_eroare(f"A apărut o eroare neașteptată:\n{e_gen}", self)
        finally:
            if conn_m:  # Dacă a rămas deschisă din cauza unei erori
                conn_m.close()
            if button_to_disable:  # Reactivăm butonul
                button_to_disable.setEnabled(True)
                button_to_disable.setText(original_text)

    def _export_log(self):
        """Exportă conținutul curent al log-ului într-un fișier text."""
        log_content = self.status_text.toPlainText().strip()
        if not log_content:
            afiseaza_info("Nu există conținut în log pentru a fi exportat.", self)
            return

        # Propunem un nume de fișier default
        default_filename = os.path.join(
            os.getcwd(),  # Sau alt director preferat, ex: os.path.expanduser("~")
            f"rezumat_generare_{datetime.now():%Y%m%d_%H%M%S}.txt"
        )
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Opțional, pt dialog custom Qt

        fileName, _ = QFileDialog.getSaveFileName(
            self, "Salvare Rezumat Log", default_filename,
            "Fișiere Text (*.txt);;Toate Fișierele (*)", options=options
        )

        if fileName:
            try:
                with open(fileName, "w", encoding="utf-8") as f:
                    f.write(f"--- Rezumat Operațiuni ---\n")
                    f.write(f"Data export: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
                    # Adăugăm și ultima lună procesată în momentul exportului
                    if self._current_month > 0 and self._current_year > 0:
                        f.write(
                            f"Ultima lună procesată (la momentul exportului): {self._current_month:02d}-{self._current_year}\n")
                    f.write(f"{'-' * 40}\n\n")
                    f.write(log_content)
                afiseaza_info(f"Logul a fost salvat cu succes în:\n'{fileName}'.", self)
                logging.info(f"Log exportat în: {fileName}")
            except Exception as e:
                logging.error(f"Eroare la exportul logului: {e}", exc_info=True)
                afiseaza_eroare(f"Salvarea logului a eșuat:\n{e}", self)


# --- Blocul __main__ --- (Punctul de intrare al aplicației)
if __name__ == '__main__':
    # Inițializare aplicație Qt
    app = QApplication(sys.argv)

    # Creare și afișare widget principal
    widget = GenerareLunaNouaWidget()
    # Setăm un titlu mai specific versiunii curente
    widget.setWindowTitle("Generare Lunară CAR v1.2 (Cotizatie Standard + Rata Anterioară)")
    widget.resize(950, 750)  # Dimensiune inițială fereastră
    widget.show()

    # Pornire buclă evenimente Qt și ieșire curată
    sys.exit(app.exec_())
