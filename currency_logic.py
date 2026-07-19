"""
Logica pentru comutarea RON/EUR
Modul central pentru managementul monedelor în sistemul C.A.R. Petroșani
Versiunea de producție cu suport complet pentru cele trei stări ale sistemului
"""
import json
import sys
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal


class CurrencyLogic(QObject):
    """Logica centrală pentru gestionarea comutării RON/EUR cu trei stări operaționale"""

    # Semnale pentru comunicarea cu interfața utilizator
    currency_changed = pyqtSignal(str)  # Emite "RON" sau "EUR"
    permission_changed = pyqtSignal(str)  # Emite "readonly" sau "readwrite"
    system_state_changed = pyqtSignal(str)  # Emite "pre_conversion", "post_conversion_eur", "post_conversion_ron"

    def __init__(self):
        super().__init__()

        # Starea internă a sistemului
        self.current_currency = "RON"
        self.conversion_applied = False
        self.eur_databases_available = False

        # Inițializarea sistemului
        self._initialize_system_state()

    def _initialize_system_state(self):
        """Inițializează starea sistemului pe baza configurației existente"""
        try:
            # Verifică starea conversiei
            self.conversion_applied = self._check_conversion_applied()

            # Verifică disponibilitatea bazelor EUR
            self.eur_databases_available = self._check_eur_databases_availability()

            # Setează moneda inițială pe baza stării conversiei
            if self.conversion_applied:
                self.current_currency = "EUR"
                print("INFO: Sistem inițializat în modul EUR (conversia aplicată)")
            else:
                self.current_currency = "RON"
                print("INFO: Sistem inițializat în modul RON (pre-conversie)")

        except Exception as e:
            print(f"AVERTISMENT: Eroare la inițializarea stării sistemului: {e}")
            # Fallback la starea de siguranță
            self.current_currency = "RON"
            self.conversion_applied = False
            self.eur_databases_available = False

    def _get_base_path(self):
        """Returnează calea de bază pentru aplicație"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).resolve().parent

    def _get_config_path(self):
        """Returnează calea către fișierul de configurare"""
        # Actualizat pentru compatibilitate cu conversie_widget
        base_path = self._get_base_path()

        # Numele canonic este dual_currency.json — el este scris de
        # conversie_widget.py (_save_conversion_status) și citit de main_ui.py.
        # Trebuie să fie PRIMUL: fallback-ul de la finalul funcției întoarce
        # possible_config_files[0] ca fișier de creat, iar înainte acela era
        # "conversion_config.json", un nume pe care nu îl citește nimeni —
        # statusul conversiei s-ar fi scris unde nu se uită nicio componentă.
        # Celelalte rămân doar pentru compatibilitate la citire.
        possible_config_files = [
            "dual_currency.json",
            "conversion_config.json",
            "car_conversion_config.json"
        ]

        for config_file in possible_config_files:
            config_path = base_path / config_file
            if config_path.exists():
                return config_path

        # Returnează primul nume ca fallback pentru creare
        return base_path / possible_config_files[0]

    def _check_conversion_applied(self):
        """Verifică dacă conversia definitivă RON->EUR a fost aplicată"""
        try:
            config_path = self._get_config_path()

            if not config_path.exists():
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Verifică diferite chei posibile pentru compatibilitate
            conversion_keys = [
                'conversie_aplicata',
                'conversion_applied',
                'final_conversion_completed'
            ]

            for key in conversion_keys:
                if key in config:
                    return bool(config[key])

            return False

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"INFO: Nu s-a putut verifica starea conversiei: {e}")
            return False
        except Exception as e:
            print(f"EROARE: Verificare stare conversie: {e}")
            return False

    def _check_eur_databases_availability(self):
        """Verifică disponibilitatea bazelor de date EUR"""
        try:
            base_path = self._get_base_path()

            # Lista bazelor de date EUR necesare
            required_eur_databases = [
                "DEPCREDEUR.db",
                "MEMBRIIEUR.db",
                "activiEUR.db",
                "INACTIVIEUR.db",
                "LICHIDATIEUR.db"
            ]

            existing_count = 0
            for db_name in required_eur_databases:
                db_path = base_path / db_name
                if db_path.exists():
                    existing_count += 1

            # Consideră EUR disponibil dacă există cel puțin 80% din baze
            availability_threshold = len(required_eur_databases) * 0.8
            is_available = existing_count >= availability_threshold

            if is_available:
                print(f"INFO: Baze EUR disponibile: {existing_count}/{len(required_eur_databases)}")
            else:
                print(f"AVERTISMENT: Baze EUR insuficiente: {existing_count}/{len(required_eur_databases)}")

            return is_available

        except Exception as e:
            print(f"EROARE: Verificare baze EUR: {e}")
            return False

    def _count_eur_databases(self):
        """Numără bazele de date EUR existente pentru raportare detaliată"""
        try:
            base_path = self._get_base_path()
            eur_dbs = ["DEPCREDEUR.db", "MEMBRIIEUR.db", "activiEUR.db", "INACTIVIEUR.db", "LICHIDATIEUR.db"]
            count = sum(1 for db in eur_dbs if (base_path / db).exists())
            return count
        except Exception:
            return 0

    def get_current_currency(self):
        """Returnează moneda curentă selectată"""
        return self.current_currency

    def get_current_permission(self):
        """Returnează tipul de permisiuni pentru starea curentă"""
        if not self.conversion_applied:
            # Pre-conversie: RON cu funcționalitate completă
            return "readwrite"
        elif self.current_currency == "EUR":
            # Post-conversie EUR: funcționalitate completă
            return "readwrite"
        else:
            # Post-conversie RON: doar citire pentru protecția datelor
            return "readonly"

    def get_system_state(self):
        """Returnează starea curentă a sistemului"""
        if not self.conversion_applied:
            return "pre_conversion"
        elif self.current_currency == "EUR":
            return "post_conversion_eur"
        else:
            return "post_conversion_ron"

    def is_eur_conversion_available(self):
        """Verifică dacă conversia EUR este disponibilă"""
        return self.conversion_applied and self.eur_databases_available

    def is_eur_available(self):
        """Alias pentru compatibilitate cu interfața existentă"""
        return self.is_eur_conversion_available()

    def can_write_data(self):
        """Verifică dacă operațiunile de scriere sunt permise în starea curentă"""
        return self.get_current_permission() == "readwrite"

    def switch_to_ron(self):
        """Comută la modul RON cu logica specifică stării sistemului"""
        old_currency = self.current_currency
        old_permission = self.get_current_permission()
        old_state = self.get_system_state()

        self.current_currency = "RON"

        new_permission = self.get_current_permission()
        new_state = self.get_system_state()

        # Emite semnale doar dacă starea s-a schimbat efectiv
        if old_currency != self.current_currency:
            self.currency_changed.emit("RON")
            print(f"🔄 Comutat la modul RON")

            if self.conversion_applied:
                print("ℹ️  Modul doar-citire activat pentru protecția datelor")
            else:
                print("ℹ️  Modul standard RON")

        if old_permission != new_permission:
            self.permission_changed.emit(new_permission)

        if old_state != new_state:
            self.system_state_changed.emit(new_state)

    def switch_to_eur(self):
        """Comută la modul EUR dacă este disponibil"""
        if not self.conversion_applied:
            print("⚠️  EUR nu este disponibil: conversia nu a fost aplicată")
            return False

        if not self.eur_databases_available:
            print("⚠️  EUR nu este disponibil: bazele de date EUR lipsesc")
            return False

        old_currency = self.current_currency
        old_permission = self.get_current_permission()
        old_state = self.get_system_state()

        self.current_currency = "EUR"

        new_permission = self.get_current_permission()
        new_state = self.get_system_state()

        # Emite semnale pentru schimbările efectuate
        if old_currency != self.current_currency:
            self.currency_changed.emit("EUR")
            print("🔄 Comutat la modul EUR (Citire & Scriere)")

        if old_permission != new_permission:
            self.permission_changed.emit(new_permission)

        if old_state != new_state:
            self.system_state_changed.emit(new_state)

        return True

    def get_status_info(self):
        """Returnează informații despre statusul pentru afișare în interfață"""
        status_parts = []

        # Informații despre starea conversiei
        if self.conversion_applied:
            if self.eur_databases_available:
                status_parts.append("Sistem EUR Complet")
            else:
                status_parts.append("Conversie Aplicată - Baze EUR Incomplete")
        else:
            if self._count_eur_databases() > 0:
                status_parts.append("Conversie Parțială")
            else:
                status_parts.append("Sistem RON Standard")

        # Modul și permisiuni curente
        permission_info = "R/W" if self.can_write_data() else "R-O"
        status_parts.append(f"Mod: {self.current_currency} ({permission_info})")

        return " • ".join(status_parts) if status_parts else "Status Necunoscut"

    def refresh_status(self):
        """Reîmprospătează statusul prin reverificare completă"""
        old_conversion_status = self.conversion_applied
        old_eur_availability = self.eur_databases_available
        old_state = self.get_system_state()

        # Reverificare completă
        self.conversion_applied = self._check_conversion_applied()
        self.eur_databases_available = self._check_eur_databases_availability()

        # Ajustează moneda curentă dacă este necesar
        if not old_conversion_status and self.conversion_applied:
            # Conversia tocmai a fost aplicată
            self.switch_to_eur()
            print("🎯 Detectată aplicarea conversiei - comutat automat la EUR")
        elif old_conversion_status and not self.conversion_applied:
            # Conversia a fost anulată (caz rar)
            self.switch_to_ron()
            print("🔄 Detectată anularea conversiei - comutat la RON standard")
        elif self.conversion_applied and self.current_currency == "EUR" and not self.eur_databases_available:
            # Bazele EUR au dispărut
            self.switch_to_ron()
            print("⚠️  Baze EUR indisponibile - comutat la RON doar-citire")

        new_state = self.get_system_state()
        if old_state != new_state:
            self.system_state_changed.emit(new_state)

    def validate_system_integrity(self):
        """Validează integritatea sistemului și returnează raport detaliat"""
        validation_report = {
            "status": "OK",
            "warnings": [],
            "errors": [],
            "recommendations": []
        }

        try:
            # Verifică existența fișierului de configurare
            config_path = self._get_config_path()
            if not config_path.exists() and self.conversion_applied:
                validation_report["errors"].append("Fișierul de configurare lipsește dar sistemul indică conversie aplicată")
                validation_report["status"] = "ERROR"

            # Verifică consistența bazelor EUR
            if self.conversion_applied:
                eur_count = self._count_eur_databases()
                if eur_count == 0:
                    validation_report["errors"].append("Conversia aplicată dar nu există baze EUR")
                    validation_report["status"] = "ERROR"
                elif eur_count < 5:
                    validation_report["warnings"].append(f"Lipsesc {5 - eur_count} baze EUR din totalul de 5")
                    if validation_report["status"] != "ERROR":
                        validation_report["status"] = "WARNING"

            # Verifică consistența stării curente
            if self.current_currency == "EUR" and not self.is_eur_conversion_available():
                validation_report["errors"].append("Modul EUR activ dar EUR nu este disponibil")
                validation_report["status"] = "ERROR"
                validation_report["recommendations"].append("Comutați la modul RON")

            return validation_report

        except Exception as e:
            validation_report["status"] = "ERROR"
            validation_report["errors"].append(f"Eroare la validarea sistemului: {e}")
            return validation_report

    def get_detailed_status(self):
        """Returnează status detaliat pentru diagnostic și troubleshooting"""
        try:
            status = {
                "currency": self.current_currency,
                "permission": self.get_current_permission(),
                "system_state": self.get_system_state(),
                "conversion_applied": self.conversion_applied,
                "eur_databases_available": self.eur_databases_available,
                "eur_databases_count": self._count_eur_databases(),
                "config_file_exists": self._get_config_path().exists(),
                "config_file_path": str(self._get_config_path()),
                "can_write": self.can_write_data(),
                "is_eur_available": self.is_eur_conversion_available()
            }

            # Adaugă validarea integrității
            validation = self.validate_system_integrity()
            status["integrity_status"] = validation["status"]
            status["integrity_issues"] = validation.get("errors", []) + validation.get("warnings", [])

            return status

        except Exception as e:
            return {
                "error": f"Nu s-a putut genera statusul detaliat: {e}",
                "currency": self.current_currency,
                "system_state": "unknown"
            }