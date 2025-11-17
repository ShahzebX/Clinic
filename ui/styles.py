"""Shared style constants for the Clinic app UI."""

from __future__ import annotations

from tkinter import ttk


PRIMARY_FONT = ("Segoe UI", 11)
CLINIC_TITLE_FONT = ("Segoe UI", 22, "bold")
FORM_HEADING_FONT = ("Segoe UI", 14)
BUTTON_FONT = ("Segoe UI", 11, "bold")
STATUS_COLORS = {
	"default": "#2D3748",
	"success": "#2F855A",
	"error": "#C53030",
}


def apply_theme(root) -> None:
	"""Configure ttk styles to deliver a clean, readable layout."""

	style = ttk.Style(root)
	# Use a reliable platform theme when available
	try:
		style.theme_use("clam")
	except Exception:
		pass

	style.configure("TLabel", font=PRIMARY_FONT, padding=2)
	style.configure("ClinicTitle.TLabel", font=CLINIC_TITLE_FONT, padding=(0, 0, 0, 8))
	style.configure("FormHeading.TLabel", font=FORM_HEADING_FONT, padding=(0, 0, 0, 16))
	style.configure("TButton", font=PRIMARY_FONT)
	style.configure("Accent.TButton", font=BUTTON_FONT)
	style.configure("Danger.TButton", font=BUTTON_FONT, foreground="#FFFFFF", background="#C53030")
	style.map(
		"Accent.TButton",
		foreground=[("pressed", "#1A202C"), ("active", "#1A202C")],
		background=[("pressed", "#EDF2F7"), ("active", "#E2E8F0"), ("!disabled", "#CBD5F5")],
	)


__all__ = ["apply_theme", "STATUS_COLORS"]
