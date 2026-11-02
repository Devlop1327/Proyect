from ...state import State
import reflex as rx
from ...usuario_model import Usuario

def nav_icon_link(icon_name: str, text: str, href: str, active: bool = False, display_cond=None) -> rx.Component:
    link_content = rx.link(
        rx.hstack(
            rx.icon(icon_name, size=20, color="rgba(255,255,255,0.85)", transition="transform 0.2s ease"),
            rx.text(
                text,
                class_name="nav-text",
                color="white",
                font_weight="600",
                font_size="13px",
                white_space="nowrap",
                opacity="0",
                max_width="0px",
                overflow="hidden",
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                margin_left="0px"
            ),
            align_items="center",
            padding="8px",
            border_radius="12px",
            bg="rgba(255,255,255,0.15)" if active else "transparent",
            transition="all 0.2s ease",
            _hover={
                "bg": "rgba(255,255,255,0.25)",
                "& > svg": {
                    "color": "white",
                    "transform": "scale(1.1)"
                },
                "& .nav-text": {
                    "opacity": "1",
                    "max_width": "200px",
                    "margin_left": "8px"
                }
            }
        ),
        href=href,
        text_decoration="none"
    )
    if display_cond is not None:
        return rx.cond(display_cond, link_content, rx.box(display="none"))
    return link_content

def navbar() -> rx.Component:
    return rx.fragment(rx.box(
        rx.hstack(
            # Logo / marca
            rx.link(
                rx.hstack(
                    rx.box(
                        rx.icon("shield-check", size=18, color="#e85d04"),
                        width="36px", height="36px",
                        border_radius="10px",
                        bg="rgba(232,93,4,0.18)",
                        display="flex", align_items="center", justify_content="center", flex_shrink="0",
                    ),
                    rx.text("PQRS", font_size="18px", font_weight="800", color="white", letter_spacing="-0.01em"),
                    spacing="3", align_items="center",
                ),
                href=State.home_url, text_decoration="none", flex_shrink="0",
            ),
            
            rx.box(width="1px", height="24px", bg="rgba(255,255,255,0.2)", margin_x="4"),
            
            # Navegación con iconos dinámicos
            rx.hstack(
                nav_icon_link("home", "Inicio", State.home_url),
                nav_icon_link("file-plus", "Nueva Solicitud", "/solicitudes"),
                
                # Opciones de Funcionario
                nav_icon_link("bar-chart-2", "Reportes", "/reportes", display_cond=State.es_autenticada & (State.rol_usuario == "funcionario")),
                nav_icon_link("users", "Ver Usuarios", "/usuarios", display_cond=State.es_autenticada & (State.rol_usuario == "funcionario")),
                nav_icon_link("user-plus", "Registrar Func.", "/registro-funcionario", display_cond=State.es_autenticada & (State.rol_usuario == "funcionario")),
                nav_icon_link("settings", "Cambiar Rol", "/cambiar-rol", display_cond=State.es_autenticada & (State.rol_usuario == "funcionario")),
                nav_icon_link("help-circle", "Ayuda", "/ayuda-funcionario", display_cond=State.es_autenticada & (State.rol_usuario == "funcionario")),
                
                # Dashboards
                nav_icon_link("layout", "Dashboard Func.", "/dashboard-funcionario", active=True, display_cond=State.es_autenticada & (State.rol_usuario == "funcionario")),
                nav_icon_link("layout", "Mi Panel", "/dashboard", active=True, display_cond=State.es_autenticada & (State.rol_usuario != "funcionario")),
                
                spacing="2",
                align_items="center",
                flex_wrap="nowrap",
                overflow_x="auto"
            ),
            
            rx.spacer(),
            
            # Controles derecha
            rx.hstack(
                rx.color_mode.button(color="rgba(255,255,255,0.8)", _hover={"color": "white"}),
                # Chip animado con icono y nombre del funcionario/usuario
                rx.cond(
                    State.es_autenticada,
                    rx.hstack(
                        rx.box(
                            rx.icon("user-circle", size=20, color="rgba(255,255,255,0.9)"),
                            id="navbar-user-avatar",
                            width="36px",
                            height="36px",
                            border_radius="full",
                            bg="rgba(255,255,255,0.15)",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            flex_shrink="0",
                            transition="all 0.2s ease",
                        ),
                        rx.box(
                            rx.el.span(
                                State.nombres,
                                id="navbar-user-name",
                                style={
                                    "color": "white",
                                    "font_weight": "700",
                                    "font_size": "13px",
                                    "white_space": "nowrap",
                                    "opacity": "0",
                                    "max_width": "0px",
                                    "overflow": "hidden",
                                    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                                    "margin_left": "0px",
                                    "display": "block",
                                    "line_height": "1.2",
                                },
                            ),
                            rx.el.span(
                                State.rol_usuario,
                                id="navbar-user-role",
                                style={
                                    "color": "rgba(255,255,255,0.65)",
                                    "font_weight": "500",
                                    "font_size": "10px",
                                    "white_space": "nowrap",
                                    "opacity": "0",
                                    "max_width": "0px",
                                    "overflow": "hidden",
                                    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                                    "margin_left": "0px",
                                    "display": "block",
                                    "text_transform": "capitalize",
                                    "line_height": "1.2",
                                    "margin_top": "1px",
                                },
                            ),
                            display="flex",
                            flex_direction="column",
                            align_items="flex-start",
                        ),
                        align_items="center",
                        id="navbar-user-chip",
                        spacing="2",
                        padding="6px 10px",
                        border_radius="12px",
                        bg="rgba(255,255,255,0.10)",
                        border="1px solid rgba(255,255,255,0.18)",
                        cursor="default",
                        transition="all 0.2s ease",
                    ),
                    rx.box(display="none"),
                ),
                # CSS global para animaciones hover del chip y botón salir
                rx.el.style("""
                    #navbar-user-chip:hover {
                        background: rgba(255,255,255,0.22) !important;
                        border-color: rgba(255,255,255,0.35) !important;
                    }
                    #navbar-user-chip:hover #navbar-user-name {
                        opacity: 1 !important;
                        max-width: 160px !important;
                        margin-left: 4px !important;
                    }
                    #navbar-user-chip:hover #navbar-user-role {
                        opacity: 1 !important;
                        max-width: 160px !important;
                        margin-left: 4px !important;
                    }
                    #navbar-user-chip:hover #navbar-user-avatar {
                        background: rgba(255,255,255,0.28) !important;
                        transform: scale(1.08);
                    }
                    #navbar-logout-btn:hover {
                        background: rgba(239,68,68,0.22) !important;
                        border-color: rgba(239,68,68,0.45) !important;
                    }
                    #navbar-logout-btn:hover #navbar-logout-icon {
                        background: rgba(239,68,68,0.35) !important;
                        transform: scale(1.08) rotate(-8deg);
                    }
                    #navbar-logout-btn:hover #navbar-logout-text {
                        opacity: 1 !important;
                        max-width: 60px !important;
                        margin-left: 8px !important;
                    }
                """),
                # Botón Salir animado con CSS global (sin class_name)
                rx.cond(
                    State.es_autenticada,
                    rx.hstack(
                        rx.box(
                            rx.icon("log-out", size=18, color="rgba(252,165,165,0.95)"),
                            id="navbar-logout-icon",
                            width="34px",
                            height="34px",
                            border_radius="10px",
                            bg="rgba(239,68,68,0.15)",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            flex_shrink="0",
                            transition="all 0.2s ease",
                        ),
                        rx.el.span(
                            "Salir",
                            id="navbar-logout-text",
                            style={
                                "color": "rgba(252,165,165,1)",
                                "font_weight": "600",
                                "font_size": "13px",
                                "white_space": "nowrap",
                                "opacity": "0",
                                "max_width": "0px",
                                "overflow": "hidden",
                                "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                                "margin_left": "0px",
                                "display": "inline-block",
                            },
                        ),
                        id="navbar-logout-btn",
                        align_items="center",
                        spacing="0",
                        padding="4px 8px",
                        border_radius="12px",
                        bg="rgba(239,68,68,0.10)",
                        border="1px solid rgba(239,68,68,0.25)",
                        cursor="pointer",
                        transition="all 0.2s ease",
                        on_click=State.abrir_logout_confirm,
                    ),
                    rx.box(display="none"),
                ),
                spacing="4", align_items="center"
            ),
            justify="between", align_items="center", width="100%", max_width="1400px", margin="0 auto"
        ),
        bg=rx.color_mode_cond(light="linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%)", dark="linear-gradient(90deg, #0f172a 0%, #172554 100%)"),
        padding_y="12px", padding_x={"base": "16px", "md": "32px"}, width="100%",
        box_shadow="0 4px 20px -2px rgba(0, 0, 0, 0.2)",
        position="sticky", top="0", z_index="50", border_bottom="1px solid rgba(255,255,255,0.1)"
    ), logout_confirm_modal())


def access_denied_widget(message: str) -> rx.Component:
    # Auto-redirect to login if not authenticated; show access denied if authenticated but wrong role
    return rx.cond(
        rx.State.is_hydrated,
        rx.cond(
            State.es_autenticada,
            rx.vstack(
                rx.heading("Acceso Denegado", size="8", color="red.500"),
                rx.text(message, color="gray.600"),
                rx.vstack(
                    rx.button("Cerrar Sesión", on_click=State.logout, color_scheme="red", width="100%"),
                    rx.link(rx.button("Volver al inicio", color_scheme="blue"), href="/"),
                    spacing="4",
                    align_items="center"
                ),
                spacing="4",
                align_items="center"
            ),
            rx.script("window.location.href = '/login'")
        ),
        rx.center(rx.spinner(size="3", color="#3b82f6"), height="50vh")
    )


def utility_bar() -> rx.Component:
    return rx.hstack(
        rx.link(
            rx.hstack(rx.icon("globe", size=14), rx.text("GOV.CO"), spacing="2", align_items="center"),
            href="/", font_weight="bold", color="rgba(255,255,255,0.9)", text_decoration="none", _hover={"color": "white"}
        ),
        rx.spacer(),
        rx.hstack(
            rx.link(rx.hstack(rx.icon("accessibility", size=14), rx.text("Accesibilidad"), spacing="1"), href="#", font_size="xs", color="rgba(255,255,255,0.8)", text_decoration="none", _hover={"color": "white"}),
            rx.text("|", color="rgba(255,255,255,0.3)"),
            rx.link(rx.hstack(rx.icon("log-in", size=14), rx.text("Inicia sesión"), spacing="1"), href="/login", font_size="xs", color="rgba(255,255,255,0.8)", text_decoration="none", _hover={"color": "white"}),
            rx.text("|", color="rgba(255,255,255,0.3)"),
            rx.link(rx.hstack(rx.icon("user-plus", size=14), rx.text("Regístrate"), spacing="1"), href="/registro", font_size="xs", color="rgba(255,255,255,0.8)", text_decoration="none", _hover={"color": "white"}),
            spacing="4", align_items="center"
        ),
        width="100%", padding_x="24px", padding_y="8px",
        bg=rx.color_mode_cond(light="#0f172a", dark="#020617"),
        border_bottom="1px solid rgba(255,255,255,0.08)"
    )

def logout_confirm_modal():
    """Modal de confirmacion de cierre de sesion."""
    return rx.cond(
        State.show_logout_confirm,
        rx.box(
            rx.box(
                position="fixed", inset="0",
                bg="rgba(0,0,0,0.55)",
                backdrop_filter="blur(4px)",
                z_index="1000",
                on_click=State.cerrar_logout_confirm,
            ),
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.center(
                            rx.box(
                                rx.icon("log-out", size=32, color="#f87171"),
                                width="64px", height="64px",
                                border_radius="full",
                                bg="rgba(239,68,68,0.12)",
                                border="2px solid rgba(239,68,68,0.30)",
                                display="flex",
                                align_items="center",
                                justify_content="center",
                            ),
                            width="100%",
                        ),
                        rx.text(
                            "¿Cerrar sesión",
                            font_size="22px",
                            font_weight="800",
                            color="white",
                            text_align="center",
                            letter_spacing="-0.02em",
                        ),
                        rx.text(
                            "Tu sesión se cerrará y tendrás que volver a iniciar sesión.",
                            font_size="14px",
                            color="rgba(255,255,255,0.65)",
                            text_align="center",
                            line_height="1.6",
                        ),
                        rx.box(width="100%", height="1px", bg="rgba(255,255,255,0.10)"),
                        rx.hstack(
                            rx.box(
                                rx.hstack(
                                    rx.icon("x", size=16, color="rgba(255,255,255,0.85)"),
                                    rx.text("Cancelar", font_weight="600", font_size="14px", color="rgba(255,255,255,0.9)"),
                                    spacing="2", align_items="center",
                                ),
                                padding="10px 22px",
                                border_radius="12px",
                                bg="rgba(255,255,255,0.08)",
                                border="1px solid rgba(255,255,255,0.15)",
                                cursor="pointer",
                                transition="all 0.2s ease",
                                on_click=State.cerrar_logout_confirm,
                                _hover={
                                    "bg": "rgba(255,255,255,0.16)",
                                    "border": "1px solid rgba(255,255,255,0.30)",
                                    "transform": "translateY(-1px)",
                                },
                            ),
                            rx.box(
                                rx.hstack(
                                    rx.icon("log-out", size=16, color="white"),
                                    rx.text("Sí, salir", font_weight="700", font_size="14px", color="white"),
                                    spacing="2", align_items="center",
                                ),
                                padding="10px 22px",
                                border_radius="12px",
                                bg="linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
                                border="1px solid rgba(220,38,38,0.5)",
                                cursor="pointer",
                                transition="all 0.2s ease",
                                box_shadow="0 8px 20px -6px rgba(220,38,38,0.55)",
                                on_click=State.logout,
                                _hover={
                                    "bg": "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
                                    "box_shadow": "0 12px 28px -6px rgba(220,38,38,0.75)",
                                    "transform": "translateY(-2px)",
                                },
                            ),
                            spacing="3",
                            justify="center",
                            width="100%",
                        ),
                        spacing="5",
                        align_items="center",
                        width="100%",
                    ),
                    bg="linear-gradient(135deg, rgba(15,23,42,0.97) 0%, rgba(30,27,75,0.97) 100%)",
                    border="1px solid rgba(255,255,255,0.12)",
                    border_radius="24px",
                    padding="36px 32px",
                    width="390px",
                    max_width="90vw",
                    box_shadow="0 30px 60px -20px rgba(0,0,0,0.85)",
                    backdrop_filter="blur(24px)",
                    position="relative",
                    z_index="1002",
                ),
                position="fixed",
                inset="0",
                z_index="1001",
            ),
            position="fixed", inset="0", z_index="1000",
        ),
        rx.box(display="none"),
    )

def toast_notification() -> rx.Component:
    return rx.cond(
        State.toast_visible,
        rx.box(
            rx.hstack(
                rx.box(
                    rx.cond(
                        State.toast_tipo == "success",
                        rx.icon("circle-check", size=22, color="white"),
                        rx.icon("circle-x", size=22, color="white"),
                    ),
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    width="36px",
                    height="36px",
                    border_radius="full",
                    bg=rx.cond(State.toast_tipo == "success", "rgba(255,255,255,0.25)", "rgba(255,255,255,0.25)"),
                    flex_shrink="0",
                ),
                rx.vstack(
                    rx.text(
                        rx.cond(State.toast_tipo == "success", "¡Éxito!", "Error"),
                        font_weight="bold",
                        color="white",
                        font_size="sm",
                        line_height="1.1",
                    ),
                    rx.text(
                        State.toast_mensaje,
                        color="rgba(255,255,255,0.95)",
                        font_size="xs",
                        line_height="1.3",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=16, color="white"),
                    on_click=State.ocultar_toast,
                    variant="ghost",
                    size="1",
                    _hover={"bg": "rgba(255,255,255,0.15)"},
                    padding="0",
                    min_width="24px",
                    height="24px",
                ),
                spacing="3",
                align_items="center",
                width="100%",
            ),
            position="fixed",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            z_index="9999",
            min_width="200px",
            max_width="280px",
            padding="10px 12px",
            border_radius="18px",
            bg=rx.cond(
                State.toast_tipo == "success",
                "linear-gradient(135deg, #16a34a, #15803d)",
                "linear-gradient(135deg, #dc2626, #b91c1c)",
            ),
            box_shadow="0 8px 32px rgba(0,0,0,0.22), 0 2px 8px rgba(0,0,0,0.12)",
            style={
                "animation": "slideInToast 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
                "@keyframes slideInToast": {
                    "from": {"opacity": "0", "transform": "translateY(24px) scale(0.95)"},
                    "to": {"opacity": "1", "transform": "translateY(0) scale(1)"},
                }
            }
        ),
        rx.box()
    )


