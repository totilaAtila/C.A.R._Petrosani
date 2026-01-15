"""
security_manager.py - Modul pentru gestionarea securității bazelor de date MEMBRII

Acest modul oferă funcționalități pentru:
- Dezarhivare cu parolă la pornirea aplicației
- Arhivare cu parolă la închiderea aplicației
- Curățare baze de date expuse din crash-uri anterioare
- Gestionare completă erori și scenarii excepționale
- Suport pentru tranziția la euro (MEMBRII.db și MEMBRIIEUR.db)

Autor: C.A.R. Petroșani
Data: 2025
"""

import os
import sys
import zipfile  # Păstrat pentru compatibilitate verificare integritate
import pyzipper  # Criptare AES-256 reală
import sqlite3
import gc
import time
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QMessageBox,
    QProgressDialog,
    QApplication
)
from PyQt5.QtCore import Qt

# ==============================================================================
# DIALOG PERSONALIZAT PENTRU PAROLĂ
# ==============================================================================

class CustomPasswordDialog(QDialog):
    """
    Dialog personalizat pentru introducerea parolei cu opțiune de vizualizare.
    
    Oferă utilizatorului posibilitatea de a vizualiza parola introdusă
    prin bifarea opțiunii "Arată parola".
    """
    
    def __init__(self, parent=None, title="Autentificare", message="Introduceți parola:", 
                 attempt_info=None):
        """
        Inițializare dialog parolă
        
        Args:
            parent: Widget părinte
            title: Titlul ferestrei
            message: Mesajul principal de afișat
            attempt_info: Text cu informații despre încercare (ex: "Încercarea 1 din 3")
        """
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Mesaj principal
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Informații despre încercare (dacă există)
        if attempt_info:
            attempt_label = QLabel(attempt_info)
            attempt_label.setStyleSheet("font-weight: bold; color: #333;")
            layout.addWidget(attempt_label)
        
        # Label pentru câmp parolă
        password_label = QLabel("Parolă:")
        layout.addWidget(password_label)
        
        # Câmp pentru parolă
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(30)
        self.password_input.setPlaceholderText("Introduceți parola...")
        layout.addWidget(self.password_input)
        
        # Checkbox pentru arătare parolă
        self.show_password_checkbox = QCheckBox("Arată parola")
        self.show_password_checkbox.stateChanged.connect(self._toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)
        
        # Spațiu
        layout.addSpacing(10)
        
        # Butoane OK și Anulare
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setMinimumWidth(80)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Anulare")
        self.cancel_button.setMinimumWidth(80)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Focus pe câmpul de parolă
        self.password_input.setFocus()
    
    def _toggle_password_visibility(self, state):
        """
        Comută vizibilitatea parolei între mascat și text normal
        
        Args:
            state: Starea checkbox-ului (Qt.Checked sau Qt.Unchecked)
        """
        if state == Qt.Checked:
            # Arată parola ca text normal
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            # Mascare parolă
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def get_password(self):
        """
        Returnează parola introdusă
        
        Returns:
            str: Parola introdusă de utilizator
        """
        return self.password_input.text()
    
    @staticmethod
    def get_password_from_user(parent=None, title="Autentificare", 
                                message="Introduceți parola:", attempt_info=None):
        """
        Metodă statică pentru obținere rapidă parolă de la utilizator
        
        Args:
            parent: Widget părinte
            title: Titlul dialogului
            message: Mesajul de afișat
            attempt_info: Informații despre încercare
            
        Returns:
            tuple: (password: str, ok: bool)
                   password = parola introdusă (sau "" dacă anulat)
                   ok = True dacă user a apăsat OK, False dacă a anulat
        """
        dialog = CustomPasswordDialog(parent, title, message, attempt_info)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return dialog.get_password(), True
        else:
            return "", False


# ==============================================================================
# CONFIGURARE CONSTANTE
# ==============================================================================

# Liste baze de date de protejat (suport tranziție la euro)
DB_NAMES = ["MEMBRII.db", "MEMBRIIEUR.db"]

# Arhiva unică pentru toate bazele de date
ZIP_NAME = "MEMBRII.zip"

# Număr maxim de încercări pentru parolă
MAX_ATTEMPTS = 3


# ==============================================================================
# FUNCȚII HELPER PRIVATE
# ==============================================================================

def _show_progress_dialog(parent, title, message):
    """
    Afișează un dialog de progres pentru operații care durează
    
    Args:
        parent: Widget părinte pentru dialog
        title: Titlul dialogului
        message: Mesajul de afișat
        
    Returns:
        QProgressDialog: Instanța dialogului de progres
    """
    progress = QProgressDialog(message, None, 0, 0, parent)
    progress.setWindowTitle(title)
    progress.setWindowModality(Qt.WindowModal)
    progress.setCancelButton(None)
    progress.setMinimumDuration(0)
    progress.setValue(0)
    
    # Force update UI
    QApplication.processEvents()
    
    return progress


def _get_existing_databases():
    """
    Returnează lista bazelor de date care există pe disc
    
    Returns:
        list: Lista cu numele bazelor de date care există
    """
    return [db for db in DB_NAMES if os.path.exists(db)]


def _verify_zip_integrity(zip_path):
    """
    Verifică integritatea de bază a arhivei ZIP (criptată sau nu).

    NOTĂ: Pentru arhive criptate AES-256, verificarea completă de integritate
    nu este posibilă fără parolă. Funcția verifică doar:
    - Că fișierul este o arhivă ZIP validă
    - Că există cel puțin o bază de date în listă

    Verificarea reală de integritate și parolă se face la extragere.

    Args:
        zip_path: Calea către fișierul ZIP

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        # Folosim pyzipper care poate lucra cu arhive criptate
        with pyzipper.AESZipFile(zip_path, 'r') as zf:
            # Verifică dacă există măcar o bază de date în arhivă
            # namelist() funcționează fără parolă - returnează numele fișierelor
            files_in_archive = zf.namelist()

            if not files_in_archive:
                return False, "Arhiva este goală"

            db_found = any(db in files_in_archive for db in DB_NAMES)

            if not db_found:
                return False, f"Nicio bază de date validă găsită în arhivă (așteptat: {', '.join(DB_NAMES)})"

            # Pentru arhive criptate, testzip() nu funcționează fără parolă
            # Verificarea completă de integritate se va face la extragere
            # când utilizatorul introduce parola corectă

            return True, None

    except zipfile.BadZipFile:
        return False, "Arhiva este coruptă sau invalidă (format ZIP incorect)"
    except Exception as e:
        # Dacă primim eroare de tip "password required", arhiva e validă dar criptată
        if "password" in str(e).lower() or "encrypted" in str(e).lower():
            # Arhiva este criptată - OK, nu putem verifica fără parolă
            # Verificarea se va face la extragere
            return True, None
        return False, f"Eroare la verificare: {str(e)}"


def _test_password(zip_path, password):
    """
    Testează dacă parola este corectă pentru arhiva dată (criptată cu AES-256)

    Args:
        zip_path: Calea către fișierul ZIP
        password: Parola de testat

    Returns:
        bool: True dacă parola este corectă, False altfel
    """
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zf:
            zf.setpassword(password.encode('utf-8'))

            # Încearcă să citească info și să extragă primul byte din primul fișier
            # Dacă parola e greșită, va arunca RuntimeError sau BadZipFile
            files_in_archive = zf.namelist()
            if files_in_archive:
                # Încearcă să citească efectiv date (nu doar info)
                # Aceasta este singura metodă sigură de testare parolă cu AES
                first_file = files_in_archive[0]
                zf.read(first_file, pwd=password.encode('utf-8'))

            return True

    except RuntimeError as e:
        # Parolă incorectă
        if "Bad password" in str(e) or "password" in str(e).lower():
            return False
        # Altă eroare Runtime
        raise
    except (zipfile.BadZipFile, Exception) as e:
        # Parolă incorectă poate manifesta și ca BadZipFile cu pyzipper
        if "password" in str(e).lower() or "bad" in str(e).lower():
            return False
        # Altă eroare
        raise


def _force_close_database_connections():
    """
    Forțează închiderea TUTUROR conexiunilor active la bazele de date SQLite.

    Această funcție este CRITICĂ pentru a preveni WinError 32 (file locked)
    la arhivarea bazelor de date pe Windows.

    Procedură:
    1. Găsește toate conexiunile sqlite3.Connection active în memorie
    2. Execută PRAGMA wal_checkpoint(TRUNCATE) pentru fiecare DB
    3. Închide explicit toate conexiunile
    4. Forțează garbage collection pentru cleanup
    5. Așteaptă scurt pentru eliberare file locks de către Windows

    Returns:
        int: Numărul de conexiuni închise
    """
    closed_count = 0

    # Database names to checkpoint
    db_files = _get_existing_databases()

    # Step 1: WAL checkpoint pe toate DB-urile existente
    # Aceasta forțează scrierea tuturor tranzacțiilor pending în fișierul principal
    for db_file in db_files:
        try:
            # Conexiune temporară DOAR pentru checkpoint
            temp_conn = sqlite3.connect(db_file, timeout=5.0)
            temp_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            temp_conn.commit()
            temp_conn.close()
            print(f"[OK] WAL checkpoint executat pentru {db_file}")
        except Exception as e:
            print(f"[WARNING] WAL checkpoint esuat pentru {db_file}: {e}")

    # Step 2: Găsește și închide TOATE conexiunile sqlite3 active din memorie
    # Folosim garbage collector pentru a găsi toate obiectele Connection
    for obj in gc.get_objects():
        try:
            if isinstance(obj, sqlite3.Connection):
                # Încearcă să aflăm la ce DB este conectat (pentru logging)
                db_path = "unknown"
                try:
                    # Execută un query dummy pentru a verifica dacă conexiunea e activă
                    obj.execute("SELECT 1")
                    # Dacă reușește, conexiunea e activă și trebuie închisă
                except sqlite3.ProgrammingError:
                    # Conexiunea e deja închisă, skip
                    continue
                except Exception:
                    pass

                # Închide conexiunea
                try:
                    obj.close()
                    closed_count += 1
                    print(f"[OK] Conexiune sqlite3 inchisa: {db_path}")
                except Exception as e:
                    print(f"[WARNING] Nu s-a putut inchide conexiune: {e}")
        except Exception:
            # Ignoră orice erori la iterare prin gc.get_objects()
            pass

    # Step 3: Forțează garbage collection pentru cleanup final
    gc.collect()

    # Step 4: Așteaptă scurt pentru ca Windows să elibereze file locks
    # Windows poate avea delay în eliberarea handle-urilor de fișiere
    if closed_count > 0:
        time.sleep(0.5)  # 500ms - suficient pentru Windows file system
        print(f"[OK] Total {closed_count} conexiuni sqlite3 inchise")

    return closed_count


# ==============================================================================
# FUNCȚII PUBLICE PRINCIPALE
# ==============================================================================

def cleanup_exposed_database():
    """
    Verifică și curăță bazele de date care au rămas expuse
    din cauza unui crash sau închidere anormală anterioară.
    
    Gestionează atât MEMBRII.db cât și MEMBRIIEUR.db.
    
    Această funcție trebuie apelată la pornirea aplicației,
    ÎNAINTE de orice altă operație.
    
    Returns:
        bool: True dacă totul e OK, False dacă trebuie să se oprească aplicația
    """
    exposed_dbs = _get_existing_databases()
    
    # Verificare: există baze de date expuse?
    if exposed_dbs and os.path.exists(ZIP_NAME):
        # Baze de date expuse din crash anterior
        
        # Verifică dacă vreuna dintre ele este mai recentă decât arhiva
        zip_time = os.path.getmtime(ZIP_NAME)
        newer_dbs = []
        
        for db in exposed_dbs:
            db_time = os.path.getmtime(db)
            if db_time > zip_time:
                newer_dbs.append(db)
        
        if newer_dbs:
            # Cel puțin o bază de date pare mai recentă → Posibil date noi
            db_list = "\n".join([f"• {db}" for db in exposed_dbs])
            newer_list = "\n".join([f"• {db}" for db in newer_dbs])

            # Dialog cu butoane clare
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Baze de date neprotejate detectate")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText(
                f"Următoarele baze de date au fost găsite neprotejate pe disc:\n{db_list}\n\n"
                f"Următoarele par mai recente decât arhiva:\n{newer_list}\n\n"
                f"Aceasta sugerează că aplicația s-a închis anormal și\n"
                f"ar putea conține date nesalvate."
            )
            msg_box.setInformativeText("Doriți să arhivați aceste fișiere înainte de ștergere?")

            btn_arhiveaza = msg_box.addButton("Arhivează (recomandat)", QMessageBox.AcceptRole)
            btn_sterge = msg_box.addButton("Șterge fără arhivare", QMessageBox.RejectRole)
            msg_box.setDefaultButton(btn_arhiveaza)

            msg_box.exec_()

            clicked = msg_box.clickedButton()
            # Edge case: utilizatorul a închis dialogul prin X → tratăm ca "arhivează" (opțiunea sigură)
            if clicked == btn_arhiveaza or clicked is None:
                # Solicită parolă pentru arhivare
                if not archive_database_with_password(None):
                    # User a anulat sau a eșuat arhivarea
                    err_box = QMessageBox()
                    err_box.setWindowTitle("Eroare critică")
                    err_box.setIcon(QMessageBox.Critical)
                    err_box.setText(
                        f"Nu s-au putut arhiva bazele de date.\n\n"
                        f"Aplicația nu poate porni în siguranță."
                    )
                    err_box.setInformativeText(
                        f"Opțiuni:\n"
                        f"• Arhivați manual fișierele\n"
                        f"• Contactați suportul tehnic"
                    )

                    btn_oprire = err_box.addButton("Oprire aplicație", QMessageBox.AcceptRole)
                    btn_ignora = err_box.addButton("Ignoră (RISC DATE)", QMessageBox.RejectRole)
                    err_box.setDefaultButton(btn_oprire)

                    err_box.exec_()

                    if err_box.clickedButton() == btn_oprire or err_box.clickedButton() is None:
                        return False  # Oprește aplicația
                    # Dacă Ignoră, continuă cu ștergerea
        
        else:
            # Toate DB-urile sunt mai vechi sau la fel → Probabil nu conțin date noi
            db_list = "\n".join([f"• {db}" for db in exposed_dbs])
            
            QMessageBox.information(
                None,
                "Curățare necesară",
                f"Următoarele baze de date au fost găsite neprotejate pe disc:\n{db_list}\n\n"
                f"Acestea vor fi șterse pentru siguranță.\n"
                f"(Arhiva '{ZIP_NAME}' conține versiunea protejată)",
                QMessageBox.Ok
            )
        
        # Șterge toate DB-urile expuse
        for db in exposed_dbs:
            try:
                os.remove(db)
                print(f"✓ {db} expus a fost curățat")
            except Exception as e:
                QMessageBox.critical(
                    None,
                    "Eroare",
                    f"Nu s-a putut șterge '{db}':\n{e}"
                )
                return False
    
    # Verificare: există DB-uri dar lipsește arhiva?
    elif exposed_dbs and not os.path.exists(ZIP_NAME):
        db_list = "\n".join([f"• {db}" for db in exposed_dbs])

        # Dialog cu butoane clare
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Configurare incompletă")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(
            f"Următoarele baze de date există dar arhiva '{ZIP_NAME}' lipsește:\n{db_list}\n\n"
            f"Aceasta este o configurare invalidă."
        )
        msg_box.setInformativeText("Doriți să creați arhiva acum? (Veți fi întrebat parola)")

        btn_creaza = msg_box.addButton("Creează arhiva", QMessageBox.AcceptRole)
        btn_anuleaza = msg_box.addButton("Anulează", QMessageBox.RejectRole)
        msg_box.setDefaultButton(btn_creaza)

        msg_box.exec_()

        clicked = msg_box.clickedButton()
        if clicked == btn_creaza:
            if not archive_database_with_password(None):
                QMessageBox.critical(
                    None,
                    "Eroare",
                    "Aplicația nu poate porni fără arhivă validă."
                )
                return False
        else:
            # User a anulat sau a închis dialogul prin X
            QMessageBox.critical(
                None,
                "Configurare invalidă",
                "Aplicația nu poate porni fără arhivă protejată."
            )
            return False
    
    return True


def extract_database_with_password():
    """
    Solicită parola utilizatorului și încearcă dezarhivarea MEMBRII.zip.
    
    Extrage TOATE bazele de date prezente în arhivă:
    - MEMBRII.db (dacă există)
    - MEMBRIIEUR.db (dacă există)
    - Sau ambele
    
    Această funcție trebuie apelată la pornirea aplicației,
    DUPĂ cleanup_exposed_database().
    
    Oferă MAX_ATTEMPTS încercări pentru introducerea parolei corecte.
    
    Returns:
        bool: True dacă dezarhivare reușită, False altfel
    """
    # Verificare: arhiva există?
    if not os.path.exists(ZIP_NAME):
        QMessageBox.critical(
            None,
            "Arhivă lipsă",
            f"Fișierul '{ZIP_NAME}' nu a fost găsit!\n\n"
            f"Pentru prima utilizare:\n"
            f"1. Asigurațivă că MEMBRII.db și/sau MEMBRIIEUR.db sunt în același director cu aplicația\n"
            f"2. Reporniți aplicația\n"
            f"3. Introduceți o parolă\n"
            f"4. Confirmați parola pentru arhivare\n"
            f"5. Aplicația va funcționa normal\n\n"
            
            f"Pentru utilizare normală:\n"
            f"• Verificați că fișierul '{ZIP_NAME}' există\n"
            f"• Verificați că nu a fost mutat sau șters"
        )
        return False
    
    # Verificare integritate arhivă
    integrity_ok, error_msg = _verify_zip_integrity(ZIP_NAME)
    if not integrity_ok:
        QMessageBox.critical(
            None,
            "Arhivă invalidă",
            f"Arhiva '{ZIP_NAME}' este coruptă sau invalidă!\n\n"
            f"Detalii: {error_msg}\n\n"
            f"Acțiuni recomandate:\n"
            f"• Restaurați dintr-un backup\n"
            f"• Verificați integritatea fișierului\n"
            f"• Contactați suportul tehnic"
        )
        return False
    
    # Bucla de solicitare parolă cu retry
    for attempt in range(1, MAX_ATTEMPTS + 1):
        password, ok = CustomPasswordDialog.get_password_from_user(
            parent=None,
            title="Autentificare necesară",
            message="Introduceți parola pentru deschiderea bazelor de date:",
            attempt_info=f"Încercarea {attempt} din {MAX_ATTEMPTS}"
        )
        
        if not ok:
            # User a anulat
            QMessageBox.warning(
                None,
                "Autentificare anulată",
                "Aplicația nu poate porni fără autentificare validă.\n\n"
                "Bazele de date sunt protejate și necesită parolă pentru acces."
            )
            return False
        
        if not password:
            # Parolă goală
            QMessageBox.warning(
                None,
                "Parolă invalidă",
                "Parola nu poate fi goală.\n\n"
                f"Mai aveți {MAX_ATTEMPTS - attempt} încercări."
            )
            continue
        
        # Testează parola
        try:
            if _test_password(ZIP_NAME, password):
                # Parolă corectă → Extrage bazele de date
                progress = _show_progress_dialog(
                    None,
                    "Autentificare",
                    "Se încarcă bazele de date..."
                )
                
                try:
                    with pyzipper.AESZipFile(ZIP_NAME, 'r') as zf:
                        zf.setpassword(password.encode('utf-8'))
                        zf.extractall(pwd=password.encode('utf-8'))

                    progress.close()
                    
                    # Verifică ce s-a extras
                    extracted = _get_existing_databases()
                    if extracted:
                        db_list = ", ".join(extracted)
                        print(f"✓ Autentificare reușită, extrase: {db_list}")
                    else:
                        print(f"⚠ Autentificare reușită dar nicio bază de date găsită")
                    
                    return True
                    
                except Exception as e:
                    progress.close()
                    QMessageBox.critical(
                        None,
                        "Eroare la extragere",
                        f"Nu s-au putut extrage bazele de date!\n\n"
                        f"Eroare: {e}\n\n"
                        f"Contactați suportul tehnic."
                    )
                    return False
            
            else:
                # Parolă incorectă
                if attempt < MAX_ATTEMPTS:
                    QMessageBox.warning(
                        None,
                        "Parolă incorectă",
                        f"Parola introdusă este incorectă.\n\n"
                        f"Mai aveți {MAX_ATTEMPTS - attempt} încercări."
                    )
                else:
                    # Ultima încercare eșuată
                    QMessageBox.critical(
                        None,
                        "Acces refuzat",
                        f"Parolă incorectă după {MAX_ATTEMPTS} încercări.\n\n"
                        f"Aplicația se va închide.\n\n"
                        f"Dacă ați uitat parola:\n"
                        f"• Contactați administratorul\n"
                        f"• Restaurați dintr-un backup cunoscut"
                    )
                    return False
        
        except Exception as e:
            # Eroare neprevăzută la testare parolă
            QMessageBox.critical(
                None,
                "Eroare critică",
                f"Eroare neprevăzută la verificare parolă:\n{e}\n\n"
                f"Contactați suportul tehnic."
            )
            return False
    
    # Nu ar trebui să ajungă aici niciodată
    return False


def archive_database_with_password(parent_widget):
    """
    Solicită parola utilizatorului și arhivează toate bazele de date existente.
    
    Arhivează în MEMBRII.zip:
    - MEMBRII.db (dacă există)
    - MEMBRIIEUR.db (dacă există)  
    - Sau ambele
    
    Utilizatorul poate introduce:
    - Aceeași parolă (păstrare parolă)
    - O parolă nouă (schimbare parolă)
    
    Această funcție trebuie apelată la închiderea aplicației.
    
    Args:
        parent_widget: Widget părinte pentru dialoguri (poate fi None)
        
    Returns:
        bool: True dacă arhivare reușită sau user acceptă închidere fără arhivare,
              False dacă user dorește să rămână în aplicație
    """
    # Verificare: există baze de date de arhivat?
    existing_dbs = _get_existing_databases()
    
    if not existing_dbs:
        # Nicio bază de date → Nimic de arhivat
        # Asta e OK, posibil DB-urile au fost deja arhivate
        print(f"⚠ Nicio bază de date găsită, nu este nimic de arhivat")
        return True
    
    db_list = "\n".join([f"• {db}" for db in existing_dbs])
    
    # Solicită parola pentru arhivare
    password, ok = CustomPasswordDialog.get_password_from_user(
        parent=parent_widget,
        title="Securizare necesară",
        message=f"Introduceți parola pentru arhivarea bazelor de date:\n\n"
                f"Baze de date de arhivat:\n{db_list}\n\n"
                f"Această parolă va fi necesară la următoarea deschidere.\n\n"
                f"Puteți introduce:\n"
                f"• Aceeași parolă (păstrare)\n"
                f"• O parolă nouă (schimbare)"
    )
    
    if not ok:
        # User a anulat → Întreabă ce dorește să facă cu butoane clare
        msg_box = QMessageBox(parent_widget)
        msg_box.setWindowTitle("Arhivare anulată")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(
            f"Arhivarea a fost anulată.\n\n"
            f"Fără arhivare, următoarele fișiere vor rămâne\n"
            f"NEPROTEJATE pe disc:\n{db_list}"
        )
        msg_box.setInformativeText("Ce doriți să faceți?")

        # Butoane personalizate clare pentru utilizator
        btn_ramai = msg_box.addButton("Rămân în aplicație", QMessageBox.AcceptRole)
        btn_iesire = msg_box.addButton("Ieșire fără arhivare", QMessageBox.RejectRole)

        # Setează butonul implicit (recomandat)
        msg_box.setDefaultButton(btn_ramai)

        msg_box.exec_()

        clicked = msg_box.clickedButton()
        # Edge case: utilizatorul a închis dialogul prin X → tratăm ca "Rămân în aplicație" (opțiunea sigură)
        if clicked == btn_ramai or clicked is None:
            # User dorește să rămână în aplicație pentru a încerca din nou
            return False
        else:
            # User a apăsat explicit "Ieșire fără arhivare" - acceptă riscul
            QMessageBox.warning(
                parent_widget,
                "Avertisment securitate",
                f"ATENȚIE: Următoarele fișiere vor rămâne NEPROTEJATE pe disc:\n{db_list}\n\n"
                f"Recomandări:\n"
                f"• Arhivați manual fișierele\n"
                f"• Sau reporniți aplicația și arhivați corect"
            )
            return True
    
    if not password:
        # Parolă goală
        QMessageBox.warning(
            parent_widget,
            "Parolă invalidă",
            "Parola nu poate fi goală.\n\n"
            "Încercați din nou."
        )
        return False
    
    # CRITICAL: Închide TOATE conexiunile active la DB ÎNAINTE de arhivare
    # Previne WinError 32 (file locked) pe Windows
    print("[INFO] Inchidere conexiuni active la baze de date...")
    closed_count = _force_close_database_connections()
    print(f"[OK] {closed_count} conexiuni inchise, gata pentru arhivare")

    # Arhivează cu parola introdusă
    progress = _show_progress_dialog(
        parent_widget,
        "Securizare",
        f"Se arhivează bazele de date..."
    )

    try:
        # Creează arhiva nouă cu criptare AES-256 (suprascrie cea veche)
        with pyzipper.AESZipFile(ZIP_NAME, 'w',
                                  compression=pyzipper.ZIP_DEFLATED,
                                  encryption=pyzipper.WZ_AES) as zf:
            # Setează parola pentru criptare AES-256
            zf.setpassword(password.encode('utf-8'))

            # Arhivează toate bazele de date existente cu criptare
            for db in existing_dbs:
                zf.write(db, compress_type=pyzipper.ZIP_DEFLATED)
                print(f"[OK] {db} adaugat in arhiva cu criptare AES-256")

        print(f"[OK] Arhivare completa cu criptare AES-256: {', '.join(existing_dbs)}")
        
        # Șterge toate DB-urile de pe disc
        for db in existing_dbs:
            os.remove(db)
            print(f"✓ {db} șters de pe disc")
        
        progress.close()
        return True
        
    except Exception as e:
        progress.close()
        
        QMessageBox.critical(
            parent_widget,
            "Eroare la arhivare",
            f"Nu s-au putut arhiva bazele de date!\n\n"
            f"Eroare: {e}\n\n"
            f"Aplicația nu se poate închide în siguranță.\n"
            f"Verificați:\n"
            f"• Spațiu disponibil pe disc\n"
            f"• Permisiuni de scriere\n"
            f"• Arhiva nu este deschisă în alt program\n\n"
            f"Încercați din nou sau contactați suportul."
        )
        return False


# ==============================================================================
# FUNCȚII UTILITARE PENTRU DEBUGGING
# ==============================================================================

def get_security_status():
    """
    Returnează status-ul curent al sistemului de securitate.
    Util pentru debugging și logging.
    
    Returns:
        dict: Dicționar cu informații despre status
    """
    status = {
        'zip_exists': os.path.exists(ZIP_NAME),
        'zip_size': os.path.getsize(ZIP_NAME) if os.path.exists(ZIP_NAME) else 0,
    }
    
    # Status pentru fiecare bază de date
    for db in DB_NAMES:
        db_key = db.replace('.', '_')
        status[f'{db_key}_exists'] = os.path.exists(db)
        status[f'{db_key}_size'] = os.path.getsize(db) if os.path.exists(db) else 0
    
    # Verificare integritate arhivă
    if status['zip_exists']:
        integrity_ok, error_msg = _verify_zip_integrity(ZIP_NAME)
        status['zip_integrity'] = 'OK' if integrity_ok else f'ERROR: {error_msg}'
        
        # Verifică ce conține arhiva (funcționează cu arhive criptate AES)
        try:
            with pyzipper.AESZipFile(ZIP_NAME, 'r') as zf:
                status['zip_contents'] = zf.namelist()
        except:
            status['zip_contents'] = []
    else:
        status['zip_integrity'] = 'N/A'
        status['zip_contents'] = []
    
    return status


def print_security_status():
    """
    Afișează status-ul sistemului de securitate în consolă.
    Util pentru debugging.
    """
    status = get_security_status()
    
    print("\n" + "="*60)
    print("STATUS SISTEM SECURITATE")
    print("="*60)
    print(f"Arhivă ({ZIP_NAME}):")
    print(f"  Există: {status['zip_exists']}")
    print(f"  Mărime: {status['zip_size']} bytes")
    print(f"  Integritate: {status['zip_integrity']}")
    print(f"  Conținut: {', '.join(status['zip_contents']) if status['zip_contents'] else 'N/A'}")
    
    for db in DB_NAMES:
        db_key = db.replace('.', '_')
        print(f"\nBază de date ({db}):")
        print(f"  Există: {status[f'{db_key}_exists']}")
        print(f"  Mărime: {status[f'{db_key}_size']} bytes")
    
    print("="*60 + "\n")


# ==============================================================================
# MAIN - Pentru testare standalone
# ==============================================================================

if __name__ == "__main__":
    """
    Cod de testare pentru modulul security_manager.
    NU se execută când modulul este importat.
    """
    print("TESTARE MODUL security_manager.py")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    print("\n1. Verificare status inițial:")
    print_security_status()
    
    print("\n2. Test cleanup:")
    if cleanup_exposed_database():
        print("✓ Cleanup OK")
    else:
        print("✗ Cleanup eșuat")
        sys.exit(1)
    
    print("\n3. Test extragere:")
    if extract_database_with_password():
        print("✓ Extragere OK")
    else:
        print("✗ Extragere eșuată")
        sys.exit(1)
    
    print("\n4. Verificare status după extragere:")
    print_security_status()
    
    print("\n5. Test arhivare:")
    if archive_database_with_password(None):
        print("✓ Arhivare OK")
    else:
        print("✗ Arhivare eșuată")
    
    print("\n6. Verificare status final:")
    print_security_status()
    
    print("\n" + "="*60)
    print("TESTARE COMPLETĂ")
    print("="*60)
