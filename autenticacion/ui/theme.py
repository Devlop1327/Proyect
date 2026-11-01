"""Tokens de diseño, temas y colores reutilizables para el sistema PQRS."""
import reflex as rx


def _ldc_reg(light: str, dark: str):
    """Condicional de modo claro/oscuro."""
    return rx.color_mode_cond(light=light, dark=dark)


ORANGE = "#e85d04"
ORANGE_LIGHT = "#fff7ed"
ORANGE_BORDER = "#fdba74"
NAVY = "#1e3a8a"
NAVY_DARK = "#172554"
BLUE_ACC = "#2563eb"
RED_ERR = "#ef4444"
GREEN_OK = "#16a34a"
VIOLET = "#8b5cf6"

PAGE_BG = _ldc_reg("#f8fafc", "#0b1120")
CARD_BG = _ldc_reg("#ffffff", "#1e293b")
CARD_BDR = _ldc_reg("#e2e8f0", "#334155")
TEXT_MAIN = _ldc_reg("#1e293b", "#f1f5f9")
TEXT_SUB = _ldc_reg("#64748b", "#94a3b8")
TEXT_LABEL = _ldc_reg("#374151", "#cbd5e1")
INPUT_BG = _ldc_reg("#ffffff", "#0f172a")
INPUT_BDR = _ldc_reg("#d1d5db", "#475569")
INPUT_FOC = BLUE_ACC
SECT_BG = _ldc_reg("#f0f7ff", "#0f172a")
DIVIDER = _ldc_reg("#e2e8f0", "#334155")

