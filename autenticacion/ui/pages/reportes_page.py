from ..components.attachments import (
    ui_boton_descargar_adjunto,
    ui_enlace_archivo,
    ui_tarjeta_adjunto,
    ui_tarjeta_adjunto_historial,
)
from ..components.kpi import (
    kpi_metric_card,
    dashboard_chart_card,
    action_icon_button,
    modal_vencimiento_solicitudes,
)
import reflex as rx
from reflex.components import recharts as rc
from ...state import State
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar, access_denied_widget
from ..components.footer import footer

def reportes_page() -> rx.Component:
    def chart_card(title: str, chart_component, width="100%", extra_content=None):
        return rx.box(
            rx.vstack(
                rx.heading(title, size="5", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc"), font_weight="bold"),
                chart_component,
                extra_content if extra_content else rx.box(),
                spacing="4",
                align_items="center",
                width="100%"
            ),
            p="6",
            bg=rx.color_mode_cond(light="#ffffff", dark="#1e293b"),
            border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
            border_radius="3xl",
            box_shadow=rx.color_mode_cond(light="0 4px 6px -1px rgba(0, 0, 0, 0.05)", dark="none"),
            width=width,
            _hover={"box_shadow": rx.color_mode_cond(light="0 10px 15px -3px rgba(0, 0, 0, 0.1)", dark="0 10px 15px -3px rgba(0, 0, 0, 0.5)"), "transform": "translateY(-2px)", "border_color": rx.color_mode_cond(light="#93c5fd", dark="#3b82f6")},
            transition="all 0.3s ease"
        )

    content = rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                # Encabezado y Command Center
                rx.hstack(
                    rx.vstack(
                        rx.heading("Centro de Reportes", size="8", color=rx.color_mode_cond(light="#0f172a", dark="#f8fafc"), font_weight="bold", letter_spacing="-0.02em"),
                        rx.text("Análisis avanzado y métricas de solicitudes", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"), font_size="lg"),
                        align_items="start",
                        spacing="1"
                    ),
                    rx.spacer(),
                    # Barra de Filtros y Descarga
                    rx.box(
                        rx.hstack(
                            rx.hstack(
                                rx.icon("calendar", size=16, color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                rx.select(
                                    ["�?ltimos 12 meses", "�?ltimos 6 meses", "Este año"],
                                    placeholder="Rango",
                                    variant="soft", radius="full", size="2"
                                ),
                                spacing="2", align_items="center"
                            ),
                            rx.divider(orientation="vertical", height="20px", border_color=rx.color_mode_cond(light="#e2e8f0", dark="#334155")),
                            rx.hstack(
                                rx.icon("filter", size=16, color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                rx.select(
                                    ["Todos", "Petición", "Queja", "Reclamo", "Sugerencia"],
                                    placeholder="Tipo",
                                    value=State.filter_tipo_solicitud,
                                    on_change=State.set_filter_tipo_solicitud,
                                    variant="soft", radius="full", size="2"
                                ),
                                spacing="2", align_items="center"
                            ),
                            rx.divider(orientation="vertical", height="20px", border_color=rx.color_mode_cond(light="#e2e8f0", dark="#334155")),
                            rx.box(
                                rx.button(
                                    rx.icon("download", size=16),
                                    "Exportar",
                                    on_click=State.toggle_menu_descarga,
                                    color_scheme="blue",
                                    variant="solid",
                                    radius="full",
                                    box_shadow="0 4px 6px -1px rgba(59, 130, 246, 0.3)",
                                ),
                                rx.cond(
                                    State.mostrar_menu_descarga,
                                    rx.vstack(
                                        rx.button(rx.icon("file-spreadsheet", size=16), "Excel + Gráfica", on_click=State.descargar_excel_y_abrir, color_scheme="green", width="100%", size="2", variant="soft", justify="start"),
                                        rx.button(rx.icon("file-text", size=16), "CSV", on_click=State.descargar_csv_y_abrir, color_scheme="cyan", width="100%", size="2", variant="soft", justify="start"),
                                        spacing="2",
                                        position="absolute",
                                        top="120%",
                                        right="0",
                                        bg=rx.color_mode_cond(light="rgba(255, 255, 255, 0.9)", dark="rgba(30, 41, 59, 0.9)"),
                                        backdrop_filter="blur(12px)",
                                        border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                                        border_radius="xl",
                                        p="2",
                                        box_shadow="xl",
                                        z_index="10",
                                        width="140px"
                                    ),
                                    rx.box()
                                ),
                                position="relative"
                            ),
                            spacing="4",
                            align_items="center"
                        ),
                        bg=rx.color_mode_cond(light="rgba(248, 250, 252, 0.6)", dark="rgba(15, 23, 42, 0.4)"),
                        backdrop_filter="blur(16px)",
                        border=rx.color_mode_cond(light="1px solid rgba(226, 232, 240, 0.8)", dark="1px solid rgba(30, 41, 59, 0.8)"),
                        border_radius="full",
                        padding="2",
                        padding_x="5",
                        box_shadow=rx.color_mode_cond(light="0 4px 6px -1px rgba(0,0,0,0.05)", dark="0 4px 6px -1px rgba(0,0,0,0.5)")
                    ),
                    width="100%",
                    align_items="end",
                ),
                
                # Fila de KPIs (Top Row)
                rx.grid(
                    kpi_metric_card(
                        "Total Solicitudes",
                        State.numero_solicitudes,
                        "layers",
                        "#2563eb",
                        rx.color_mode_cond(light="#eff6ff", dark="rgba(37, 99, 235, 0.18)"),
                    ),
                    kpi_metric_card(
                        "Radicadas",
                        State.numero_solicitudes_radicadas,
                        "file-plus-2",
                        "#f59e0b",
                        rx.color_mode_cond(light="#fffbeb", dark="rgba(245, 158, 11, 0.16)"),
                    ),
                    kpi_metric_card(
                        "En Proceso",
                        State.kpi_en_curso_count,
                        "activity",
                        "#0ea5e9",
                        rx.color_mode_cond(light="#f0fdfe", dark="rgba(14, 165, 233, 0.16)"),
                    ),
                    kpi_metric_card(
                        "Cerradas",
                        State.kpi_cerradas_count,
                        "circle-check",
                        "#10b981",
                        rx.color_mode_cond(light="#ecfdf5", dark="rgba(16, 185, 129, 0.14)"),
                    ),
                    columns={"base": "1", "sm": "2", "lg": "4"},
                    spacing="6",
                    width="100%",
                    margin_y="6",
                    style={"gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))"},
                ),

                # Contenedor de Layout Horizontal Responsivo (Gráficas + Sidebar Premium)
                rx.flex(
                    # Columna Izquierda: Gráficas y Distribución por Área
                    rx.vstack(
                        # Rejilla de Gráficas (2 Columnas)
                        rx.grid(
                            # 1. Cumplimiento (Dona)
                            chart_card(
                                "Nivel de Cumplimiento",
                                rc.pie_chart(
                                    rc.tooltip(),
                                    rc.legend(layout="horizontal", vertical_align="bottom", align="center"),
                                    rc.pie(
                                        rc.cell(fill="#10b981"),
                                        rc.cell(fill="#ef4444"),
                                        data=State.compliance_chart_data,
                                        data_key="value",
                                        name_key="name",
                                        cx="50%",
                                        cy="50%",
                                        outer_radius=100,
                                        inner_radius=65,
                                        label=True,
                                    ),
                                    width="100%",
                                    height=300,
                                ),
                                extra_content=rx.center(
                                    rx.hstack(
                                        rx.text(State.compliance_percentage, font_size="4xl", font_weight="bold", color="#10b981"),
                                        rx.text("%", font_size="xl", font_weight="bold", color="#10b981"),
                                    ),
                                    margin_top="-150px",
                                    margin_bottom="110px",
                                    pointer_events="none"
                                )
                            ),

                            # 2. Tipos de Solicitud (Barras)
                            chart_card(
                                "Volumen por Tipo",
                                rc.bar_chart(
                                    rc.x_axis(data_key="name"),
                                    rc.y_axis(domain=[0, State.max_registros_tipo]),
                                    rc.tooltip(),
                                    rc.bar(data_key="cantidad", fill="#3b82f6", radius=[6, 6, 0, 0]),
                                    data=State.data_grafica_tipo,
                                    width="100%",
                                    height=300,
                                )
                            ),

                            # 3. Tiempos de Respuesta (Línea)
                            chart_card(
                                "Tiempos Promedio de Respuesta",
                                rc.line_chart(
                                    rc.x_axis(data_key="month"),
                                    rc.y_axis(),
                                    rc.tooltip(),
                                    rc.line(type="monotone", data_key="dias", stroke="#8b5cf6", stroke_width=4, dot={"r": 5, "fill": "#8b5cf6", "stroke": "#ffffff", "strokeWidth": 2}),
                                    data=State.monthly_response_times,
                                    width="100%",
                                    height=300,
                                ),
                                extra_content=rx.box(),
                            ),

                            # 4. Solicitudes por vencer (Barras semáforo)
                            chart_card(
                                "Estado de Vencimiento",
                                rx.box(
                                    # Gráfico principal
                                    rc.bar_chart(
                                        rc.x_axis(data_key="name"),
                                        rc.y_axis(),
                                        rc.tooltip(),
                                        rc.bar(
                                            rc.cell(fill="#ef4444"),
                                            rc.cell(fill="#f59e0b"),
                                            rc.cell(fill="#f59e0b"),
                                            rc.cell(fill="#10b981"),
                                            data_key="cantidad",
                                            radius=[6, 6, 0, 0]
                                        ),
                                        data=State.solicitudes_por_vencer_data,
                                        width="100%",
                                        height=300,
                                    ),
                                    # Capa superpuesta con botones invisibles sobre cada barra para capturar clicks
                                    rx.hstack(
                                        rx.box(width="25%", height="100%", cursor="pointer", on_click=lambda: State.abrir_vencimiento_modal("Vencidas")),
                                        rx.box(width="25%", height="100%", cursor="pointer", on_click=lambda: State.abrir_vencimiento_modal("1-5 días")),
                                        rx.box(width="25%", height="100%", cursor="pointer", on_click=lambda: State.abrir_vencimiento_modal("6-10 días")),
                                        rx.box(width="25%", height="100%", cursor="pointer", on_click=lambda: State.abrir_vencimiento_modal(">10 días")),
                                        position="absolute",
                                        top="0",
                                        left="10%",  # offset for y-axis
                                        width="90%",
                                        height="85%", # offset for x-axis
                                        z_index="10",
                                        opacity="0"
                                    ),
                                    position="relative",
                                    width="100%"
                                ),
                                extra_content=rx.center(
                                    rx.hstack(
                                        rx.button("Vencidas", size="1", variant="soft", color_scheme="red", radius="full", on_click=lambda: State.abrir_vencimiento_modal("Vencidas")),
                                        rx.button("1-5 días", size="1", variant="soft", color_scheme="orange", radius="full", on_click=lambda: State.abrir_vencimiento_modal("1-5 días")),
                                        rx.button("6-10 días", size="1", variant="soft", color_scheme="yellow", radius="full", on_click=lambda: State.abrir_vencimiento_modal("6-10 días")),
                                        rx.button(">10 días", size="1", variant="soft", color_scheme="green", radius="full", on_click=lambda: State.abrir_vencimiento_modal(">10 días")),
                                        spacing="2",
                                        flex_wrap="wrap",
                                        justify_content="center"
                                    ),
                                    width="100%",
                                    margin_top="2"
                                )
                            ),
                            columns={"base": "1", "lg": "2"},
                            spacing="6",
                            width="100%",
                        ),

                        spacing="6",
                        flex="1",
                        width="100%",
                        align_items="stretch"
                    ),

                    # Columna Derecha: Sidebar con Tarjetas Premium
                    rx.vstack(
                        # 1. Resumen numérico
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("activity", size=16, color="#2563eb"),
                                    rx.text("Resumen de Actividad", font_size="sm", font_weight="700", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc")),
                                    spacing="2", align_items="center"
                                ),
                                rx.divider(border_color=rx.color_mode_cond(light="#e2e8f0", dark="#334155")),
                                rx.hstack(
                                    rx.text("Solicitudes Totales", font_size="13px", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"), flex="1"),
                                    rx.text(State.numero_solicitudes, font_size="13px", font_weight="700", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc")),
                                    width="100%", align_items="center",
                                    padding_y="2",
                                    border_bottom=f"1px solid {rx.color_mode_cond(light='#f1f5f9', dark='#1e293b')}"
                                ),
                                rx.hstack(
                                    rx.text("Tiempo Promedio Cierre", font_size="13px", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"), flex="1"),
                                    rx.text("10 min", font_size="13px", font_weight="700", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc")),
                                    width="100%", align_items="center",
                                    padding_y="2"
                                ),
                                spacing="3", align_items="stretch", width="100%"
                            ),
                            p="5",
                            bg=rx.color_mode_cond(light="#ffffff", dark="#1e293b"),
                            border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                            border_radius="2xl",
                            box_shadow="0 4px 6px -1px rgba(0,0,0,0.05)",
                            width="100%"
                        ),

                        # 2. Áreas Destacadas
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("building-2", size=16, color="#8b5cf6"),
                                    rx.text("Áreas con más solicitudes", font_size="sm", font_weight="700", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc")),
                                    spacing="2", align_items="center"
                                ),
                                rx.divider(border_color=rx.color_mode_cond(light="#e2e8f0", dark="#334155")),
                                rx.input(
                                    placeholder="Filtrar área...",
                                    value=State.search_area_query,
                                    on_change=State.set_search_area_query,
                                    variant="surface",
                                    radius="full",
                                    size="1",
                                    width="100%"
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.foreach(
                                            State.top_areas,
                                            lambda row: rx.hstack(
                                                rx.box(
                                                    rx.icon("users", size=14, color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                                    p="1",
                                                    bg=rx.color_mode_cond(light="#f1f5f9", dark="rgba(255,255,255,0.05)"),
                                                    border_radius="md",
                                                    flex_shrink="0"
                                                ),
                                                rx.text(row.get('name'), font_size="13px", font_weight="medium", color=rx.color_mode_cond(light="#334155", dark="#cbd5e1"), flex="1", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                                                rx.badge(row.get('total'), color_scheme="purple", variant="soft", radius="full", size="1"),
                                                width="100%",
                                                padding_y="2",
                                                border_bottom=f"1px solid {rx.color_mode_cond(light='#f1f5f9', dark='#1e293b')}",
                                                align_items="center",
                                                spacing="2"
                                            )
                                        ),
                                        spacing="0", width="100%"
                                    ),
                                    max_height="240px",
                                    overflow_y="auto",
                                    width="100%",
                                    padding_right="1"
                                ),
                                spacing="3", align_items="stretch", width="100%"
                            ),
                            p="5",
                            bg=rx.color_mode_cond(light="#ffffff", dark="#1e293b"),
                            border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                            border_radius="2xl",
                            box_shadow="0 4px 6px -1px rgba(0,0,0,0.05)",
                            width="100%"
                        ),

                        # 3. Estados Resumen
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("layers", size=16, color="#f59e0b"),
                                    rx.text("Estados actuales", font_size="sm", font_weight="700", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc")),
                                    spacing="2", align_items="center"
                                ),
                                rx.divider(border_color=rx.color_mode_cond(light="#e2e8f0", dark="#334155")),
                                rx.vstack(
                                    rx.foreach(
                                        State.data_grafica_estado,
                                        lambda row: rx.hstack(
                                            rx.box(
                                                width="8px", height="8px",
                                                border_radius="full",
                                                bg=rx.match(
                                                    row.get("name"),
                                                    ("Radicada", "#f59e0b"),
                                                    ("Asignada a Area", "#3b82f6"),
                                                    ("En Gestion de Area", "#8b5cf6"),
                                                    ("Solucionada", "#10b981"),
                                                    ("Reabierta", "#eab308"),
                                                    ("Cerrada", "#16a34a"),
                                                    "#64748b"
                                                ),
                                                flex_shrink="0"
                                            ),
                                            rx.text(row.get("name", ""), font_size="13px", color=rx.color_mode_cond(light="#334155", dark="#cbd5e1"), flex="1"),
                                            rx.text(row.get("cantidad", 0), font_size="13px", font_weight="700", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc")),
                                            spacing="3", align_items="center",
                                            padding_y="2",
                                            border_bottom=f"1px solid {rx.color_mode_cond(light='#f1f5f9', dark='#1e293b')}",
                                            width="100%"
                                        )
                                    ),
                                    spacing="0", width="100%"
                                ),
                                spacing="3", align_items="stretch", width="100%"
                            ),
                            p="5",
                            bg=rx.color_mode_cond(light="#ffffff", dark="#1e293b"),
                            border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                            border_radius="2xl",
                            box_shadow="0 4px 6px -1px rgba(0,0,0,0.05)",
                            width="100%"
                        ),
                        spacing="6",
                        width={"base": "100%", "lg": "320px"},
                        flex_shrink="0",
                        align_items="stretch"
                    ),
                    flex_direction={"base": "column", "lg": "row"},
                    spacing="6",
                    width="100%",
                    align_items="start",
                ),

                spacing="6",
                width="100%",
                max_width="1400px",
                padding_y="8"
            ),
            width="100%",
        ),
        
        # Modal de Vencimiento de Solicitudes
        rx.cond(
            State.vencimiento_modal_abierto,
            rx.box(
                rx.vstack(
                    rx.box(
                        # Orbes Decorativos Translúcidos
                        rx.box(position="absolute", top="-40px", left="-20%", width="150px", height="150px", 
                               bg=rx.cond(State.rango_vencimiento_seleccionado == "Vencidas", "rgba(239, 68, 68, 0.6)", 
                                          rx.cond(State.rango_vencimiento_seleccionado == "1-5 días", "rgba(245, 158, 11, 0.6)", "rgba(16, 185, 129, 0.6)")), 
                               border_radius="full", filter="blur(40px)"),
                        
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
                                    rx.cond(
                                        State.rango_vencimiento_seleccionado == "Vencidas",
                                        "Solicitudes Vencidas",
                                        rx.cond(
                                            State.rango_vencimiento_seleccionado == "1-5 días",
                                            "Críticas (1-5 días)",
                                            rx.cond(
                                                State.rango_vencimiento_seleccionado == "6-10 días",
                                                "Por Vencer (6-10 días)",
                                                "A Salvo (>10 días)"
                                            )
                                        )
                                    ),
                                    size="6", font_weight="900", background_image="linear-gradient(90deg, #ffffff, #e2e8f0)", background_clip="text", color="transparent"
                                ),
                                rx.hstack(
                                    rx.text(
                                        "Total:",
                                        color="rgba(255,255,255,0.9)",
                                        font_size="sm",
                                        font_weight="bold"
                                    ),
                                    rx.badge(
                                        State.solicitudes_vencimiento_filtradas.length(),
                                        color_scheme="blue",
                                        variant="solid",
                                        radius="full"
                                    ),
                                    rx.text(
                                        "solicitudes filtradas en este rango.",
                                        color="rgba(255,255,255,0.8)",
                                        font_size="sm",
                                        font_weight="medium"
                                    ),
                                    spacing="2",
                                    align_items="center"
                                ),
                                spacing="1"
                            ),
                            spacing="4",
                            align_items="center",
                            position="relative",
                            z_index="2",
                            width="100%"
                        ),
                        p="8",
                        bg="linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                        border_bottom="1px solid rgba(255,255,255,0.05)",
                        border_top_left_radius="3xl",
                        border_top_right_radius="3xl",
                        position="relative",
                        overflow="hidden",
                        width="100%"
                    ),
                    
                    # Contenido / Tabla de Solicitudes
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
                                                            border_radius="full"
                                                        ),
                                                        rx.text(
                                                            s.get("remaining_str", ""),
                                                            font_weight="semibold",
                                                            color=s.get("semaforo_fill")
                                                        ),
                                                        spacing="2",
                                                        align_items="center"
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("eye", size=16),
                                                        on_click=lambda: State.abrir_detalle_solicitud(s.get("id")),
                                                        variant="soft",
                                                        color_scheme="blue",
                                                        size="1",
                                                        radius="full"
                                                    )
                                                )
                                            )
                                        )
                                    ),
                                    width="100%",
                                    variant="ghost"
                                ),
                                spacing="4",
                                width="100%"
                            ),
                            # Estado Vacío
                            rx.center(
                                rx.vstack(
                                    rx.icon("inbox", size=48, color="gray"),
                                    rx.text("No se encontraron solicitudes pendientes en este rango.", font_weight="semibold", color="gray"),
                                    spacing="2",
                                    padding_y="8"
                                ),
                                width="100%"
                            )
                        ),
                        p="6",
                        max_height="400px",
                        overflow_y="auto",
                        width="100%",
                        bg=rx.color_mode_cond(light="rgba(255, 255, 255, 0.4)", dark="rgba(15, 23, 42, 0.4)")
                    ),
                    
                    # Botón de Cerrar
                    rx.box(
                        rx.button(
                            "Cerrar Ventana",
                            on_click=State.cerrar_vencimiento_modal,
                            bg="linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
                            color="white",
                            size="3",
                            width="100%",
                            box_shadow="0 4px 14px 0 rgba(59,130,246,0.39)",
                            _hover={"transform": "translateY(-2px)", "box_shadow": "0 6px 20px rgba(59,130,246,0.5)"},
                            transition="all 0.2s"
                        ),
                        p="5",
                        border_top=rx.color_mode_cond(light="1px solid rgba(0,0,0,0.05)", dark="1px solid rgba(255,255,255,0.05)"),
                        bg=rx.color_mode_cond(light="rgba(248, 250, 252, 0.4)", dark="rgba(11, 17, 32, 0.4)"),
                        border_bottom_left_radius="3xl",
                        border_bottom_right_radius="3xl",
                        width="100%"
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
                box_shadow=rx.color_mode_cond(light="0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0,0,0,0.05)", dark="0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.1)")
            )
        ),
        
        # Modal de Detalles de la Solicitud Seleccionada
        rx.cond(
            State.detalle_solicitud_modal_abierto,
            rx.box(
                # Fondo oscuro semitransparente detrás del modal
                rx.box(
                    position="fixed",
                    top="0",
                    left="0",
                    width="100vw",
                    height="100vh",
                    bg="rgba(15, 23, 42, 0.75)",
                    backdrop_filter="blur(10px)",
                    z_index="1050",
                    on_click=State.cerrar_detalle_solicitud
                ),
                # Contenido del Modal de Detalles
                rx.box(
                    rx.vstack(
                        # Encabezado con Gradiente Premium
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("info", size=24, color="#3b82f6"),
                                    rx.heading(
                                        f"Detalles de Solicitud: {State.solicitud_consultada.get('radicado', '')}",
                                        size="5",
                                        color="#ffffff"
                                    ),
                                    rx.spacer(),
                                    rx.button(
                                        rx.icon("x", size=20),
                                        on_click=State.cerrar_detalle_solicitud,
                                        variant="ghost",
                                        color="#ffffff",
                                        _hover={"bg": "rgba(255,255,255,0.1)"}
                                    ),
                                    width="100%",
                                    align_items="center"
                                ),
                                spacing="1",
                                align_items="start"
                            ),
                            p="6",
                            bg="linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                            border_bottom="1px solid rgba(255,255,255,0.05)",
                            border_top_left_radius="3xl",
                            border_top_right_radius="3xl",
                            position="relative",
                            overflow="hidden",
                            width="100%"
                        ),
                        
                        # Cuerpo del Modal (Scrollable)
                        rx.vstack(
                            rx.grid(
                                rx.vstack(
                                    rx.text("Número de Radicado:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                    rx.text(State.solicitud_consultada.get("radicado", ""), color=rx.color_mode_cond(light="#0f172a", dark="#ffffff"), font_size="sm", font_weight="semibold")
                                ),
                                rx.vstack(
                                    rx.text("Tipo de Solicitud:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                    rx.text(State.solicitud_consultada.get("tipo_solicitud", ""), color=rx.color_mode_cond(light="#0f172a", dark="#ffffff"), font_size="sm", font_weight="semibold")
                                ),
                                rx.vstack(
                                    rx.text("Estado Actual:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                    rx.badge(
                                        State.solicitud_consultada.get("estado", ""),
                                        color_scheme=rx.cond(
                                            State.solicitud_consultada.get("estado") == "Radicada",
                                            "orange",
                                            rx.cond(
                                                State.solicitud_consultada.get("estado") == "Actualizada",
                                                "blue",
                                                "green"
                                            )
                                        ),
                                        radius="full",
                                        variant="solid"
                                    )
                                ),
                                rx.vstack(
                                    rx.text("Fecha de Radicación:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                    rx.text(State.solicitud_consultada.get("fecha", ""), color=rx.color_mode_cond(light="#0f172a", dark="#ffffff"), font_size="sm")
                                ),
                                rx.vstack(
                                    rx.text("Área Responsable:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                    rx.text(State.solicitud_consultada.get("area_responsable", "No asignada"), color=rx.color_mode_cond(light="#0f172a", dark="#ffffff"), font_size="sm")
                                ),
                                rx.vstack(
                                    rx.text("Creado Por:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                    rx.text(State.solicitud_consultada.get("creado_por", ""), color=rx.color_mode_cond(light="#0f172a", dark="#ffffff"), font_size="sm")
                                ),
                                rx.cond(
                                    State.solicitud_consultada.get("calificacion_servicio") != None,
                                    rx.vstack(
                                        rx.text("Calificación:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                        rx.hstack(
                                            rx.icon("star", color="#f59e0b", size=16),
                                            rx.text(State.solicitud_consultada.get("calificacion_servicio", ""), font_weight="bold", color="#f59e0b", font_size="sm"),
                                            spacing="1", align_items="center"
                                        )
                                    )
                                ),
                                template_columns={"base": "1fr", "sm": "repeat(2, 1fr)", "md": "repeat(3, 1fr)"},
                                gap="4",
                                width="100%",
                                p="4",
                                border_radius="2xl",
                                bg=rx.color_mode_cond(light="#f1f5f9", dark="rgba(255,255,255,0.02)"),
                                border="1px dashed rgba(128,128,128,0.2)"
                            ),
                            
                            rx.vstack(
                                rx.text("Asunto:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                rx.text(State.solicitud_consultada.get("asunto", ""), color=rx.color_mode_cond(light="#0f172a", dark="#ffffff"), font_weight="bold", font_size="md"),
                                width="100%",
                                align_items="start"
                            ),
                            
                            # Descripción
                            rx.vstack(
                                rx.text("Descripción Detallada:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                rx.box(
                                    rx.text(State.solicitud_consultada.get("descripcion", ""), color=rx.color_mode_cond(light="#1e293b", dark="#cbd5e1"), font_size="sm", white_space="pre-wrap"),
                                    p="4",
                                    border=rx.color_mode_cond(light="1px solid #cbd5e0", dark="1px solid rgba(255,255,255,0.08)"),
                                    border_radius="2xl",
                                    bg=rx.color_mode_cond(light="#f8fafc", dark="rgba(15,23,42,0.6)"),
                                    width="100%"
                                ),
                                width="100%",
                                align_items="start"
                            ),
                            
                            # Respuesta
                            rx.cond(
                                State.solicitud_consultada.get("respuesta"),
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("message_square_plus", size=18, color="#10b981"),
                                        rx.text("Respuesta del Funcionario:", font_weight="bold", color="#10b981", font_size="xs", text_transform="uppercase"),
                                        spacing="2"
                                    ),
                                    rx.box(
                                        rx.text(State.solicitud_consultada.get("respuesta", ""), color=rx.color_mode_cond(light="#14532d", dark="#a7f3d0"), font_size="sm", white_space="pre-wrap"),
                                        p="4",
                                        border="1px solid #10b981",
                                        border_radius="2xl",
                                        bg=rx.color_mode_cond(light="#f0fff4", dark="rgba(16,185,129,0.08)"),
                                        width="100%"
                                    ),
                                    width="100%",
                                    align_items="start"
                                )
                            ),
                            rx.cond(
                                State.solicitud_consultada_tiene_adjunto_respuesta,
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("paperclip", size=16, color="#10b981"),
                                        rx.text("Adjunto de respuesta (funcionario):", font_weight="bold", color="#10b981", font_size="xs", text_transform="uppercase"),
                                        spacing="2",
                                    ),
                                    rx.cond(
                                        State.solicitud_consultada_respuesta_adjuntos.length() > 0,
                                        rx.vstack(
                                            rx.foreach(
                                                State.solicitud_consultada_respuesta_adjuntos,
                                                lambda doc: rx.vstack(
                                                    rx.cond(
                                                        doc.documento_preview_src != "",
                                                        rx.image(
                                                            src=doc.documento_preview_src,
                                                            alt="Adjunto de respuesta",
                                                            width="100%",
                                                            max_height="120px",
                                                            object_fit="contain",
                                                            border_radius="lg",
                                                        ),
                                                        rx.box(),
                                                    ),
                                                    ui_boton_descargar_adjunto(
                                                        doc.documento_href,
                                                        doc.documento_adjunto,
                                                        color_scheme="green",
                                                    ),
                                                    spacing="2",
                                                    width="100%",
                                                    align_items="start",
                                                    margin_bottom="2",
                                                )
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        rx.text("El archivo ya no está en el servidor", font_size="xs", color="#ef4444"),
                                    ),
                                    width="100%",
                                    align_items="start",
                                    spacing="2",
                                ),
                            ),
                            # Adjuntos Ciudadano
                            rx.cond(
                                State.solicitud_consultada.get("documento_adjuntos"),
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("paperclip", size=16, color="#3b82f6"),
                                        rx.text("Documentos Adjuntos por Ciudadano:", font_weight="bold", color=rx.color_mode_cond(light="#475569", dark="#94a3b8"), font_size="xs", text_transform="uppercase"),
                                        spacing="2"
                                    ),
                                    rx.vstack(
                                        rx.foreach(
                                            State.solicitud_consultada_adjuntos,
                                            lambda doc: ui_tarjeta_adjunto(doc),
                                        ),
                                        align_items="start",
                                        spacing="2",
                                        width="100%"
                                    ),
                                    width="100%",
                                    align_items="start"
                                )
                            ),
                            rx.cond(
                                State.historial_solicitud.length() > 0,
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("history", size=16, color="#8b5cf6"),
                                        rx.text("Bitácora", font_weight="bold", font_size="xs", color="#8b5cf6", text_transform="uppercase"),
                                        spacing="2",
                                    ),
                                    rx.foreach(
                                        State.historial_solicitud,
                                        lambda h: rx.box(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.badge(h["estado_anterior"], size="1", variant="soft"),
                                                    rx.icon("arrow-right", size=12),
                                                    rx.badge(h["estado_nuevo"], size="1", color_scheme="purple", variant="soft"),
                                                    rx.spacer(),
                                                    rx.text(h["fecha_cambio"], font_size="2xs", color="#64748b"),
                                                    width="100%",
                                                    align_items="center",
                                                ),
                                                rx.cond(
                                                    h["observaciones"] != "",
                                                    rx.text(h["observaciones"], font_size="xs", white_space="pre-wrap"),
                                                    rx.box(),
                                                ),
                                                rx.cond(
                                                    h["documento_adjunto"] != "",
                                                    ui_tarjeta_adjunto_historial(h),
                                                    rx.box(),
                                                ),
                                                spacing="2",
                                                width="100%",
                                            ),
                                            p="3",
                                            border="1px solid #e2e8f0",
                                            border_radius="lg",
                                            width="100%",
                                            margin_bottom="2",
                                        ),
                                    ),
                                    width="100%",
                                    align_items="start",
                                    spacing="2",
                                ),
                            ),
                            p="6",
                            max_height="450px",
                            overflow_y="auto",
                            width="100%",
                            spacing="4"
                        ),
                        
                        # Botón de Cerrar del Modal Detalles
                        rx.box(
                            rx.button(
                                "Cerrar Detalles",
                                on_click=State.cerrar_detalle_solicitud,
                                bg="linear-gradient(135deg, #475569 0%, #334155 100%)",
                                color="#ffffff",
                                size="3",
                                width="100%",
                                box_shadow="0 4px 14px 0 rgba(100,116,139,0.3)",
                                _hover={"transform": "translateY(-2px)", "box_shadow": "0 6px 20px rgba(100,116,139,0.4)"},
                                transition="all 0.2s"
                            ),
                            p="5",
                            border_top=rx.color_mode_cond(light="1px solid rgba(0,0,0,0.05)", dark="1px solid rgba(255,255,255,0.05)"),
                            bg=rx.color_mode_cond(light="#f8fafc", dark="rgba(11, 17, 32, 0.4)"),
                            border_bottom_left_radius="3xl",
                            border_bottom_right_radius="3xl",
                            width="100%"
                        ),
                        spacing="0",
                    ),
                    p="0",
                    border=rx.color_mode_cond(light="1px solid #cbd5e1", dark="1px solid rgba(255,255,255,0.08)"),
                    border_radius="3xl",
                    bg=rx.color_mode_cond(light="#ffffff", dark="#111827"),
                    width="95%",
                    max_width="720px",
                    position="fixed",
                    top="50%",
                    left="50%",
                    transform="translate(-50%, -50%)",
                    z_index="1100",
                    box_shadow="0 30px 60px -15px rgba(0,0,0,0.5)"
                )
            )
        ),
        width="100%",
        min_height="100vh",
        bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a")
    )
    # Restringir acceso: solo funcionarios y administradores
    return rx.cond(
        State.es_autenticada & ((State.rol_usuario == "funcionario") | (State.rol_usuario == "administrador")),
        content,
        rx.box(
            navbar(),
            rx.center(
                access_denied_widget("Solo funcionarios autenticados pueden ver esta página."),
                size="3"
            )
        )
    )

