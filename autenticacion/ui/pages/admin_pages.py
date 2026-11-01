import reflex as rx
from ...state import State
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar, access_denied_widget
from ..components.footer import footer

def usuarios_page() -> rx.Component:
    return rx.cond(
        State.es_autenticada & (State.rol_usuario == "funcionario"),
        rx.box(
            navbar(),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.heading("Directorio de Personal", size="7", color=rx.color_mode_cond(light="#0f172a", dark="#f8fafc"), font_weight="bold", letter_spacing="-0.02em"),
                            rx.text("Gestión y control de cuentas de usuarios registrados", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"), font_size="md"),
                            align_items="start",
                            spacing="1"
                        ),
                        rx.spacer(),
                        rx.box(
                            rx.icon("users", size=24, color=rx.color_mode_cond(light="#2563eb", dark="#60a5fa")),
                            p="3",
                            bg=rx.color_mode_cond(light="#eff6ff", dark="rgba(96, 165, 250, 0.1)"),
                            border_radius="xl"
                        ),
                        width="100%",
                        align_items="center"
                    ),
                    
                    rx.divider(margin_y="4", border_color=rx.color_mode_cond(light="#e2e8f0", dark="#334155")),

                    rx.box(
                        rx.cond(
                            State.usuarios_registrados,
                            rx.vstack(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Usuario"),
                                            rx.table.column_header_cell("Contacto"),
                                            rx.table.column_header_cell("Rol", align="center"),
                                            rx.table.column_header_cell("Registro"),
                                            rx.table.column_header_cell("Estado", align="center"),
                                            rx.table.column_header_cell("Acciones", align="center"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            State.usuarios_registrados,
                                            lambda usuario: rx.table.row(
                                                rx.table.cell(
                                                    rx.hstack(
                                                        rx.avatar(fallback=rx.cond(usuario["rol"] == "funcionario", "FN", "CD"), size="3", radius="full", color_scheme=rx.cond(usuario["rol"] == "funcionario", "blue", "gray")),
                                                        rx.vstack(
                                                            rx.text(f"{usuario['nombres']} {usuario['apellidos']}", font_weight="semibold", font_size="sm", color=rx.color_mode_cond(light="#1e293b", dark="#f8fafc")),
                                                            rx.text(f"ID: {usuario['id']}", font_size="xs", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                                            spacing="0", align_items="start"
                                                        ),
                                                        spacing="3", align_items="center"
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.hstack(
                                                        rx.icon("mail", size=14, color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                                                        rx.text(usuario["email"], font_size="sm", color=rx.color_mode_cond(light="#475569", dark="#cbd5e1")),
                                                        spacing="2", align_items="center"
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.badge(
                                                        rx.cond(usuario["rol"] == "funcionario", rx.icon("shield", size=12), rx.icon("user", size=12)),
                                                        usuario["rol"],
                                                        color_scheme=rx.cond(usuario["rol"] == "funcionario", "blue", "gray"),
                                                        variant="soft",
                                                        radius="full",
                                                        size="2",
                                                    ),
                                                    align="center"
                                                ),
                                                rx.table.cell(rx.text(usuario["fecha_creacion"], font_size="sm", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"))),
                                                rx.table.cell(
                                                    rx.hstack(
                                                        rx.box(width="8px", height="8px", border_radius="full", bg=rx.cond(usuario["is_active"] == "True", "#10b981", rx.cond(usuario["is_active"], "#10b981", "#ef4444"))),
                                                        rx.text(rx.cond(usuario["is_active"] == "True", "Activo", rx.cond(usuario["is_active"], "Activo", "Inactivo")), font_size="sm", color=rx.color_mode_cond(light="#475569", dark="#cbd5e1")),
                                                        spacing="2", align_items="center", justify="center"
                                                    ),
                                                    align="center"
                                                ),
                                                rx.table.cell(
                                                    rx.cond(
                                                        usuario["rol"] == "funcionario",
                                                        rx.button(
                                                            "Degradar a ciudadano",
                                                            size="2",
                                                            variant="soft",
                                                            color_scheme="red",
                                                            on_click=State.degradar_funcionario_a_ciudadano(usuario["email"]),
                                                            is_disabled=State.email_actual.to_string().lower() == usuario["email"].to_string().lower(),
                                                        ),
                                                        rx.box(),
                                                    ),
                                                    align="center",
                                                ),
                                                align_items="center",
                                                _hover={"bg": rx.color_mode_cond(light="#f8fafc", dark="rgba(30, 41, 59, 0.5)")},
                                                transition="background 0.2s"
                                            )
                                        )
                                    ),
                                    width="100%",
                                    size="3",
                                    variant="surface"
                                ),
                                rx.hstack(
                                    rx.text(f"Total de registros: {State.usuarios_registrados_count}", font_weight="medium", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"), font_size="sm"),
                                    rx.spacer(),
                                    width="100%",
                                    padding_top="4"
                                ),
                                spacing="4",
                                width="100%"
                            ),
                            rx.vstack(
                                rx.icon("users", size=48, color=rx.color_mode_cond(light="#cbd5e1", dark="#475569")),
                                rx.text("No hay usuarios registrados en el sistema.", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"), font_size="lg", font_weight="medium"),
                                spacing="4",
                                padding_y="12",
                                align_items="center"
                            )
                        ),
                        p="6",
                        border=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155"),
                        border_radius="2xl",
                        bg=rx.color_mode_cond(light="rgba(255, 255, 255, 0.8)", dark="rgba(15, 23, 42, 0.6)"),
                        backdrop_filter="blur(16px)",
                        box_shadow=rx.color_mode_cond(light="0 4px 6px -1px rgba(0, 0, 0, 0.05)", dark="0 10px 15px -3px rgba(0, 0, 0, 0.5)"),
                        width="100%",
                        overflow_x="auto"
                    ),
                    
                    spacing="6",
                    align_items="stretch",
                    width="100%"
                ),
                bg=rx.color_mode_cond(light="white", dark="#1a202c"),
                max_width="100%",
                p=rx.breakpoints(initial="4", md="6"),
                box_shadow="2xl",
                border_radius="3xl",
                width="100%",
                margin_y="4"
            ),
            width="100%",
            max_width="100%",
            p=rx.breakpoints(initial="2", md="3"),
            bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a"),
            min_height="100vh"
        ),
        rx.box(
            navbar(),
            rx.center(
                access_denied_widget("Solo funcionarios autenticados pueden ver esta página."),
                size="3"
            )
        )
    )


def cambiar_rol_page() -> rx.Component:
    text_main = rx.color_mode_cond(light="#1e293b", dark="#f1f5f9")
    text_sub = rx.color_mode_cond(light="#64748b", dark="#94a3b8")
    card_bg = rx.color_mode_cond(light="white", dark="#1e293b")
    card_bdr = rx.color_mode_cond(light="#e2e8f0", dark="#334155")
    page_bg = rx.color_mode_cond(light="#f8fafc", dark="#0f172a")
    input_bg = rx.color_mode_cond(light="#f8fafc", dark="#0f172a")
    input_bdr = rx.color_mode_cond(light="#e2e8f0", dark="#1e293b")
    blue_acc = "#2563eb"
    navy = "#1e3a8a"
    navy_dark = "#172554"
    red_err = "#ef4444"
    green = "#10b981"

    acceso_denegado = rx.center(
        rx.vstack(
            rx.icon("shield-x", size=48, color=red_err),
            rx.heading("Acceso Denegado", size="7", color=red_err),
            rx.text("Solo funcionarios autenticados pueden acceder.", color=text_sub),
            rx.link(rx.button("Ir al Login", color_scheme="blue", border_radius="10px"), href="/login"),
            spacing="4", align_items="center",
        ),
        min_height="80vh",
    )
 
    contenido = rx.box(
        navbar(),
        rx.center(
            rx.box(
                rx.vstack(
                    # Encabezado con ícono
                    rx.vstack(
                        rx.box(
                            rx.icon("user-cog", size=28, color="white"),
                            bg=f"linear-gradient(135deg, {navy_dark}, {navy})",
                            border_radius="16px",
                            width="60px", height="60px",
                            display="flex", align_items="center", justify_content="center",
                            box_shadow=f"0 8px 24px {navy}55",
                        ),
                        rx.heading(
                            "Cambiar Rol de Usuario",
                            size="6", color=text_main,
                            font_weight="800", letter_spacing="-0.02em",
                            text_align="center",
                        ),
                        rx.text(
                            "Promueve a un ciudadano al rol de funcionario del sistema",
                            font_size="14px", color=text_sub, text_align="center",
                        ),
                        spacing="3", align_items="center", width="100%",
                    ),
                    # Tarjeta formulario
                    rx.box(
                        rx.vstack(
                            # Aviso informativo
                            rx.hstack(
                                rx.box(
                                    rx.icon("info", size=15, color=blue_acc),
                                    width="30px", height="30px",
                                    border_radius="8px",
                                    bg=rx.color_mode_cond(light="#eff6ff", dark="#0f2744"),
                                    display="flex", align_items="center", justify_content="center",
                                    flex_shrink="0",
                                ),
                                rx.text(
                                    "Al promover un ciudadano, tendrá acceso al panel de "
                                    "funcionario y recibirá una notificación por correo.",
                                    font_size="13px", color=text_sub, line_height="1.6",
                                ),
                                spacing="3", align_items="start",
                                bg=rx.color_mode_cond(light="#eff6ff", dark="#0a1628"),
                                border=rx.color_mode_cond(light="1px solid #bfdbfe", dark="1px solid #1e3a5f"),
                                border_radius="10px",
                                padding="12px 16px",
                                width="100%",
                            ),
                            # Campo correo
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Correo del usuario a promover", font_size="13px", font_weight="600", color=text_main),
                                    rx.text("*", color="#e85d04", font_size="13px"),
                                    spacing="1",
                                ),
                                rx.box(
                                    rx.hstack(
                                        rx.icon("mail", size=16, color=text_sub),
                                        rx.input(
                                            placeholder="usuario@ejemplo.com",
                                            value=State.cambiar_rol_email,
                                            on_change=State.set_cambiar_rol_email,
                                            type="email",
                                            border="none",
                                            bg="transparent",
                                            color=text_main,
                                            font_size="14px",
                                            flex="1",
                                            _focus={"outline": "none"},
                                        ),
                                        spacing="2", align_items="center", width="100%",
                                    ),
                                    bg=input_bg,
                                    border=f"1.5px solid {input_bdr}",
                                    border_radius="10px",
                                    padding="10px 14px",
                                    width="100%",
                                    _focus_within={
                                        "border_color": blue_acc,
                                        "box_shadow": "0 0 0 3px rgba(37,99,235,0.12)",
                                    },
                                ),
                                spacing="2", align_items="start", width="100%",
                            ),
                            
                            # Checkbox para PQRS-1 backend
                            rx.checkbox(
                                "Confirmo validación de identidad y autorización.",
                                is_checked=State.confirmar_promocion_rol,
                                on_change=State.set_confirmar_promocion_rol,
                                color=text_sub,
                                size="2",
                            ),

                            # Mensaje resultado
                            rx.cond(
                                State.cambiar_rol_mensaje != "",
                                rx.hstack(
                                    rx.icon(
                                        rx.cond(State.cambiar_rol_mensaje.contains("�??"), "circle-check", "circle-x"),
                                        size=16,
                                        color=rx.cond(State.cambiar_rol_mensaje.contains("�??"), green, red_err),
                                    ),
                                    rx.text(
                                        State.cambiar_rol_mensaje,
                                        font_size="13px", font_weight="500",
                                        color=rx.cond(State.cambiar_rol_mensaje.contains("�??"), green, red_err),
                                    ),
                                    spacing="2", align_items="center",
                                    bg=rx.cond(State.cambiar_rol_mensaje.contains("�??"), rx.color_mode_cond(light="#f0fdf4", dark="#002818"), rx.color_mode_cond(light="#fef2f2", dark="#2d0000")),
                                    border=rx.cond(State.cambiar_rol_mensaje.contains("�??"), "1px solid #bbf7d0", "1px solid #fecaca"),
                                    border_radius="8px",
                                    padding="10px 14px",
                                    width="100%",
                                ),
                            ),
                            # Botón
                            rx.button(
                                rx.hstack(
                                    rx.icon("arrow-up-circle", size=16),
                                    rx.text("Promover a Funcionario", font_size="14px", font_weight="600"),
                                    spacing="2",
                                ),
                                on_click=State.cambiar_rol_ciudadano_a_funcionario,
                                width="100%", height="46px",
                                bg=f"linear-gradient(135deg, {navy_dark}, {navy})",
                                color="white",
                                border_radius="10px",
                                box_shadow=f"0 4px 14px {navy}44",
                                _hover={"opacity": "0.92", "transform": "translateY(-1px)"},
                                transition="all 0.15s ease",
                                is_disabled=(State.cambiar_rol_email == "") | (~State.confirmar_promocion_rol),
                            ),
                            spacing="4", align_items="stretch", width="100%",
                        ),
                        bg=card_bg,
                        border=f"1px solid {card_bdr}",
                        border_radius="18px",
                        padding="28px 30px",
                        box_shadow=rx.color_mode_cond(light="0 4px 24px rgba(0,0,0,0.07)", dark="0 4px 32px rgba(0,0,0,0.4)"),
                        width="100%",
                    ),
                    spacing="6", align_items="center", width="100%",
                ),
                width="100%", max_width="480px",
                padding={"base": "24px 16px", "md": "48px 24px"},
            ),
            width="100%", min_height="90vh",
        ),
        bg=page_bg, min_height="100vh", width="100%",
    )
 
    return rx.cond(
        State.es_autenticada & (State.rol_usuario == "funcionario"),
        contenido, acceso_denegado,
    )


