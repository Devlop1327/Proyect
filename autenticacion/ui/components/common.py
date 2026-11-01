"""Componentes básicos y utilitarios de interfaz de usuario."""
import reflex as rx


def label_requerido(texto: str) -> rx.Component:
    """Etiqueta de formulario con indicador de asterisco obligatorio."""
    return rx.hstack(
        rx.text(texto, color=rx.color_mode_cond(light="black", dark="white")),
        rx.text("*", color="orange.500"),
        spacing="1",
        align_items="center",
    )


def password_strength_label(password: str) -> rx.Component:
    """Indicador visual de robustez de contraseña para formularios."""
    return rx.cond(
        password != "",
        rx.text(
            "Fortaleza de la contraseña: ",
            rx.cond(
                (password.length() >= 8) & (password != ""),
                "Media",
                "Débil",
            ),
            color=rx.cond(
                (password.length() >= 8) & (password != ""),
                "yellow.400",
                "red.400",
            ),
            font_size="xs",
        ),
        rx.box(),
    )


def pqrs_badge(title: str, desc: str, color: str) -> rx.Component:
    """Badge / Tarjeta informativa de tipo de solicitud PQRS."""
    card_bg = rx.color_mode_cond(light="white", dark="#111827")
    border = rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155")
    text_sec = rx.color_mode_cond(light="#475569", dark="#cbd5e1")

    return rx.card(
        rx.vstack(
            rx.box(
                rx.text(title, color="white", font_weight="bold", font_size="sm"),
                bg=color,
                padding_x="3",
                padding_y="2",
                border_radius="full",
            ),
            rx.text(desc, color=text_sec, font_size="sm"),
            spacing="3",
            align_items="start",
        ),
        bg=card_bg,
        border=border,
        border_radius="xl",
        p="5",
        width="100%",
        max_width="360px",
        box_shadow="sm",
    )


def brand_footer() -> rx.Component:
    """Franja inferior con logos institucionales (Universidad del Valle y GOV.CO)."""
    return rx.container(
        rx.hstack(
            rx.image(src="/unival_logo.svg", alt="Universidad del Valle", height="48px"),
            rx.spacer(),
            rx.image(src="/govco_logo.svg", alt="Gobierno de Colombia", height="48px"),
            spacing="6",
            align_items="center",
            justify="center",
        ),
        width="100%",
        padding_top="12px",
        padding_bottom="12px",
        bg="white",
        _dark={"bg": "gray.900", "borderColor": "gray.700"},
        border_top="1px solid #e2e8f0",
    )

