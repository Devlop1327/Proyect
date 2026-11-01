import reflex as rx
from ...state import State

def kpi_metric_card(title: str, value, icon_name: str, accent_color: str, icon_bg: str) -> rx.Component:
    """Tarjeta KPI reutilizable (reportes y dashboard funcionario)."""
    text_main = rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")
    text_sub = rx.color_mode_cond(light="#64748b", dark="#7ea8c9")
    card_bg = rx.color_mode_cond(light="#ffffff", dark="#0f1e35")
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon_name, size=18, color=accent_color),
                    bg=icon_bg,
                    border_radius="10px",
                    width="38px",
                    height="38px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    flex_shrink="0",
                ),
                rx.spacer(),
                width="100%",
            ),
            rx.vstack(
                rx.text(
                    value,
                    font_size="2rem",
                    font_weight="800",
                    color=text_main,
                    line_height="1",
                    letter_spacing="-0.03em",
                ),
                rx.text(title, font_size="12px", color=text_sub, font_weight="500"),
                spacing="1",
                align_items="start",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        bg=card_bg,
        border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
        border_top=f"3px solid {accent_color}",
        border_radius="14px",
        padding="18px 20px",
        box_shadow=rx.color_mode_cond(
            light="0 1px 3px rgba(0,0,0,0.05)",
            dark="0 2px 12px rgba(0,0,0,0.3)",
        ),
        transition="transform 0.18s ease, box-shadow 0.18s ease",
        _hover={
            "transform": "translateY(-3px)",
            "box_shadow": f"0 8px 24px {accent_color}28",
        },
        width="100%",
    )


def dashboard_chart_card(title: str, chart_component, card_bg=None, card_border=None, extra_content=None) -> rx.Component:
    """Tarjeta contenedora de gráficas reutilizable en dashboards."""
    bg = card_bg if card_bg is not None else rx.color_mode_cond(light="rgba(255, 255, 255, 0.85)", dark="rgba(15, 23, 42, 0.7)")
    border = card_border if card_border is not None else rx.color_mode_cond(light="1px solid rgba(255, 255, 255, 0.5)", dark="1px solid rgba(51, 65, 85, 0.5)")
    return rx.box(
        rx.vstack(
            rx.heading(
                title,
                size="5",
                color=rx.color_mode_cond(light="#0f172a", dark="#f8fafc"),
                font_weight="bold",
            ),
            chart_component,
            extra_content if extra_content is not None else rx.box(),
            spacing="4",
            align_items="stretch",
            width="100%",
        ),
        p="5",
        width="100%",
        bg=bg,
        backdrop_filter="blur(24px)",
        border=border,
        border_radius="2xl",
        box_shadow="0 14px 28px -16px rgba(15,23,42,0.2)",
    )


def action_icon_button(icon_name: str, text: str, color_scheme: str = "blue", is_disabled: bool = False) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(icon_name, size=16, transition="transform 0.2s ease"),
            rx.text(
                text,
                class_name="action-text",
                font_weight="600",
                font_size="12px",
                white_space="nowrap",
                opacity="0",
                max_width="0px",
                overflow="hidden",
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                margin_left="0px"
            ),
            spacing="0",
            align_items="center",
        ),
        variant="soft",
        size="2",
        radius="full",
        color_scheme=color_scheme,
        is_disabled=is_disabled,
        transition="all 0.2s ease",
        _hover={
            "transform": "translateY(-1px)",
            "& > svg": {
                "transform": "scale(1.1)"
            },
            "& .action-text": {
                "opacity": "1",
                "max_width": "120px",
                "margin_left": "6px"
            }
        }
    )

def modal_vencimiento_solicitudes() -> rx.Component:
    """Modal compartido para listar solicitudes por rango/semáforo de vencimiento."""
    return rx.cond(
        State.vencimiento_modal_abierto,
        rx.box(
            rx.vstack(
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon("layers", color="white", size=28),
                            bg="linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
                            p="3",
                            border_radius="2xl",
                            box_shadow="0 10px 25px -5px rgba(59, 130, 246, 0.5)",
                        ),
                        rx.vstack(
                            rx.heading(
                                State.rango_vencimiento_seleccionado,
                                size="6",
                                font_weight="900",
                                color="white",
                            ),
                            rx.hstack(
                                rx.text("Total:", color="rgba(255,255,255,0.9)", font_size="sm", font_weight="bold"),
                                rx.badge(
                                    State.solicitudes_vencimiento_filtradas.length(),
                                    color_scheme="blue",
                                    variant="solid",
                                    radius="full",
                                ),
                                rx.text(
                                    "solicitudes en este rango.",
                                    color="rgba(255,255,255,0.8)",
                                    font_size="sm",
                                    font_weight="medium",
                                ),
                                spacing="2",
                                align_items="center",
                            ),
                            spacing="1",
                        ),
                        spacing="4",
                        align_items="center",
                        width="100%",
                    ),
                    p="8",
                    bg="linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                    border_bottom="1px solid rgba(255,255,255,0.05)",
                    border_top_left_radius="3xl",
                    border_top_right_radius="3xl",
                    width="100%",
                ),
                rx.box(
                    rx.cond(
                        State.solicitudes_vencimiento_filtradas,
                        rx.vstack(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Radicado"),
                                        rx.table.column_header_cell("Tipo"),
                                        rx.table.column_header_cell("Asunto"),
                                        rx.table.column_header_cell("Área Responsable"),
                                        rx.table.column_header_cell("Días Restantes"),
                                        rx.table.column_header_cell("Acción"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.solicitudes_vencimiento_filtradas,
                                        lambda s: rx.table.row(
                                            rx.table.row_header_cell(
                                                rx.badge(s.get("radicado"), color_scheme="blue", variant="surface", radius="full")
                                            ),
                                            rx.table.cell(s.get("tipo_solicitud")),
                                            rx.table.cell(s.get("asunto")),
                                            rx.table.cell(s.get("area_responsable")),
                                            rx.table.cell(
                                                rx.hstack(
                                                    rx.box(
                                                        width="8px",
                                                        height="8px",
                                                        bg=s.get("semaforo_fill"),
                                                        border_radius="full",
                                                    ),
                                                    rx.text(
                                                        s.get("remaining_str", ""),
                                                        font_weight="semibold",
                                                        color=s.get("semaforo_fill"),
                                                    ),
                                                    spacing="2",
                                                    align_items="center",
                                                )
                                            ),
                                            rx.table.cell(
                                                rx.button(
                                                    rx.icon("eye", size=16),
                                                    on_click=lambda: State.abrir_detalle_solicitud(s.get("id")),
                                                    variant="soft",
                                                    color_scheme="blue",
                                                    size="1",
                                                    radius="full",
                                                )
                                            ),
                                        ),
                                    )
                                ),
                                width="100%",
                                variant="ghost",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("inbox", size=48, color="gray"),
                                rx.text(
                                    "No se encontraron solicitudes en este rango.",
                                    font_weight="semibold",
                                    color="gray",
                                ),
                                spacing="2",
                                padding_y="8",
                            ),
                            width="100%",
                        ),
                    ),
                    p="6",
                    max_height="400px",
                    overflow_y="auto",
                    width="100%",
                    bg=rx.color_mode_cond(light="rgba(255, 255, 255, 0.4)", dark="rgba(15, 23, 42, 0.4)"),
                ),
                rx.box(
                    rx.button(
                        "Cerrar Ventana",
                        on_click=State.cerrar_vencimiento_modal,
                        bg="linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
                        color="white",
                        size="3",
                        width="100%",
                    ),
                    p="5",
                    border_top=rx.color_mode_cond(light="1px solid rgba(0,0,0,0.05)", dark="1px solid rgba(255,255,255,0.05)"),
                    bg=rx.color_mode_cond(light="rgba(248, 250, 252, 0.4)", dark="rgba(11, 17, 32, 0.4)"),
                    border_bottom_left_radius="3xl",
                    border_bottom_right_radius="3xl",
                    width="100%",
                ),
                spacing="0",
            ),
            p="0",
            border=rx.color_mode_cond(light="1px solid rgba(255,255,255,0.6)", dark="1px solid rgba(255,255,255,0.08)"),
            border_radius="3xl",
            bg=rx.color_mode_cond(light="rgba(255, 255, 255, 0.9)", dark="rgba(15, 23, 42, 0.8)"),
            backdrop_filter="blur(20px)",
            width="100%",
            max_width="850px",
            position="fixed",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            z_index="1000",
            box_shadow=rx.color_mode_cond(
                light="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                dark="0 25px 50px -12px rgba(0, 0, 0, 0.5)",
            ),
        ),
    )


