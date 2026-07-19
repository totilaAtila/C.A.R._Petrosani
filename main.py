# main.py
from PyQt5.QtCore import Qt
import sys
import os
import builtins  # Import corect pentru monkey patching

# === ADAUGĂ ACEST COD ÎNAINTE DE ORICE ALTCEVA ===
if sys.platform == "darwin":
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
# === Sfârșit cod adăugat ===
from PyQt5.QtWidgets import QApplication

# ===== INTEGRARE SECURITATE: Import modul de securitate =====
from security_manager import (
    cleanup_exposed_database,
    extract_database_with_password
)
# ===== Sfârșit integrare securitate =====


def setup_early_database_patching():
    """Configurează patchuirea bazelor de date ÎNAINTE de importuri"""
    from currency_logic import CurrencyLogic
    from pathlib import Path

    currency_logic = CurrencyLogic()

    # Maparea bazelor RON -> EUR (DOAR cele procesate de conversie_widget.py)
    db_mapping = {
        "MEMBRII.db": "MEMBRIIEUR.db",
        "DEPCRED.db": "DEPCREDEUR.db",
        # Cheia trebuie scrisă exact ca în modulele UI (DB_ACTIVI = "ACTIVI.db").
        # Era "activi.db", iar potrivirea de mai jos e pe subșir: "activi.db" nu se
        # regăsește în "ACTIVI.db", deci DB_ACTIVI nu era patchuit NICIODATĂ, iar în
        # modul EUR se citea și se scria în baza RON. Fișierul EUR chiar se numește
        # cu 'a' mic — așa îl creează conversie_widget.py.
        "ACTIVI.db": "activiEUR.db",
        "INACTIVI.db": "INACTIVIEUR.db",
        "LICHIDATI.db": "LICHIDATIEUR.db"
        # NOTĂ: CHITANTE.db nu se convertește - este doar pentru tipărire
    }

    def patch_module_database_paths(module):
        """Patchuiește căile din modulul dat"""
        base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

        for attr_name in dir(module):
            # Unificat: verificăm toate atributele DB_* pentru consistență cu main_ui.py
            if attr_name.startswith('DB_'):
                current_value = getattr(module, attr_name)

                # Verifică dacă trebuie să folosească EUR
                if (currency_logic.conversion_applied and
                        currency_logic.current_currency == "EUR"):

                    # Înlocuiește cu calea EUR
                    current_value_str = str(current_value)
                    # Potrivire pe NUMELE EXACT al fișierului, nu pe subșir din cale.
                    # "ACTIVI.db" este subșir al lui "INACTIVI.db", deci o potrivire
                    # pe subșir ar patchui INACTIVI cu activiEUR.db. Comparația e
                    # insensibilă la majuscule, ca o diferență de scriere să nu mai
                    # lase un modul nepatchuit în tăcere.
                    nume_fisier = os.path.basename(current_value_str)
                    for ron_db, eur_db in db_mapping.items():
                        if nume_fisier.lower() == ron_db.lower():
                            new_value = current_value_str[:len(current_value_str) - len(nume_fisier)] + eur_db

                            # Verifică că fișierul EUR există
                            if (base_path / eur_db).exists():
                                setattr(module, attr_name, new_value)
                                print(f"PATCHED: {module.__name__}.{attr_name} -> {eur_db}")
                            else:
                                # Fara else, o lipsa/diferenta de caz a fisierului EUR
                                # ar sari patch-ul in tacere, lasand modulul pe baza RON
                                # in mod EUR. Anuntam (ca la main_ui.py).
                                print(f"WARNING: fisierul EUR '{eur_db}' lipseste sau are alt caz "
                                      f"-> {module.__name__}.{attr_name} RAMANE pe RON!")
                            break

    # Hook pentru interceptarea import-urilor
    # CORECTAT: folosim 'builtins' în loc de '__builtins__' pentru consistență Python 3
    original_import = builtins.__import__

    def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
        module = original_import(name, globals, locals, fromlist, level)

        # Patchuiește modulele CAR UI
        if name.startswith('ui.') and hasattr(module, 'DB_MEMBRII'):
            patch_module_database_paths(module)

        return module

    builtins.__import__ = patched_import
    return patched_import, original_import


# ---------------------------------------------------------------------------
# NORMALIZARE CASING FISIERE BAZA 'activi' (tool defensiv la pornire)
# ---------------------------------------------------------------------------
# Forma canonica: RON = "ACTIVI.db" (toate constantele DB_ACTIVI o folosesc,
# la fel sursa conversiei), EUR = "activiEUR.db" (creata de conversie_widget.py
# si asteptata de maparea EUR din setup_early_database_patching).
#
# 'activi' e SINGURA baza care rupe simetria de casing RON->EUR, deci singura
# expusa la fisiere cu caz gresit (backup restaurat, mutare cross-OS). Pe
# Windows (FS case-insensitive) cazul nu conteaza functional, dar pe un FS
# case-sensitive un caz gresit ar face patch-ul EUR sa fie sarit silentios
# (ramura exists() din setup_early_database_patching) -> date rutate in baza
# gresita. Tool pur defensiv, rulat INAINTE de patch si de orice sqlite3.connect.
_BAZE_CANONICE = ("ACTIVI.db", "activiEUR.db")


def _redenumeste_caz(base_path, src_nume, canon):
    """Redenumeste un fisier la forma canonica de caz, in doua trepte (sigur pe
    Windows, unde o redenumire care difera DOAR prin caz poate fi ignorata)."""
    src = os.path.join(base_path, src_nume)
    dst = os.path.join(base_path, canon)
    tmp = os.path.join(base_path, canon + ".casingtmp")
    try:
        os.rename(src, tmp)
        os.rename(tmp, dst)
        print(f"[casing] Normalizat numele bazei: '{src_nume}' -> '{canon}'")
    except OSError as e:
        # fisier blocat / alt proces -> NU opri pornirea; incearca sa refaci starea
        print(f"[casing] Nu pot normaliza '{src_nume}' -> '{canon}': {e}")
        try:
            if os.path.exists(tmp) and not os.path.exists(dst):
                os.rename(tmp, src)
        except OSError:
            pass


def _anunta_casing_ambigu(canon, gresite):
    """Doua fisiere DISTINCTE cu acelasi nume in cazuri diferite (posibil doar pe
    FS case-sensitive). Nu unificam automat date financiare -> anuntam userul si
    NU atingem nimic (motivul cerut pentru acord)."""
    mesaj = (
        f"In directorul aplicatiei exista simultan doua variante ale bazei de date "
        f"'{canon}', scrise cu litere diferite:\n\n"
        f"   • {canon}  (forma corecta)\n"
        + "".join(f"   • {g}\n" for g in gresite)
        + f"\nNu le pot unifica automat, fiindca as putea pierde date financiare. "
        f"Va rugam sa pastrati manual fisierul corect ('{canon}'), sa il stergeti "
        f"sau mutati pe celalalt, apoi sa reporniti aplicatia."
    )
    try:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(None, "Fisiere baza de date cu litere diferite", mesaj)
    except Exception:
        print(f"[casing] AMBIGUU: {mesaj}")


def normalizeaza_casing_baze(base_path):
    """Aduce numele fisierelor 'activi' la forma canonica (vezi nota de mai sus).
    Nu creeaza fisiere, nu suprascrie, nu atinge tabelul (ACTIVI) sau SQL."""
    try:
        intrari = os.listdir(base_path)
    except OSError as e:
        print(f"[casing] Nu pot lista directorul '{base_path}': {e}")
        return

    pe_lower = {}
    for nume in intrari:
        pe_lower.setdefault(nume.lower(), []).append(nume)

    for canon in _BAZE_CANONICE:
        variante = pe_lower.get(canon.lower(), [])
        if not variante:
            continue  # fisierul nu exista (pre-conversie / instalare curata) -> skip
        gresite = [v for v in variante if v != canon]
        if not gresite:
            continue  # deja in forma canonica
        if canon in variante:
            # ambele forme exista ca fisiere distincte (doar pe FS case-sensitive)
            _anunta_casing_ambigu(canon, gresite)
            continue  # NU atinge nimic (risc pierdere date)
        _redenumeste_caz(base_path, gresite[0], canon)  # o singura varianta, caz gresit


def main():
    """Punctul de intrare cu early database patching"""
    # Atributele HiDPI trebuie setate ÎNAINTE de crearea QApplication, altfel Qt
    # le ignoră ("must be set before QCoreApplication is created") și scalarea
    # nu se aplică — de unde text tăiat în butoane pe ecrane cu scalare != 100%.
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    # ✨ APLICĂ STILURI GLOBALE PENTRU DIALOGURI
    from dialog_styles import apply_global_dialog_styles
    apply_global_dialog_styles(app)

    # ✨ BUTOANE VIZIBILE ÎN QMessageBox (fix global)
    # Pe Windows, stilul aplicat la nivel de APLICAȚIE nu comută butoanele native
    # QMessageBox în modul stilizat (fundalul și chenarul lor nu se randează ->
    # butoanele apar doar ca text, fără cutie). Aplicat DIRECT pe instanța de
    # dialog, se randează corect. Suprascriem metodele statice QMessageBox.* ca
    # să creeze un box cu stilul aplicat direct — o singură intervenție repară
    # toate apelurile brute din aplicație. (Aplicația deja face monkey-patch la
    # __import__ pentru sistemul EUR, deci tiparul e consistent cu codul.)
    from PyQt5.QtWidgets import QMessageBox as _QMB
    from dialog_styles import get_dialog_stylesheet as _dlg_ss

    def _styled_static(_icon, _default_buttons):
        def _f(parent=None, title="", text="",
               buttons=_default_buttons, defaultButton=_QMB.NoButton):
            box = _QMB(parent)
            box.setIcon(_icon)
            box.setWindowTitle(title)
            box.setText(text)
            box.setStandardButtons(buttons)
            if defaultButton != _QMB.NoButton:
                box.setDefaultButton(defaultButton)
            box.setStyleSheet(_dlg_ss())
            return box.exec_()
        return staticmethod(_f)

    _QMB.information = _styled_static(_QMB.Information, _QMB.Ok)
    _QMB.warning     = _styled_static(_QMB.Warning,     _QMB.Ok)
    _QMB.critical    = _styled_static(_QMB.Critical,    _QMB.Ok)
    _QMB.question    = _styled_static(_QMB.Question,    _QMB.Yes | _QMB.No)

    # Si instantele create direct (msg_box = QMessageBox(self)) primesc tema pe
    # __init__ -> butoane vizibile fara editari per-loc. Cine isi pune apoi un
    # stylesheet propriu il suprascrie (ex. dialogul detaliat din Optimizare, care
    # e reparat separat sa includa tema).
    _QMB_orig_init = _QMB.__init__

    def _qmb_styled_init(self, *args, **kwargs):
        _QMB_orig_init(self, *args, **kwargs)
        try:
            self.setStyleSheet(_dlg_ss())
        except Exception:
            pass

    _QMB.__init__ = _qmb_styled_init

    # Normalizeaza cazul numelui fisierelor 'activi' (ACTIVI.db / activiEUR.db)
    # INAINTE de patch-ul DB si de orice sqlite3.connect (fisierul sa nu fie
    # tinut deschis chiar de aplicatie). Tool defensiv - vezi normalizeaza_casing_baze.
    _casing_base = (os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)
                    else os.path.dirname(os.path.abspath(__file__)))
    normalizeaza_casing_baze(_casing_base)

    # ===== INTEGRARE SECURITATE: Verificări la pornire =====
    # 1. Curățare baze de date expuse din crash-uri anterioare
    if not cleanup_exposed_database():
        # Cleanup a eșuat → Oprește aplicația
        sys.exit(1)
    
    # 2. Dezarhivare cu parolă (autentificare)
    if not extract_database_with_password():
        # Autentificare eșuată → Oprește aplicația
        sys.exit(1)
    # ===== Sfârșit integrare securitate =====

    # CRITICAL: Setup early patching ÎNAINTE de import main_ui
    patched_import, original_import = setup_early_database_patching()

    try:
        # Import și lansare - ACUM cu patching activ
        from main_ui import CARApp

        window = CARApp()
        window.show()

        print("=" * 60)
        print("C.A.R. Petrosani - Aplicatia principala lansata cu early patching")
        print("=" * 60)

        sys.exit(app.exec_())

    finally:
        # Restore original import
        builtins.__import__ = original_import


if __name__ == "__main__":
    main()
