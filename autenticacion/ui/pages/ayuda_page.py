import reflex as rx
from ...state import State
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar, access_denied_widget
from ..components.footer import footer

def ayuda_funcionario_page() -> rx.Component:
    def acordeon_item(titulo: str, key: str, icono: str, contenido: rx.Component) -> rx.Component:
        abierto = State.ayuda_seccion_abierta == key
        return rx.box(
            rx.vstack(
                rx.button(
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.icon(icono, size=18, color=rx.color_mode_cond(light="#2563eb", dark="#60a5fa")),
                                p="2",
                                bg=rx.color_mode_cond(light="#eff6ff", dark="rgba(96, 165, 250, 0.12)"),
                                border_radius="lg",
                            ),
                            rx.text(titulo, font_weight="bold", font_size="lg"),
                            spacing="3",
                            align_items="center",
                        ),
                        rx.spacer(),
                        rx.icon(rx.cond(abierto, "chevron_up", "chevron_down"), size=20),
                        width="100%",
                        align_items="center",
                    ),
                    on_click=State.toggle_ayuda_seccion(key),
                    variant="ghost",
                    width="100%",
                    justify="start",
                    p="4",
                ),
                rx.cond(
                    abierto,
                    rx.box(contenido, px="6", pb="6", width="100%"),
                    rx.box(),
                ),
                spacing="0",
                width="100%",
                align_items="start",
            ),
            bg=rx.color_mode_cond(light="rgba(255,255,255,0.95)", dark="rgba(30,41,59,0.9)"),
            border=rx.color_mode_cond(light="1px solid #dbeafe", dark="1px solid #334155"),
            border_radius="2xl",
            box_shadow=rx.color_mode_cond(light="0 10px 20px -12px rgba(0,0,0,0.12)", dark="0 10px 25px -15px rgba(0,0,0,0.7)"),
            width="100%",
        )

    hero = rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("circle_help", size=38, color="white"),
                    p="4",
                    bg="linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)",
                    border_radius="2xl",
                    box_shadow="0 10px 25px -10px rgba(59,130,246,0.7)",
                ),
                rx.vstack(
                    rx.heading("Centro de Ayuda para Funcionarios", size="9", color="white", font_weight="bold"),
                    rx.text(
                        "Todo lo que necesitas para operar PQRS con rapidez, trazabilidad y calidad de servicio.",
                        color="rgba(255,255,255,0.9)",
                        font_size="lg",
                    ),
                    spacing="2",
                    align_items="start",
                ),
                spacing="4",
                width="100%",
                align_items="center",
            ),
            rx.grid(
                rx.box(
                    rx.text("Estado sugerido", font_size="sm", color="rgba(255,255,255,0.8)"),
                    rx.text("Radicada �?? En Proceso �?? Cerrada", font_weight="bold", color="white", font_size="lg"),
                ),
                rx.box(
                    rx.text("Tiempo de respuesta", font_size="sm", color="rgba(255,255,255,0.8)"),
                    rx.text("Métrica en días hábiles reales", font_weight="bold", color="white", font_size="lg"),
                ),
                rx.box(
                    rx.text("Objetivo", font_size="sm", color="rgba(255,255,255,0.8)"),
                    rx.text("Cerrar más rápido y mejor", font_weight="bold", color="white", font_size="lg"),
                ),
                columns={"base": "1", "md": "3"},
                spacing="4",
                width="100%",
            ),
            spacing="5",
            width="100%",
        ),
        p={"base": "6", "md": "8"},
        border_radius="3xl",
        bg="linear-gradient(120deg, #0f172a 0%, #1e3a8a 45%, #6d28d9 100%)",
        width="100%",
    )

    return rx.cond(
        State.es_autenticada & (State.rol_usuario == "funcionario"),
        rx.box(
            navbar(),
            rx.box(
                rx.box(
                    rx.vstack(
                        hero,
                        rx.vstack(
                        acordeon_item(
                            "1. Flujo recomendado de atención",
                            "estados",
                            "list_checks",
                            rx.vstack(
                                rx.text("Radicada: se recibió la solicitud y aún no ha sido gestionada.", font_size="lg"),
                                rx.text("En Proceso: ya existe análisis, contacto o trabajo activo sobre el caso.", font_size="lg"),
                                rx.text("Cerrada: se entregó respuesta final y, de ser necesario, adjuntos de soporte.", font_size="lg"),
                                rx.text("Consejo: evita cierres vacíos; documenta siempre la solución.", font_size="lg", font_weight="medium", color=rx.color_mode_cond(light="#475569", dark="#cbd5e1")),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        acordeon_item(
                            "2. Respuestas y documentos adjuntos",
                            "adjuntos",
                            "paperclip",
                            rx.vstack(
                                rx.text("En 'Actualizar estado' redacta una respuesta clara y orientada al ciudadano.", font_size="lg"),
                                rx.text("Si adjuntas evidencia (PDF/imagen), el sistema la envía por correo al cerrar.", font_size="lg"),
                                rx.text("Nombra archivos de forma descriptiva para facilitar auditorías y seguimiento.", font_size="lg"),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        acordeon_item(
                            "3. Reportes y lectura de métricas",
                            "reportes",
                            "chart_line",
                            rx.vstack(
                                rx.text("La gráfica de tiempos usa solicitudes cerradas con fecha real de respuesta.", font_size="lg"),
                                rx.text("Tooltip 'dias: X' significa promedio de días hábiles en esa fecha.", font_size="lg"),
                                rx.text("Usa filtros por tipo y exportaciones (Excel/CSV) para informes ejecutivos.", font_size="lg"),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        acordeon_item(
                            "4. Administración de usuarios",
                            "usuarios",
                            "users",
                            rx.vstack(
                                rx.text("Consulta roles y estado de cuentas desde 'Ver Usuarios'.", font_size="lg"),
                                rx.text("Puedes degradar de funcionario a ciudadano cuando corresponda.", font_size="lg"),
                                rx.text("Por seguridad, no está permitido degradar tu propia cuenta.", font_size="lg"),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        acordeon_item(
                            "5. Buenas prácticas operativas",
                            "buenas_practicas",
                            "shield_check",
                            rx.vstack(
                                rx.text("Prioriza vencidas y críticas con el semáforo de vencimientos.", font_size="lg"),
                                rx.text("Mantén respuestas concretas, respetuosas y con lenguaje ciudadano.", font_size="lg"),
                                rx.text("Antes de cerrar: valida ortografía, adjuntos y consistencia del estado.", font_size="lg"),
                                spacing="2",
                                width="100%",
                                align_items="start",
                            ),
                        ),
                        spacing="4",
                        width="100%",
                        ),
                        # Bloque de cierre para ocupar altura y mantener estética profesional
                        rx.box(
                            rx.grid(
                                rx.box(
                                    rx.text("SLA recomendado", font_size="sm", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                    rx.text("Responder en < 5 días hábiles", font_weight="bold", font_size="lg"),
                                    p="4",
                                    border_radius="xl",
                                    bg=rx.color_mode_cond(light="#f8fafc", dark="rgba(15,23,42,0.55)"),
                                    border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                                ),
                                rx.box(
                                    rx.text("Calidad de respuesta", font_size="sm", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                    rx.text("Clara, completa y verificable", font_weight="bold", font_size="lg"),
                                    p="4",
                                    border_radius="xl",
                                    bg=rx.color_mode_cond(light="#f8fafc", dark="rgba(15,23,42,0.55)"),
                                    border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                                ),
                                rx.box(
                                    rx.text("Seguimiento", font_size="sm", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                    rx.text("Revisar vencimientos cada día", font_weight="bold", font_size="lg"),
                                    p="4",
                                    border_radius="xl",
                                    bg=rx.color_mode_cond(light="#f8fafc", dark="rgba(15,23,42,0.55)"),
                                    border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                                ),
                                columns={"base": "1", "md": "3"},
                                spacing="4",
                                width="100%",
                            ),
                            width="100%",
                            margin_top="auto",
                            pt="6",
                        ),
                        spacing="6",
                        width="100%",
                        max_width="1650px",
                        min_height="calc(100vh - 130px)",
                        p={"base": "3", "md": "4"},
                    ),
                    width="100%",
                    bg=rx.color_mode_cond(light="rgba(255,255,255,0.7)", dark="rgba(15,23,42,0.45)"),
                    border=rx.color_mode_cond(light="1px solid #dbeafe", dark="1px solid #1e293b"),
                    border_radius="3xl",
                    box_shadow=rx.color_mode_cond(light="0 16px 40px -24px rgba(0,0,0,0.2)", dark="0 18px 45px -25px rgba(0,0,0,0.8)"),
                    margin_x={"base": "6px", "md": "14px"},
                ),
                width="100%",
                bg=rx.color_mode_cond(light="#f1f5f9", dark="#0f172a"),
                min_height="100vh",
                padding_top={"base": "6px", "md": "10px"},
                padding_bottom={"base": "12px", "md": "18px"},
            ),
        ),
        rx.box(
            navbar(),
            rx.center(access_denied_widget("Solo funcionarios autenticados pueden acceder a esta función."), size="3"),
        ),
    )

