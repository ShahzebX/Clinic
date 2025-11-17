"""Database manager module for the Clinic app.

Provides a thin wrapper around SQLite with a high-level interface for
initialising the database, persisting patient records, and performing the most
common read operations required by the UI and export pipelines.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Generator, Iterable, List, Optional, Sequence


SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	date TEXT NOT NULL,
	opd_no TEXT NOT NULL,
	name TEXT NOT NULL,
	father_name TEXT,
	age INTEGER NOT NULL,
	gender TEXT NOT NULL,
	cnic TEXT,
	address TEXT,
	temperature REAL NOT NULL,
	bp TEXT NOT NULL,
	weight REAL,
	diabetic REAL,
	fees_type TEXT NOT NULL
);
"""


EXTRA_COLUMNS: dict[str, str] = {
	"opd_no": "opd_no TEXT DEFAULT ''",
	"father_name": "father_name TEXT DEFAULT ''",
	"cnic": "cnic TEXT",
	"address": "address TEXT",
	"weight": "weight REAL",
	"diabetic": "diabetic REAL",
	"fees_type": "fees_type TEXT DEFAULT 'Normal'",
}


@dataclass(slots=True)
class PatientRecord:
	"""Dataclass representing a patient visit entry."""

	date: datetime
	opd_no: str
	name: str
	father_name: str
	age: int
	gender: str
	cnic: Optional[str]
	address: str
	temperature: float
	bp: str
	weight: Optional[float]
	diabetic: Optional[float]
	fees_type: str
	id: Optional[int] = None

	def to_db_tuple(self) -> Sequence[object]:
		return (
			self.date.isoformat(),
			self.opd_no,
			self.name,
			self.father_name,
			self.age,
			self.gender,
			self.cnic,
			self.address,
			self.temperature,
			self.bp,
			self.weight,
			self.diabetic,
			self.fees_type,
		)

	@classmethod
	def from_row(cls, row: sqlite3.Row) -> "PatientRecord":
		return cls(
			id=row["id"],
			date=datetime.fromisoformat(row["date"]),
			opd_no=row["opd_no"] or "",
			name=row["name"],
			father_name=row["father_name"] or "",
			age=row["age"],
			gender=row["gender"],
			cnic=row["cnic"] or None,
			address=row["address"] or "",
			temperature=row["temperature"],
			bp=row["bp"],
			weight=row["weight"],
			diabetic=row["diabetic"],
			fees_type=row["fees_type"] or "Normal",
		)

	def as_dict(self) -> dict:
		payload = asdict(self)
		payload["date"] = self.date.isoformat()
		return payload


class DatabaseManager:
	"""Small utility class to manage the clinic SQLite database."""

	def __init__(self, db_path: Path | str | None = None) -> None:
		base_dir = Path(db_path) if db_path else Path(__file__).resolve().parent
		if base_dir.is_dir():
			self.db_path = base_dir / "clinic.db"
		else:
			self.db_path = base_dir

		self.db_path.parent.mkdir(parents=True, exist_ok=True)
		self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
		self._connection.row_factory = sqlite3.Row
		self.initialize_database()

	def initialize_database(self) -> None:
		"""Ensure the patients table exists."""

		with self._connection:
			self._connection.executescript(SCHEMA)
			self._ensure_columns()

	def _ensure_columns(self) -> None:
		columns = {
			row["name"]
			for row in self._connection.execute("PRAGMA table_info(patients)").fetchall()
		}
		for column, definition in EXTRA_COLUMNS.items():
			if column not in columns:
				self._connection.execute(f"ALTER TABLE patients ADD COLUMN {definition}")

	def add_patient(self, record: PatientRecord) -> int:
		"""Insert a new patient record and return the new row id."""

		query = (
			"INSERT INTO patients (date, opd_no, name, father_name, age, gender, cnic, address, temperature, bp, weight, diabetic, fees_type) "
			"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		)
		with self._connection:
			cursor = self._connection.execute(query, record.to_db_tuple())
			record.id = cursor.lastrowid
		return record.id

	def bulk_insert(self, records: Iterable[PatientRecord]) -> None:
		"""Insert multiple patient records in a single transaction."""

		query = (
			"INSERT INTO patients (date, opd_no, name, father_name, age, gender, cnic, address, temperature, bp, weight, diabetic, fees_type) "
			"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		)
		payload = [rec.to_db_tuple() for rec in records]
		with self._connection:
			self._connection.executemany(query, payload)

	def fetch_all(self) -> List[PatientRecord]:
		"""Return all saved patient records ordered by date descending."""

		query = "SELECT * FROM patients ORDER BY date DESC"
		cursor = self._connection.execute(query)
		return [PatientRecord.from_row(row) for row in cursor.fetchall()]

	def fetch_between(self, start: datetime, end: datetime) -> List[PatientRecord]:
		"""Return patient records whose visit dates fall between the bounds."""

		query = (
			"SELECT * FROM patients WHERE date BETWEEN ? AND ? ORDER BY date DESC"
		)
		cursor = self._connection.execute(
			query, (start.isoformat(), end.isoformat())
		)
		return [PatientRecord.from_row(row) for row in cursor.fetchall()]

	def fetch_by_month(self, year: int, month: int) -> List[PatientRecord]:
		"""Return records for a specific calendar month."""

		start = datetime(year=year, month=month, day=1)
		if month == 12:
			end = datetime(year=year + 1, month=1, day=1)
		else:
			end = datetime(year=year, month=month + 1, day=1)
		return self.fetch_between(start, end)

	def count(self) -> int:
		"""Return the total number of stored records."""

		query = "SELECT COUNT(*) FROM patients"
		cursor = self._connection.execute(query)
		(total,) = cursor.fetchone()
		return int(total)

	def delete(self, patient_id: int) -> None:
		"""Remove a patient record by id."""

		with self._connection:
			self._connection.execute("DELETE FROM patients WHERE id = ?", (patient_id,))

	def close(self) -> None:
		if self._connection:
			self._connection.close()

	def __enter__(self) -> "DatabaseManager":
		return self

	def __exit__(self, exc_type, exc, tb) -> None:
		self.close()

	@contextmanager
	def transaction(self) -> Generator[sqlite3.Connection, None, None]:
		"""Context manager that yields a transactional connection."""

		with self._connection:
			yield self._connection


__all__ = ["DatabaseManager", "PatientRecord"]
