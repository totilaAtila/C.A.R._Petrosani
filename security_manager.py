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
import zipfile
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
    Verifică integritatea arhivei ZIP
    
    Args:
        zip_path: Calea către fișierul ZIP
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Testează integritatea fișierelor din arhivă
            bad_file = zf.testzip()
            if bad_file:
                return False, f"Fișierul '{bad_file}' din arhivă este corupt"
            
            # Verifică dacă există măcar o bază de date în arhivă
            files_in_archive = zf.namelist()
            db_found = any(db in files_in_archive for db in DB_NAMES)
            
            if not db_found:
                return False, f"Nicio bază de date validă găsită în arhivă (așteptat: {', '.join(DB_NAMES)})"
            
            return True, None
            
    except zipfile.BadZipFile:
        return False, "Arhiva este coruptă sau invalidă"
    except Exception as e:
        return False, f"Eroare la verificare: {str(e)}"


def _test_password(zip_path, password):
    """
    Testează dacă parola este corectă pentru arhiva dată
    
    Args:
        zip_path: Calea către fișierul ZIP
        password: Parola de testat
        
    Returns:
        bool: True dacă parola este corectă, False altfel
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.setpassword(password.encode('utf-8'))
            
            # Încearcă să citească info despre primul fișier din arhivă
            # Dacă parola e greșită, va arunca RuntimeError
            files_in_archive = zf.namelist()
            if files_in_archive:
                info = zf.getinfo(files_in_archive[0])
            
            return True
            
    except RuntimeError as e:
        # Parolă incorectă
        if "Bad password" in str(e) or "password" in str(e).lower():
            return False
        # Altă eroare Runtime
        raise
    except Exception:
        # Alte erori (nu legate de parolă)
        raise


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
            
            result = QMessageBox.question(
                None,
                "Baze de date neprotejate detectate",
                f"Următoarele baze de date au fost găsite neprotejate pe disc:\n{db_list}\n\n"
                f"Următoarele par mai recente decât arhiva:\n{newer_list}\n\n"
                f"Aceasta sugerează că aplicația s-a închis anormal și\n"
                f"ar putea conține date nesalvate.\n\n"
                f"Doriți să arhivați aceste fișiere înainte de ștergere?\n"
                f"(Veți fi întrebat parola pentru arhivare)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if result == QMessageBox.Yes:
                # Solicită parolă pentru arhivare
                if not archive_database_with_password(None):
                    # User a anulat sau a eșuat arhivarea
                    result = QMessageBox.critical(
                        None,
                        "Eroare critică",
                        f"Nu s-au putut arhiva bazele de date.\n\n"
                        f"Aplicația nu poate porni în siguranță.\n\n"
                        f"Opțiuni:\n"
                        f"• Arhivați manual fișierele\n"
                        f"• Contactați suportul tehnic\n"
                        f"• Ignorați și ștergeți fișierele (RISC PIERDERE DATE)",
                        QMessageBox.Abort | QMessageBox.Ignore,
                        QMessageBox.Abort
                    )
                    
                    if result == QMessageBox.Abort:
                        return False  # Oprește aplicația
                    # Dacă Ignore, continuă cu ștergerea
        
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
        
        result = QMessageBox.warning(
            None,
            "Configurare incompletă",
            f"Următoarele baze de date există dar arhiva '{ZIP_NAME}' lipsește:\n{db_list}\n\n"
            f"Aceasta este o configurare invalidă.\n\n"
            f"Doriți să creați arhiva acum?\n"
            f"(Veți fi întrebat parola pentru arhivare)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if result == QMessageBox.Yes:
            if not archive_database_with_password(None):
                QMessageBox.critical(
                    None,
                    "Eroare",
                    "Aplicația nu poate porni fără arhivă validă."
                )
                return False
        else:
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
            f"1. Creați arhiva cu parolă din bazele de date\n"
            f"2. Denumiți arhiva '{ZIP_NAME}'\n"
            f"3. Plasați-o în același director cu aplicația\n"
            f"4. Reporniți aplicația\n\n"
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
                    with zipfile.ZipFile(ZIP_NAME, 'r') as zf:
                        zf.setpassword(password.encode('utf-8'))
                        zf.extractall()
                    
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
        # User a anulat → Întreabă ce dorește să facă
        result = QMessageBox.question(
            parent_widget,
            "Arhivare anulată",
            f"Arhivarea a fost anulată.\n\n"
            f"Fără arhivare, următoarele fișiere vor rămâne\n"
            f"NEPROTEJATE pe disc:\n{db_list}\n\n"
            f"Ce doriți să faceți?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if result == QMessageBox.Yes:
            # User dorește să rămână în aplicație
            return False
        else:
            # User acceptă riscul și dorește să închidă oricum
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
    
    # Arhivează cu parola introdusă
    progress = _show_progress_dialog(
        parent_widget,
        "Securizare",
        f"Se arhivează bazele de date..."
    )
    
    try:
        # Creează arhiva nouă (suprascrie cea veche)
        with zipfile.ZipFile(ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.setpassword(password.encode('utf-8'))
            
            # Arhivează toate bazele de date existente
            for db in existing_dbs:
                zf.write(db)
                print(f"✓ {db} adăugat în arhivă")
        
        print(f"✓ Arhivare completă: {', '.join(existing_dbs)}")
        
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
        
        # Verifică ce conține arhiva
        try:
            with zipfile.ZipFile(ZIP_NAME, 'r') as zf:
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
