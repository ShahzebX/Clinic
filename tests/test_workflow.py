"""Lightweight end-to-end tests for the clinic application services."""

from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from database.db_manager import DatabaseManager, PatientRecord
from utils.excel_manager import ExcelManager
from utils.pdf_generator import PdfGenerator


class WorkflowTestCase(unittest.TestCase):
	def test_save_and_export_workflow(self) -> None:
		with TemporaryDirectory() as tmp_dir:
			base_path = Path(tmp_dir)

			database = DatabaseManager(base_path / "clinic.db")
			excel_manager = ExcelManager(base_path / "data")
			pdf_generator = PdfGenerator(base_path / "reports", "Test Clinic")

			record = PatientRecord(
				date=datetime.now(),
				opd_no="OPD-001",
				name="John Doe",
				father_name="Richard Roe",
				age=34,
				gender="Male",
				cnic="12345-1234567-1",
				address="123 Demo Street, Springfield",
				temperature=98.6,
				bp="120/80",
				weight=72.5,
				diabetic=110.0,
				fees_type="Normal",
			)

			database.add_patient(record)
			self.assertIsNotNone(record.id)
			self.assertEqual(database.count(), 1)

			workbook_path = excel_manager.append_record(record)
			self.assertTrue(workbook_path.exists())

			pdf_path = pdf_generator.generate(record)
			self.assertTrue(pdf_path.exists())

			fetched = database.fetch_all()
			self.assertEqual(len(fetched), 1)
			self.assertEqual(fetched[0].opd_no, "OPD-001")

			database.close()


if __name__ == "__main__":
	unittest.main()
