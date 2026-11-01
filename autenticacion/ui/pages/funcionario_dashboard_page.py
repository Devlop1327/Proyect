import reflex as rx
from reflex.components import recharts as rc
from ...state import State
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar, access_denied_widget
from ..components.footer import footer
from ..components.attachments import (
    ui_boton_descargar_adjunto,
    ui_enlace_archivo,
    ui_tarjeta_adjunto,
    ui_fila_adjunto_respuesta_modal,
    ui_tarjeta_adjunto_historial,
)
from ..components.kpi import (
    kpi_metric_card,
    dashboard_chart_card,
    action_icon_button,
    modal_vencimiento_solicitudes,
)

def funcionario_dashboard() -> rx.Component:
    text_color = rx.color_mode_cond(light="#0f172a", dark="#f8fafc")
    subtext_color = rx.color_mode_cond(light="#64748b", dark="#94a3b8")
    card_bg = rx.color_mode_cond(light="rgba(255, 255, 255, 0.85)", dark="rgba(15, 23, 42, 0.7)")
    card_border = rx.color_mode_cond(light="1px solid rgba(255, 255, 255, 0.5)", dark="1px solid rgba(51, 65, 85, 0.5)")

    return rx.cond(
        rx.State.is_hydrated,
        rx.cond(
            State.es_autenticada & (State.rol_usuario == "funcionario"),
            rx.box(
                navbar(),
                rx.center(
                    # Fondo Atmosférico
                    rx.box(position="absolute", top="-10%", left="-5%", width="600px", height="600px", bg="rgba(59, 130, 246, 0.15)", border_radius="full", filter="blur(150px)", z_index="0"),
                    rx.box(position="absolute", bottom="-10%", right="-5%", width="700px", height="700px", bg="rgba(139, 92, 246, 0.1)", border_radius="full", filter="blur(150px)", z_index="0"),
                    
                    # Contenedor Principal (GRID BENTO BOX)
                    rx.grid(
                        # ==========================================
                        # COLUMNA IZQUIERDA (1/3) - Perfil y Admin
                        # ==========================================
                        rx.vstack(
                            # Perfil de Funcionario
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.box(rx.icon("shield-check", size=32, color="white"), p="3", bg="linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)", border_radius="2xl", box_shadow="0 10px 15px -3px rgba(59, 130, 246, 0.4)"),
                                        rx.vstack(
                                            rx.heading("Consola Operativa", size="6", color=text_color, font_weight="bold"),
                                            rx.badge("Admin / Funcionario", color_scheme="blue", variant="soft", radius="full"),
                                            spacing="1", align_items="start"
                                        ),
                                        spacing="4", align_items="center"
                                    ),
                                    rx.divider(margin_y="4", opacity="0.3"),
                                    rx.text("Supervisa, gestiona y da respuesta a las solicitudes ciudadanas desde este panel centralizado.", color=subtext_color, font_size="sm"),
                                    align_items="stretch"
                                ),
                                p="6", width="100%", bg=card_bg, backdrop_filter="blur(24px)", border=card_border, border_radius="3xl", box_shadow="0 20px 40px -15px rgba(0,0,0,0.1)"
                            ),
                            
                            # Modulo de Usuarios Registrados
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("users", size=20, color="#3b82f6"),
                                        rx.heading("Directorio", size="4", color=text_color, font_weight="bold"),
                                        rx.spacer(),
                                        rx.badge(State.usuarios_registrados_count, color_scheme="blue", radius="full"),
                                        width="100%", align_items="center"
                                    ),
                                    rx.divider(margin_y="2", opacity="0.3"),
                                    rx.box(
                                        rx.grid(
                                            rx.foreach(
                                                State.usuarios_registrados[:6],
                                                lambda usuario: rx.box(
                                                    rx.hstack(
                                                        rx.avatar(
                                                            fallback=rx.cond(usuario["rol"] == "funcionario", "FN", "CD"),
                                                            size="2",
                                                            radius="full",
                                                            color_scheme=rx.cond(usuario["rol"] == "funcionario", "blue", "gray"),
                                                        ),
                                                        rx.vstack(
                                                            rx.text(
                                                                usuario["email"],
                                                                font_size="xs",
                                                                font_weight="bold",
                                                                color=text_color,
                                                                no_wrap=True,
                                                                overflow="hidden",
                                                                text_overflow="ellipsis",
                                                                max_width="190px",
                                                            ),
                                                            rx.badge(
                                                                rx.cond(usuario["rol"] == "funcionario", rx.icon("shield", size=12), rx.icon("user", size=12)),
                                                                usuario["rol"],
                                                                color_scheme=rx.cond(usuario["rol"] == "funcionario", "blue", "gray"),
                                                                variant="soft",
                                                                radius="full",
                                                                size="1",
                                                            ),
                                                            spacing="1",
                                                            align_items="start",
                                                        ),
                                                        rx.spacer(),
                                                        rx.hstack(
                                                            action_icon_button("mail", "Contactar", color_scheme="blue", is_disabled=True),
                                                            rx.link(
                                                                action_icon_button("arrow-right", "Detalles", color_scheme="gray"),
                                                                href="/usuarios",
                                                            ),
                                                            spacing="2",
                                                            align_items="center",
                                                        ),
                                                        width="100%",
                                                        align_items="center",
                                                    ),
                                                    p="3",
                                                    border_radius="xl",
                                                    bg=rx.color_mode_cond(light="rgba(248, 250, 252, 0.65)", dark="rgba(30, 41, 59, 0.25)"),
                                                    border=rx.color_mode_cond(light="1px solid rgba(226,232,240,0.9)", dark="1px solid rgba(51,65,85,0.6)"),
                                                    box_shadow=rx.color_mode_cond(light="0 8px 16px -12px rgba(15,23,42,0.25)", dark="0 10px 20px -16px rgba(0,0,0,0.65)"),
                                                    _hover={"transform": "translateY(-1px)"},
                                                    transition="all 0.18s",
                                                ),
                                            ),
                                            columns=rx.breakpoints(initial="1", sm="2"),
                                            spacing="3",
                                            width="100%",
                                        ),
                                        width="100%",
                                        max_height="320px",
                                        overflow_y="auto",
                                        pr="1",
                                    ),
                                    rx.cond(
                                        State.usuarios_registrados_count > 5,
                                        rx.link(rx.button("Ver directorio completo", variant="soft", size="2", width="100%", color_scheme="blue", mt="2"), href="/usuarios")
                                    ),
                                    align_items="stretch"
                                ),
                                p="5", width="100%", bg=card_bg, backdrop_filter="blur(24px)", border=card_border, border_radius="3xl", box_shadow="0 20px 40px -15px rgba(0,0,0,0.1)"
                            ),
                            
                            spacing="6", width="100%"
                        ),

                        # ==========================================
                        # COLUMNA DERECHA (2/3) - Gestion Operativa
                        # ==========================================
                        rx.vstack(
                            # Grid de Metricas (4 Tarjetas KPI modernas)
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
                                    State.numero_solicitudes_actualizadas,
                                    "activity",
                                    "#0ea5e9",
                                    rx.color_mode_cond(light="#f0fdfe", dark="rgba(14, 165, 233, 0.16)"),
                                ),
                                kpi_metric_card(
                                    "Cerradas",
                                    State.numero_solicitudes_cerradas,
                                    "circle-check",
                                    "#10b981",
                                    rx.color_mode_cond(light="#ecfdf5", dark="rgba(16, 185, 129, 0.14)"),
                                ),
                                columns={"base": "1", "sm": "2", "lg": "4"},
                                gap="4",
                                width="100%",
                                style={"gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))"},
                            ),

                            # Gráfica: estado de vencimiento (solo activas, misma lógica que Excel)
                            dashboard_chart_card(
                                "Estado de Vencimiento (Activas)",
                                rx.box(
                                    rc.bar_chart(
                                        rc.x_axis(data_key="name"),
                                        rc.y_axis(domain=[0, State.max_semaforo_activas_cantidad]),
                                        rc.tooltip(),
                                        rc.bar(
                                            rc.cell(fill="#10b981"),
                                            rc.cell(fill="#f59e0b"),
                                            rc.cell(fill="#ef4444"),
                                            data_key="cantidad",
                                            radius=[6, 6, 0, 0],
                                        ),
                                        data=State.semaforo_activas_chart_data,
                                        width="100%",
                                        height=260,
                                    ),
                                    position="relative",
                                    width="100%",
                                ),
                                card_bg=card_bg,
                                card_border=card_border,
                                extra_content=rx.vstack(
                                    rx.hstack(
                                        rx.badge(
                                            rx.hstack(
                                                rx.icon("layers", size=12),
                                                State.semaforo_activas_total,
                                                spacing="1",
                                                align_items="center",
                                            ),
                                            color_scheme="blue",
                                            variant="soft",
                                            radius="full",
                                        ),
                                        
                                        spacing="2",
                                        align_items="center",
                                        flex_wrap="wrap",
                                    ),
                                    rx.hstack(
                                        rx.button(
                                            "Verde (>5 días)",
                                            size="1",
                                            variant="soft",
                                            color_scheme="green",
                                            radius="full",
                                            on_click=lambda: State.abrir_semaforo_activas_modal("Verde"),
                                        ),
                                        rx.button(
                                            "Amarillo (1-5 días)",
                                            size="1",
                                            variant="soft",
                                            color_scheme="orange",
                                            radius="full",
                                            on_click=lambda: State.abrir_semaforo_activas_modal("Amarillo"),
                                        ),
                                        rx.button(
                                            "Rojo (Vencidas)",
                                            size="1",
                                            variant="soft",
                                            color_scheme="red",
                                            radius="full",
                                            on_click=lambda: State.abrir_semaforo_activas_modal("Rojo"),
                                        ),
                                        spacing="2",
                                        flex_wrap="wrap",
                                        justify_content="center",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                            ),
                            
                            # Command Bar (Buscador y Filtros Cristalinos)
                            rx.box(
                                rx.hstack(
                                    rx.hstack(
                                        rx.icon("search", size=20, color=subtext_color),
                                        rx.input(placeholder="Buscar por radicado, asunto...", value=State.query_solicitud, on_change=State.set_query_solicitud, variant="surface", outline="none", border="none", bg="transparent", _focus={"box_shadow": "none"}, width="250px"),
                                        align_items="center", bg=rx.color_mode_cond(light="rgba(255,255,255,0.5)", dark="rgba(15,23,42,0.5)"), p="2", border_radius="xl", flex="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Estado", font_size="xs", color=subtext_color, font_weight="medium"),
                                        rx.select(
                                            ["Todas", "Radicada", "Asignada a Area", "En Gestion de Area", "Solucionada", "Reabierta", "Cerrada"],
                                            value=State.filter_estado_solicitud,
                                            on_change=State.set_filter_estado_solicitud,
                                            size="3",
                                            radius="full",
                                            variant="soft",
                                            width="170px",
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    rx.vstack(
                                        rx.text("Tipo Solicitud", font_size="xs", color=subtext_color, font_weight="medium"),
                                        rx.select(
                                            ["Todas", "Petición", "Queja", "Reclamo", "Sugerencia"],
                                            value=State.filter_tipo_solicitud,
                                            on_change=State.set_filter_tipo_solicitud,
                                            size="3",
                                            radius="full",
                                            variant="soft",
                                            width="170px",
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    rx.vstack(
                                        rx.text("Días Restantes", font_size="xs", color=subtext_color, font_weight="medium"),
                                        rx.select(
                                            ["Todos", "Vencidas", "0-3", "4-10", "11+"],
                                            value=State.filter_dias_restantes,
                                            on_change=State.set_filter_dias_restantes,
                                            size="3",
                                            radius="full",
                                            variant="soft",
                                            width="170px",
                                            placeholder="Días restantes",
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    rx.button(rx.icon("filter", size=18), "Buscar", on_click=State.buscar_solicitudes, size="3", color_scheme="blue", radius="full", box_shadow="0 4px 10px rgba(59, 130, 246, 0.3)"),
                                    spacing="4", width="100%", align_items="center", flex_wrap="wrap"
                                ),
                                p="4", width="100%", bg=card_bg, backdrop_filter="blur(24px)", border=card_border, border_radius="2xl", margin_top="4"
                            ),
                            
                            # Solicitudes activas (las cerradas van a pestaña aparte)
                            rx.vstack(
                                rx.box(
                                    rx.hstack(
                                        rx.heading("Solicitudes activas", size="5", color=text_color, font_weight="bold"),
                                        rx.spacer(),
                                        rx.badge(State.solicitudes_abiertas.length(), color_scheme="blue", variant="soft", radius="full"),
                                        rx.link(
                                            rx.button(
                                                "Ver cerradas",
                                                size="2",
                                                variant="soft",
                                                color_scheme="green",
                                                radius="full",
                                            ),
                                            href="/dashboard-funcionario-cerradas",
                                        ),
                                        width="100%",
                                    ),
                                    width="100%",
                                    mt="2",
                                ),
                                rx.cond(
                                    State.solicitudes_abiertas,
                                    rx.grid(
                                        rx.foreach(
                                            State.solicitudes_abiertas,
                                            lambda solicitud: rx.box(
                                                rx.vstack(
                                                    # Header: Radicado + Badge de estado
                                                    rx.box(
                                                        rx.hstack(
                                                            rx.hstack(
                                                                rx.icon("hash", size=12, color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9")),
                                                                rx.text(
                                                                    solicitud['radicado'],
                                                                    font_size="xs",
                                                                    font_weight="700",
                                                                    color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9"),
                                                                    letter_spacing="0.02em",
                                                                ),
                                                                spacing="1", align_items="center",
                                                            ),
                                                            rx.spacer(),
                                                            rx.badge(
                                                                rx.cond(solicitud['estado'] == 'Radicada', rx.icon("file-plus-2", size=11),
                                                                    rx.cond(solicitud['estado'] == 'Asignada a Area', rx.icon("building-2", size=11),
                                                                        rx.cond(solicitud['estado'] == 'En Gestion de Area', rx.icon("activity", size=11),
                                                                            rx.cond(solicitud['estado'] == 'Reabierta', rx.icon("refresh-cw", size=11),
                                                                                rx.icon("circle-check", size=11))))),
                                                                solicitud['estado'],
                                                                color_scheme=rx.cond(solicitud['estado'] == 'Radicada', "orange",
                                                                    rx.cond(solicitud['estado'] == 'Asignada a Area', "purple",
                                                                        rx.cond(solicitud['estado'] == 'En Gestion de Area', "blue",
                                                                            rx.cond(solicitud['estado'] == 'Reabierta', "red", "green")))),
                                                                variant="soft", size="1", radius="full",
                                                            ),
                                                            width="100%", align_items="center",
                                                        ),
                                                        padding="12px 16px",
                                                        border_bottom=rx.color_mode_cond(light="1px solid #f1f5f9", dark="1px solid #1e3a5f"),
                                                        width="100%",
                                                    ),
                                                    # Cuerpo: Asunto + Descripción
                                                    rx.box(
                                                        rx.vstack(
                                                            rx.text(
                                                                solicitud['asunto'],
                                                                font_size="sm",
                                                                font_weight="700",
                                                                color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff"),
                                                                line_height="1.35",
                                                                style={"display": "-webkit-box", "WebkitLineClamp": "2", "WebkitBoxOrient": "vertical", "overflow": "hidden"},
                                                            ),
                                                            rx.text(
                                                                solicitud['descripcion'],
                                                                font_size="xs",
                                                                color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9"),
                                                                line_height="1.5",
                                                                style={"display": "-webkit-box", "WebkitLineClamp": "3", "WebkitBoxOrient": "vertical", "overflow": "hidden"},
                                                                min_height="54px",
                                                            ),
                                                            spacing="2", align_items="start", width="100%",
                                                        ),
                                                        padding="12px 16px",
                                                        width="100%",
                                                    ),
                                                    # Footer: Etiquetas + Botones
                                                    rx.box(
                                                        rx.vstack(
                                                            rx.hstack(
                                                                rx.badge(
                                                                    rx.icon("layers", size=11),
                                                                    solicitud['tipo_solicitud'],
                                                                    variant="soft", color_scheme="purple", radius="full", size="1",
                                                                ),
                                                                rx.badge(
                                                                    rx.icon("users", size=11),
                                                                    solicitud.get('area_responsable', 'Sin asignar'),
                                                                    variant="soft", color_scheme="cyan", radius="full", size="1",
                                                                ),
                                                                rx.cond(
                                                                    solicitud['estado'] != 'Cerrada',
                                                                    rx.badge(
                                                                        rx.icon("clock", size=11),
                                                                        rx.cond(solicitud['semaforo_expired'], "Vencida", f"{solicitud['semaforo_remaining']} días"),
                                                                        color_scheme=rx.cond(solicitud['semaforo_fill'] == "green", "green",
                                                                            rx.cond(solicitud['semaforo_fill'] == "orange", "orange", "red")),
                                                                        variant="soft", radius="full", size="1",
                                                                    ),
                                                                    rx.box(),
                                                                ),
                                                                spacing="2", width="100%", flex_wrap="wrap",
                                                            ),
                                                            rx.hstack(
                                                                rx.button(
                                                                    rx.icon("history", size=14), "Historial",
                                                                    on_click=lambda _event, id=solicitud['id']: State.abrir_historial(id),
                                                                    size="1", variant="soft", color_scheme="gray", radius="full",
                                                                    _hover={"transform": "translateY(-1px)"}, transition="all 0.2s ease",
                                                                ),
                                                                rx.button(
                                                                    rx.icon("refresh-cw", size=14), "Estado",
                                                                    on_click=lambda _event, id=solicitud['id'], estado=solicitud['estado']: State.abrir_editor_estado(id, estado),
                                                                    size="1", color_scheme="blue", variant="solid", radius="full",
                                                                    _hover={"transform": "translateY(-1px)"}, transition="all 0.2s ease",
                                                                ),
                                                                rx.button(
                                                                    rx.icon("network", size=14), "Área",
                                                                    on_click=lambda _event, id=solicitud['id'], area=solicitud.get('area_responsable', ''): State.abrir_asignar_area(id, area),
                                                                    size="1", color_scheme="green", variant="soft", radius="full",
                                                                    _hover={"transform": "translateY(-1px)"}, transition="all 0.2s ease",
                                                                ),
                                                                spacing="2", width="100%",
                                                            ),
                                                            spacing="3", width="100%",
                                                        ),
                                                        padding="12px 16px",
                                                        border_top=rx.color_mode_cond(light="1px solid #f1f5f9", dark="1px solid #1e3a5f"),
                                                        bg=rx.color_mode_cond(light="#f8fafc", dark="#0b1120"),
                                                        border_bottom_left_radius="14px",
                                                        border_bottom_right_radius="14px",
                                                        width="100%",
                                                    ),
                                                    spacing="0", align_items="start", width="100%",
                                                ),
                                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                                border_top=rx.cond(solicitud['estado'] == 'Radicada', "3px solid #f59e0b",
                                                    rx.cond(solicitud['estado'] == 'Asignada a Area', "3px solid #8b5cf6",
                                                        rx.cond(solicitud['estado'] == 'En Gestion de Area', "3px solid #2563eb",
                                                            rx.cond(solicitud['estado'] == 'Reabierta', "3px solid #ef4444",
                                                                "3px solid #10b981")))),
                                                border_radius="14px",
                                                width="100%",
                                                overflow="hidden",
                                                box_shadow=rx.color_mode_cond(light="0 1px 3px rgba(0,0,0,0.06)", dark="0 2px 12px rgba(0,0,0,0.3)"),
                                                _hover={"transform": "translateY(-4px)", "box_shadow": rx.color_mode_cond(light="0 8px 24px rgba(37,99,235,0.12)", dark="0 8px 24px rgba(0,0,0,0.5)")},
                                                transition="all 0.22s ease",
                                            )
                                        ),
                                        display="grid",
                                        grid_template_columns=rx.breakpoints(initial="repeat(1, minmax(0, 1fr))", md="repeat(2, minmax(0, 1fr))", lg="repeat(3, minmax(0, 1fr))"),
                                        gap="38px",
                                        padding="38px",
                                        width="100%",
                                    ),
                                    rx.center(
                                        rx.vstack(
                                            rx.icon("inbox", size=64, color=subtext_color, opacity="0.3"),
                                            rx.heading("Sin solicitudes activas", size="5", color=text_color),
                                            rx.text("No hay radicados activos en este filtro.", color=subtext_color),
                                            align_items="center", spacing="4"
                                        ),
                                        min_height="220px", width="100%"
                                    )
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            
                            spacing="4", width="100%"
                        ),
                        
                        template_columns={"base": "1fr", "lg": "340px 1fr"}, gap="6", width="100%", max_width="100%", padding_y="8", padding_x={"base": "2", "md": "4"}, z_index="1"
                    ),
                    
                    # ==========================================
                    # MODALES DE ACCION (Pop-ups Glassmorphism)
                    # ==========================================
                    
                    # Modal: Historial
                    rx.cond(
                        State.historial_modal_abierto,
                        rx.dialog.root(
                            rx.dialog.content(
                                rx.dialog.title("Historial de Estados", display="none"),
                                rx.dialog.description("Historial de cambios de estado", display="none"),
                                rx.vstack(
                                    rx.hstack(rx.icon("history", size=24, color="#3b82f6"), rx.heading("Historial de Estados", size="5"), rx.spacer(), rx.dialog.close(rx.button(rx.icon("x", size=20), on_click=State.cerrar_historial, variant="ghost", color_scheme="gray")), width="100%", align_items="center"),
                                    rx.divider(margin_y="2"),
                                    rx.cond(
                                        State.historial_estados,
                                        rx.vstack(
                                            rx.foreach(
                                                State.historial_estados,
                                                lambda evento: rx.box(
                                                    rx.hstack(
                                                        rx.box(rx.icon("git-commit-horizontal", size=20, color="#10b981"), p="2", bg="rgba(16, 185, 129, 0.1)", border_radius="full"),
                                                        rx.vstack(
                                                            rx.hstack(rx.text("Cambió a:", font_size="sm", color=subtext_color), rx.badge(evento['nuevo'], color_scheme="blue", radius="full"), rx.spacer(), rx.text(evento['fecha'], font_size="xs", color=subtext_color), width="100%", align_items="center"),
                                                            rx.text(rx.cond(evento['obs'] != "", f'"{evento["obs"]}"', "Sin comentarios."), font_size="sm", font_style="italic", color=text_color),
                                                            rx.text(f"Estado anterior: {evento['anterior']}", font_size="xs", color=subtext_color),
                                                            rx.cond(
                                                                evento["documento_adjunto"] != "",
                                                                ui_tarjeta_adjunto_historial(evento),
                                                                rx.box(),
                                                            ),
                                                            spacing="1", width="100%", align_items="start"
                                                        ),
                                                        spacing="4", align_items="start", width="100%"
                                                    ),
                                                    p="4", bg=rx.color_mode_cond(light="#f8fafc", dark="#1e293b"), border_radius="xl", width="100%", margin_bottom="3"
                                                )
                                            ),
                                            width="100%", max_height="400px", overflow_y="auto"
                                        ),
                                        rx.center(rx.text("Aún no hay historial de cambios para esta solicitud.", color=subtext_color), p="6")
                                    ),
                                    spacing="4", width="100%"
                                ),
                                style={"maxWidth": "600px", "borderRadius": "24px", "padding": "24px", "backgroundColor": card_bg, "backdropFilter": "blur(40px)", "border": card_border}
                            ),
                            open=True, on_open_change=State.cerrar_historial
                        )
                    ),
                    
                    # Modal: Editor de Estado (estilo KPI)
                    rx.cond(
                        State.editar_estado_id,
                        rx.fragment(
                            rx.box(
                                position="fixed",
                                top="0",
                                left="0",
                                width="100vw",
                                height="100vh",
                                bg=rx.color_mode_cond(light="rgba(15, 23, 42, 0.45)", dark="rgba(0, 0, 0, 0.65)"),
                                z_index="999",
                                on_click=State.cerrar_editor_estado,
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.box(
                                        rx.hstack(
                                            rx.box(
                                                rx.icon("sliders-horizontal", size=18, color="#2563eb"),
                                                bg=rx.color_mode_cond(light="#eff6ff", dark="rgba(37, 99, 235, 0.18)"),
                                                border_radius="10px",
                                                width="42px",
                                                height="42px",
                                                display="flex",
                                                align_items="center",
                                                justify_content="center",
                                                flex_shrink="0",
                                            ),
                                            rx.vstack(
                                                rx.text(
                                                    "Actualizar estado",
                                                    font_size={"base": "xl", "md": "2rem"},
                                                    font_weight="800",
                                                    color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff"),
                                                    line_height="1",
                                                    letter_spacing="-0.03em",
                                                ),
                                                rx.text(
                                                    "Gestión y seguimiento de la solicitud",
                                                    font_size="12px",
                                                    color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9"),
                                                    font_weight="500",
                                                ),
                                                spacing="1",
                                                align_items="start",
                                            ),
                                            rx.spacer(),
                                            rx.button(
                                                rx.icon("x", size=18),
                                                type="button",
                                                on_click=State.cerrar_editor_estado,
                                                variant="ghost",
                                                color_scheme="gray",
                                                size="2",
                                            ),
                                            spacing="3",
                                            align_items="center",
                                            width="100%",
                                        ),
                                        padding="18px 20px",
                                        border_bottom=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                        width="100%",
                                    ),
                                    rx.box(
                                        rx.vstack(
                                            rx.box(
                                                rx.vstack(
                                                    rx.text(
                                                        "Nuevo estado",
                                                        font_weight="600",
                                                        font_size="sm",
                                                        color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff"),
                                                    ),
                                                    rx.select(
                                                        ["Radicada", "Asignada a Area", "En Gestion de Area", "Solucionada", "Reabierta", "Cerrada"],
                                                        value=State.nuevo_estado,
                                                        on_change=State.set_nuevo_estado,
                                                        required=True,
                                                        width="100%",
                                                        size="3",
                                                    ),
                                                    rx.cond(
                                                        State.nuevo_estado == "Asignada a Area",
                                                        rx.vstack(
                                                            rx.hstack(
                                                                rx.text("Área responsable", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                                rx.badge("Requerido", color_scheme="orange", size="1"),
                                                                spacing="2",
                                                                align_items="center",
                                                            ),
                                                            rx.select(
                                                                State.AREAS_DISPONIBLES,
                                                                placeholder="Selecciona el área...",
                                                                value=State.area_para_asignar,
                                                                on_change=State.set_area_para_asignar,
                                                                width="100%",
                                                                size="3",
                                                                color_scheme="orange",
                                                            ),
                                                            spacing="2",
                                                            width="100%",
                                                            align_items="start",
                                                        ),
                                                    ),
                                                    spacing="3",
                                                    width="100%",
                                                    align_items="stretch",
                                                ),
                                                padding="16px 18px",
                                                border_radius="14px",
                                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                                border_top="3px solid #2563eb",
                                                width="100%",
                                            ),
                                            rx.box(
                                                rx.vstack(
                                                    rx.hstack(
                                                        rx.text("Justificación", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                        rx.badge("Obligatorio", color_scheme="red", size="1"),
                                                        spacing="2",
                                                    ),
                                                    rx.text_area(
                                                        placeholder="Describe el motivo del cambio de estado...",
                                                        value=State.respuesta_solicitud,
                                                        on_change=State.set_respuesta_solicitud,
                                                        rows="3",
                                                        required=True,
                                                        width="100%",
                                                        size="3",
                                                        min_height="88px",
                                                    ),
                                                    spacing="2",
                                                    width="100%",
                                                    align_items="start",
                                                ),
                                                padding="16px 18px",
                                                border_radius="14px",
                                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                                border_top="3px solid #10b981",
                                                width="100%",
                                            ),
                                            rx.box(
                                                rx.vstack(
                                                    rx.text(
                                                        "Documento adjunto (opcional)",
                                                        font_weight="600",
                                                        font_size="sm",
                                                        color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff"),
                                                    ),
                                                    rx.box(
                                                        rx.vstack(
                                                            rx.upload(
                                                                rx.hstack(
                                                                    rx.icon("paperclip", size=16, color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9")),
                                                                    rx.text("PDF, JPG o PNG �?? hasta 3 archivos, máx. 10 MB c/u", font_size="sm", color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9")),
                                                                    spacing="2",
                                                                    align_items="center",
                                                                    justify="center",
                                                                ),
                                                                id="upload_respuesta",
                                                                multiple=True,
                                                                accept={
                                                                    "application/pdf": [".pdf"],
                                                                    "image/png": [".png"],
                                                                    "image/jpeg": [".jpg", ".jpeg"],
                                                                },
                                                                border="none",
                                                                width="100%",
                                                                padding="3",
                                                                on_drop=State.set_respuesta_documento,
                                                            ),
                                                            rx.cond(
                                                                rx.selected_files("upload_respuesta").length() > 0,
                                                                rx.vstack(
                                                                    rx.foreach(
                                                                        rx.selected_files("upload_respuesta"),
                                                                        lambda fname: rx.text(fname, font_size="xs", color=subtext_color),
                                                                    ),
                                                                ),
                                                            ),
                                                            rx.cond(
                                                                State.respuesta_documento_error != "",
                                                                rx.box(
                                                                    rx.hstack(
                                                                        rx.icon("ban", size=15, color="#ef4444"),
                                                                        rx.text(
                                                                            State.respuesta_documento_error,
                                                                            font_size="sm",
                                                                            color="#ef4444",
                                                                            font_weight="medium",
                                                                        ),
                                                                        spacing="2",
                                                                        align_items="center",
                                                                    ),
                                                                    bg=rx.color_mode_cond(light="#fef2f2", dark="#450a0a"),
                                                                    border=rx.color_mode_cond(light="1px solid #fecaca", dark="1px solid #991b1b"),
                                                                    border_radius="10px",
                                                                    p="3",
                                                                    width="100%",
                                                                ),
                                                            ),
                                                            rx.cond(
                                                                State.respuesta_documentos.length() > 0,
                                                                rx.vstack(
                                                                    rx.foreach(
                                                                        State.respuesta_documentos,
                                                                        ui_fila_adjunto_respuesta_modal,
                                                                    ),
                                                                    rx.button(
                                                                        rx.icon("trash-2", size=14),
                                                                        "Quitar todos los adjuntos",
                                                                        type="button",
                                                                        size="2",
                                                                        variant="outline",
                                                                        color_scheme="red",
                                                                        on_click=State.quitar_todos_respuesta_documentos,
                                                                        width="100%",
                                                                    ),
                                                                    spacing="2",
                                                                    width="100%",
                                                                ),
                                                            ),
                                                            spacing="2",
                                                            width="100%",
                                                        ),
                                                        padding="3",
                                                        border=rx.color_mode_cond(light="2px dashed #cbd5e1", dark="2px dashed #334155"),
                                                        border_radius="12px",
                                                        bg=rx.color_mode_cond(light="#f8fafc", dark="#0b1528"),
                                                        width="100%",
                                                    ),
                                                    spacing="2",
                                                    width="100%",
                                                    align_items="start",
                                                ),
                                                padding="16px 18px",
                                                border_radius="14px",
                                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                                border_top="3px solid #8b5cf6",
                                                width="100%",
                                            ),
                                            rx.cond(
                                                State.mensaje_actualizar_estado,
                                                rx.box(
                                                    rx.text(
                                                        State.mensaje_actualizar_estado,
                                                        color=rx.cond(
                                                            State.mensaje_actualizar_estado.contains("correctamente"),
                                                            "green.700",
                                                            "red.700",
                                                        ),
                                                        font_weight="semibold",
                                                        font_size="sm",
                                                    ),
                                                    bg=rx.cond(
                                                        State.mensaje_actualizar_estado.contains("correctamente"),
                                                        rx.color_mode_cond(light="#d1fae5", dark="#064e3b"),
                                                        rx.color_mode_cond(light="#fee2e2", dark="#450a0a"),
                                                    ),
                                                    border=rx.cond(
                                                        State.mensaje_actualizar_estado.contains("correctamente"),
                                                        rx.color_mode_cond(light="1px solid #a7f3d0", dark="1px solid #065f46"),
                                                        rx.color_mode_cond(light="1px solid #fecaca", dark="1px solid #991b1b"),
                                                    ),
                                                    border_radius="10px",
                                                    p="3",
                                                    width="100%",
                                                ),
                                            ),
                                            spacing="4",
                                            align_items="stretch",
                                            padding="18px 20px",
                                            max_height="65vh",
                                            overflow_y="auto",
                                            width="100%",
                                        ),
                                        width="100%",
                                    ),
                                    rx.box(
                                        rx.hstack(
                                            rx.button(
                                                "Cancelar",
                                                type="button",
                                                on_click=State.cerrar_editor_estado,
                                                variant="soft",
                                                color_scheme="gray",
                                                size="3",
                                                flex="1",
                                            ),
                                            rx.button(
                                                rx.icon("check", size=16),
                                                "Actualizar estado",
                                                type="button",
                                                on_click=State.actualizar_estado_solicitud(
                                                    rx.upload_files(upload_id="upload_respuesta"),
                                                ),
                                                color_scheme="blue",
                                                size="3",
                                                flex="2",
                                            ),
                                            spacing="3",
                                            width="100%",
                                        ),
                                        padding="16px 20px",
                                        border_top=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                        bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                        border_bottom_left_radius="14px",
                                        border_bottom_right_radius="14px",
                                        width="100%",
                                    ),
                                    spacing="0",
                                    width="100%",
                                ),
                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                border_top="3px solid #2563eb",
                                border_radius="14px",
                                width="100%",
                                max_width="560px",
                                max_height="92vh",
                                overflow="hidden",
                                position="fixed",
                                top="50%",
                                left="50%",
                                transform="translate(-50%, -50%)",
                                z_index="1000",
                                box_shadow=rx.color_mode_cond(
                                    light="0 8px 24px rgba(37, 99, 235, 0.16)",
                                    dark="0 2px 12px rgba(0,0,0,0.3)",
                                ),
                            ),
                        ),
                    ),
                    
                    # Modal: Asignar Área
                    rx.cond(
                        State.asignar_area_id,
                        rx.fragment(
                            rx.box(
                                position="fixed", top="0", left="0", width="100vw", height="100vh",
                                bg=rx.color_mode_cond(light="rgba(15, 23, 42, 0.45)", dark="rgba(0, 0, 0, 0.65)"),
                                z_index="999",
                                on_click=State.cerrar_asignar_area,
                            ),
                            rx.box(
                                rx.vstack(
                                    # Header
                                    rx.box(
                                        rx.hstack(
                                            rx.box(
                                                rx.icon("network", size=18, color="#10b981"),
                                                bg=rx.color_mode_cond(light="#ecfdf5", dark="rgba(16, 185, 129, 0.18)"),
                                                border_radius="10px",
                                                width="42px", height="42px",
                                                display="flex", align_items="center",
                                                justify_content="center", flex_shrink="0",
                                            ),
                                            rx.vstack(
                                                rx.text("Asignar Área", font_size={"base": "xl", "md": "2rem"}, font_weight="800", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff"), line_height="1", letter_spacing="-0.03em"),
                                                rx.text("Derivación y direccionamiento de la solicitud", font_size="12px", color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9"), font_weight="500"),
                                                spacing="1", align_items="start",
                                            ),
                                            rx.spacer(),
                                            rx.button(rx.icon("x", size=18), type="button", on_click=State.cerrar_asignar_area, variant="ghost", color_scheme="gray", size="2"),
                                            spacing="3", align_items="center", width="100%",
                                        ),
                                        padding="18px 20px",
                                        border_bottom=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                        width="100%",
                                    ),
                                    # Body
                                    rx.box(
                                        rx.vstack(
                                            # Sección área
                                            rx.box(
                                                rx.vstack(
                                                    rx.text("Área responsable", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                    rx.select(
                                                        ["Secretaría", "Contabilidad", "Bienestar", "Tesorería", "Atención al Ciudadano", "Otros"],
                                                        placeholder="Selecciona el área...",
                                                        value=State.asignar_area_seleccionada,
                                                        on_change=State.set_asignar_area_seleccionada,
                                                        width="100%", size="3",
                                                    ),
                                                    rx.cond(
                                                        State.asignar_area_seleccionada == "Otros",
                                                        rx.vstack(
                                                            rx.text("Especifique otra área", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                            rx.input(placeholder="Escribe el nombre del área...", value=State.asignar_area_nombre, on_change=State.set_asignar_area_nombre, width="100%", size="3"),
                                                            spacing="2", width="100%", align_items="start",
                                                        ),
                                                    ),
                                                    spacing="3", width="100%", align_items="stretch",
                                                ),
                                                padding="16px 18px", border_radius="14px",
                                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                                border_top="3px solid #10b981", width="100%",
                                            ),
                                            # Sección mensaje
                                            rx.box(
                                                rx.vstack(
                                                    rx.hstack(
                                                        rx.text("Mensaje para el ciudadano", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                        rx.badge("Obligatorio", color_scheme="red", size="1"),
                                                        spacing="2",
                                                    ),
                                                    rx.text_area(
                                                        placeholder="Escribe la comunicación que se notificará al ciudadano...",
                                                        value=State.asignar_area_mensaje,
                                                        on_change=State.set_asignar_area_mensaje,
                                                        rows="3", required=True, width="100%", size="3", min_height="88px",
                                                    ),
                                                    spacing="2", width="100%", align_items="start",
                                                ),
                                                padding="16px 18px", border_radius="14px",
                                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                                border_top="3px solid #06b6d4", width="100%",
                                            ),
                                            # Mensaje éxito/error
                                            rx.cond(
                                                State.mensaje_asignacion,
                                                rx.box(
                                                    rx.text(State.mensaje_asignacion, color=rx.cond(State.mensaje_asignacion.contains("correctamente"), "green.700", "red.700"), font_weight="semibold", font_size="sm"),
                                                    bg=rx.cond(State.mensaje_asignacion.contains("correctamente"), rx.color_mode_cond(light="#d1fae5", dark="#064e3b"), rx.color_mode_cond(light="#fee2e2", dark="#450a0a")),
                                                    border=rx.cond(State.mensaje_asignacion.contains("correctamente"), rx.color_mode_cond(light="1px solid #a7f3d0", dark="1px solid #065f46"), rx.color_mode_cond(light="1px solid #fecaca", dark="1px solid #991b1b")),
                                                    border_radius="10px", p="3", width="100%",
                                                ),
                                            ),
                                            spacing="4", align_items="stretch",
                                            padding="18px 20px", max_height="65vh", overflow_y="auto", width="100%",
                                        ),
                                        width="100%",
                                    ),
                                    # Footer
                                    rx.box(
                                        rx.hstack(
                                            rx.button("Cancelar", type="button", on_click=State.cerrar_asignar_area, variant="soft", color_scheme="gray", size="3", flex="1"),
                                            rx.button(rx.icon("check", size=16), "Asignar y Enviar", type="button", on_click=State.asignar_area_con_mensaje, color_scheme="green", size="3", flex="2"),
                                            spacing="3", width="100%",
                                        ),
                                        padding="16px 20px",
                                        border_top=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                        bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                        border_bottom_left_radius="14px", border_bottom_right_radius="14px", width="100%",
                                    ),
                                    spacing="0", width="100%",
                                ),
                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                border_top="3px solid #10b981",
                                border_radius="14px",
                                width="100%", max_width="560px", max_height="92vh", overflow="hidden",
                                position="fixed", top="50%", left="50%", transform="translate(-50%, -50%)",
                                z_index="1000",
                                box_shadow=rx.color_mode_cond(light="0 8px 24px rgba(16, 185, 129, 0.16)", dark="0 2px 12px rgba(0,0,0,0.3)"),
                            ),
                        )
                    ),

                    modal_vencimiento_solicitudes(),
                    
                    padding_x={"base": "4", "md": "8"}, width="100%", position="relative", min_height="90vh", align_items="start"
                ),
                bg=rx.color_mode_cond(light="#f1f5f9", dark="#020617"), width="100%", min_height="100vh", style={"margin": "0"}
            ),
            access_denied_widget("Esta página es solo para funcionarios autorizados.")
        ),
        rx.center(rx.spinner(size="3", color="#3b82f6"), height="100vh", bg=rx.color_mode_cond(light="#f1f5f9", dark="#0f172a"))
    )


def funcionario_cerradas_dashboard() -> rx.Component:
    text_color = rx.color_mode_cond(light="#0f172a", dark="#f8fafc")
    subtext_color = rx.color_mode_cond(light="#64748b", dark="#94a3b8")
    card_bg = rx.color_mode_cond(light="rgba(255, 255, 255, 0.85)", dark="rgba(15, 23, 42, 0.7)")
    card_border = rx.color_mode_cond(light="1px solid rgba(255, 255, 255, 0.5)", dark="1px solid rgba(51, 65, 85, 0.5)")

    return rx.cond(
        rx.State.is_hydrated,
        rx.cond(
            State.es_autenticada & (State.rol_usuario == "funcionario"),
            rx.box(
                navbar(),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.heading("Solicitudes cerradas", size="7", color=text_color, font_weight="bold"),
                                rx.text("Histórico de radicados finalizados.", color=subtext_color),
                                align_items="start",
                                spacing="1",
                            ),
                            rx.spacer(),
                            rx.link(
                                rx.button("Volver a activas", variant="soft", color_scheme="blue", radius="full"),
                                href="/dashboard-funcionario",
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        rx.divider(margin_y="4", opacity="0.3"),
                        rx.cond(
                            State.solicitudes_cerradas_lista,
                            rx.grid(
                                rx.foreach(
                                    State.solicitudes_cerradas_lista,
                                    lambda solicitud: rx.box(
                                        rx.vstack(
                                            # Header: Radicado + Badge de estado
                                            rx.box(
                                                rx.hstack(
                                                    rx.hstack(
                                                        rx.icon("hash", size=12, color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9")),
                                                        rx.text(
                                                            solicitud['radicado'],
                                                            font_size="xs",
                                                            font_weight="700",
                                                            color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9"),
                                                            letter_spacing="0.02em",
                                                        ),
                                                        spacing="1", align_items="center",
                                                    ),
                                                    rx.spacer(),
                                                    rx.badge(
                                                        rx.icon("circle-check", size=11),
                                                        solicitud['estado'],
                                                        color_scheme="green",
                                                        variant="soft", size="1", radius="full",
                                                    ),
                                                    width="100%", align_items="center",
                                                ),
                                                padding="12px 16px",
                                                border_bottom=rx.color_mode_cond(light="1px solid #f1f5f9", dark="1px solid #1e3a5f"),
                                                width="100%",
                                            ),
                                            # Cuerpo: Asunto + Descripción
                                            rx.box(
                                                rx.vstack(
                                                    rx.text(
                                                        solicitud['asunto'],
                                                        font_size="sm",
                                                        font_weight="700",
                                                        color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff"),
                                                        line_height="1.35",
                                                        style={"display": "-webkit-box", "WebkitLineClamp": "2", "WebkitBoxOrient": "vertical", "overflow": "hidden"},
                                                    ),
                                                    rx.text(
                                                        solicitud['descripcion'],
                                                        font_size="xs",
                                                        color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9"),
                                                        line_height="1.5",
                                                        style={"display": "-webkit-box", "WebkitLineClamp": "3", "WebkitBoxOrient": "vertical", "overflow": "hidden"},
                                                        min_height="54px",
                                                    ),
                                                    spacing="2", align_items="start", width="100%",
                                                ),
                                                padding="12px 16px",
                                                width="100%",
                                            ),
                                            # Footer: Etiquetas + Botones
                                            rx.box(
                                                rx.vstack(
                                                    rx.hstack(
                                                        rx.badge(
                                                            rx.icon("layers", size=11),
                                                            solicitud['tipo_solicitud'],
                                                            variant="soft", color_scheme="purple", radius="full", size="1",
                                                        ),
                                                        rx.badge(
                                                            rx.icon("users", size=11),
                                                            solicitud.get('area_responsable', 'Sin asignar'),
                                                            variant="soft", color_scheme="cyan", radius="full", size="1",
                                                        ),
                                                        spacing="2", width="100%", flex_wrap="wrap",
                                                    ),
                                                    rx.hstack(
                                                        rx.button(
                                                            rx.icon("history", size=14), "Historial",
                                                            on_click=lambda _event, id=solicitud['id']: State.abrir_historial(id),
                                                            size="1", variant="soft", color_scheme="gray", radius="full",
                                                            _hover={"transform": "translateY(-1px)"}, transition="all 0.2s ease",
                                                        ),
                                                        rx.button(
                                                            rx.icon("refresh-cw", size=14), "Estado",
                                                            on_click=lambda _event, id=solicitud['id'], estado=solicitud['estado']: State.abrir_editor_estado(id, estado),
                                                            size="1", color_scheme="blue", variant="solid", radius="full",
                                                            _hover={"transform": "translateY(-1px)"}, transition="all 0.2s ease",
                                                        ),
                                                        rx.button(
                                                            rx.icon("network", size=14), "Área",
                                                            on_click=lambda _event, id=solicitud['id'], area=solicitud.get('area_responsable', ''): State.abrir_asignar_area(id, area),
                                                            size="1", color_scheme="green", variant="soft", radius="full",
                                                            _hover={"transform": "translateY(-1px)"}, transition="all 0.2s ease",
                                                        ),
                                                        spacing="2", width="100%",
                                                    ),
                                                    spacing="3", width="100%",
                                                ),
                                                padding="12px 16px",
                                                border_top=rx.color_mode_cond(light="1px solid #f1f5f9", dark="1px solid #1e3a5f"),
                                                bg=rx.color_mode_cond(light="#f8fafc", dark="#0b1120"),
                                                border_bottom_left_radius="14px",
                                                border_bottom_right_radius="14px",
                                                width="100%",
                                            ),
                                            spacing="0", align_items="start", width="100%",
                                        ),
                                        bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                        border=card_border,
                                        border_top="3px solid #10b981",
                                        border_radius="14px",
                                        width="100%",
                                        overflow="hidden",
                                        box_shadow=rx.color_mode_cond(light="0 1px 3px rgba(0,0,0,0.06)", dark="0 2px 12px rgba(0,0,0,0.3)"),
                                        _hover={"transform": "translateY(-4px)", "box_shadow": rx.color_mode_cond(light="0 8px 24px rgba(37,99,235,0.12)", dark="0 8px 24px rgba(0,0,0,0.5)")},
                                        transition="all 0.22s ease",
                                    ),
                                ),
                                display="grid",
                                grid_template_columns=rx.breakpoints(initial="repeat(1, minmax(0, 1fr))", md="repeat(2, minmax(0, 1fr))", lg="repeat(3, minmax(0, 1fr))"),
                                gap="38px",
                                width="100%",
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon("inbox", size=64, color=subtext_color, opacity="0.3"),
                                    rx.heading("Sin solicitudes cerradas", size="5", color=text_color),
                                    rx.text("No hay cerradas para el filtro actual.", color=subtext_color),
                                    align_items="center",
                                    spacing="4",
                                ),
                                min_height="260px",
                                width="100%",
                            ),
                        ),
                        spacing="4",
                        width="100%",
                        max_width="100%",
                        p={"base": "3", "md": "5"},
                    ),
                    width="100%",
                    bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a"),
                    min_height="100vh",
                ),
                # Modal: Editor de Estado (Reabrir desde cerradas)
                rx.cond(
                    State.editar_estado_id,
                    rx.fragment(
                        rx.box(
                            position="fixed", top="0", left="0", width="100vw", height="100vh",
                            bg=rx.color_mode_cond(light="rgba(15, 23, 42, 0.45)", dark="rgba(0, 0, 0, 0.65)"),
                            z_index="999",
                            on_click=State.cerrar_editor_estado,
                        ),
                        rx.box(
                            rx.vstack(
                                # Header
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon("refresh-cw", size=18, color="#f59e0b"),
                                            bg=rx.color_mode_cond(light="#fffbeb", dark="rgba(245, 158, 11, 0.18)"),
                                            border_radius="10px",
                                            width="42px", height="42px",
                                            display="flex", align_items="center",
                                            justify_content="center", flex_shrink="0",
                                        ),
                                        rx.vstack(
                                            rx.text("Reabrir Solicitud", font_size={"base": "xl", "md": "2rem"}, font_weight="800", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff"), line_height="1", letter_spacing="-0.03em"),
                                            rx.text("Reactivación y cambio de estado del radicado", font_size="12px", color=rx.color_mode_cond(light="#64748b", dark="#7ea8c9"), font_weight="500"),
                                            spacing="1", align_items="start",
                                        ),
                                        rx.spacer(),
                                        rx.button(rx.icon("x", size=18), type="button", on_click=State.cerrar_editor_estado, variant="ghost", color_scheme="gray", size="2"),
                                        spacing="3", align_items="center", width="100%",
                                    ),
                                    padding="18px 20px",
                                    border_bottom=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                    width="100%",
                                ),
                                # Body
                                rx.box(
                                    rx.vstack(
                                        # Sección nuevo estado
                                        rx.box(
                                            rx.vstack(
                                                rx.text("Nuevo estado", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                rx.select(
                                                    ["Reabierta", "Radicada", "Asignada a Area", "En Gestion de Area"],
                                                    value=State.nuevo_estado,
                                                    on_change=State.set_nuevo_estado,
                                                    width="100%", size="3",
                                                ),
                                                rx.cond(
                                                    State.nuevo_estado == "Asignada a Area",
                                                    rx.vstack(
                                                        rx.hstack(
                                                            rx.text("Área responsable", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                            rx.badge("Requerido", color_scheme="orange", size="1"),
                                                            spacing="2", align_items="center",
                                                        ),
                                                        rx.select(
                                                            State.AREAS_DISPONIBLES,
                                                            placeholder="Selecciona el área...",
                                                            value=State.area_para_asignar,
                                                            on_change=State.set_area_para_asignar,
                                                            width="100%", size="3", color_scheme="orange",
                                                        ),
                                                        spacing="2", width="100%", align_items="start",
                                                    ),
                                                ),
                                                spacing="3", width="100%", align_items="stretch",
                                            ),
                                            padding="16px 18px", border_radius="14px",
                                            bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                            border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                            border_top="3px solid #f59e0b", width="100%",
                                        ),
                                        # Sección justificación
                                        rx.box(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.text("Justificación", font_weight="600", font_size="sm", color=rx.color_mode_cond(light="#0f172a", dark="#f0f6ff")),
                                                    rx.badge("Obligatorio", color_scheme="red", size="1"),
                                                    spacing="2",
                                                ),
                                                rx.text_area(
                                                    placeholder="Describe las razones por las cuales se reactiva y reabre este radicado...",
                                                    value=State.respuesta_solicitud,
                                                    on_change=State.set_respuesta_solicitud,
                                                    rows="3", required=True, width="100%", size="3", min_height="88px",
                                                ),
                                                spacing="2", width="100%", align_items="start",
                                            ),
                                            padding="16px 18px", border_radius="14px",
                                            bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                            border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                            border_top="3px solid #10b981", width="100%",
                                        ),
                                        # Mensaje éxito/error
                                        rx.cond(
                                            State.mensaje_actualizar_estado,
                                            rx.box(
                                                rx.text(State.mensaje_actualizar_estado, color=rx.cond(State.mensaje_actualizar_estado.contains("correctamente"), "green.700", "red.700"), font_weight="semibold", font_size="sm"),
                                                bg=rx.cond(State.mensaje_actualizar_estado.contains("correctamente"), rx.color_mode_cond(light="#d1fae5", dark="#064e3b"), rx.color_mode_cond(light="#fee2e2", dark="#450a0a")),
                                                border=rx.cond(State.mensaje_actualizar_estado.contains("correctamente"), rx.color_mode_cond(light="1px solid #a7f3d0", dark="1px solid #065f46"), rx.color_mode_cond(light="1px solid #fecaca", dark="1px solid #991b1b")),
                                                border_radius="10px", p="3", width="100%",
                                            ),
                                        ),
                                        # Error de archivo
                                        rx.cond(
                                            State.respuesta_documento_error != "",
                                            rx.box(
                                                rx.hstack(
                                                    rx.icon("ban", size=15, color="#ef4444"),
                                                    rx.text(State.respuesta_documento_error, font_size="xs", color="#ef4444", font_weight="medium"),
                                                    spacing="2", align_items="center",
                                                ),
                                                bg=rx.color_mode_cond(light="#fef2f2", dark="rgba(127,29,29,0.25)"),
                                                border=rx.color_mode_cond(light="1px solid #fecaca", dark="1px solid rgba(239,68,68,0.4)"),
                                                border_radius="10px", p="3", width="100%",
                                            ),
                                        ),
                                        spacing="4", align_items="stretch",
                                        padding="18px 20px", max_height="65vh", overflow_y="auto", width="100%",
                                    ),
                                    width="100%",
                                ),
                                # Footer
                                rx.box(
                                    rx.hstack(
                                        rx.button("Cancelar", type="button", on_click=State.cerrar_editor_estado, variant="soft", color_scheme="gray", size="3", flex="1"),
                                        rx.button(
                                            rx.icon("refresh-cw", size=16),
                                            "Reabrir Solicitud",
                                            type="button",
                                            on_click=State.actualizar_estado_solicitud(rx.upload_files(upload_id="upload_respuesta_cerradas")),
                                            color_scheme="orange", size="3", flex="2",
                                        ),
                                        spacing="3", width="100%",
                                    ),
                                    padding="16px 20px",
                                    border_top=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                                    bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                                    border_bottom_left_radius="14px", border_bottom_right_radius="14px", width="100%",
                                ),
                                spacing="0", width="100%",
                            ),
                            bg=rx.color_mode_cond(light="#ffffff", dark="#0f1e35"),
                            border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #1e3a5f"),
                            border_top="3px solid #f59e0b",
                            border_radius="14px",
                            width="100%", max_width="560px", max_height="92vh", overflow="hidden",
                            position="fixed", top="50%", left="50%", transform="translate(-50%, -50%)",
                            z_index="1000",
                            box_shadow=rx.color_mode_cond(light="0 8px 24px rgba(245, 158, 11, 0.16)", dark="0 2px 12px rgba(0,0,0,0.3)"),
                        ),
                    )
                ),
                # Modal: Historial
                rx.cond(
                    State.historial_modal_abierto,
                    rx.dialog.root(
                        rx.dialog.content(
                            rx.dialog.title("Historial de Estados", display="none"),
                            rx.dialog.description("Historial de cambios de estado", display="none"),
                            rx.vstack(
                                rx.hstack(rx.icon("history", size=24, color="#3b82f6"), rx.heading("Historial de Estados", size="5"), rx.spacer(), rx.dialog.close(rx.button(rx.icon("x", size=20), on_click=State.cerrar_historial, variant="ghost", color_scheme="gray")), width="100%", align_items="center"),
                                rx.divider(margin_y="2"),
                                rx.cond(
                                    State.historial_estados,
                                    rx.vstack(
                                        rx.foreach(
                                            State.historial_estados,
                                            lambda evento: rx.box(
                                                # Log to browser console whether this event has multimedia/comments
                                                rx.hstack(
                                                    rx.text("DEBUG:", font_size="xs", color=subtext_color),
                                                    rx.text(evento["nuevo"], font_size="xs"),
                                                    rx.text("doc_exists:", font_size="xs", color=subtext_color),
                                                    rx.text(rx.cond(evento["documento_existe"], "Sí", "No"), font_size="xs"),
                                                    rx.text("comentarios:", font_size="xs", color=subtext_color),
                                                    rx.text(rx.cond(evento["obs"] != "", "Con comentario", "Sin comentarios"), font_size="xs"),
                                                    spacing="3", align_items="center"
                                                ),
                                                rx.hstack(
                                                    rx.box(rx.icon("git-commit-horizontal", size=20, color="#10b981"), p="2", bg="rgba(16, 185, 129, 0.1)", border_radius="full"),
                                                    rx.vstack(
                                                        rx.hstack(rx.text("Cambió a:", font_size="sm", color=subtext_color), rx.badge(evento['nuevo'], color_scheme="blue", radius="full"), rx.spacer(), rx.text(evento['fecha'], font_size="xs", color=subtext_color), width="100%", align_items="center"),
                                                        rx.text(rx.cond(evento['obs'] != "", f'"{evento["obs"]}"', "Sin comentarios."), font_size="sm", font_style="italic", color=text_color),
                                                        rx.text(f"Estado anterior: {evento['anterior']}", font_size="xs", color=subtext_color),
                                                        rx.cond(
                                                            evento["documento_adjunto"] != "",
                                                            ui_tarjeta_adjunto_historial(evento),
                                                            rx.box(),
                                                        ),
                                                        spacing="1", width="100%", align_items="start"
                                                    ),
                                                    spacing="4", align_items="start", width="100%"
                                                ),
                                                p="4", bg=rx.color_mode_cond(light="#f8fafc", dark="#1e293b"), border_radius="xl", width="100%", margin_bottom="3"
                                            )
                                        ),
                                        width="100%", max_height="400px", overflow_y="auto"
                                    ),
                                    rx.center(rx.text("Aún no hay historial de cambios para esta solicitud.", color=subtext_color), p="6")
                                ),
                                spacing="4", width="100%"
                            ),
                            style={"maxWidth": "600px", "borderRadius": "24px", "padding": "24px", "backgroundColor": card_bg, "backdropFilter": "blur(40px)", "border": card_border}
                        ),
                        open=True, on_open_change=State.cerrar_historial
                    )
                ),
            ),
            rx.box(
                navbar(),
                rx.center(access_denied_widget("Solo funcionarios autenticados pueden acceder a esta función."), size="3"),
                bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a"),
                min_height="100vh",
            ),
        ),
        rx.center(rx.spinner(size="3", color="#3b82f6"), height="50vh"),
    )


