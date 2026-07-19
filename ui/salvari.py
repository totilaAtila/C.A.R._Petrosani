from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLabel, QFrame, QFileDialog, QMessageBox, QProgressDialog,
    QTextEdit, QGroupBox, QListWidget, QSplitter, QListWidgetItem,
    QApplication, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import os
import sys
import shutil
import sqlite3
from datetime import datetime
import glob

# Importuri pentru dialoguri stilizate
from utils import (afiseaza_warning, afiseaza_eroare, afiseaza_info,
                   afiseaza_intrebare, input_intreg, input_text)
from dialog_styles import get_dialog_stylesheet

# Gardian scriere: blocheaza modificarile pe RON dupa conversie (doar-citire).
from permisiuni import poate_scrie, MESAJ_READONLY

# Paleta unica de stil (redesign "Glass Verde"). Doar culori/tokeni, fara logica.
from ui.palette import P, RADIUS


class BackupWorker(QThread):
    """Thread pentru operațiile de backup în background"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, source_dir, backup_dir, operation_type):
        super().__init__()
        self.source_dir = source_dir
        self.backup_dir = backup_dir
        self.operation_type = operation_type  # 'backup' sau 'restore'

    def run(self):
        try:
            if self.operation_type == 'backup':
                self._perform_backup()
            elif self.operation_type == 'restore':
                self._perform_restore()
        except Exception as e:
            self.finished.emit(False, str(e))

    def _perform_backup(self):
        db_files = glob.glob(os.path.join(self.source_dir, "*.db"))
        total_files = len(db_files)

        if total_files == 0:
            self.finished.emit(False, "Nu s-au găsit fișiere de baze de date!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(self.backup_dir, f"Backup_CAR_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)

        copied_files = 0
        for i, db_file in enumerate(db_files):
            filename = os.path.basename(db_file)
            self.status.emit(f"Copiez {filename}...")

            destination = os.path.join(backup_folder, filename)
            shutil.copy2(db_file, destination)

            copied_files += 1
            self.progress.emit(int((copied_files / total_files) * 100))

        self.finished.emit(True, f"Backup realizat cu succes!\n{copied_files} fișiere copiate în:\n{backup_folder}")

    def _perform_restore(self):
        db_files = glob.glob(os.path.join(self.backup_dir, "*.db"))
        total_files = len(db_files)

        if total_files == 0:
            self.finished.emit(False, "Nu s-au găsit fișiere de backup!")
            return

        copied_files = 0
        for i, db_file in enumerate(db_files):
            filename = os.path.basename(db_file)
            self.status.emit(f"Restaurez {filename}...")

            destination = os.path.join(self.source_dir, filename)
            shutil.copy2(db_file, destination)

            copied_files += 1
            self.progress.emit(int((copied_files / total_files) * 100))

        self.finished.emit(True, f"Restaurare completă!\n{copied_files} fișiere restaurate.")


class OperatiuniSalvareWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_directory = self._get_database_directory()
        self.backup_worker = None
        self._init_ui()
        self._apply_styles()
        self._update_status()

    def _get_database_directory(self):
        """Determină directorul cu bazele de date"""
        try:
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            else:
                return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except:
            return os.getcwd()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # === Panoul de Control (Stânga) ===
        control_frame = QFrame()
        control_frame.setObjectName("controlFrame")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(15)

        # Header cu titlu și ora
        header_layout = QHBoxLayout()
        title_label = QLabel("🛡️ Managementul Bazelor de Date")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignLeft)

        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignRight)

        # Timer pentru actualizarea orei
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)
        self._update_time()

        header_layout.addWidget(title_label)
        header_layout.addWidget(self.time_label)
        control_layout.addLayout(header_layout)

        # === Informații despre Director ===
        info_group = QGroupBox("📁 Informații Director")
        info_group.setObjectName("infoGroup")
        info_layout = QVBoxLayout(info_group)

        self.directory_label = QLabel()
        self.directory_label.setObjectName("directoryLabel")
        self.directory_label.setWordWrap(True)
        info_layout.addWidget(self.directory_label)

        change_dir_btn = QPushButton("📂 Schimbă Director")
        change_dir_btn.setObjectName("changeDirButton")
        change_dir_btn.clicked.connect(self._change_directory)
        info_layout.addWidget(change_dir_btn)

        control_layout.addWidget(info_group)

        # === Operațiuni Principale ===
        operations_group = QGroupBox("⚡ Operațiuni Principale")
        operations_group.setObjectName("operationsGroup")
        operations_layout = QGridLayout(operations_group)
        operations_layout.setSpacing(10)

        # Butonul de Backup
        backup_btn = QPushButton("💾 Backup Complet")
        backup_btn.setObjectName("backupButton")
        backup_btn.clicked.connect(self._create_backup)
        operations_layout.addWidget(backup_btn, 0, 0)

        # Butonul de Restaurare
        restore_btn = QPushButton("🔄 Restaurare")
        restore_btn.setObjectName("restoreButton")
        restore_btn.clicked.connect(self._restore_backup)
        operations_layout.addWidget(restore_btn, 0, 1)

        # Butonul de Ștergere An
        delete_year_btn = QPushButton("🗑️ Ștergere An")
        delete_year_btn.setObjectName("deleteYearButton")
        delete_year_btn.clicked.connect(self._delete_year)
        operations_layout.addWidget(delete_year_btn, 1, 0)

        # Butonul de Verificare Integritate
        check_integrity_btn = QPushButton("🔍 Verifică Integritatea")
        check_integrity_btn.setObjectName("checkIntegrityButton")
        check_integrity_btn.clicked.connect(self._check_database_integrity)
        operations_layout.addWidget(check_integrity_btn, 1, 1)

        control_layout.addWidget(operations_group)

        # === Operațiuni Rapide ===
        quick_group = QGroupBox("⚡ Acțiuni Rapide")
        quick_group.setObjectName("quickGroup")
        quick_layout = QVBoxLayout(quick_group)

        refresh_btn = QPushButton("🔄 Reîmprospătează Lista")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.clicked.connect(self._update_status)
        quick_layout.addWidget(refresh_btn)

        open_folder_btn = QPushButton("📂 Deschide în Explorer")
        open_folder_btn.setObjectName("openFolderButton")
        open_folder_btn.clicked.connect(self._open_in_explorer)
        quick_layout.addWidget(open_folder_btn)

        control_layout.addWidget(quick_group)

        # Spacer pentru a împinge totul în sus
        control_layout.addStretch()

        # === Panoul de Status (Dreapta) ===
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(10)

        # Lista cu fișiere găsite
        files_group = QGroupBox("📋 Fișiere Detectate")
        files_group.setObjectName("filesGroup")
        files_layout = QVBoxLayout(files_group)

        self.files_list = QListWidget()
        self.files_list.setObjectName("filesList")
        files_layout.addWidget(self.files_list)

        status_layout.addWidget(files_group)

        # Log zone
        log_group = QGroupBox("📝 Jurnal Operațiuni")
        log_group.setObjectName("logGroup")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setPlaceholderText("Operațiunile vor fi înregistrate aici...")
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        # Butoane pentru log
        log_buttons_layout = QHBoxLayout()

        clear_log_btn = QPushButton("🗑️ Curăță Log")
        clear_log_btn.setObjectName("clearLogButton")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_buttons_layout.addWidget(clear_log_btn)

        save_log_btn = QPushButton("💾 Salvează Log")
        save_log_btn.setObjectName("saveLogButton")
        save_log_btn.clicked.connect(self._save_log)
        log_buttons_layout.addWidget(save_log_btn)

        log_layout.addLayout(log_buttons_layout)
        status_layout.addWidget(log_group)

        # Adăugăm frame-urile la layout principal
        main_layout.addWidget(control_frame, 4)  # 40% width
        main_layout.addWidget(status_frame, 6)  # 60% width

    def _apply_styles(self):
        # Re-tematizare pe paleta unica (verde). Geometria (padding/font/min)
        # ramane; se schimba doar culorile -> tokeni. Rol butoane pastrat prin
        # culoare semantica: backup=ACCENT, restore=INFO, delete=DANGER,
        # verifica=WARNING, actiuni utilitare=NEUTRAL.
        self.setStyleSheet(f"""
            QLabel#titleLabel {{
                font-size: 16pt;
                font-weight: bold;
                color: {P.INK};
                margin-bottom: 5px;
            }}
            QLabel#timeLabel {{
                font-size: 12pt;
                color: {P.FAINT};
                margin-bottom: 5px;
            }}
            QLabel#directoryLabel {{
                font-size: 10pt;
                color: {P.MUTED};
                background-color: {P.PANEL_2};
                padding: 8px;
                border-radius: {RADIUS.SM};
                border: 1px solid {P.LINE};
            }}
            QFrame#controlFrame, QFrame#statusFrame {{
                border: 1px solid {P.LINE};
                border-radius: {RADIUS.LG};
                background-color: {P.PANEL_2};
                padding: 10px;
            }}
            QGroupBox {{
                font-size: 12pt;
                font-weight: bold;
                color: {P.INK};
                border: 1px solid {P.LINE};
                border-radius: {RADIUS.MD};
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: {P.PANEL_2};
                color: {P.MUTED};
            }}
            QPushButton#backupButton {{
                background-color: {P.ACCENT};
                color: {P.WHITE};
                border: 1px solid {P.ACCENT_DEEP};
                border-radius: {RADIUS.MD};
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton#backupButton:hover {{
                background-color: {P.ACCENT_DEEP};
            }}
            QPushButton#restoreButton {{
                background-color: {P.INFO};
                color: {P.WHITE};
                border: 1px solid {P.INFO_DEEP};
                border-radius: {RADIUS.MD};
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton#restoreButton:hover {{
                background-color: {P.INFO_DEEP};
            }}
            QPushButton#deleteYearButton {{
                background-color: {P.DANGER};
                color: {P.WHITE};
                border: 1px solid {P.DANGER_DEEP};
                border-radius: {RADIUS.MD};
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton#deleteYearButton:hover {{
                background-color: {P.DANGER_DEEP};
            }}
            QPushButton#checkIntegrityButton {{
                background-color: {P.WARNING};
                color: {P.WHITE};
                border: 1px solid {P.WARNING_DEEP};
                border-radius: {RADIUS.MD};
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton#checkIntegrityButton:hover {{
                background-color: {P.WARNING_DEEP};
            }}
            QPushButton#changeDirButton, QPushButton#refreshButton, QPushButton#openFolderButton {{
                background-color: {P.NEUTRAL};
                color: {P.WHITE};
                border: 1px solid {P.NEUTRAL_DEEP};
                border-radius: {RADIUS.SM};
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 15px;
            }}
            QPushButton#changeDirButton:hover, QPushButton#refreshButton:hover, QPushButton#openFolderButton:hover {{
                background-color: {P.NEUTRAL_DEEP};
            }}
            QPushButton#clearLogButton {{
                background-color: {P.DANGER};
                color: {P.WHITE};
                border: 1px solid {P.DANGER_DEEP};
                border-radius: {RADIUS.SM};
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: bold;
            }}
            QPushButton#clearLogButton:hover {{
                background-color: {P.DANGER_DEEP};
            }}
            QPushButton#saveLogButton {{
                background-color: {P.ACCENT};
                color: {P.WHITE};
                border: 1px solid {P.ACCENT_DEEP};
                border-radius: {RADIUS.SM};
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: bold;
            }}
            QPushButton#saveLogButton:hover {{
                background-color: {P.ACCENT_DEEP};
            }}
            QListWidget#filesList {{
                border: 1px solid {P.LINE};
                border-radius: {RADIUS.SM};
                background-color: {P.PANEL};
                font-size: 10pt;
                padding: 5px;
                min-height: 120px;
                color: {P.INK};
            }}
            QListWidget#filesList::item {{
                padding: 5px;
                border-bottom: 1px solid {P.LINE_SOFT};
            }}
            QListWidget#filesList::item:selected {{
                background-color: {P.ACCENT};
                color: {P.WHITE};
            }}
            QTextEdit#logText {{
                border: 1px solid {P.LINE};
                border-radius: {RADIUS.SM};
                background-color: {P.PANEL};
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                padding: 8px;
                color: {P.INK};
            }}
        """)

    def _update_time(self):
        """Actualizează afișajul cu ora curentă"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"🕐 {current_time}")

    def _update_status(self):
        """Actualizează informațiile despre directorul curent și fișierele găsite"""
        self.directory_label.setText(f"📁 {self.current_directory}")

        # Curățăm lista
        self.files_list.clear()

        # Găsim fișierele .db
        db_files = glob.glob(os.path.join(self.current_directory, "*.db"))

        if db_files:
            for db_file in sorted(db_files):
                filename = os.path.basename(db_file)
                file_size = os.path.getsize(db_file)
                size_mb = file_size / (1024 * 1024)

                item_text = f"📄 {filename} ({size_mb:.2f} MB)"
                item = QListWidgetItem(item_text)
                self.files_list.addItem(item)

            self._log_message(f"✅ Găsite {len(db_files)} fișiere de baze de date")
        else:
            item = QListWidgetItem("❌ Nu s-au găsit fișiere .db")
            self.files_list.addItem(item)
            self._log_message("⚠️ Nu s-au găsit fișiere de baze de date în directorul curent")

    def _log_message(self, message):
        """Adaugă un mesaj în jurnalul operațiunilor"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)

    def _change_directory(self):
        """Permite utilizatorului să schimbe directorul cu bazele de date"""
        new_directory = QFileDialog.getExistingDirectory(
            self,
            "Selectează directorul cu bazele de date",
            self.current_directory
        )

        if new_directory:
            self.current_directory = new_directory
            self._update_status()
            self._log_message(f"📂 Director schimbat: {new_directory}")

    def _create_backup(self):
        """Creează backup-ul bazelor de date"""
        backup_dir = QFileDialog.getExistingDirectory(
            self,
            "Selectează locația pentru backup",
            os.path.expanduser("~/Desktop")
        )

        if not backup_dir:
            return

        # Verificăm dacă avem fișiere de backup
        db_files = glob.glob(os.path.join(self.current_directory, "*.db"))
        if not db_files:
            afiseaza_warning("Nu s-au găsit fișiere de backup în directorul curent!", parent=self)
            return

        # Confirmăm operațiunea
        if not afiseaza_intrebare(
            f"Doriți să creați backup pentru {len(db_files)} fișiere?\n\nLocația: {backup_dir}",
            titlu="Confirmare Backup",
            parent=self
        ):
            return

        # Creăm dialog-ul de progres
        progress_dialog = QProgressDialog("Inițializare backup...", "Anulează", 0, 100, self)
        progress_dialog.setWindowTitle("Backup în progres")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        # Lansăm worker thread-ul
        self.backup_worker = BackupWorker(self.current_directory, backup_dir, 'backup')
        self.backup_worker.progress.connect(progress_dialog.setValue)
        self.backup_worker.status.connect(progress_dialog.setLabelText)
        self.backup_worker.finished.connect(lambda success, msg: self._backup_finished(success, msg, progress_dialog))
        progress_dialog.canceled.connect(self._cancel_operation)

        self.backup_worker.start()
        self._log_message("🚀 Backup pornit...")

    def _restore_backup(self):
        """Restaurează backup-ul bazelor de date"""
        backup_dir = QFileDialog.getExistingDirectory(
            self,
            "Selectează directorul cu backup-ul",
            os.path.expanduser("~/Desktop")
        )

        if not backup_dir:
            return

        # Verificăm dacă avem fișiere de restaurat
        db_files = glob.glob(os.path.join(backup_dir, "*.db"))
        if not db_files:
            afiseaza_warning("Nu s-au găsit fișiere de backup în directorul selectat!", parent=self)
            return

        # Avertizare serioasă
        msgBox = QMessageBox(self)
        msgBox.setStyleSheet(get_dialog_stylesheet())
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle("⚠️ ATENȚIE - Restaurare")
        msgBox.setText(
            f"ACEASTĂ OPERAȚIUNE VA SUPRASCRIE BAZELE DE DATE CURENTE!\n\n"
            f"Fișiere de restaurat: {len(db_files)}\n"
            f"Sursă: {backup_dir}\n"
            f"Destinație: {self.current_directory}\n\n"
            f"Sunteți absolut sigur că doriți să continuați?"
        )
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        reply = msgBox.exec_()

        if reply != QMessageBox.Yes:
            return

        # A doua confirmare
        if not afiseaza_intrebare(
            "Ultima șansă de a anula!\n\nConfirmați restaurarea?",
            titlu="Ultima Confirmare",
            parent=self,
            buton_default=QMessageBox.No
        ):
            return

        # Creăm dialog-ul de progres
        progress_dialog = QProgressDialog("Inițializare restaurare...", "Anulează", 0, 100, self)
        progress_dialog.setWindowTitle("Restaurare în progres")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        # Lansăm worker thread-ul
        self.backup_worker = BackupWorker(backup_dir, self.current_directory, 'restore')
        self.backup_worker.progress.connect(progress_dialog.setValue)
        self.backup_worker.status.connect(progress_dialog.setLabelText)
        self.backup_worker.finished.connect(lambda success, msg: self._backup_finished(success, msg, progress_dialog))
        progress_dialog.canceled.connect(self._cancel_operation)

        self.backup_worker.start()
        self._log_message("🔄 Restaurare pornită...")

    def _backup_finished(self, success, message, progress_dialog):
        """Gestionează finalizarea operațiunii de backup/restaurare"""
        progress_dialog.close()

        if success:
            afiseaza_info(message, parent=self)
            self._log_message(f"✅ {message}")
        else:
            afiseaza_eroare(f"Operațiunea a eșuat:\n{message}", parent=self)
            self._log_message(f"❌ Eroare: {message}")

        self._update_status()
        self.backup_worker = None

    def _cancel_operation(self):
        """Anulează operațiunea în curs"""
        if self.backup_worker and self.backup_worker.isRunning():
            self.backup_worker.terminate()
            self.backup_worker.wait()
            self._log_message("🛑 Operațiune anulată de utilizator")

    def _delete_year(self):
        """Șterge toate datele dintr-un an specificat"""
        # Gardian scriere: in modul RON post-conversie stergerea e interzisa
        # (arhiva RON e inghetata); modificarile se fac doar pe EUR.
        if not poate_scrie():
            afiseaza_warning(MESAJ_READONLY, parent=self)
            return

        year, ok = input_intreg(
            self,
            "Ștergere An",
            "Introduceți anul de șters (YYYY):",
            2024,
            2000,
            2100
        )

        if not ok:
            return

        # Avertizare foarte serioasă
        msgBox = QMessageBox(self)
        msgBox.setStyleSheet(get_dialog_stylesheet())
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle("🚨 ATENȚIE MAXIMĂ - Ștergere Definitivă")
        msgBox.setText(
            f"ACEASTĂ ACȚIUNE VA ȘTERGE DEFINITIV ȘI IREVERSIBIL\n"
            f"TOATE DATELE DIN ANUL {year}!\n\n"
            f"Nu există modalitate de recuperare după această operațiune!\n\n"
            f"Sunteți absolut sigur că doriți să ștergeți anul {year}?"
        )
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        reply = msgBox.exec_()

        if reply != QMessageBox.Yes:
            return

        # A doua confirmare cu scrierea anului
        text, ok = input_text(
            self,
            "Confirmare Finală",
            f"Pentru a confirma ștergerea definitivă,\n"
            f"tastați anul: {year}"
        )

        if not ok or text.strip() != str(year):
            afiseaza_info("Operațiunea a fost anulată.", parent=self)
            return

        try:
            # Căutăm fișierul DEPCRED.db
            depcred_path = os.path.join(self.current_directory, "DEPCRED.db")
            if not os.path.exists(depcred_path):
                afiseaza_warning("Nu s-a găsit fișierul DEPCRED.db!", parent=self)
                return

            # Conectăm la baza de date și ștergem
            conn = sqlite3.connect(depcred_path, timeout=30.0)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM DEPCRED WHERE anul = ?", (year,))
            deleted_rows = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_rows > 0:
                afiseaza_info(
                    f"S-au șters {deleted_rows} înregistrări din anul {year}.",
                    parent=self
                )
                self._log_message(f"🗑️ Șters anul {year}: {deleted_rows} înregistrări")
            else:
                afiseaza_info(
                    f"Nu s-au găsit înregistrări pentru anul {year}.",
                    parent=self
                )
                self._log_message(f"ℹ️ Anul {year} nu conținea date")

        except Exception as e:
            afiseaza_eroare(f"Eroare la ștergerea anului:\n{str(e)}", parent=self)
            self._log_message(f"❌ Eroare ștergere an {year}: {str(e)}")

    def _check_database_integrity(self):
        """Verifică integritatea bazelor de date"""
        db_files = glob.glob(os.path.join(self.current_directory, "*.db"))

        if not db_files:
            afiseaza_warning("Nu s-au găsit fișiere de baze de date!", parent=self)
            return

        progress_dialog = QProgressDialog("Verificare integritate...", "Anulează", 0, len(db_files), self)
        progress_dialog.setWindowTitle("Verificare în progres")
        progress_dialog.setWindowModality(Qt.WindowModal)

        results = []

        for i, db_file in enumerate(db_files):
            if progress_dialog.wasCanceled():
                break

            filename = os.path.basename(db_file)
            progress_dialog.setLabelText(f"Verificare {filename}...")

            try:
                conn = sqlite3.connect(db_file, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()

                if result == "ok":
                    results.append(f"✅ {filename}: OK")
                    self._log_message(f"✅ {filename}: Integritate OK")
                else:
                    results.append(f"❌ {filename}: {result}")
                    self._log_message(f"❌ {filename}: Probleme detectate")

            except Exception as e:
                results.append(f"⚠️ {filename}: Eroare - {str(e)}")
                self._log_message(f"⚠️ {filename}: Eroare verificare")

            progress_dialog.setValue(i + 1)

        progress_dialog.close()

        # Afișăm rezultatele
        result_text = "Rezultatele verificării integrității:\n\n" + "\n".join(results)
        afiseaza_info(result_text, parent=self)

    def _open_in_explorer(self):
        """Deschide directorul curent în Windows Explorer"""
        try:
            os.startfile(self.current_directory)
            self._log_message(f"📂 Deschis în Explorer: {self.current_directory}")
        except Exception as e:
            afiseaza_eroare(f"Nu s-a putut deschide Explorer:\n{str(e)}", parent=self)
            self._log_message(f"❌ Eroare deschidere Explorer: {str(e)}")

    def _save_log(self):
        """Salvează jurnalul operațiunilor"""
        if not self.log_text.toPlainText().strip():
            afiseaza_warning("Nu există conținut de salvat în jurnal!", parent=self)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"jurnal_salvari_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvează Jurnalul",
            default_filename,
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Jurnal Operațiuni Salvări - C.A.R. Petroșani\n")
                    f.write(f"Generat la: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(self.log_text.toPlainText())

                afiseaza_info(f"Jurnalul a fost salvat!\n\nLocație: {file_path}", parent=self)
                self._log_message(f"💾 Jurnal salvat: {file_path}")
            except Exception as e:
                afiseaza_eroare(f"Eroare la salvarea jurnalului:\n{e}", parent=self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OperatiuniSalvareWidget()
    window.setWindowTitle("Managementul Bazelor de Date - C.A.R.")
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())