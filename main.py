"""Clinic Data Entry Desktop App entry point."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from database.db_manager import DatabaseManager, PatientRecord
from ui.main_window import MainWindow
from utils.excel_manager import ExcelManager
from utils.pdf_generator import PdfGenerator
from utils.helpers import get_clinic_data_folder


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)


DEFAULT_CLINIC_NAME = "Kashmiri Welfare Clinic & Maternity Home"
CLINIC_SUBTITLE = "Main Badin Road, Matli"
CLINIC_DOCTORS = (
    ("Dr. Gulab Hussain Kashmiri", "M.B.B.S, R.M.P"),
    ("Dr. Abdullah Umar Kashmiri", "M.B.B.S, R.M.P"),
)
CLINIC_FOOTER_DAYS = "Monday to Saturday"
CLINIC_FOOTER_TIME = "Time: 04 P.M to 10 P.M"


class ClinicApplication:
    """Coordinate the UI and backend components."""

    def __init__(self, clinic_name: str = DEFAULT_CLINIC_NAME) -> None:
        base_dir = Path(__file__).resolve().parent
        self._clinic_name = clinic_name

        self.database = DatabaseManager(base_dir / "database")
        self.excel_manager = ExcelManager(get_clinic_data_folder())
        self.pdf_generator = PdfGenerator(
            base_dir / "reports",
            clinic_name,
            subtitle=CLINIC_SUBTITLE,
            doctors=CLINIC_DOCTORS,
            footer_days=CLINIC_FOOTER_DAYS,
            footer_time=CLINIC_FOOTER_TIME,
        )

        self.window = MainWindow(
            on_save=self._handle_save,
            on_generate_report=self._handle_generate_report,
            clinic_name=self._clinic_name,
            on_exit=self.shutdown,
        )

    def _handle_save(self, data: dict) -> PatientRecord:
        """Persist form *data* and update the monthly Excel workbook."""

        record = PatientRecord(
            date=data["date"],
            opd_no=data["opd_no"],
            name=data["name"],
            father_name=data["father_name"],
            age=data["age"],
            gender=data["gender"],
            temperature=data["temperature"],
            bp=data["bp"],
            cnic=data["cnic"],
            address=data["address"],
            weight=data["weight"],
            diabetic=data["diabetic"],
            fees_type=data["fees_type"],
        )

        logging.debug("Saving patient record: %s", record)

        try:
            self.database.add_patient(record)
            self.excel_manager.append_record(record)
        except Exception:
            if record.id is not None:
                self.database.delete(record.id)
            logging.exception("Failed to save patient record")
            raise

        return record

    def _handle_generate_report(self, record: PatientRecord) -> Path:
        logging.debug("Generating report for record %s", record.id)
        return self.pdf_generator.generate(record, auto_open=True)

    def run(self) -> None:
        try:
            self.window.mainloop()
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        logging.info("Shutting down Clinic application")
        self.database.close()
        try:
            if self.window.winfo_exists():
                self.window.destroy()
        except Exception:
            # Window already destroyed, ignore
            pass


def main(args: Optional[list[str]] = None) -> int:
    _ = args or sys.argv[1:]
    app = ClinicApplication()
    app.run()
    return 0


if __name__ == "__main__":  # pragma: no cover - GUI entry point
    raise SystemExit(main())
