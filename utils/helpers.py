"""Generic helper functions for the Clinic app."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


INVALID_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
DATE_FORMAT = "%d/%m/%Y"
FEES_LABELS = {
	"Normal": "Normal - Rs. 100",
	"Urgent": "Urgent - Rs. 200",
}


def ensure_directory(path: Path | str) -> Path:
	"""Create *path* if required and return it as a :class:`Path`."""

	p = Path(path)
	p.mkdir(parents=True, exist_ok=True)
	return p


def get_user_documents_folder() -> Path:
	"""Return the user's Documents folder path in a cross-platform way."""
	
	if sys.platform.startswith("win"):
		# On Windows, use USERPROFILE\Documents
		import os
		user_profile = os.environ.get("USERPROFILE")
		if user_profile:
			return Path(user_profile) / "Documents"
		# Fallback to home directory
		return Path.home() / "Documents"
	else:
		# On Unix-like systems (macOS, Linux)
		return Path.home() / "Documents"


def get_clinic_data_folder() -> Path:
	"""Return the clinic data folder path and ensure it exists."""
	
	data_folder = get_user_documents_folder() / "OPD Data"
	return ensure_directory(data_folder)


def sanitize_filename(name: str) -> str:
	"""Return a filesystem-safe representation of *name*."""

	cleaned = INVALID_FILENAME_CHARS.sub("_", name.strip())
	return cleaned.strip("._") or "record"


def current_month_filename(prefix: str, timestamp: datetime) -> str:
	"""Return an Excel-friendly monthly filename."""

	month_name = timestamp.strftime("%B%Y")
	return f"{prefix}_{month_name}.xlsx"


def month_subdirectory(base_dir: Path | str, timestamp: datetime) -> Path:
	"""Return the subdirectory for reports belonging to *timestamp*'s month."""

	base = ensure_directory(base_dir)
	folder = base / timestamp.strftime("%Y_%m")
	return ensure_directory(folder)


def open_path(path: Path) -> None:
	"""Open *path* with the system default application."""

	if sys.platform.startswith("win"):
		os.startfile(path)  # type: ignore[attr-defined]
	elif sys.platform == "darwin":
		subprocess.run(["open", path], check=False)
	else:
		subprocess.run(["xdg-open", path], check=False)


def open_directory(directory: Path) -> None:
	"""Open *directory* in the system file explorer."""

	if sys.platform.startswith("win"):
		# On Windows, explorer sometimes returns non-zero exit code even on success
		subprocess.run(["explorer", str(directory)], check=False)
	elif sys.platform == "darwin":
		subprocess.run(["open", str(directory)], check=False)
	else:
		subprocess.run(["xdg-open", str(directory)], check=False)


def format_datetime(value: datetime) -> str:
	"""Return a human-readable datetime string."""

	return value.strftime("%Y-%m-%d %H:%M")


def format_date(value: datetime) -> str:
	"""Return a DD/MM/YYYY formatted date string."""

	return value.strftime(DATE_FORMAT)


def parse_date(value: str) -> datetime:
	"""Parse a DD/MM/YYYY date string into a :class:`datetime`."""

	return datetime.strptime(value, DATE_FORMAT)


def coerce_optional_float(value: str) -> float | None:
	"""Return float(value) or ``None`` when *value* is empty."""

	stripped = value.strip()
	if not stripped:
		return None
	return float(stripped)


def format_fees(value: str) -> str:
	"""Return a human-readable fees label."""

	return FEES_LABELS.get(value, value)


__all__ = [
	"ensure_directory",
	"get_user_documents_folder",
	"get_clinic_data_folder",
	"sanitize_filename",
	"current_month_filename",
	"month_subdirectory",
	"open_path",
	"open_directory",
	"format_datetime",
	"format_date",
	"parse_date",
	"coerce_optional_float",
	"format_fees",
]
