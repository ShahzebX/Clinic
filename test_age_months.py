"""Quick test to generate PDF with age months displayed."""

from datetime import datetime
from pathlib import Path
from database.db_manager import PatientRecord
from utils.pdf_generator import PdfGenerator
from utils.helpers import open_path

# Create test record with age and months
test_record = PatientRecord(
    date=datetime(2025, 11, 19),
    opd_no="TEST-001",
    name="Test Patient",
    father_name="Test Father",
    age=2.3,
    age_months=5,
    gender="Female",
    cnic="12345-1234567-1",
    address="Test Address, Matli",
    temperature=98.6,
    bp="120/80",
    weight=25.5,
    diabetic=110.0,
    fees_type="Normal",
    id=999
)

# Generate PDF
pdf_gen = PdfGenerator(
    reports_dir=Path(__file__).parent / "test_pdf",
    clinic_name="Kashmiri Welfare Clinic & Maternity Home",
    subtitle="Main Badin Road, Matli",
    doctors=(
        ("Dr. Gulab Hussain Kashmiri", "M.B.B.S, R.M.P"),
        ("Dr. Abdullah Umar Kashmiri", "M.B.B.S, R.M.P"),
    ),
    footer_days="Monday to Saturday",
    footer_time="Time: 04 P.M to 10 P.M",
)

pdf_path = pdf_gen.generate(test_record, auto_open=False)
print(f"PDF generated at: {pdf_path}")
print(f"\nTest data:")
print(f"Age: {test_record.age} years")
print(f"Age (Months): {test_record.age_months} months")
print(f"\nPDF will show: '{test_record.age} years {test_record.age_months} months'")

# Open the PDF
open_path(pdf_path)
print(f"\nPDF opened!")
