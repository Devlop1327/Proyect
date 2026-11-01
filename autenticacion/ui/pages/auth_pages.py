import reflex as rx
from ...state import State
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar, toast_notification
from ..components.footer import footer

def auth_card(title: str, on_submit, show_confirm: bool = False) -> rx.Component:
    text_color = rx.color_mode_cond(light="#1e293b", dark="#f8fafc")
    input_bg = rx.color_mode_cond(light="rgba(255, 255, 255, 0.8)", dark="rgba(30, 41, 59, 0.6)")
    input_border = rx.color_mode_cond(light="rgba(226, 232, 240, 0.8)", dark="rgba(51, 65, 85, 0.8)")
    placeholder_color = rx.color_mode_cond(light="#94a3b8", dark="#64748b")

    input_style = {
        "bg": input_bg,
        "border": f"1px solid {input_border}",
        "color": text_color,
        "size": "2",
        "radius": "large",
        "_placeholder": {"color": placeholder_color},
    }

    confirmar_field = (
        rx.vstack(
            label_requerido("Confirmar Contraseña"),
            rx.input(
                placeholder="Confirmar Contraseña",
                type=rx.cond(State.show_password, "text", "password"),
                value=State.confirmar_contraseña,
                on_change=State.set_confirmar_contraseña,
                width="100%",
                **input_style,
            ),
        )
        if show_confirm
        else rx.box(display="none")
    )

    return rx.box(
        rx.form(
            rx.vstack(
                rx.hstack(
                    rx.heading("CO.", size="6", color=rx.color_mode_cond(light="#1e3a8a", dark="#93c5fd"), font_weight="black"),
                  
                    justify="between",
                    width="100%",
                ),
                rx.heading(title, size="7", color=text_color, font_weight="bold", margin_bottom="0.4em"),
                rx.text(
                    "Completa tus datos para activar tu cuenta y gestionar tus solicitudes.",
                    color=rx.color_mode_cond(light="#475569", dark="#94a3b8"),
                    font_size="sm",
                    width="100%",
                ),
                
                rx.hstack(
                    rx.button("1. Cuenta", type="button", size="2", variant=rx.cond(State.registro_seccion_abierta == "cuenta", "solid", "soft"), color_scheme="blue", on_click=State.set_registro_seccion_abierta("cuenta")),
                    rx.button("2. Identidad", type="button", size="2", variant=rx.cond(State.registro_seccion_abierta == "identidad", "solid", "soft"), color_scheme="blue", on_click=State.set_registro_seccion_abierta("identidad"), is_disabled=State.registro_paso_habilitado < 2),
                    rx.button("3. Ubicación", type="button", size="2", variant=rx.cond(State.registro_seccion_abierta == "ubicacion", "solid", "soft"), color_scheme="blue", on_click=State.set_registro_seccion_abierta("ubicacion"), is_disabled=State.registro_paso_habilitado < 3),
                    width="100%",
                    spacing="2",
                    flex_wrap="wrap",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Progreso del registro", font_size="xs", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                        rx.spacer(),
                        rx.text(
                            rx.cond(
                                State.registro_seccion_abierta == "cuenta",
                                "33%",
                                rx.cond(
                                    State.registro_seccion_abierta == "identidad",
                                    "66%",
                                    "100%",
                                ),
                            ),
                            font_size="xs",
                            font_weight="semibold",
                            color=rx.color_mode_cond(light="#1d4ed8", dark="#93c5fd"),
                        ),
                        width="100%",
                    ),
                    rx.box(
                        rx.box(
                            height="100%",
                            width=rx.cond(
                                State.registro_seccion_abierta == "cuenta",
                                "33%",
                                rx.cond(
                                    State.registro_seccion_abierta == "identidad",
                                    "66%",
                                    "100%",
                                ),
                            ),
                            bg="linear-gradient(90deg, #2563eb 0%, #0ea5e9 100%)",
                            border_radius="full",
                            transition="width 0.25s ease",
                        ),
                        width="100%",
                        height="8px",
                        border_radius="full",
                        bg=rx.color_mode_cond(light="#dbeafe", dark="rgba(30, 64, 175, 0.28)"),
                        overflow="hidden",
                    ),
                    spacing="1",
                    width="100%",
                ),

                rx.cond(
                    State.registro_seccion_abierta == "cuenta",
                    rx.vstack(
                        rx.vstack(
                            label_requerido("Correo electrónico"),
                            rx.hstack(
                                rx.input(
                                    placeholder="usuario@ejemplo.com",
                                    type="email",
                                    value=State.correo,
                                    on_change=State.set_and_validate_correo,
                                    on_blur=State.validar_correo_accion,
                                    width="100%",
                                    **input_style,
                                ),
                                rx.cond(State.correo_validado, rx.icon("circle-check", color="#10b981", size=20, ml="2"), rx.box()),
                                width="100%",
                            ),
                            rx.cond(State.correo_confirmacion_visible, rx.text(State.correo_confirmacion_mensaje, color=rx.cond(State.correo_validado, "green.500", "red.500"), font_size="sm", mt="1"), rx.box()),
                            width="100%",
                        ),
                        rx.vstack(
                            label_requerido("Contraseña"),
                            rx.hstack(
                                rx.input(
                                    placeholder="�?��?��?��?��?��?��?��?�",
                                    type=rx.cond(State.show_password, "text", "password"),
                                    value=State.contraseña,
                                    on_change=State.set_contraseña,
                                    width="100%",
                                    **input_style,
                                ),
                                rx.button(rx.cond(State.show_password, rx.icon("eye-off", size=18), rx.icon("eye", size=18)), on_click=State.toggle_show_password, variant="soft", size="3", radius="large"),
                                width="100%",
                                spacing="2",
                            ),
                            rx.text("Mínimo 8 caracteres, mayúscula, número y símbolo.", font_size="xs", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                            password_strength_label(State.contraseña),
                            width="100%",
                        ),
                        confirmar_field,
                        rx.hstack(
                            rx.spacer(),
                            rx.button("Continuar", type="button", size="3", color_scheme="blue", on_click=State.continuar_a_identidad),
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                        animation="fadeInUp 0.28s ease",
                        style={
                            "@keyframes fadeInUp": {
                                "0%": {"opacity": "0", "transform": "translateY(8px)"},
                                "100%": {"opacity": "1", "transform": "translateY(0px)"},
                            }
                        },
                    ),
                    rx.box(),
                ),

                rx.cond(
                    State.registro_seccion_abierta == "identidad",
                    rx.vstack(
                        rx.grid(
                            rx.vstack(
                                label_requerido("Nombres"),
                                rx.hstack(
                                    rx.input(placeholder="Tus nombres", value=State.nombres, on_change=State.set_and_validate_nombres, width="100%", **input_style),
                                    rx.cond(State.nombres_valid, rx.icon("circle-check", color="#10b981", size=18, ml="2"), rx.box()),
                                    width="100%",
                                ),
                                width="100%",
                            ),
                            rx.vstack(
                                label_requerido("Apellidos"),
                                rx.hstack(
                                    rx.input(placeholder="Tus apellidos", value=State.apellidos, on_change=State.set_and_validate_apellidos, width="100%", **input_style),
                                    rx.cond(State.apellidos_valid, rx.icon("circle-check", color="#10b981", size=18, ml="2"), rx.box()),
                                    width="100%",
                                ),
                                width="100%",
                            ),
                            template_columns={"base": "1fr", "md": "1fr 1fr"},
                            gap="3",
                            width="100%",
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text("Sexo", color=text_color, font_weight="medium", font_size="sm"),
                                rx.select(["Femenino", "Masculino", "Prefiero no decirlo"], placeholder="Selecciona", value=State.sexo, on_change=State.set_sexo, **input_style),
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("Tipo de ID", font_weight="medium", font_size="sm", color=text_color),
                                rx.select(["Cédula", "Pasaporte", "Tarjeta de Identidad"], placeholder="Selecciona", value=State.tipo_identificacion, on_change=State.set_tipo_identificacion, **input_style),
                                width="100%",
                            ),
                            rx.vstack(
                                label_requerido("Número de ID"),
                                rx.hstack(
                                    rx.input(placeholder="123456789", value=State.numero_identificacion, on_change=State.set_and_validate_numero_identificacion, width="100%", **input_style),
                                    rx.cond(State.numero_identificacion_valid, rx.icon("circle-check", color="#10b981", size=20, ml="2"), rx.box()),
                                ),
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("Teléfono", color=text_color, font_weight="medium", font_size="sm"),
                                rx.hstack(
                                    rx.input(placeholder="Tu teléfono", value=State.telefono, on_change=State.set_and_validate_telefono, width="100%", **input_style),
                                    rx.cond(State.telefono_valid, rx.icon("circle-check", color="#10b981", size=20, ml="2"), rx.box()),
                                ),
                                width="100%",
                            ),
                            template_columns={"base": "1fr", "md": "1fr 1fr"},
                            gap="3",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.button("Atrás", type="button", size="3", variant="soft", on_click=State.set_registro_seccion_abierta("cuenta")),
                            rx.spacer(),
                            rx.button("Continuar", type="button", size="3", color_scheme="blue", on_click=State.continuar_a_ubicacion),
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                        animation="fadeInUp 0.28s ease",
                        style={
                            "@keyframes fadeInUp": {
                                "0%": {"opacity": "0", "transform": "translateY(8px)"},
                                "100%": {"opacity": "1", "transform": "translateY(0px)"},
                            }
                        },
                    ),
                    rx.box(),
                ),

                rx.cond(
                    State.registro_seccion_abierta == "ubicacion",
                    rx.vstack(
                        rx.grid(
                            rx.vstack(
                                rx.text("Departamento", color=text_color, font_weight="medium", font_size="sm"),
                                rx.select(
                                    [
                                        "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba",
                                        "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo", "Quindío", "Risaralda",
                                        "Santander", "Sucre", "Tolima", "Valle del Cauca", "Vaupés", "Vichada",
                                    ],
                                    placeholder="Selecciona",
                                    value=State.departamento,
                                    on_change=State.set_and_validate_departamento,
                                    **input_style,
                                ),
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("Ciudad", color=text_color, font_weight="medium", font_size="sm"),
                                rx.select(State.ciudades_disponibles, placeholder="Selecciona", value=State.ciudad, on_change=State.set_and_validate_ciudad, is_disabled=State.departamento == "", **input_style),
                                width="100%",
                            ),
                            template_columns={"base": "1fr", "md": "1fr 1fr"},
                            gap="3",
                            width="100%",
                        ),
                        rx.vstack(
                            label_requerido("Dirección"),
                            rx.input(placeholder="Tu dirección", value=State.direccion, on_change=State.set_direccion, width="100%", **input_style),
                            width="100%",
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text("Etnia", color=text_color, font_weight="medium", font_size="sm"),
                                rx.select(["Ninguna", "Indígena", "Afrocolombiano", "Raizal", "Palenquero", "Gitano/a", "Otro"], placeholder="Selecciona", value=State.etnia, on_change=State.set_etnia, **input_style),
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("Características especiales", color=text_color, font_weight="medium", font_size="sm"),
                                rx.select(
                                    ["Ninguna", "Habitante de la calle", "No brinda información", "Peligro Inminente", "Periodistas en ejercicio de su actividad", "Primera Infancia", "Veteranos Fuerza Pública", "Víctimas - Conflicto Armado"],
                                    placeholder="Selecciona",
                                    value=State.persona_vulnerable_registro,
                                    on_change=State.set_persona_vulnerable_registro,
                                    **input_style,
                                ),
                                width="100%",
                            ),
                            template_columns={"base": "1fr", "md": "1fr 1fr"},
                            gap="3",
                            width="100%",
                        ),
                        rx.divider(margin_y="2", bg=input_border),
                        rx.vstack(
                            rx.checkbox("Acepto recibir notificaciones por correo", is_checked=State.acepta_notificaciones, on_change=State.set_acepta_notificaciones, color=text_color, size="3"),
                            rx.checkbox(
                                rx.hstack(
                                    rx.link("He leído y acepto la Política de Protección de Datos", href="/politica-privacidad", color="#3b82f6", font_weight="medium"),
                                    rx.text("(Aviso obligatorio)", color=rx.color_mode_cond(light="#94a3b8", dark="#64748b"), font_size="sm"),
                                ),
                                is_checked=State.acepta_politica_datos,
                                on_change=State.preconfirmar_politica,
                                color=text_color,
                                size="3",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.button("Atrás", type="button", size="3", variant="soft", on_click=State.set_registro_seccion_abierta("identidad")),
                            rx.spacer(),
                            rx.text("�?ltimo paso", font_size="xs", color=rx.color_mode_cond(light="#64748b", dark="#94a3b8")),
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                        animation="fadeInUp 0.28s ease",
                        style={
                            "@keyframes fadeInUp": {
                                "0%": {"opacity": "0", "transform": "translateY(8px)"},
                                "100%": {"opacity": "1", "transform": "translateY(0px)"},
                            }
                        },
                    ),
                    rx.box(),
                ),
                
                rx.cond(
                    State.modal_politica_visible,
                    rx.box(
                        rx.box(
                            rx.box(
                                position="absolute",
                                top="-60px",
                                right="-40px",
                                width="180px",
                                height="180px",
                                bg="rgba(59, 130, 246, 0.35)",
                                border_radius="full",
                                filter="blur(50px)",
                            ),
                            rx.box(
                                position="absolute",
                                bottom="-40px",
                                left="-30px",
                                width="140px",
                                height="140px",
                                bg="rgba(14, 165, 233, 0.25)",
                                border_radius="full",
                                filter="blur(45px)",
                            ),
                            rx.vstack(
                                rx.center(
                                    rx.box(
                                        rx.icon("shield-check", size=32, color="#60a5fa"),
                                        p="4",
                                        bg=rx.color_mode_cond(
                                            light="linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
                                            dark="linear-gradient(135deg, rgba(37, 99, 235, 0.25) 0%, rgba(14, 165, 233, 0.15) 100%)",
                                        ),
                                        border=rx.color_mode_cond(
                                            light="1px solid #93c5fd",
                                            dark="1px solid rgba(96, 165, 250, 0.35)",
                                        ),
                                        border_radius="2xl",
                                        box_shadow=rx.color_mode_cond(
                                            light="0 12px 28px -8px rgba(37, 99, 235, 0.35)",
                                            dark="0 12px 28px -8px rgba(2, 6, 23, 0.8)",
                                        ),
                                    ),
                                    width="100%",
                                ),
                                rx.badge(
                                    "Ley 1581 de 2012",
                                    color_scheme="blue",
                                    variant="soft",
                                    radius="full",
                                    size="1",
                                ),
                                rx.heading(
                                    "Política de Privacidad",
                                    size="6",
                                    color=rx.color_mode_cond(light="#0f172a", dark="#f8fafc"),
                                    font_weight="bold",
                                    text_align="center",
                                    letter_spacing="-0.02em",
                                ),
                                rx.text(
                                    "Al aceptar, confirmas que has leído y comprendido cómo tratamos tus datos personales para la gestión de PQRS.",
                                    color=rx.color_mode_cond(light="#475569", dark="#94a3b8"),
                                    font_size="sm",
                                    line_height="1.6",
                                    text_align="center",
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("lock", size=16, color="#38bdf8"),
                                            rx.text(
                                                "Tus datos se usan solo para trámites y notificaciones.",
                                                font_size="xs",
                                                color=rx.color_mode_cond(light="#334155", dark="#cbd5e1"),
                                            ),
                                            spacing="2",
                                            align_items="center",
                                        ),
                                        rx.hstack(
                                            rx.icon("file-text", size=16, color="#38bdf8"),
                                            rx.link(
                                                "Leer política completa",
                                                href="/politica-privacidad",
                                                font_size="xs",
                                                font_weight="semibold",
                                                color=rx.color_mode_cond(light="#2563eb", dark="#93c5fd"),
                                                _hover={"text_decoration": "underline"},
                                            ),
                                            spacing="2",
                                            align_items="center",
                                        ),
                                        spacing="2",
                                        align_items="start",
                                        width="100%",
                                    ),
                                    width="100%",
                                    p="4",
                                    border_radius="xl",
                                    bg=rx.color_mode_cond(
                                        light="rgba(239, 246, 255, 0.85)",
                                        dark="rgba(15, 23, 42, 0.55)",
                                    ),
                                    border=rx.color_mode_cond(
                                        light="1px solid #bfdbfe",
                                        dark="1px solid rgba(51, 65, 85, 0.8)",
                                    ),
                                ),
                                rx.vstack(
                                    rx.button(
                                        rx.hstack(
                                            rx.icon("check", size=18),
                                            rx.text("Acepto y continúo", font_weight="bold"),
                                            spacing="2",
                                            justify="center",
                                        ),
                                        on_click=State.confirmar_politica,
                                        color_scheme="blue",
                                        size="3",
                                        width="100%",
                                        radius="full",
                                        box_shadow="0 10px 24px -10px rgba(37, 99, 235, 0.65)",
                                    ),
                                    rx.button(
                                        "Cancelar",
                                        on_click=State.cancelar_politica,
                                        variant="ghost",
                                        size="3",
                                        width="100%",
                                        color=rx.color_mode_cond(light="#64748b", dark="#94a3b8"),
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="4",
                                align_items="center",
                                width="100%",
                                z_index="1",
                            ),
                            position="relative",
                            overflow="hidden",
                            p={"base": "6", "md": "8"},
                            bg=rx.color_mode_cond(
                                light="rgba(255, 255, 255, 0.92)",
                                dark="rgba(15, 23, 42, 0.88)",
                            ),
                            backdrop_filter="blur(24px)",
                            border=rx.color_mode_cond(
                                light="1px solid rgba(147, 197, 253, 0.9)",
                                dark="1px solid rgba(96, 165, 250, 0.28)",
                            ),
                            border_radius="3xl",
                            box_shadow=rx.color_mode_cond(
                                light="0 32px 64px -20px rgba(30, 64, 175, 0.45), 0 0 0 1px rgba(255,255,255,0.5) inset",
                                dark="0 32px 64px -16px rgba(2, 6, 23, 0.95), 0 0 0 1px rgba(255,255,255,0.06) inset",
                            ),
                            width="100%",
                            max_width="480px",
                            animation="modalPop 0.32s cubic-bezier(0.22, 1, 0.36, 1)",
                            style={
                                "@keyframes modalPop": {
                                    "0%": {"opacity": "0", "transform": "scale(0.94) translateY(12px)"},
                                    "100%": {"opacity": "1", "transform": "scale(1) translateY(0px)"},
                                }
                            },
                        ),
                        position="fixed",
                        inset="0",
                        bg="rgba(2, 6, 23, 0.72)",
                        backdrop_filter="blur(10px)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        z_index="1000",
                        p="6",
                    ),
                ),
                
                rx.cond(
                    State.error_de_registro != "",
                    rx.box(
                        rx.text(State.error_de_registro, color="#ef4444", font_size="sm", font_weight="medium"),
                        p="3", bg=rx.color_mode_cond(light="#fef2f2", dark="rgba(239, 68, 68, 0.1)"),
                        border_radius="lg",
                        width="100%",
                        animation="flashMessage 5s ease forwards",
                        style={
                            "@keyframes flashMessage": {
                                "0%": {"opacity": "0", "transform": "translateY(-4px)"},
                                "10%": {"opacity": "1", "transform": "translateY(0px)"},
                                "80%": {"opacity": "1", "transform": "translateY(0px)"},
                                "100%": {"opacity": "0", "transform": "translateY(-4px)"},
                            }
                        },
                    ),
                    rx.box(),
                ),
                rx.cond(
                    State.succes != "",
                    rx.box(
                        rx.text(State.succes, color="#10b981", font_size="sm", font_weight="medium"),
                        p="3", bg=rx.color_mode_cond(light="#ecfdf5", dark="rgba(16, 185, 129, 0.1)"),
                        border_radius="lg",
                        width="100%",
                        animation="flashMessage 5s ease forwards",
                        style={
                            "@keyframes flashMessage": {
                                "0%": {"opacity": "0", "transform": "translateY(-4px)"},
                                "10%": {"opacity": "1", "transform": "translateY(0px)"},
                                "80%": {"opacity": "1", "transform": "translateY(0px)"},
                                "100%": {"opacity": "0", "transform": "translateY(-4px)"},
                            }
                        },
                    ),
                    rx.box(),
                ),
                
                rx.hstack(
                    rx.button(
                        "Crear cuenta",
                        type="submit",
                        color_scheme="blue",
                        size="4",
                        radius="large",
                        width={"base": "100%", "md": "300px"},
                        box_shadow="0 8px 20px -8px rgba(37, 99, 235, 0.55)",
                        is_disabled=(State.registro_paso_habilitado < 3) | (State.registro_seccion_abierta != "ubicacion"),
                    ),
                    rx.link("¿Ya tienes una cuenta? Inicia sesión", href="/login", margin_left={"base": "0", "md": "4"}, color="#3b82f6", font_weight="medium"),
                    spacing="6",
                    justify={"base": "center", "md": "start"},
                    width="100%",
                    margin_top="4"
                ),
                
                spacing="4",
                width="100%",
            ),
            on_submit=on_submit,
            width="100%",
        ),
        p={"base": "6", "md": "8"},
        max_width="1100px",
        width="100%",
        bg=rx.color_mode_cond(light="linear-gradient(145deg, #dbeafe 0%, #bfdbfe 100%)", dark="linear-gradient(145deg, #0f172a 0%, #1e3a8a 100%)"),
        border=rx.color_mode_cond(light="1px solid #93c5fd", dark="1px solid #1e40af"),
        border_radius="2xl",
        box_shadow=rx.color_mode_cond(light="0 30px 60px -25px rgba(30, 64, 175, 0.35)", dark="0 30px 60px -25px rgba(2, 6, 23, 0.85)"),
        z_index="1",
        position="relative",
        overflow="hidden",
        style={"borderLeft": "8px solid #2563eb"},
        max_height={"base": "none", "lg": "84vh"},
        overflow_y={"base": "visible", "lg": "auto"},
    )




def change_password_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.heading("Cambiar Contraseña", size={"base": "5", "md": "7"}, color=rx.color_mode_cond(light="black", dark="white")),
                    rx.input(placeholder="Contraseña actual", type="password", value=State.current_password, on_change=State.set_current_password, width="100%"),
                    rx.input(placeholder="Nueva contraseña", type="password", value=State.new_password, on_change=State.set_new_password, width="100%"),
                    rx.input(placeholder="Confirmar nueva contraseña", type="password", value=State.confirm_new_password, on_change=State.set_confirm_new_password, width="100%"),
                    rx.button("Cambiar contraseña", on_click=State.change_password, color_scheme="blue", width="100%"),
                    rx.text(State.change_pw_message, color="green.500", font_size="sm")
                ),
                p={"base": "4", "md": "8"},
                max_width={"base": "90%", "md": "560px"},
                width="100%",
            ),
            size="3"
        ),
        bg=rx.color_mode_cond(light="#f8fafc", dark="#0f172a")
    )

def login_page() -> rx.Component:
    """Login split-screen: izquierda blanca con form, derecha azul con ilustracion.
    Bindings: State.correo, State.contrasena, State.show_password, State.login
    """
    text_main = rx.color_mode_cond(light="#111827", dark="#f1f5f9")
    text_sub  = rx.color_mode_cond(light="#6b7280", dark="#94a3b8")
    panel_bg  = rx.color_mode_cond(light="#ffffff", dark="#0f172a")
    input_bdr = rx.color_mode_cond(light="#e5e7eb", dark="#334155")
    divider_c = rx.color_mode_cond(light="#e5e7eb", dark="#334155")
    root_bg   = rx.color_mode_cond(light="#e8edf2", dark="#0b1120")

    return rx.box(
        toast_notification(),
        rx.toast.provider(position="top-center", close_button=True, offset="20px"),
        rx.center(
            rx.flex(
                # ── Panel izquierdo: formulario ─────────────────────────
                rx.box(
                    rx.vstack(
                        # Logo + marca
                        rx.hstack(
                            rx.box(
                                rx.icon("shield-check", size=18, color="#1d4ed8"),
                                width="36px", height="36px", border_radius="8px",
                                bg="#dbeafe", display="flex",
                                align_items="center", justify_content="center",
                            ),
                            rx.text("Sistema PQRS", font_size="15px",
                                    font_weight="800", color=text_main,
                                    letter_spacing="-0.01em"),
                            spacing="2", align_items="center",
                        ),
                        # Heading
                        rx.vstack(
                            rx.heading("Bienvenido de vuelta", size="7",
                                       color=text_main, font_weight="800",
                                       text_align="center", letter_spacing="-0.02em"),
                            rx.text("Ingresa tus credenciales para continuar.",
                                    font_size="13px", color=text_sub, text_align="center"),
                            spacing="1", width="100%",
                        ),
                        # Tab Sign In / Registro - segmented control simetrico
                        rx.box(
                            rx.button(
                                "Iniciar sesión",
                                size="2", radius="full",
                                color_scheme="blue", variant="solid",
                                width="50%", height="36px",
                                style={"font_size": "13px", "font_weight": "600"},
                            ),
                            rx.link(
                                "Registrarse",
                                href="/registro",
                                display="flex",
                                align_items="center",
                                justify_content="center",
                                width="50%",
                                height="36px",
                                font_size="13px",
                                font_weight="500",
                                color=text_sub,
                                text_decoration="none",
                                border_radius="full",
                                _hover={"color": "#2563eb", "bg": "rgba(37,99,235,0.06)"},
                            ),
                            display="flex",
                            align_items="center",
                            width="100%",
                            p="1",
                            border_radius="full",
                            bg=rx.color_mode_cond(light="#f3f4f6", dark="#1e293b"),
                        ),
                        # Formulario
                        rx.form(
                            rx.vstack(
                                # Email input con icono
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon("mail", size=15, color="#9ca3af"),
                                            padding_left="14px", padding_right="10px",
                                            border_right="1px solid",
                                            border_color=input_bdr,
                                            display="flex", align_items="center", height="100%",
                                        ),
                                        rx.input(
                                            placeholder="Correo electrónico",
                                            name="correo",
                                            type="email",
                                            value=State.correo,
                                            on_change=State.set_correo,
                                            width="100%",
                                            size="2",
                                            variant="soft",
                                            font_size="13px",
                                        ),
                                        rx.cond(
                                            State.correo != "",
                                            rx.box(
                                                rx.icon("circle-check", size=16, color="#10b981"),
                                                padding_right="14px",
                                                display="flex", align_items="center",
                                            ),
                                            rx.box(width="14px"),
                                        ),
                                        width="100%", height="46px", spacing="0",
                                        align_items="center",
                                    ),
                                    width="100%",
                                    border="1px solid",
                                    border_color=input_bdr,
                                    border_radius="full",
                                    overflow="hidden",
                                    bg=rx.color_mode_cond(light="#ffffff", dark="#1e293b"),
                                ),
                                # Password input con icono
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon("lock", size=15, color="#9ca3af"),
                                            padding_left="14px", padding_right="10px",
                                            border_right="1px solid",
                                            border_color=input_bdr,
                                            display="flex", align_items="center", height="100%",
                                        ),
                                        rx.input(
                                            placeholder="Contraseña",
                                            name="contraseña",
                                            type=rx.cond(State.show_password, "text", "password"),
                                            value=State.contraseña,
                                            on_change=State.set_contraseña,
                                            width="100%",
                                            size="2",
                                            variant="soft",
                                            font_size="13px",
                                        ),
                                        rx.box(
                                            rx.icon(
                                                rx.cond(State.show_password, "eye-off", "eye"),
                                                size=15, color="#9ca3af",
                                            ),
                                            padding_right="14px",
                                            display="flex", align_items="center",
                                            cursor="pointer",
                                            on_click=State.toggle_show_password,
                                        ),
                                        width="100%", height="46px", spacing="0",
                                        align_items="center",
                                    ),
                                    width="100%",
                                    border="1px solid",
                                    border_color=input_bdr,
                                    border_radius="full",
                                    overflow="hidden",
                                    bg=rx.color_mode_cond(light="#ffffff", dark="#1e293b"),
                                ),
                                # Error mensaje
                                rx.cond(
                                    State.error_de_contraseña != "",
                                    rx.hstack(
                                        rx.icon("circle-x", size=13, color="#ef4444"),
                                        rx.text(State.error_de_contraseña,
                                                color="#ef4444", font_size="12px"),
                                        spacing="2", align_items="center",
                                    ),
                                    rx.box(),
                                ),
                                # Boton continuar
                                rx.button(
                                    "Continuar",
                                    type="submit",
                                    width="100%", size="3", radius="full",
                                    color_scheme="blue",
                                    style={"font_weight": "700", "font_size": "14px"},
                                ),
                                spacing="3", width="100%",
                            ),
                            on_submit=State.login,
                            width="100%",
                        ),
                        # Divider
                        rx.hstack(
                            rx.box(flex="1", height="1px", bg=divider_c),
                            rx.text("o", color=text_sub, font_size="12px"),
                            rx.box(flex="1", height="1px", bg=divider_c),
                            width="100%", align_items="center", spacing="3",
                        ),
                        # Volver al inicio
                        rx.center(
                            rx.link(
                                rx.hstack(
                                    rx.icon("home", size=13),
                                    rx.text("Volver al inicio", font_size="13px", font_weight="500"),
                                    spacing="2", align_items="center",
                                ),
                                href="/",
                                color=text_sub, text_decoration="none",
                                _hover={"color": "#1d4ed8"},
                            ),
                            width="100%",
                        ),
                        rx.spacer(),
                        # Footer legal
                        rx.text(
                            "Plataforma para la gestión de PQRS institucionales. "
                            "Accede de forma segura, consulta el estado de tus solicitudes "
                            "y recibe notificaciones en tiempo real.",
                            font_size="11px", color=text_sub,
                            text_align="center", line_height="1.55",
                        ),
                        spacing="5", width="100%", align_items="stretch",
                        height="100%",
                    ),
                    bg=panel_bg,
                    p={"base": "8", "md": "10"},
                    flex="1",
                    display="flex",
                    flex_direction="column",
                    align_self="stretch",
                    border_radius={"base": "20px", "lg": "20px 0 0 20px"},
                ),
                # ── Panel derecho: fondo azul + ilustracion ─────────────
                rx.box(
                    rx.vstack(
                        rx.spacer(),
                        rx.image(
                            src="/pqrs.png",
                            alt="PQRS ilustracion",
                            max_width="320px",
                            width="80%",
                            object_fit="contain",
                            filter="drop-shadow(0 24px 40px rgba(0,0,0,0.25))",
                        ),
                        rx.spacer(),
                        width="100%", align_items="center", height="100%",
                    ),
                    flex="1",
                    bg=rx.color_mode_cond(
                        light="linear-gradient(160deg, #bfdbfe 0%, #93c5fd 40%, #3b82f6 80%, #1d4ed8 100%)",
                        dark="linear-gradient(160deg, #1e3a8a 0%, #1d4ed8 60%, #2563eb 100%)",
                    ),
                    border_radius={"base": "0 0 20px 20px", "lg": "0 20px 20px 0"},
                    min_height={"base": "260px", "lg": "0"},
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    align_self="stretch",
                    overflow="hidden",
                ),
                direction={"base": "column", "lg": "row"},
                align_items="stretch",
                width="100%",
                max_width={"base": "95%", "sm": "480px", "lg": "900px"},
                border_radius="20px",
                overflow="hidden",
                box_shadow=rx.color_mode_cond(
                    light="0 20px 60px -10px rgba(30,64,175,0.18), 0 4px 16px -4px rgba(0,0,0,0.08)",
                    dark="0 20px 60px -10px rgba(0,0,0,0.6)",
                ),
            ),
            width="100%",
            min_height="100vh",
            px={"base": "4", "md": "6"},
        ),
        bg=root_bg,
        width="100%",
        min_height="100vh",
    )
