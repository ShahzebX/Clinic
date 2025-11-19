"""PDF report generator for the Clinic app."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from database.db_manager import PatientRecord
from utils.helpers import (
	format_date,
	month_subdirectory,
	open_path,
	sanitize_filename,
)


class PdfGenerator:
	"""Create printable patient visit reports using ReportLab."""

	DEFAULT_DOCTORS: Sequence[tuple[str, str]] = (
		("Dr. Gulab Hussain Kashmiri", "M.B.B.S, R.M.P"),
		("Dr. Abdullah Umar Kashmiri", "M.B.B.S, R.M.P"),
	)

	def __init__(
		self,
		reports_dir: Path | str,
		clinic_name: str,
		subtitle: str | None = "Main Badin Road, Matli",
		doctors: Iterable[tuple[str, str]] | None = None,
		footer_days: str = "Monday to Saturday",
		footer_time: str = "Time: 04 P.M to 10 P.M",
		footer_sunday_hours: str = "Sunday Time: 10 A.M to 10 P.M",
		footer_credit: str = "Developed by M.Shahzeb | Custom Software Solutions | +92 312 7021303",
	) -> None:
		self.reports_dir = Path(reports_dir)
		self.clinic_name = clinic_name
		self.subtitle = subtitle or ""
		self.doctors = tuple(doctors) if doctors else self.DEFAULT_DOCTORS
		self.footer_days = footer_days
		self.footer_time = footer_time
		self.footer_sunday_hours = footer_sunday_hours
		self.footer_credit = footer_credit

	def generate(self, record: PatientRecord, auto_open: bool = False) -> Path:
		month_dir = month_subdirectory(self.reports_dir, record.date)
		filename = (
			f"{sanitize_filename(record.name)}_{record.date.strftime('%Y%m%d')}_{sanitize_filename(record.opd_no)}.pdf"
		)
		pdf_path = month_dir / filename

		doc = canvas.Canvas(str(pdf_path), pagesize=A5)
		width, height = A5
		outer_margin = 12 * mm
		inner_margin = outer_margin + 8

		doc.setTitle(f"Visit Report - {record.name}")
		doc.setFillColor(black)

		y = height - 30  # Added top padding
		doc.setFont("Helvetica-Bold", 15)  # Reduced font size
		doc.drawCentredString(width / 2, y, self.clinic_name)

		if self.subtitle:
			y -= 11
			doc.setFont("Helvetica", 10)
			doc.drawCentredString(width / 2, y, f"({self.subtitle})")

		y -= 15  # Removed line and reduced padding

		if self.doctors:
			left_doc = self.doctors[0]
			doc.setFont("Helvetica-Bold", 10)
			doc.drawString(inner_margin, y, left_doc[0])
			doc.setFont("Helvetica", 9)
			doc.drawString(inner_margin, y - 12, left_doc[1])

			if len(self.doctors) > 1:
				right_doc = self.doctors[1]
				doc.setFont("Helvetica-Bold", 10)
				doc.drawRightString(width - inner_margin, y, right_doc[0])
				doc.setFont("Helvetica", 9)
				doc.drawRightString(width - inner_margin - 70, y - 12, right_doc[1])

			y -= 30
		else:
			y -= 18

		left_x = inner_margin + 10
		right_x = width - inner_margin - 10
		line_gap = 11
		label_font = ("Helvetica-Bold", 9.5)
		value_font = ("Helvetica", 9.5)

		def draw_label_value(x: float, text_y: float, label: str, value: str) -> None:
			doc.setFont(*label_font)
			label_text = f"{label}:"
			doc.drawString(x, text_y, label_text)
			label_width = doc.stringWidth(label_text, label_font[0], label_font[1])
			doc.setFont(*value_font)
			doc.drawString(x + label_width + 4, text_y, value)

		def draw_label_value_right(x: float, text_y: float, label: str, value: str) -> None:
			doc.setFont(*value_font)
			value_width = doc.stringWidth(value, value_font[0], value_font[1])
			doc.setFont(*label_font)
			label_text = f"{label}:"
			label_width = doc.stringWidth(label_text, label_font[0], label_font[1])
			start_x = x - (label_width + 4 + value_width)
			doc.drawString(start_x, text_y, label_text)
			doc.setFont(*value_font)
			doc.drawString(start_x + label_width + 4, text_y, value)

		draw_label_value(inner_margin, y, "Date", format_date(record.date))
		draw_label_value_right(width - inner_margin, y, "OPD No ", record.opd_no or "—")
		y -= line_gap+3

		# Removed left_x and right_x redefinition - using inner_margin directly

		draw_label_value(inner_margin, y, "Patient Name", record.name)
		y -= line_gap
		draw_label_value(inner_margin, y, "Father / Husband Name", record.father_name or "—")
		y -= line_gap
		# Display age with months
		age_text = f"{record.age} years"
		if hasattr(record, 'age_months') and record.age_months:
			age_text += f" {record.age_months} months"
		draw_label_value(inner_margin, y, "Age", age_text)
		draw_label_value_right(width - inner_margin - 17, y, "Sex", record.gender)
		y -= line_gap
		draw_label_value(inner_margin, y, "CNIC (if available)", record.cnic or "—")
		y -= line_gap
		draw_label_value(inner_margin, y, "Address", record.address or "—")
		y -= line_gap+3
		
		fees_y = y
		doc.setFont(*label_font)
		fees_label = "Type of Fees:"
		normal_text = "Normal - Rs. 100"
		urgent_text = "Urgent - Rs. 200"

		# Draw "Type of Fees:" label
		doc.drawString(inner_margin, fees_y, fees_label)
		fees_label_width = doc.stringWidth(fees_label, label_font[0], label_font[1])
		
		# Draw Normal Fee
		normal_x = inner_margin + fees_label_width + 10
		doc.drawString(normal_x, fees_y, normal_text)
		normal_text_width = doc.stringWidth(normal_text, label_font[0], label_font[1])
		doc.setFont("ZapfDingbats", 12)
		doc.drawString(normal_x + normal_text_width + 8, fees_y, "✓" if record.fees_type == "Normal" else "")

		# Draw Urgent Fee
		doc.setFont(*label_font)
		urgent_text_width = doc.stringWidth(urgent_text, label_font[0], label_font[1])
		urgent_x_start = width - inner_margin - urgent_text_width - 20
		doc.drawString(urgent_x_start, fees_y, urgent_text)
		doc.setFont("ZapfDingbats", 12)
		doc.drawString(urgent_x_start + urgent_text_width + 8, fees_y, "✓" if record.fees_type == "Urgent" else "")

		doc.setFillColor(black)
		y = fees_y - (line_gap - 2)

		y -= 10
		doc.setFont("Helvetica-Bold", 11)
		doc.drawAlignedString(width / 3 + 5, y, "Diagnosis")
		
		# Add horizontal line after Diagnosis
		y -= 3
		doc.setLineWidth(1)
		doc.line(0, y, width, y)

		body_top = y - 5
		bottom_rule_y = outer_margin + 6
		body_bottom = bottom_rule_y + 3
		body_height = body_top - body_bottom

		left_col_width = 30 * mm
		left_col_x0 = outer_margin - 16  # Start within printable area
		left_col_x1 = left_col_x0 + left_col_width
		doc.line(left_col_x1, body_bottom, left_col_x1, body_top)

		# Follow-Up section
		follow_label_y = body_top - 10
		doc.setFont("Helvetica-Bold", 10)
		doc.drawString(left_col_x0, follow_label_y, "Follow-Up:")

		# VITALS section
		vitals_title_y = follow_label_y - 30
		doc.setFont("Helvetica-Bold", 10)
		doc.drawString(left_col_x0, vitals_title_y, "VITALS")


		line_x_start = left_col_x0 + 6
		line_x_end = left_col_x1 - 6
		row_gap = 45
		current_y = vitals_title_y - 20
		
		# Prepare vitals data from record
		vitals = (
			("Temp", f"{record.temperature}°F" if record.temperature else ""),
			("Pulse ", ""),
			("B.P ", record.bp if record.bp else ""),
			("SPO  ", ""),
			("Wt ", f"{record.weight} kg" if record.weight else ""),
			("RBS", f"{record.diabetic}" if record.diabetic else ""),
		)
		
		for label, value in vitals:
			doc.setFont("Helvetica-Bold", 9)
			doc.drawString(line_x_start, current_y, f"{label}:")
			# Draw subscript 2 for SPO2
			if label == "SPO  ":
				spo_width = doc.stringWidth("SPO", "Helvetica-Bold", 9)
				doc.setFont("Helvetica-Bold", 6)
				doc.drawString(line_x_start + spo_width, current_y - 2, "2")
				doc.setFont("Helvetica-Bold", 9)
			doc.line(line_x_start + 35, current_y - 2, line_x_end, current_y - 2)
			if value:
				doc.setFont("Helvetica", 9)
				doc.drawString(line_x_start + 37, current_y, value)
			current_y -= row_gap

		doc.setFont("Helvetica-Bold", 9)
		doc.drawString(line_x_start, current_y, "H/O:")

		# Treatment section
		treatment_label_y = body_top - 10
		doc.setFont("Helvetica-Bold", 10)
		doc.drawString(left_col_x1 + 6, treatment_label_y, "Treatment:")

		doc.setLineWidth(1)
		doc.line(0, bottom_rule_y, width, bottom_rule_y)
		
		# Footer line: Days and times distributed across the width
		doc.setFont("Helvetica-Bold", 8)
		footer_y = bottom_rule_y - 12
		
		# Left: Monday to Saturday + Time (with proper margin)
		left_text = f"{self.footer_days}    {self.footer_time}"
		doc.drawString(outer_margin, footer_y, left_text)
		
		# Right: Sunday hours (with proper margin)
		doc.drawRightString(width - outer_margin, footer_y, self.footer_sunday_hours)
		
		# Second line: Developer credit (centered, smaller font, within margins)
		doc.setFont("Helvetica", 7)
		doc.drawCentredString(width / 2, footer_y - 13, self.footer_credit)

		doc.showPage()
		doc.save()

		if auto_open:
			open_path(pdf_path)

		return pdf_path


__all__ = ["PdfGenerator"]
