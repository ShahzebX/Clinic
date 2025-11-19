"""Fix existing Excel files by regenerating them from the database."""

from pathlib import Path
from database.db_manager import DatabaseManager
from utils.excel_manager import ExcelManager
from utils.helpers import get_clinic_data_folder
import shutil
from datetime import datetime

# Paths
base_dir = Path(__file__).resolve().parent
data_folder = get_clinic_data_folder()

# Backup existing Excel files
backup_folder = data_folder / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_folder.mkdir(exist_ok=True)

print(f"Backing up existing Excel files to: {backup_folder}")
for excel_file in data_folder.glob("ClinicData_*.xlsx"):
    backup_path = backup_folder / excel_file.name
    shutil.copy2(excel_file, backup_path)
    print(f"  Backed up: {excel_file.name}")
    # Delete the original
    excel_file.unlink()
    print(f"  Deleted: {excel_file.name}")

# Regenerate Excel files from database
print("\nRegenerating Excel files from database...")
db = DatabaseManager(base_dir / "database")
excel_manager = ExcelManager(data_folder)

all_records = db.fetch_all()
print(f"Found {len(all_records)} records in database")

# Group records by month and regenerate
excel_manager.append_records(all_records)

print("\n✓ Excel files regenerated successfully!")
print(f"  Backups saved in: {backup_folder}")
print(f"  New Excel files in: {data_folder}")

db.close()
