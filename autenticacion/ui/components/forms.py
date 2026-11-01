import reflex as rx
from ..theme import (
    _ldc_reg, ORANGE, ORANGE_LIGHT, ORANGE_BORDER, NAVY, NAVY_DARK, BLUE_ACC,
    RED_ERR, GREEN_OK, VIOLET, PAGE_BG, CARD_BG, CARD_BDR, TEXT_MAIN, TEXT_SUB,
    TEXT_LABEL, INPUT_BG, INPUT_BDR, INPUT_FOC, SECT_BG, DIVIDER,
)

def _label(texto: str, required: bool = False) -> rx.Component:
    """Label con asterisco naranja si es requerido."""
    return rx.hstack(
        rx.text(texto, font_size="13px", font_weight="600", color=TEXT_LABEL),
        rx.cond(
            required,
            rx.text("*", color=ORANGE, font_size="13px", font_weight="700"),
            rx.box(),
        ),
        spacing="1",
        align_items="center",
        margin_bottom="4px",
    )


def _input_style() -> dict:
    return dict(
        bg=INPUT_BG,
        border=f"1px solid {INPUT_BDR}",
        border_radius="8px",
        color=TEXT_MAIN,
        font_size="14px",
        height="42px",
        padding_x="12px",
        width="100%",
        _placeholder={"color": TEXT_SUB, "font_size": "13px"},
        _focus={
            "outline": "none",
            "border_color": INPUT_FOC,
            "box_shadow": f"0 0 0 3px rgba(37,99,235,0.12)",
        },
    )


def _select_style() -> dict:
    return dict(
        bg=INPUT_BG,
        border=f"1px solid {INPUT_BDR}",
        border_radius="8px",
        color=TEXT_MAIN,
        font_size="14px",
        _focus={"border_color": INPUT_FOC},
    )


def _input_s() -> dict:
    """Compatibilidad: alias de `_input_style` usado en el código."""
    return _input_style()


def _select_s() -> dict:
    """Compatibilidad: alias de `_select_style` usado en el código."""
    return _select_style()


def _field(label: str, component: rx.Component, required: bool = True) -> rx.Component:
    """Campo completo: label + input."""
    return rx.vstack(
        _label(label, required),
        component,
        spacing="0",
        align_items="start",
        width="100%",
    )


def _field_with_check(
    label: str,
    component: rx.Component,
    is_valid,
    required: bool = True,
) -> rx.Component:
    """Campo con ícono de validación verde a la derecha."""
    return rx.vstack(
        _label(label, required),
        rx.hstack(
            component,
            rx.cond(
                is_valid,
                rx.box(
                    rx.icon("circle-check", size=18, color="#16a34a"),
                    flex_shrink="0",
                ),
                rx.box(width="18px"),
            ),
            spacing="2",
            align_items="center",
            width="100%",
        ),
        spacing="0",
        align_items="start",
        width="100%",
    )


def _section_header(icon: str, title: str, subtitle: str = "") -> rx.Component:
    """Encabezado de sección con línea naranja inferior."""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=16, color=ORANGE),
                width="32px", height="32px",
                border_radius="8px",
                bg=ORANGE_LIGHT,
                border=f"1px solid {ORANGE_BORDER}",
                display="flex", align_items="center", justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(title, font_size="14px", font_weight="700", color=TEXT_MAIN),
                rx.cond(
                    subtitle != "",
                    rx.text(subtitle, font_size="12px", color=TEXT_SUB),
                    rx.box(),
                ),
                spacing="0", align_items="start",
            ),
            spacing="3", align_items="center",
        ),
        border_bottom=f"2px solid {ORANGE}",
        padding_bottom="10px",
        margin_bottom="16px",
        width="100%",
    )


def _section(icon: str, title: str, content: rx.Component, subtitle: str = "") -> rx.Component:
    """Sección con encabezado y contenido en tarjeta estilizada."""
    return rx.box(
        _section_header(icon, title, subtitle),
        rx.box(
            content,
            bg=CARD_BG,
            border=f"1px solid {CARD_BDR}",
            border_radius="14px",
            padding="18px 20px",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


