from ..components.attachments import (
    ui_boton_descargar_adjunto,
    ui_enlace_archivo,
    ui_tarjeta_adjunto,
)
import reflex as rx
from ...state import State
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar, access_denied_widget
from ..components.footer import footer

def dashboard() -> rx.Component:
    # Bento Variables
    text_color = rx.color_mode_cond(light="#0f172a", dark="#f8fafc")
    subtext_color = rx.color_mode_cond(light="#64748b", dark="#94a3b8")
    card_bg = rx.color_mode_cond(light="rgba(255, 255, 255, 0.6)", dark="rgba(30, 41, 59, 0.4)")
    card_border = rx.color_mode_cond(light="1px solid rgba(255, 255, 255, 0.8)", dark="1px solid rgba(51, 65, 85, 0.5)")
    accent_bg = rx.color_mode_cond(light="linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)", dark="linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(30, 64, 175, 0.2) 100%)")

    # Bloque A: Perfil Izquierdo
    bento_profile = rx.box(
        rx.vstack(
            rx.box(
                rx.heading(rx.cond(State.nombres, State.nombres.to_string()[0:1], "C"), size="9", color="#3b82f6"),
                width="80px", height="80px", border_radius="2xl", bg=rx.color_mode_cond(light="white", dark="#0f172a"),
                display="flex", align_items="center", justify_content="center", box_shadow="0 10px 15px -3px rgba(0,0,0,0.1)",
                margin_bottom="4"
            ),
            rx.heading("¡Hola, ", State.nombres, "!", size="7", color=text_color, font_weight="bold"),
            rx.text("Bienvenido a tu panel digital.", color=subtext_color, font_size="sm"),
            
            rx.divider(margin_y="6", opacity="0.5"),
            
            rx.vstack(
                rx.hstack(rx.icon("file-text", size=18, color="#3b82f6"), rx.text("Total Solicitudes", font_weight="medium"), rx.spacer(), rx.heading(State.solicitudes.length(), size="4"), width="100%"),
                spacing="4", width="100%"
            ),
            
            rx.spacer(),
            rx.box(
                rx.icon("shield-check", size=24, color="#10b981", margin_bottom="2"),
                rx.text("Cuenta verificada y segura.", font_size="xs", color=subtext_color),
                bg=rx.color_mode_cond(light="white", dark="rgba(15, 23, 42, 0.5)"), padding="4", border_radius="xl", width="100%"
            ),
            spacing="2", align_items="start", height="100%", width="100%"
        ),
        p="8", bg=card_bg, backdrop_filter="blur(24px)", border=card_border, border_radius="3xl",
        box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.05)", height="100%", width="100%", grid_row="span 2"
    )

    # Bloque B: Nueva Solicitud (estilo kpi_metric_card)
    _kpi_card_bg = rx.color_mode_cond(light="#ffffff", dark="#0f1e35")
    bento_action = rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("file-plus-2", size=18, color="#3b82f6"),
                    bg=rx.color_mode_cond(light="#eff6ff", dark="rgba(59,130,246,0.18)"),
                    border_radius="10px",
                    width="38px", height="38px",
                    display="flex", align_items="center", justify_content="center",
                    flex_shrink="0",
                ),
                rx.spacer(),
                width="100%"
            ),
            rx.vstack(
                rx.text("Nueva", font_size="2rem", font_weight="800", color=text_color, line_height="1", letter_spacing="-0.03em"),
                rx.text("Crear Solicitud PQRS", font_size="12px", color=subtext_color, font_weight="500"),
                rx.link(
                    rx.button("Crear ahora ", rx.icon("arrow-right", size=14), size="2", color_scheme="blue", radius="full", margin_top="2"),
                    href="/solicitudes"
                ),
                spacing="1", align_items="start"
            ),
            spacing="3", align_items="start", width="100%"
        ),
        bg=_kpi_card_bg,
        border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
        border_top="3px solid #3b82f6",
        border_radius="14px",
        padding="18px 20px",
        box_shadow=rx.color_mode_cond(light="0 1px 3px rgba(0,0,0,0.05)", dark="0 2px 12px rgba(0,0,0,0.3)"),
        transition="transform 0.18s ease, box-shadow 0.18s ease",
        _hover={"transform": "translateY(-3px)", "box_shadow": "0 8px 24px rgba(59,130,246,0.2)"},
        width="100%"
    )

    # Bloque B2: Rastrea Solicitud (estilo kpi_metric_card)
    bento_consulta = rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("search", size=18, color="#8b5cf6"),
                    bg=rx.color_mode_cond(light="#f5f3ff", dark="rgba(139,92,246,0.18)"),
                    border_radius="10px",
                    width="38px", height="38px",
                    display="flex", align_items="center", justify_content="center",
                    flex_shrink="0",
                ),
                rx.spacer(),
                width="100%"
            ),
            rx.vstack(
                rx.text("Rastrea", font_size="2rem", font_weight="800", color=text_color, line_height="1", letter_spacing="-0.03em"),
                rx.text("Consultar estado de tu solicitud", font_size="12px", color=subtext_color, font_weight="500"),
                rx.hstack(
                    rx.input(
                        placeholder="Número de radicado...",
                        value=State.consulta_radicado,
                        on_change=State.set_consulta_radicado,
                        bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a"),
                        border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                        size="2", radius="full", width="100%"
                    ),
                    rx.button(rx.icon("arrow-right", size=14), on_click=State.consultar_desde_dashboard, color_scheme="purple", size="2", radius="full"),
                    width="100%", margin_top="2", spacing="2"
                ),
                spacing="1", align_items="start"
            ),
            spacing="3", align_items="start", width="100%"
        ),
        bg=_kpi_card_bg,
        border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
        border_top="3px solid #8b5cf6",
        border_radius="14px",
        padding="18px 20px",
        box_shadow=rx.color_mode_cond(light="0 1px 3px rgba(0,0,0,0.05)", dark="0 2px 12px rgba(0,0,0,0.3)"),
        transition="transform 0.18s ease, box-shadow 0.18s ease",
        _hover={"transform": "translateY(-3px)", "box_shadow": "0 8px 24px rgba(139,92,246,0.2)"},
        width="100%"
    )

    # Bloque C: Bandeja de Entrada (Grid Inferior)
    bento_grid = rx.cond(
        State.solicitudes,
        rx.grid(
            rx.foreach(
                State.solicitudes,
                lambda solicitud: rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.badge(
                                solicitud["tipo_solicitud"],
                                variant="soft",
                                radius="full",
                                size="2",
                                color_scheme=rx.cond(
                                    solicitud["tipo_solicitud"] == "Petición",
                                    "blue",
                                    rx.cond(
                                        solicitud["tipo_solicitud"] == "Queja",
                                        "orange",
                                        rx.cond(solicitud["tipo_solicitud"] == "Reclamo", "red", "green"),
                                    ),
                                ),
                            ),
                            rx.spacer(),
                            rx.badge(
                                solicitud["estado"],
                                variant="soft",
                                radius="full",
                                size="2",
                                font_weight="medium",
                                color_scheme=rx.cond(
                                    solicitud["estado"] == "Radicada",
                                    "blue",
                                    rx.cond(
                                        solicitud["estado"] == "Cerrada",
                                        "green",
                                        "orange",
                                    ),
                                ),
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        rx.box(rx.text(solicitud["radicado"], font_size="xs", font_family="monospace", color="#94a3b8"), rx.text(solicitud["fecha"], font_size="xs", color="#94a3b8"), display="flex", justify_content="space-between", width="100%", margin_bottom="2"),
                        rx.heading(solicitud["asunto"], size="4", color=text_color, margin_bottom="1", line_height="1.3"),
                        rx.text(solicitud["descripcion"], font_size="sm", color=subtext_color, style={"display": "-webkit-box", "WebkitLineClamp": "2", "WebkitBoxOrient": "vertical", "overflow": "hidden"}),
                        # Mostrar el área responsable si está asignada
                        rx.cond(
                            solicitud.get("area_responsable") != "",
                            rx.hstack(
                                rx.icon("building-2", size=12, color="#f59e0b"),
                                rx.text(
                                    solicitud.get("area_responsable", "Sin área"),
                                    font_size="xs",
                                    color="#f59e0b",
                                    font_weight="medium",
                                ),
                                spacing="1",
                                align_items="center",
                                padding_x="2",
                                padding_y="1",
                                bg=rx.color_mode_cond(light="#fffbeb", dark="rgba(245,158,11,0.15)"),
                                border="1px solid rgba(245,158,11,0.3)",
                                border_radius="md",
                                width="fit-content",
                                margin_top="1",
                            ),
                            rx.box(),
                        ),
                        rx.spacer(),
                        rx.cond(solicitud.get("documento_basename"), rx.hstack(rx.icon("paperclip", size=14, color="#3b82f6"), ui_enlace_archivo(solicitud.get("documento_href", "#"), rx.text("Ver adjunto", color="#3b82f6", font_size="xs"), _hover={"text_decoration": "underline"}), spacing="2", align_items="center", bg=rx.color_mode_cond(light="white", dark="rgba(15,23,42,0.5)"), padding_x="3", padding_y="1.5", border_radius="md", width="100%"), rx.box()),
                        spacing="0", align_items="start", width="100%", height="100%"
                    ),
                    p="6", bg=card_bg, border=card_border, border_radius="2xl", width="100%", height="100%", box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)", backdrop_filter="blur(16px)", _hover={"transform": "translateY(-4px)", "border_color": "rgba(59, 130, 246, 0.5)", "box_shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"}, transition="all 0.3s ease"
                )
            ),
            template_columns={"base": "1fr", "lg": "repeat(2, 1fr)"}, gap="6", width="100%"
        ),
        # Empty State
        rx.center(
            rx.vstack(
                rx.box(rx.icon("layers", size=48, color="#cbd5e1"), bg="rgba(255,255,255,0.5)", padding="6", border_radius="full"),
                rx.heading("Tu bandeja está impecable", size="5", color=text_color),
                rx.text("Aún no hay trámites aquí.", color=subtext_color),
                spacing="3", align_items="center"
            ),
            p="12", bg=card_bg, border=card_border, border_radius="3xl", width="100%", height="100%", min_height="300px", backdrop_filter="blur(16px)"
        )
    )

    return rx.cond(
        rx.State.is_hydrated,
        rx.cond(
            State.es_autenticada & (State.rol_usuario == "ciudadano"),
            rx.box(
                navbar(),
                rx.center(
                    # Fondos holográficos abstractos
                    rx.box(position="absolute", top="-10%", left="0%", width="500px", height="500px", bg="rgba(139, 92, 246, 0.1)", border_radius="full", filter="blur(120px)", z_index="0"),
                    rx.box(position="absolute", bottom="-10%", right="0%", width="600px", height="600px", bg="rgba(59, 130, 246, 0.1)", border_radius="full", filter="blur(150px)", z_index="0"),
                    
                    # Bento Grid Maestro
                    rx.grid(
                        bento_profile,
                        rx.vstack(bento_action, bento_consulta, bento_grid, spacing="6", width="100%", height="100%"),
                        template_columns={"base": "1fr", "xl": "300px 1fr"},
                        gap="6", width="100%", max_width="1400px", padding_x={"base": "4", "md": "8"}, padding_y="12", z_index="1"
                    ),
                    width="100%", min_height="90vh", position="relative", overflow="hidden", align_items="start"
                ),
                bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a"), width="100%", min_height="100vh"
            ),
            rx.box(
                navbar(),
                rx.center(access_denied_widget("Esta página es solo para ciudadanos."), size="3"),
                bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a"), min_height="100vh"
            )
        ),
        rx.center(rx.spinner(size="3", color="#3b82f6"), height="50vh")
    )



