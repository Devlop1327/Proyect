import reflex as rx
from ...state import State
from ..theme import (
    _ldc_reg, ORANGE, ORANGE_LIGHT, ORANGE_BORDER, NAVY, NAVY_DARK, BLUE_ACC,
    RED_ERR, GREEN_OK, VIOLET, PAGE_BG, CARD_BG, CARD_BDR, TEXT_MAIN, TEXT_SUB,
    TEXT_LABEL, INPUT_BG, INPUT_BDR, INPUT_FOC, SECT_BG, DIVIDER,
)
from ..components.common import label_requerido, password_strength_label, brand_footer
from ..components.navigation import navbar, utility_bar
from ..components.footer import footer

from ..components.forms import (
    _label,
    _input_style,
    _select_style,
    _input_s,
    _select_s,
    _field,
    _field_with_check,
    _section_header,
    _section,
)
def _seccion_cuenta() -> rx.Component:
    """Correo + contraseñas."""
    return rx.box(
        _section_header("lock", "Datos de acceso", "Correo y contraseña para ingresar al sistema"),
        rx.grid(
            rx.box(
                _label("Correo Electrónico", required=True),
                rx.hstack(
                    rx.input(
                        placeholder="tu buzón electrónico",
                        type="email",
                        value=State.correo,
                        on_change=State.set_and_validate_correo,
                        on_blur=State.validar_correo_accion,
                        flex="1",
                        **_input_style(),
                    ),
                    rx.cond(
                        State.correo_validado,
                        rx.box(
                            rx.icon("circle-check", size=18, color="#16a34a"),
                            flex_shrink="0",
                        ),
                        rx.box(width="18px"),
                    ),
                    spacing="2", align_items="center", width="100%",
                ),
                rx.cond(
                    State.correo_confirmacion_visible,
                    rx.text(
                        State.correo_confirmacion_mensaje,
                        color=rx.cond(State.correo_validado, "#16a34a", "#dc2626"),
                        font_size="12px",
                        margin_top="4px",
                    ),
                    rx.box(),
                ),
                grid_column="1 / -1",
            ),
            _field_with_check(
                "Confirmar Correo Electrónico",
                rx.input(
                    placeholder="Repite tu correo electrónico",
                    type="email",
                    value=State.confirmar_correo,
                    on_change=State.set_confirmar_correo,
                    on_blur=lambda: State.set_confirmar_correo_match(State.correo == State.confirmar_correo),
                    **_input_style(),
                ),
                State.confirmar_correo_match & (State.confirmar_correo != ""),
            ),
            rx.vstack(
                _label("Contraseña", required=True),
                rx.hstack(
                    rx.input(
                        placeholder="Contraseña",
                        type=rx.cond(State.show_password, "text", "password"),
                        value=State.contraseña,
                        on_change=State.set_contraseña,
                        flex="1",
                        **_input_style(),
                    ),
                    rx.button(
                        rx.cond(
                            State.show_password,
                            rx.icon("eye_off", size=16, color=TEXT_SUB),
                            rx.icon("eye", size=16, color=TEXT_SUB),
                        ),
                        on_click=State.toggle_show_password,
                        variant="ghost", size="1",
                        _hover={"bg": "transparent"},
                        flex_shrink="0",
                    ),
                    spacing="1", align_items="center", width="100%",
                ),
                spacing="0", align_items="start", width="100%",
            ),
            _field(
                "Confirmar Contraseña",
                rx.input(
                    placeholder="Confirmar Contraseña",
                    type=rx.cond(State.show_password, "text", "password"),
                    value=State.confirmar_contraseña,
                    on_change=State.set_confirmar_contraseña,
                    **_input_style(),
                ),
            ),
            template_columns={"base": "1fr", "md": "1fr 1fr"},
            gap="4",
            width="100%",
        ),
        bg=CARD_BG,
        border=f"1px solid {CARD_BDR}",
        border_radius="14px",
        padding="20px 22px",
        width="100%",
    )


def _seccion_identificacion() -> rx.Component:
    """Tipo ID + número + nombres + apellidos + sexo."""
    return rx.box(
        _section_header("id-card", "Información personal", "Datos de identificación del ciudadano"),
        rx.grid(
            _field(
                "Tipo de Identificación",
                rx.select(
                    ["Cédula", "Pasaporte", "Tarjeta de Identidad"],
                    placeholder="Seleccione...",
                    value=State.tipo_identificacion,
                    on_change=State.set_tipo_identificacion,
                    **_select_style(),
                ),
                required=False,
            ),
            _field_with_check(
                "Número de Identificación",
                rx.input(
                    placeholder="Cédula/NIT",
                    value=State.numero_identificacion,
                    on_change=State.set_and_validate_numero_identificacion,
                    **_input_style(),
                ),
                State.numero_identificacion_valid,
            ),
            _field_with_check(
                "Nombres",
                rx.input(
                    placeholder="Nombre o razón social",
                    value=State.nombres,
                    on_change=State.set_and_validate_nombres,
                    **_input_style(),
                ),
                State.nombres_valid,
            ),
            _field_with_check(
                "Apellidos",
                rx.input(
                    placeholder="Apellidos",
                    value=State.apellidos,
                    on_change=State.set_and_validate_apellidos,
                    **_input_style(),
                ),
                State.apellidos_valid,
            ),
            _field(
                "Género",
                rx.select(
                    ["Femenino", "Masculino", "Prefiero no decirlo"],
                    placeholder="Seleccione...",
                    value=State.sexo,
                    on_change=State.set_sexo,
                    **_select_style(),
                ),
                required=False,
            ),
            _field_with_check(
                "Número de Contacto",
                rx.input(
                    placeholder="un teléfono de contacto",
                    value=State.telefono,
                    on_change=State.set_and_validate_telefono,
                    **_input_style(),
                ),
                State.telefono_valid,
            ),
            template_columns={"base": "1fr", "md": "1fr 1fr 1fr"},
            gap="4",
            width="100%",
        ),
        bg=CARD_BG,
        border=f"1px solid {CARD_BDR}",
        border_radius="14px",
        padding="20px 22px",
        width="100%",
    )


def _seccion_ubicacion() -> rx.Component:
    """Dirección + departamento + ciudad."""
    return rx.box(
        _section_header("map-pin", "Ubicación", "Dirección y municipio de residencia"),
        rx.grid(
            rx.box(
                _label("Dirección", required=True),
                rx.input(
                    placeholder="tu dirección de residencia",
                    value=State.direccion,
                    on_change=State.set_direccion,
                    **_input_style(),
                ),
                grid_column="1 / -1",
            ),
            _field_with_check(
                "Departamento",
                rx.select(
                    [
                        "Amazonas","Antioquia","Arauca","Atlántico","Bogotá D.C.",
                        "Bolívar","Boyacá","Caldas","Caquetá","Casanare","Cauca",
                        "Cesar","Chocó","Córdoba","Cundinamarca","Guainía","Guaviare",
                        "Huila","La Guajira","Magdalena","Meta","Nariño",
                        "Norte de Santander","Putumayo","Quindío","Risaralda",
                        "San Andrés y Providencia","Santander","Sucre","Tolima",
                        "Valle del Cauca","Vaupés","Vichada",
                    ],
                    placeholder="Seleccione...",
                    value=State.departamento,
                    on_change=State.set_and_validate_departamento,
                    **_select_style(),
                ),
                State.departamento_valid,
                required=True,
            ),
            _field_with_check(
                "Ciudad",
                rx.select(
                    State.ciudades_disponibles,
                    placeholder="Seleccione...",
                    value=State.ciudad,
                    on_change=State.set_and_validate_ciudad,
                    is_disabled=State.departamento == "",
                    **_select_style(),
                ),
                State.ciudad_valid,
                required=True,
            ),
            template_columns={"base": "1fr", "md": "1fr 1fr"},
            gap="4",
            width="100%",
        ),
        bg=CARD_BG,
        border=f"1px solid {CARD_BDR}",
        border_radius="14px",
        padding="20px 22px",
        width="100%",
    )


def _seccion_diversidad() -> rx.Component:
    """Etnia + característica de ciudadano."""
    return rx.box(
        _section_header("heart-handshake", "Diversidad e inclusión", "Opcional �?? ayuda a mejorar la atención"),
        rx.grid(
            _field(
                "Etnia",
                rx.select(
                    ["Ninguna","Indígena","Afrocolombiano","Raizal","Palenquero","Gitano/a","Otro"],
                    placeholder="Seleccione...",
                    value=State.etnia,
                    on_change=State.set_etnia,
                    **_select_style(),
                ),
                required=False,
            ),
            _field(
                "Características del ciudadano",
                rx.select(
                    [
                        "Ninguna","Habitante de la calle","No brinda información",
                        "Peligro Inminente","Periodistas en ejercicio de su actividad",
                        "Primera Infancia","Veteranos Fuerza Pública",
                        "Víctimas - Conflicto Armado",
                    ],
                    placeholder="Seleccione...",
                    value=State.persona_vulnerable_registro,
                    on_change=State.set_persona_vulnerable_registro,
                    **_select_style(),
                ),
                required=False,
            ),
            template_columns={"base": "1fr", "md": "1fr 1fr"},
            gap="4",
            width="100%",
        ),
        bg=CARD_BG,
        border=f"1px solid {CARD_BDR}",
        border_radius="14px",
        padding="20px 22px",
        width="100%",
    )


def _seccion_autorizaciones() -> rx.Component:
    """Checkboxes de habeas data y notificaciones."""
    return rx.box(
        _section_header("shield-check", "Autorizaciones", "Política de datos y notificaciones"),
        rx.vstack(
            rx.hstack(
                rx.checkbox(
                    is_checked=State.acepta_notificaciones,
                    on_change=State.set_acepta_notificaciones,
                    color_scheme="orange",
                    size="2",
                ),
                rx.text(
                    "Autorizo de manera expresa que me notifiquen o comuniquen al correo "
                    "electrónico aquí suministrado la respuesta a escritos o solicitudes, "
                    "así como cualquier información relacionada con mis trámites.",
                    font_size="13px",
                    color=TEXT_SUB,
                    line_height="1.6",
                ),
                spacing="3",
                align_items="start",
                width="100%",
                padding="14px 16px",
                bg=SECT_BG,
                border_radius="10px",
                border=f"1px solid {_ldc_reg('#bfdbfe','#1e3a5f')}",
            ),
            rx.hstack(
                rx.checkbox(
                    is_checked=State.acepta_politica_datos,
                    on_change=State.preconfirmar_politica,
                    color_scheme="orange",
                    size="2",
                ),
                rx.hstack(
                    rx.text("He leído y acepto la ", font_size="13px", color=TEXT_SUB),
                    rx.link(
                        "Política de Protección de Datos",
                        href="/politica-privacidad",
                        color=ORANGE,
                        font_size="13px",
                        font_weight="600",
                        text_decoration="none",
                        _hover={"text_decoration": "underline"},
                    ),
                    spacing="0",
                    flex_wrap="wrap",
                ),
                spacing="3",
                align_items="center",
                width="100%",
                padding="14px 16px",
                bg=ORANGE_LIGHT,
                border_radius="10px",
                border=f"1px solid {ORANGE_BORDER}",
            ),
            spacing="3",
            width="100%",
        ),
        bg=CARD_BG,
        border=f"1px solid {CARD_BDR}",
        border_radius="14px",
        padding="20px 22px",
        width="100%",
    )


def _modal_politica() -> rx.Component:
    """Modal de confirmación de política de datos."""
    return rx.cond(
        State.modal_politica_visible,
        rx.box(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("shield-check", size=20, color=ORANGE),
                            bg=ORANGE_LIGHT,
                            border_radius="10px",
                            width="40px", height="40px",
                            display="flex", align_items="center", justify_content="center",
                        ),
                        rx.vstack(
                            rx.heading("Confirmación de Política", size="4", color=TEXT_MAIN),
                            rx.text("Política de Protección de Datos Personales", font_size="12px", color=TEXT_SUB),
                            spacing="0", align_items="start",
                        ),
                        spacing="3", align_items="center", width="100%",
                    ),
                    rx.divider(),
                    rx.text(
                        "Al aceptar confirmas que has leído y comprendido cómo se usarán "
                        "tus datos personales para gestionar solicitudes PQRS.",
                        font_size="13px", color=TEXT_SUB, line_height="1.6",
                    ),
                    rx.text(
                        "La aceptación es necesaria para continuar con el registro.",
                        font_size="13px", color=TEXT_MAIN, font_weight="600",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            on_click=State.cancelar_politica,
                            variant="outline", border_radius="8px", flex="1",
                        ),
                        rx.button(
                            "Aceptar y continuar",
                            on_click=State.confirmar_politica,
                            bg=ORANGE, color="white", border_radius="8px", flex="1",
                            _hover={"bg": "#c2410c"},
                        ),
                        spacing="3", width="100%",
                    ),
                    spacing="4", align_items="stretch", width="100%",
                ),
                bg=CARD_BG,
                border=f"2px solid {ORANGE_BORDER}",
                border_radius="18px",
                padding="28px",
                width="100%",
                max_width="480px",
                box_shadow="0 20px 60px rgba(0,0,0,0.2)",
            ),
            position="fixed", inset="0",
            bg="rgba(15,23,42,0.55)",
            display="flex", align_items="center", justify_content="center",
            z_index="1000", padding="24px",
        ),
    )


def registro_funcionario_page() -> rx.Component:
    """Página de registro de funcionario �?? solo para funcionarios autenticados."""
    acceso_denegado = rx.center(
        rx.vstack(
            rx.icon("shield-x", size=48, color="#ef4444"),
            rx.heading("Acceso Denegado", size="7", color="#ef4444"),
            rx.text("Solo funcionarios autenticados pueden registrar nuevos funcionarios.", color=TEXT_SUB),
            rx.link(rx.button("Ir al Login", color_scheme="blue", border_radius="10px"), href="/login"),
            spacing="4", align_items="center",
        ),
        min_height="80vh",
    )

    return rx.cond(
        State.es_autenticada & (State.rol_usuario == "funcionario"),
        rx.box(
            navbar(),
            _modal_politica(),
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.box(
                            rx.hstack(
                                rx.text("Registrar", font_size="2rem", font_weight="800", color=NAVY),
                                rx.text(" Nuevo Funcionario", font_size="2rem", font_weight="800", color=TEXT_MAIN),
                                spacing="0", flex_wrap="wrap",
                            ),
                            rx.text("Crea la cuenta institucional del nuevo funcionario.", font_size="14px", color=TEXT_SUB),
                            border_bottom=f"3px solid {NAVY}",
                            padding_bottom="16px",
                            margin_bottom="4px",
                            width="100%",
                        ),
                        rx.cond(
                            State.error_de_registro != "",
                            rx.hstack(
                                rx.icon("circle-x", size=16, color="#dc2626"),
                                rx.text(State.error_de_registro, font_size="13px", color="#dc2626"),
                                spacing="2", align_items="center",
                                bg="#fef2f2", border="1px solid #fecaca",
                                border_radius="8px", padding="10px 14px", width="100%",
                            ),
                        ),
                        rx.cond(
                            State.succes != "",
                            rx.hstack(
                                rx.icon("circle-check", size=16, color="#16a34a"),
                                rx.text(State.succes, font_size="13px", color="#16a34a"),
                                spacing="2", align_items="center",
                                bg="#f0fdf4", border="1px solid #bbf7d0",
                                border_radius="8px", padding="10px 14px", width="100%",
                            ),
                        ),
                        _seccion_cuenta(),
                        _seccion_identificacion(),
                        _seccion_ubicacion(),
                        _seccion_diversidad(),
                        _seccion_autorizaciones(),
                        rx.button(
                            rx.hstack(
                                rx.icon("user-check", size=16),
                                rx.text("Registrar Funcionario", font_size="15px", font_weight="600"),
                                spacing="2",
                            ),
                            on_click=State.signup_funcionario,
                            width="100%", height="48px",
                            bg=NAVY, color="white",
                            border_radius="10px",
                            _hover={"bg": "#172554"},
                            transition="background 0.15s ease",
                            is_disabled=~(State.acepta_politica_datos & State.acepta_notificaciones),
                        ),
                        spacing="5", align_items="stretch", width="100%",
                    ),
                    width="100%", max_width="900px",
                    padding={"base": "20px 16px", "md": "32px 40px"},
                ),
                width="100%",
            ),
            bg=PAGE_BG, min_height="100vh", width="100%",
        ),
        acceso_denegado,
    )


def registro_page() -> rx.Component:
    return rx.box(
        navbar(),
        _modal_politica(),

        rx.center(
            rx.box(
                rx.vstack(

                    # �??�?? Encabezado institucional �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "Regístrate en el Sistema PQRS" ,
                                    font_size={"base": "1.6rem", "md": "2rem"},
                                    font_weight="800",
                                    color=BLUE_ACC,
                                    letter_spacing="-0.02em",
                                ),
                                rx.text(
                                    "" ,
                                    font_size={"base": "1.6rem", "md": "2rem"},
                                    font_weight="800",
                                    color=TEXT_MAIN,
                                    letter_spacing="-0.02em",
                                ),
                                spacing="0", flex_wrap="wrap",
                            ),
                            rx.text(
                                "Completa el formulario para crear tu cuenta de ciudadano.",
                                font_size="14px", color=TEXT_SUB,
                            ),
                            spacing="2", align_items="start",
                        ),
                        border_bottom=f"3px solid {BLUE_ACC}",
                        padding_bottom="16px",
                        margin_bottom="4px",
                        width="100%",
                    ),

                    # �??�?? Mensajes de error / éxito globales �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.cond(
                        State.error_de_registro != "",
                        rx.hstack(
                            rx.icon("circle-x", size=16, color="#dc2626"),
                            rx.text(State.error_de_registro, font_size="13px", color="#dc2626", font_weight="500"),
                            spacing="2", align_items="center",
                            bg="#fef2f2", border="1px solid #fecaca",
                            border_radius="8px", padding="10px 14px", width="100%",
                        ),
                    ),
                    rx.cond(
                        State.succes != "",
                        rx.hstack(
                            rx.icon("circle-check", size=16, color="#16a34a"),
                            rx.text(State.succes, font_size="13px", color="#16a34a", font_weight="500"),
                            spacing="2", align_items="center",
                            bg="#f0fdf4", border="1px solid #bbf7d0",
                            border_radius="8px", padding="10px 14px", width="100%",
                        ),
                    ),

                    # �??�?? Secciones �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    _seccion_cuenta(),
                    _seccion_identificacion(),
                    _seccion_ubicacion(),
                    _seccion_diversidad(),
                    _seccion_autorizaciones(),

                    # �??�?? Botón enviar �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.vstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("user-plus", size=16),
                                rx.text("Crear mi cuenta", font_size="15px", font_weight="600"),
                                spacing="2",
                            ),
                            on_click=State.signup,
                            width="100%",
                            height="48px",
                            bg=BLUE_ACC,
                            color="white",
                            border_radius="10px",
                            cursor="pointer",
                            _hover={"bg": "#c2410c"},
                            _active={"bg": "#9a3412"},
                            transition="background 0.15s ease",
                            is_disabled=~(State.acepta_politica_datos & State.acepta_notificaciones),
                        ),
                        rx.hstack(
                            rx.text("¿Ya tienes una cuenta?", font_size="13px", color=TEXT_SUB),
                            rx.link(
                                "Inicia sesión",
                                href="/login",
                                color=BLUE_ACC,
                                font_size="13px",
                                font_weight="600",
                                text_decoration="none",
                                _hover={"text_decoration": "underline"},
                            ),
                            spacing="2", justify="center", width="100%",
                        ),
                        spacing="3", align_items="stretch", width="100%",
                    ),

                    spacing="5",
                    align_items="stretch",
                    width="100%",
                ),
                width="100%",
                max_width="900px",
                padding={"base": "20px 16px", "md": "32px 40px"},
            ),
            width="100%",
        ),

        bg=PAGE_BG,
        min_height="100vh",
        width="100%",
    )


