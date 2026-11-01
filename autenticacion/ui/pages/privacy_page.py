import reflex as rx
from ...state import State
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar
from ..components.footer import footer

def politica_privacidad_page() -> rx.Component:
    text_color = rx.color_mode_cond(light="#0f172a", dark="#f8fafc")
    subtext = rx.color_mode_cond(light="#475569", dark="#94a3b8")
    card_bg = rx.color_mode_cond(light="rgba(255, 255, 255, 0.9)", dark="rgba(15, 23, 42, 0.7)")
    card_border = rx.color_mode_cond(light="1px solid rgba(203, 213, 225, 0.75)", dark="1px solid rgba(51, 65, 85, 0.65)")

    def section_card(title: str, icon: str, body: rx.Component) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon(icon, size=18, color="#60a5fa"),
                        p="2.5",
                        border_radius="lg",
                        bg=rx.color_mode_cond(light="rgba(219, 234, 254, 0.9)", dark="rgba(37, 99, 235, 0.18)"),
                        border=rx.color_mode_cond(light="1px solid #bfdbfe", dark="1px solid rgba(96, 165, 250, 0.28)"),
                    ),
                    rx.heading(title, size="4", color=text_color, font_weight="bold"),
                    spacing="3",
                    align_items="center",
                    width="100%",
                ),
                body,
                spacing="3",
                width="100%",
                align_items="start",
            ),
            p={"base": "5", "md": "6"},
            bg=card_bg,
            border=card_border,
            border_radius="2xl",
            backdrop_filter="blur(18px)",
            box_shadow=rx.color_mode_cond(light="0 18px 40px -24px rgba(30, 64, 175, 0.4)", dark="0 18px 40px -24px rgba(2, 6, 23, 0.9)"),
            width="100%",
        )

    return rx.box(
        navbar(),
        rx.center(
            rx.box(
                rx.box(position="absolute", top="-140px", left="-120px", width="360px", height="360px", bg="rgba(37, 99, 235, 0.20)", border_radius="full", filter="blur(95px)", z_index="0"),
                rx.box(position="absolute", bottom="-140px", right="-110px", width="360px", height="360px", bg="rgba(14, 165, 233, 0.18)", border_radius="full", filter="blur(95px)", z_index="0"),
                rx.vstack(
                    rx.box(
                        rx.vstack(
                            rx.badge("Transparencia y protección de datos", color_scheme="blue", variant="soft", radius="full"),
                            rx.heading("Política de Privacidad", size="8", color=text_color, font_weight="bold", letter_spacing="-0.02em"),
                            rx.text(
                                "En esta plataforma tratamos tus datos con responsabilidad, transparencia y seguridad. "
                                "Tu información personal se usa únicamente para gestionar solicitudes PQRS y mejorar el servicio.",
                                color=subtext,
                                font_size="md",
                                line_height="1.6",
                            ),
                            rx.hstack(
                                rx.box(
                                    rx.icon("scale", size=18, color="#93c5fd"),
                                    rx.text("Ley 1581 de 2012", font_size="xs", color=subtext, font_weight="medium"),
                                    spacing="2",
                                    align_items="center",
                                ),
                                rx.box(
                                    rx.icon("clipboard-check", size=18, color="#93c5fd"),
                                    rx.text("Uso limitado a PQRS", font_size="xs", color=subtext, font_weight="medium"),
                                    spacing="2",
                                    align_items="center",
                                ),
                                spacing="4",
                                flex_wrap="wrap",
                                width="100%",
                            ),
                            spacing="3",
                            align_items="start",
                        ),
                        p={"base": "5", "md": "7"},
                        bg=rx.color_mode_cond(light="rgba(255, 255, 255, 0.75)", dark="rgba(15, 23, 42, 0.55)"),
                        border=card_border,
                        border_radius="3xl",
                        backdrop_filter="blur(18px)",
                        box_shadow=rx.color_mode_cond(light="0 30px 60px -30px rgba(30, 64, 175, 0.35)", dark="0 30px 60px -20px rgba(2, 6, 23, 0.9)"),
                        width="100%",
                        z_index="1",
                    ),
                    rx.grid(
                        section_card(
                            "Datos recolectados",
                            "database",
                            rx.vstack(
                                rx.text("Recopilamos datos necesarios para la gestión de solicitudes:", color=subtext, font_size="sm"),
                                rx.vstack(
                                    rx.text("�?� Correo electrónico", color=subtext, font_size="sm"),
                                    rx.text("�?� Identificación (tipo y número)", color=subtext, font_size="sm"),
                                    rx.text("�?� Nombres y apellidos", color=subtext, font_size="sm"),
                                    rx.text("�?� Teléfono y ubicación (departamento/ciudad/dirección)", color=subtext, font_size="sm"),
                                    spacing="1",
                                    align_items="start",
                                ),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        section_card(
                            "Finalidad del tratamiento",
                            "target",
                            rx.vstack(
                                rx.text("Usamos tus datos para:", color=subtext, font_size="sm"),
                                rx.vstack(
                                    rx.text("�?� Contactarte y notificarte sobre el estado de tu PQRS", color=subtext, font_size="sm"),
                                    rx.text("�?� Radicar y administrar la solicitud en el sistema", color=subtext, font_size="sm"),
                                    rx.text("�?� Generar trazabilidad y auditoría del proceso de atención", color=subtext, font_size="sm"),
                                    spacing="1",
                                    align_items="start",
                                ),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        section_card(
                            "Derechos del titular",
                            "badge-check",
                            rx.vstack(
                                rx.text(
                                    "Puedes solicitar consulta, actualización, corrección o eliminación de tus datos conforme a la normativa vigente.",
                                    color=subtext,
                                    font_size="sm",
                                    line_height="1.6",
                                ),
                                rx.text(
                                    "También puedes revocar la autorización cuando sea procedente.",
                                    color=subtext,
                                    font_size="sm",
                                ),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        section_card(
                            "Contacto y solicitudes",
                            "mail",
                            rx.vstack(
                                rx.text("Si necesitas ejercer tus derechos o tienes dudas:", color=subtext, font_size="sm"),
                                rx.hstack(
                                    rx.icon("at-sign", size=16, color="#60a5fa"),
                                    rx.text("Soporte: ", font_size="sm", color=subtext),
                                    rx.text("soporte@empresa.com", font_size="sm", color=rx.color_mode_cond(light="#1d4ed8", dark="#93c5fd"), font_weight="semibold"),
                                    spacing="2",
                                    flex_wrap="wrap",
                                ),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        columns={"base": "1", "lg": "2"},
                        gap="4",
                        width="100%",
                        z_index="1",
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button(
                                rx.icon("arrow-left", size=18),
                                "Volver",
                                size="3",
                                variant="soft",
                                radius="full",
                                color_scheme="gray",
                            ),
                            href="/registro",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button(
                                rx.icon("file-text", size=18),
                                "Ir a registro",
                                size="3",
                                radius="full",
                                color_scheme="blue",
                                box_shadow="0 10px 24px -12px rgba(37, 99, 235, 0.65)",
                            ),
                            href="/registro",
                        ),
                        width="100%",
                        z_index="1",
                        flex_wrap="wrap",
                        spacing="3",
                    ),
                    spacing="5",
                    width="100%",
                    z_index="1",
                ),
                width="100%",
                max_width="1100px",
                position="relative",
                px={"base": "4", "md": "8"},
                py={"base": "8", "md": "12"},
            ),
            width="100%",
            min_height="90vh",
        ),
        bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a"),
        min_height="100vh",
    )



