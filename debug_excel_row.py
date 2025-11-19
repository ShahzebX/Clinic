"""Debug Excel append with empty CNIC."""

from datetime import datetime
from database.db_manager import PatientRecord
from utils.helpers import format_date, format_fees

# Create test record with empty CNIC
record = PatientRecord(
    date=datetime(2025, 11, 18),
    opd_no="TEST-002",
    name="Debug Patient",
    father_name="Debug Father",
    age=25,
    gender="Female",
    cnic=None,
    address="Debug Address",
    temperature=98.6,
    bp="110/70",
    weight=60.0,
    diabetic=None,
    fees_type="Urgent",
)

# Build the row data exactly like excel_manager does
row_data = [
    record.opd_no,
    format_date(record.date),
    record.name,
    record.father_name,
    record.age,
    record.gender,
    record.cnic or "",
    record.address.replace("\n", ", ") if record.address else "",
    record.temperature,
    record.bp,
    record.weight if record.weight is not None else "",
    record.diabetic if record.diabetic is not None else "",
    format_fees(record.fees_type),
]

print("Row data to be appended:")
for idx, value in enumerate(row_data):
    print(f"  [{idx}] {type(value).__name__}: {repr(value)}")

print(f"\nCNIC value: {repr(record.cnic or '')}")
print(f"CNIC type: {type(record.cnic or '')}")
