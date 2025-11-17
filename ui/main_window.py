"""Main Tkinter window for the Clinic app."""

from __future__ import annotations

import re
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable, Optional

try:  # pragma: no cover - import guard for optional dependency
	from tkcalendar import DateEntry
except ImportError:  # pragma: no cover - handled gracefully at runtime
	DateEntry = None  # type: ignore[assignment]

from ui.styles import STATUS_COLORS, apply_theme
from utils.helpers import (
	coerce_optional_float,
	format_date,
	parse_date,
	open_directory,
	open_path,
	get_clinic_data_folder,
)

if tk.TkVersion < 8.6:  # pragma: no cover - defensive programming
	raise RuntimeError("Tkinter 8.6 or newer is required")


if TYPE_CHECKING:
	from database.db_manager import PatientRecord


SaveCallback = Callable[[dict], "PatientRecord"]
ReportCallback = Callable[["PatientRecord"], Path]

CNIC_PATTERN = re.compile(r"^(\d{5}-\d{7}-\d|\d{13})$")
BP_PATTERN = re.compile(r"^\d{2,3}/\d{2,3}$")
FEES_OPTIONS = {"Normal": "Normal - Rs. 100", "Urgent": "Urgent - Rs. 200"}
TEMP_RANGE_F = (80.0, 110.0)


class _VerticalScrollFrame(ttk.Frame):
	"""Reusable vertical scroll container for form-heavy layouts."""

	def __init__(self, master: tk.Misc, *, padding: int = 0) -> None:
		super().__init__(master)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		self._canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
		self._v_scroll = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
		self._canvas.configure(yscrollcommand=self._v_scroll.set)

		self._canvas.grid(row=0, column=0, sticky="nsew")
		self._v_scroll.grid(row=0, column=1, sticky="ns")

		self.container = ttk.Frame(self._canvas, padding=padding)
		self._container_id = self._canvas.create_window((0, 0), window=self.container, anchor="nw")

		self.container.bind("<Configure>", self._on_container_configure)
		self._canvas.bind("<Configure>", self._on_canvas_configure)
		self.container.bind("<Enter>", self._enable_mousewheel)
		self.container.bind("<Leave>", self._disable_mousewheel)

	def _on_container_configure(self, _event: tk.Event) -> None:
		self._canvas.configure(scrollregion=self._canvas.bbox("all"))

	def _on_canvas_configure(self, event: tk.Event) -> None:
		self._canvas.itemconfigure(self._container_id, width=event.width)

	def _on_mousewheel(self, event: tk.Event) -> None:
		if event.delta:
			self._canvas.yview_scroll(-int(event.delta / 120), "units")
		elif getattr(event, "num", None) == 4:
			self._canvas.yview_scroll(-1, "units")
		elif getattr(event, "num", None) == 5:
			self._canvas.yview_scroll(1, "units")

	def _enable_mousewheel(self, _event: tk.Event) -> None:
		self._canvas.bind("<MouseWheel>", self._on_mousewheel)
		self._canvas.bind("<Button-4>", self._on_mousewheel)
		self._canvas.bind("<Button-5>", self._on_mousewheel)

	def _disable_mousewheel(self, _event: tk.Event) -> None:
		self._canvas.unbind("<MouseWheel>")
		self._canvas.unbind("<Button-4>")
		self._canvas.unbind("<Button-5>")


class MainWindow(tk.Tk):
	"""Tkinter window containing the patient data entry form."""

	def __init__(
		self,
		on_save: SaveCallback,
		on_generate_report: ReportCallback,
		clinic_name: str,
		on_exit: Optional[Callable[[], None]] = None,
	) -> None:
		super().__init__()

		self.title("Clinic Data Entry")
		self.state('zoomed')  # Start in maximized window
		self.resizable(True, True)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		apply_theme(self)

		self._on_save = on_save
		self._on_generate_report = on_generate_report
		self._on_exit = on_exit or self.destroy
		self._clinic_name = clinic_name
		self._last_record: Optional["PatientRecord"] = None
		self._date_widget: Optional[tk.Widget] = None

		self._build_variables()
		self._build_layout()
		self.protocol("WM_DELETE_WINDOW", self._handle_exit)
		self.update_idletasks()

	def _build_variables(self) -> None:
		today_str = format_date(datetime.now())

		self.date_var = tk.StringVar(value=today_str)
		self.opd_no_var = tk.StringVar()
		self.name_var = tk.StringVar()
		self.father_name_var = tk.StringVar()
		self.age_var = tk.StringVar()
		self.gender_var = tk.StringVar(value="Female")
		self.cnic_var = tk.StringVar()
		self.temp_var = tk.StringVar(value="98.6")
		self.bp_var = tk.StringVar(value="120/80")
		self.weight_var = tk.StringVar()
		self.diabetic_var = tk.StringVar()
		self.fees_var = tk.StringVar(value="Normal")
		self.status_var = tk.StringVar(value="Ready")
		self.last_saved_var = tk.StringVar(value="—")
		self.address_text: Optional[tk.Text] = None

	def _build_layout(self) -> None:
		# Main container without scrolling
		main_frame = ttk.Frame(self, padding=10)
		main_frame.grid(row=0, column=0, sticky="nsew")
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		main_frame.columnconfigure(0, weight=0)
		main_frame.columnconfigure(1, weight=1)
		main_frame.rowconfigure(11, weight=0)  # Give space to content rows

		clinic_label = ttk.Label(
			main_frame,
			text=self._clinic_name,
			style="ClinicTitle.TLabel",
		)
		clinic_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

		form_heading = ttk.Label(
			main_frame, text="Patient Intake Form", style="FormHeading.TLabel"
		)
		form_heading.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))

		self._add_date_opd_row(main_frame, row=2)
		self._add_row(main_frame, "Patient Name", self.name_var, row=3)
		self._add_row(
			main_frame,
			"Father / Husband Name",
			self.father_name_var,
			row=4,
		)
		self._add_age_gender_row(main_frame, row=5)
		self._add_row(main_frame, "CNIC (if available)", self.cnic_var, row=6)
		self._add_address_row(main_frame, row=7)
		self._add_temperature_bp_row(main_frame, row=8)
		self._add_weight_diabetic_row(main_frame, row=9)
		self._add_fees_row(main_frame, row=10)

		button_row = ttk.Frame(main_frame)
		button_row.grid(row=11, column=0, columnspan=2, pady=(8, 5), sticky="ew")
		button_row.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

		save_btn = ttk.Button(
			button_row,
			text="Save",
			style="Accent.TButton",
			command=self._handle_save,
		)
		save_btn.grid(row=0, column=0, padx=3, sticky="ew")

		report_btn = ttk.Button(
			button_row,
			text="Generate Report",
			command=self._handle_report,
		)
		report_btn.grid(row=0, column=1, padx=3, sticky="ew")

		open_folder_btn = ttk.Button(
			button_row,
			text="Open Data Folder",
			command=self._handle_open_data_folder,
		)
		open_folder_btn.grid(row=0, column=2, padx=3, sticky="ew")

		view_excel_btn = ttk.Button(
			button_row,
			text="View Excel",
			command=self._handle_view_excel,
		)
		view_excel_btn.grid(row=0, column=3, padx=3, sticky="ew")

		clear_btn = ttk.Button(
			button_row,
			text="Clear",
			command=self.reset_form,
		)
		clear_btn.grid(row=0, column=4, padx=3, sticky="ew")

		exit_btn = ttk.Button(
			button_row,
			text="Exit",
			style="Danger.TButton",
			command=self._handle_exit,
		)
		exit_btn.grid(row=0, column=5, padx=3, sticky="ew")

		status_frame = ttk.Frame(main_frame)
		status_frame.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(5, 0))
		status_frame.columnconfigure(1, weight=1)

		ttk.Label(status_frame, text="Last Saved:").grid(row=0, column=0, sticky="w")
		self.last_saved_label = ttk.Label(status_frame, textvariable=self.last_saved_var)
		self.last_saved_label.grid(row=0, column=1, sticky="w")

		self.status_label = ttk.Label(
			status_frame,
			textvariable=self.status_var,
			foreground=STATUS_COLORS["default"],
		)
		self.status_label.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")

	def _add_date_opd_row(self, parent: ttk.Frame, row: int) -> None:
		frame = ttk.Frame(parent)
		frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)

		ttk.Label(frame, text="Date").grid(row=0, column=0, sticky="w")

		if DateEntry is not None:
			date_widget = DateEntry(
				frame,
				textvariable=self.date_var,
				date_pattern="dd/mm/yyyy",
				width=12,
			)
			date_widget.set_date(datetime.now())
		else:
			date_widget = ttk.Entry(frame, textvariable=self.date_var, width=14)
		date_widget.grid(row=0, column=1, padx=(6, 24), sticky="w")
		self._date_widget = date_widget

		ttk.Label(frame, text="OPD No").grid(row=0, column=2, sticky="w")
		opd_entry = ttk.Entry(frame, textvariable=self.opd_no_var, width=18)
		opd_entry.grid(row=0, column=3, padx=(6, 0), sticky="w")

	def _add_row(
		self,
		parent: ttk.Frame,
		label: str,
		variable: tk.StringVar,
		row: int,
	) -> None:
		ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
		entry = ttk.Entry(parent, textvariable=variable, width=46)
		entry.grid(row=row, column=1, sticky="ew", pady=3)

	def _add_age_gender_row(self, parent: ttk.Frame, row: int) -> None:
		ttk.Label(parent, text="Age & Sex").grid(row=row, column=0, sticky="w", pady=3)
		frame = ttk.Frame(parent)
		frame.grid(row=row, column=1, sticky="ew", pady=3)

		age_entry = ttk.Entry(frame, textvariable=self.age_var, width=6)
		age_entry.grid(row=0, column=0, sticky="w")
		ttk.Label(frame, text="years").grid(row=0, column=1, padx=(4, 16))

		male_btn = ttk.Radiobutton(
			frame,
			text="Male",
			variable=self.gender_var,
			value="Male",
		)
		male_btn.grid(row=0, column=2, padx=(0, 8))

		female_btn = ttk.Radiobutton(
			frame,
			text="Female",
			variable=self.gender_var,
			value="Female",
		)
		female_btn.grid(row=0, column=3, padx=(0, 8))

	def _add_address_row(self, parent: ttk.Frame, row: int) -> None:
		ttk.Label(parent, text="Address").grid(row=row, column=0, sticky="nw", pady=3)
		text_widget = tk.Text(parent, height=4, width=46, wrap="word")
		text_widget.configure(font=("Segoe UI", 11))
		text_widget.grid(row=row, column=1, sticky="ew", pady=3)
		self.address_text = text_widget

	def _add_temperature_bp_row(self, parent: ttk.Frame, row: int) -> None:
		ttk.Label(parent, text="Temperature (°F)").grid(
			row=row, column=0, sticky="w", pady=3
		)
		frame = ttk.Frame(parent)
		frame.grid(row=row, column=1, sticky="ew", pady=3)

		temp_entry = ttk.Entry(frame, textvariable=self.temp_var, width=8)
		temp_entry.grid(row=0, column=0, sticky="w")
		ttk.Label(frame, text="°F").grid(row=0, column=1, padx=(4, 16))

		ttk.Label(frame, text="B.P").grid(row=0, column=2, padx=(0, 6))
		bp_entry = ttk.Entry(frame, textvariable=self.bp_var, width=10)
		bp_entry.grid(row=0, column=3, sticky="w")

	def _add_weight_diabetic_row(self, parent: ttk.Frame, row: int) -> None:
		ttk.Label(parent, text="Weight").grid(
			row=row, column=0, sticky="w", pady=3
		)
		frame = ttk.Frame(parent)
		frame.grid(row=row, column=1, sticky="ew", pady=3)

		weight_entry = ttk.Entry(frame, textvariable=self.weight_var, width=8)
		weight_entry.grid(row=0, column=0, sticky="w")
		ttk.Label(frame, text="kg").grid(row=0, column=1, padx=(4, 16))

		ttk.Label(frame, text="Diabetic").grid(row=0, column=2, padx=(0, 6))
		diabetic_entry = ttk.Entry(frame, textvariable=self.diabetic_var, width=10)
		diabetic_entry.grid(row=0, column=3, sticky="w")
		ttk.Label(frame, text="mg/dl").grid(row=0, column=4, padx=(4, 0))

	def _add_fees_row(self, parent: ttk.Frame, row: int) -> None:
		ttk.Label(parent, text="Type of Fees").grid(row=row, column=0, sticky="w", pady=3)
		frame = ttk.Frame(parent)
		frame.grid(row=row, column=1, sticky="w", pady=3)

		for idx, (value, label) in enumerate(FEES_OPTIONS.items()):
			ttk.Radiobutton(
				frame,
				text=label,
				value=value,
				variable=self.fees_var,
			).grid(row=0, column=idx, padx=(0 if idx == 0 else 16, 0))

	def _handle_save(self) -> None:
		record = self._persist_form(status_message="Record saved successfully")
		if record:
			self._last_record = record

	def _handle_report(self) -> None:
		# Check if a record has been saved
		if not self._last_record:
			messagebox.showwarning(
				"No Record Saved",
				"Please save the record first before generating a report."
			)
			self.set_status("Save record before generating report", status="error")
			return

		try:
			report_path = self._on_generate_report(self._last_record)
		except Exception as exc:  # pragma: no cover - UI feedback path
			messagebox.showerror("Report Failed", str(exc))
			self.set_status("Error: unable to generate report", status="error")
			return

		self.set_status(f"Report generated at {report_path.name}", status="success")

	def _handle_exit(self) -> None:
		if messagebox.askokcancel("Exit", "Close the Clinic Data Entry application?"):
			try:
				self._on_exit()
			except Exception:
				# If exit handler fails, just quit
				self.quit()

	def _collect_form_data(self) -> Optional[dict]:
		try:
			visit_date = parse_date(self.date_var.get().strip())
		except ValueError:
			messagebox.showwarning(
				"Validation", "Date must follow the DD/MM/YYYY format (e.g. 25/10/2025)."
			)
			return None

		opd_no = self.opd_no_var.get().strip()
		if not opd_no:
			messagebox.showwarning("Validation", "OPD number is required.")
			return None

		name = self.name_var.get().strip()
		if not name:
			messagebox.showwarning("Validation", "Patient name is required.")
			return None

		father_name = self.father_name_var.get().strip()
		if not father_name:
			messagebox.showwarning(
				"Validation", "Father / Husband name cannot be left blank."
			)
			return None

		age_raw = self.age_var.get().strip()
		try:
			age = int(age_raw)
			if age <= 0:
				raise ValueError
		except ValueError:
			messagebox.showwarning(
				"Validation", "Please enter a valid age (positive whole number)."
			)
			return None

		gender = self.gender_var.get()
		if gender not in {"Male", "Female"}:
			messagebox.showwarning("Validation", "Select Male or Female for sex.")
			return None

		cnic_raw = self.cnic_var.get().strip()
		if cnic_raw and not CNIC_PATTERN.match(cnic_raw):
			messagebox.showwarning(
				"Validation",
				"CNIC must be 13 digits (with or without dashes), e.g. 12345-1234567-1.",
			)
			return None

		address = (self.address_text.get("1.0", "end") if self.address_text else "").strip()
		if not address:
			messagebox.showwarning("Validation", "Address is required.")
			return None

		temperature_raw = self.temp_var.get().strip()
		try:
			temperature = float(temperature_raw)
			if not (TEMP_RANGE_F[0] <= temperature <= TEMP_RANGE_F[1]):
				messagebox.showwarning(
					"Validation",
					"Temperature should be between 80°F and 110°F.",
				)
				return None
		except ValueError:
			messagebox.showwarning("Validation", "Temperature must be a numeric value.")
			return None

		bp_value = self.bp_var.get().strip()
		if not BP_PATTERN.match(bp_value):
			messagebox.showwarning(
				"Validation",
				"Blood pressure must follow the systolic/diastolic format (e.g. 120/80).",
			)
			return None

		try:
			weight = coerce_optional_float(self.weight_var.get())
			if weight is not None and weight <= 0:
				raise ValueError
		except ValueError:
			messagebox.showwarning(
				"Validation", "Weight must be a positive number if provided."
			)
			return None

		try:
			diabetic = coerce_optional_float(self.diabetic_var.get())
			if diabetic is not None and diabetic <= 0:
				raise ValueError
		except ValueError:
			messagebox.showwarning(
				"Validation", "Diabetic reading must be a positive number if provided."
			)
			return None

		fees_type = self.fees_var.get()
		if fees_type not in FEES_OPTIONS:
			messagebox.showwarning("Validation", "Select a fees type (Normal or Urgent).")
			return None

		return {
			"date": visit_date,
			"opd_no": opd_no,
			"name": name,
			"father_name": father_name,
			"age": age,
			"gender": gender,
			"cnic": cnic_raw or None,
			"address": address,
			"temperature": temperature,
			"bp": bp_value,
			"weight": weight,
			"diabetic": diabetic,
			"fees_type": fees_type,
		}

	def reset_form(self) -> None:
		today = datetime.now()
		self.date_var.set(format_date(today))
		if isinstance(self._date_widget, DateEntry):  # type: ignore[arg-type]
			try:
				self._date_widget.set_date(today)
			except Exception:  # pragma: no cover - widget specific failure
				pass

		self.opd_no_var.set("")
		self.name_var.set("")
		self.father_name_var.set("")
		self.age_var.set("")
		self.gender_var.set("Female")
		self.cnic_var.set("")
		self.temp_var.set("98.6")
		self.bp_var.set("120/80")
		self.weight_var.set("")
		self.diabetic_var.set("")
		self.fees_var.set("Normal")
		if self.address_text:
			self.address_text.delete("1.0", "end")

		self._last_record = None
		self.last_saved_var.set("—")
		self.set_status("Form cleared", status="default")

	def set_status(self, message: str, status: str = "default") -> None:
		self.status_var.set(message)
		color = STATUS_COLORS.get(status, STATUS_COLORS["default"])
		self.status_label.configure(foreground=color)

	def _persist_form(self, *, status_message: str) -> Optional["PatientRecord"]:
		form_data = self._collect_form_data()
		if not form_data:
			return None

		try:
			record = self._on_save(form_data)
		except Exception as exc:  # pragma: no cover - UI feedback path
			messagebox.showerror("Save Failed", str(exc))
			self.set_status("Error: unable to save record", status="error")
			return None

		self._last_record = record
		self.last_saved_var.set(format_date(record.date))
		self.set_status(status_message, status="success")
		return record

	def _handle_open_data_folder(self) -> None:
		"""Open the data folder in file explorer."""
		# Get the clinic data folder (Documents/OPD Data)
		data_folder = get_clinic_data_folder()
		
		# Open in file explorer
		try:
			open_directory(data_folder)
			self.set_status("Opened data folder", status="success")
		except Exception as e:
			messagebox.showerror("Error", f"Could not open data folder: {e}")
			self.set_status("Failed to open folder", status="error")

	def _handle_view_excel(self) -> None:
		"""Open the current month's Excel file."""
		from datetime import datetime

		# Get current month's Excel file in Documents/OPD Data
		now = datetime.now()
		month_name = now.strftime("%B%Y")
		excel_filename = f"ClinicData_{month_name}.xlsx"
		data_folder = get_clinic_data_folder()
		excel_path = data_folder / excel_filename

		# Check if file exists
		if not excel_path.exists():
			messagebox.showinfo(
				"File Not Found",
				f"No Excel file found for {now.strftime('%B %Y')}.\n\n"
				f"The file will be created when you save the first record this month."
			)
			self.set_status("Excel file not found", status="default")
			return

		# Open the Excel file
		try:
			open_path(excel_path)
			self.set_status(f"Opened {excel_filename}", status="success")
		except Exception as e:
			messagebox.showerror("Error", f"Could not open Excel file: {e}")
			self.set_status("Failed to open Excel", status="error")


__all__ = ["MainWindow"]
