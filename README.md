# Clinic Data Entry Desktop App

A lightweight, offline-first Tkinter application for small clinics to capture patient vitals, maintain a historical SQLite database, archive monthly Excel spreadsheets, and generate printable PDF visit reports with space for handwritten doctor notes.

## Features

- 🩺 **Patient intake form** covering visit date + OPD no., patient & father/husband details, CNIC, address, Fahrenheit temperature, blood pressure, weight, diabetic reading, and fees type.
- 💾 **Local SQLite database** (`database/clinic.db`) that persists every entry offline.
- 📊 **Automatic Excel exports** per calendar month saved to `Documents/OPD Data` folder (e.g. `ClinicData_November2025.xlsx`).
- 🧾 **ReportLab-powered PDFs** organised by month with a large notes area for doctors.
- 🖨️ **One-click report generation** that opens the PDF ready for printing.
- 📁 **Easy data access** with buttons to open the data folder and view current month's Excel file.
- 🧰 Built with standard Python 3.x tooling—easy to package into an `.exe` using PyInstaller.

## Project Layout

```
clinic_app/
├── main.py                    # Application entry point
├── requirements.txt           # Runtime dependencies
├── database/
│   ├── clinic.db              # Created on first run
│   └── db_manager.py          # SQLite helpers
├── ui/
│   ├── main_window.py         # Tkinter GUI
│   └── styles.py              # Shared ttk styles
├── utils/
│   ├── excel_manager.py       # Monthly Excel workbook handling
│   ├── pdf_generator.py       # ReportLab PDF generation
│   └── helpers.py             # Cross-cutting helpers
├── reports/                   # Auto-generated PDF folders per month
└── assets/
    ├── logo.txt               # Placeholder – replace with logo.png
    └── icons/                 # Place UI icons here if desired
```

**Note:** Excel files are automatically saved to `%USERPROFILE%\Documents\OPD Data` (e.g., `C:\Users\YourName\Documents\OPD Data`) on Windows systems for easy access and backup.

## Getting Started

1. **Create and activate a virtual environment** (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the application**:

   ```powershell
   python main.py
   ```

   The first launch creates the SQLite database and prepares monthly folders as you save records.

## Usage Tips

- Ensure the clinic logo is saved as `assets/logo.png` (replace the placeholder text file) if you plan to embed it in future UI updates.
- The date picker (powered by `tkcalendar`) defaults to today but can be edited manually in `DD/MM/YYYY` format.
- The application validates age, OPD number, temperature, blood pressure, weight/diabetic readings, and fees selections before saving.
- Saved records immediately appear in the monthly Excel workbook located in the `data/` folder.
- After saving a record, click **Generate Report** to create and auto-open a printable PDF within `reports/<YYYY_MM>/`.

## Packaging with PyInstaller

After confirming the app runs correctly, build a standalone Windows executable:

```powershell
pyinstaller --onefile --windowed main.py
```

The generated executable will be available under the `dist/` directory. Remember to ship the `assets/`, `data/`, `database/`, and `reports/` folders alongside the executable so the app can continue storing data locally.

## Testing

Automated smoke tests reside under `tests/` (see the dedicated section below for running them once created). Manual QA suggestions:

- Attempt to save with empty or invalid fields to confirm validation messages appear.
- Save entries across a month boundary to ensure a new Excel workbook is created automatically.
- Generate reports on multiple saved records and verify they open for printing.

## Troubleshooting

- If PDFs fail to open automatically, ensure your Windows default application for `.pdf` files is configured.
- For Excel write errors, close any open workbook before saving a new patient record (Excel locks files for editing).
- Delete the `database/clinic.db` file if you ever want to start with a clean slate (the schema will be recreated on the next launch).

---

**Next steps:** customise styles, add extra vitals fields, or integrate barcode/ID scanning as your clinic workflow evolves.
