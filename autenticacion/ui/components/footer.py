from ...state import State
import reflex as rx

def mantenimiento_modal() -> rx.Component:
    card_bg = rx.color_mode_cond(light="white", dark="#111827")
    border = rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155")
    text_main = rx.color_mode_cond(light="#0f172a", dark="#f8fafc")
    text_sec = rx.color_mode_cond(light="#475569", dark="#cbd5e1")
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon("x", size=18),
                            size="1",
                            variant="ghost",
                            color_scheme="gray",
                            cursor="pointer",
                        )
                    ),
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.box(
                            rx.icon("construction", size=48, color="#e85d04"),
                            bg="rgba(232, 93, 4, 0.1)",
                            padding="16px",
                            border_radius="full",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),
                        rx.heading("Enlace en Mantenimiento", size="5", color=text_main, font_weight="700"),
                        rx.text(
                            "Estamos mejorando este servicio para brindarte una mejor experiencia. Vuelve a intentarlo más tarde.",
                            font_size="13px",
                            color=text_sec,
                            text_align="center",
                        ),
                        rx.hstack(
                            rx.icon("clock", size=16, color="#e85d04"),
                            rx.text("Tiempo estimado de restauración: 24 horas", font_size="12px", color=text_sec, font_weight="500"),
                            bg=rx.color_mode_cond(light="#fff7ed", dark="rgba(232, 93, 4, 0.05)"),
                            border="1px solid rgba(232, 93, 4, 0.2)",
                            border_radius="8px",
                            padding_x="3",
                            padding_y="2",
                            width="100%",
                            justify_content="center",
                            margin_top="2",
                        ),
                        spacing="3",
                        align_items="center",
                    ),
                    width="100%",
                ),
                spacing="4",
                align_items="stretch",
            ),
            style={
                "max_width": "420px",
                "padding": "24px",
                "border_radius": "20px",
                "background_color": card_bg,
                "border": border,
                "box_shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
            }
        ),
        open=State.mantenimiento_modal_abierto,
        on_open_change=State.set_mantenimiento_modal_abierto,
    )


def footer() -> rx.Component:
    header_color = rx.color_mode_cond(light="black", dark="white")
    text_color = rx.color_mode_cond(light="gray.700", dark="gray.400")
    link_color = rx.color_mode_cond(light="blue.600", dark="blue.300")
    bg_footer = rx.color_mode_cond(light="#f7fafc", dark="#111827")
    border_color = rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #2d3748")

    return rx.box(
        rx.container(
        rx.hstack(
            # Columna 1: Información de la Entidad
            rx.vstack(
                rx.heading("Información de la Entidad", size="6", color=header_color),
                rx.text("Sede Principal: Calle 10 # 5-20, Buenaventura, Valle del Cauca", color=text_color),
                rx.text("Código Postal: 760001", color=text_color),
                rx.text("PBX: (+57) 602 XXX XXXX", color=text_color),
                rx.link(
                    "Correo institucional: atencionalciudadano@empresa.gov.co", 
                    href="mailto:atencionalciudadano@empresa.gov.co",
                    color=link_color
                ),
                rx.link(
                    "Ley 1755 de 2015", 
                    href="https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=65334", 
                    target="_blank",
                    color=link_color
                ),
                rx.text(
                    "Horario de atención presencial: Lunes a Viernes, 7:30 a.m. - 12:00 p.m. y 2:00 p.m. - 5:30 p.m.",
                    color=text_color
                ),
                align_items="start",
            ),
            # Columna 2: Servicio al Ciudadano
            rx.vstack(
                rx.heading("Servicio al Ciudadano", size="6", color=header_color),
                rx.link("Radicar solicitud PQRS", href="/solicitudes", color=link_color),
                rx.link("Consultar estado de solicitud", href="/consultar-estado", color=link_color),
                rx.link("Preguntas Frecuentes (FAQ)", href="#", on_click=State.abrir_mantenimiento, color=link_color),
                rx.link("Tiempos de respuesta (Ley 1755 de 2015)", href="#", on_click=State.abrir_mantenimiento, color=link_color),
                rx.link("Notificaciones por aviso y judiciales", href="#", on_click=State.abrir_mantenimiento, color=link_color),
                rx.link("Política de privacidad y protección de datos", href="/politica-privacidad", color=link_color),
                rx.link("Manual de usuario (Enlace 1755)", href="#", on_click=State.abrir_mantenimiento, color=link_color),
                align_items="start",
            ),
            # Columna 3: Contacto Directo y Redes
            rx.vstack(
                rx.heading("Contacto Directo y Redes", size="6", color=header_color),
                rx.text("Recepción de correspondencia física: Lunes a viernes, 8:00 a.m. a 4:00 p.m.", color=text_color),
                rx.text("Línea gratuita nacional: 01 8000 91XXXX", color=text_color),
                rx.hstack(
                    rx.link("Facebook", href="https://facebook.com", target="_blank", color=link_color),
                    rx.link("X/Twitter", href="https://twitter.com", target="_blank", color=link_color),
                    rx.link("YouTube", href="https://youtube.com", target="_blank", color=link_color),
                    rx.link("LinkedIn", href="https://linkedin.com", target="_blank", color=link_color),
                    spacing="4"
                ),
                rx.text("Sistema gestionado por: Enlace 1755 (Versión 1.0)", font_size="sm", color=text_color),
                align_items="start",
            ),
            spacing="9",
            align_items="start"
        ),
        width="100%",
        padding_top="24px",
        padding_bottom="24px",
        bg=bg_footer,
        border_top=border_color,
        justify="center"
    ),
    mantenimiento_modal(),
    width="100%",
)


