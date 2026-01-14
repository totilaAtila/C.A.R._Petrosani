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
        "activi.db": "activiEUR.db",
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
                    for ron_db, eur_db in db_mapping.items():
                        # CORECȚIA: Convertește current_value la string
                        current_value_str = str(current_value)
                        if ron_db in current_value_str:
                            new_value = current_value_str.replace(ron_db, eur_db)

                            # Verifică că fișierul EUR există
                            if (base_path / eur_db).exists():
                                setattr(module, attr_name, new_value)
                                print(f"PATCHED: {module.__name__}.{attr_name} -> {eur_db}")
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


def main():
    """Punctul de intrare cu early database patching"""
    app = QApplication(sys.argv)
    # ✨ APLICĂ STILURI GLOBALE PENTRU DIALOGURI
    from dialog_styles import apply_global_dialog_styles
    apply_global_dialog_styles(app)


    # Setări pentru efecte mai bune
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

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
