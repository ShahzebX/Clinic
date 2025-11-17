"""Quick helper to generate a sample PDF report for layout debugging."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from database.db_manager import PatientRecord
from utils.pdf_generator import PdfGenerator

DEFAULT_CLINIC_NAME = "Kashmiri Welfare Clinic & Maternity Home"
DEFAULT_CLINIC_SUBTITLE = "Main Badin Road, Matli"
DEFAULT_DOCTORS = (
    ("Dr. Gulab Hussain Kashmiri", "M.B.B.S, R.M.P"),
    ("Dr. Abdullah Umar Kashmiri", "M.B.B.S, R.M.P"),
)
DEFAULT_FOOTER_DAYS = "Monday to Saturday"
DEFAULT_FOOTER_TIME = "Time: 04 P.M to 10 P.M"


def build_sample_record() -> PatientRecord:
    """Return a synthetic patient record with representative data."""

    return PatientRecord(
        date=datetime(2025, 10, 30),
        opd_no="106",
        name="Amir Raza Jat",
        father_name="Ali Nawaz Jat",
        age=24,
        gender="Male",
        cnic="41103-12345678",
        address="Near Mehfil Lawn, Main Bypass, Matli",
        temperature=98.6,
        bp="120/80",
        weight=61.0,
        diabetic=260.0,
        fees_type="Normal",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sample clinic PDF report")
    parser.add_argument(
        "--open",
        dest="auto_open",
        action="store_true",
        help="Open the generated PDF once created.",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        type=Path,
        default=Path(__file__).resolve().parent / "reports",
        help="Directory where the PDF should be written (defaults to the app reports folder).",
    )
    args = parser.parse_args()

    generator = PdfGenerator(
        reports_dir=args.output_dir,
        clinic_name=DEFAULT_CLINIC_NAME,
        subtitle=DEFAULT_CLINIC_SUBTITLE,
        doctors=DEFAULT_DOCTORS,
        footer_days=DEFAULT_FOOTER_DAYS,
        footer_time=DEFAULT_FOOTER_TIME,
    )

    record = build_sample_record()
    pdf_path = generator.generate(record, auto_open=args.auto_open)
    print(f"Generated debug report at: {pdf_path}")


if __name__ == "__main__":
    main()
