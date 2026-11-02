from ...state import State
import reflex as rx
from ..components.common import pqrs_badge, brand_footer
from ..components.navigation import navbar, utility_bar
from ..components.footer import footer
from ..theme import (
    PAGE_BG, CARD_BG, CARD_BDR, TEXT_MAIN, TEXT_SUB, 
    BLUE_ACC, NAVY, NAVY_DARK, GREEN_OK, RED_ERR, ORANGE, SECT_BG
)

# ── Tarjeta Linear/Stripe Style: Gradiente perimetral, Glow & Tag Técnico ──
def quick_action_card(
    title: str, desc: str, button_text: str, href: str, accent: str = "blue"
) -> rx.Component:
    card_configs = {
        "blue": {
            "color": "#3b82f6",
            "tag": "TRÁMITE OFICIAL",
            "tag_icon": "shield-check",
            "icon": "file-text",
            "gradient_badge": "linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(37,99,235,0.05) 100%)",
        },
        "cyan": {
            "color": "#06b6d4",
            "tag": "TIEMPO REAL",
            "tag_icon": "radio",
            "icon": "search",
            "gradient_badge": "linear-gradient(135deg, rgba(6,182,212,0.2) 0%, rgba(14,116,144,0.05) 100%)",
        },
        "green": {
            "color": "#10b981",
            "tag": "EXPEDIENTE CIUDADANO",
            "tag_icon": "fingerprint",
            "icon": "user-check",
            "gradient_badge": "linear-gradient(135deg, rgba(16,185,129,0.2) 0%, rgba(5,150,105,0.05) 100%)",
        },
        "gray": {
            "color": "#8b5cf6",
            "tag": "PORTAL SEGURO",
            "tag_icon": "key-round",
            "icon": "log-in",
            "gradient_badge": "linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(109,40,217,0.05) 100%)",
        },
    }
    cfg = card_configs.get(accent, card_configs["blue"])
    theme_color = cfg["color"]

    return rx.link(
        rx.box(
            # Top Ambient Glow / Luz ambiental superior
            rx.box(
                position="absolute",
                top="-50px",
                right="-30px",
                width="140px",
                height="140px",
                border_radius="full",
                bg=theme_color,
                filter="blur(55px)",
                opacity="0.16",
                pointer_events="none",
                z_index="0",
            ),
            rx.vstack(
                # Fila 1: Icono de alta tecnología + Micro Tag Institucional
                rx.hstack(
                    rx.box(
                        rx.icon(cfg["icon"], size=22, color=theme_color),
                        width="40px",
                        height="40px",
                        border_radius="14px",
                        bg=cfg["gradient_badge"],
                        border=f"1px solid {theme_color}35",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        box_shadow=f"0 6px 18px -4px {theme_color}30",
                    ),
                    rx.spacer(),
                    # Micro Tag estilo Raycast/Linear
                    rx.hstack(
                        rx.icon(cfg["tag_icon"], size=12, color=theme_color),
                        rx.text(
                            cfg["tag"],
                            font_size="10px",
                            font_weight="800",
                            color=theme_color,
                            letter_spacing="0.08em",
                        ),
                        spacing="1",
                        align_items="center",
                        px="2.5",
                        py="1",
                        border_radius="full",
                        bg=rx.color_mode_cond(light=f"{theme_color}10", dark=f"{theme_color}15"),
                        border=f"1px solid {theme_color}30",
                    ),
                    width="100%",
                    align_items="center",
                    z_index="1",
                ),

                # Fila 2: Título y descripción con tipografía premium
                rx.vstack(
                    rx.text(
                        title,
                        font_size="17px",
                        font_weight="800",
                        color=TEXT_MAIN,
                        letter_spacing="-0.025em",
                    ),
                    rx.text(
                        desc,
                        font_size="13px",
                        color=TEXT_SUB,
                        line_height="1.6",
                    ),
                    spacing="2",
                    align_items="start",
                    width="100%",
                    z_index="1",
                ),

                rx.spacer(),

                # Fila 3: Separador y botón de acción integrado
                rx.box(
                    rx.hstack(
                        rx.text(
                            button_text,
                            font_size="13px",
                            font_weight="700",
                            color=TEXT_MAIN,
                        ),
                        rx.spacer(),
                        rx.box(
                            rx.icon("arrow-right", size=14, color="white"),
                            width="28px",
                            height="28px",
                            border_radius="full",
                            bg=f"linear-gradient(135deg, {theme_color} 0%, {theme_color}cc 100%)",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow=f"0 4px 12px -2px {theme_color}60",
                            transition="transform 0.25s ease",
                            class_name="action-pill-btn",
                        ),
                        width="100%",
                        align_items="center",
                        pt="3",
                        border_top=rx.color_mode_cond(
                            light="1px solid #f1f5f9",
                            dark="1px solid rgba(255, 255, 255, 0.08)"
                        ),
                    ),
                    width="100%",
                    z_index="1",
                ),

                spacing="4",
                align_items="start",
                height="100%",
                width="100%",
            ),
            p={"base": "5", "md": "6", "xl": "7"},
            min_height="240px",
            height="100%",
            width="100%",
            border_radius="24px",
            bg=rx.color_mode_cond(
                light="rgba(255, 255, 255, 0.98)",
                dark="rgba(15, 23, 42, 0.75)"
            ),
            backdrop_filter="blur(20px)",
            border=rx.color_mode_cond(
                light="1px solid #e2e8f0",
                dark="1px solid rgba(255, 255, 255, 0.12)"
            ),
            position="relative",
            overflow="hidden",
            transition="all 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
            box_shadow=rx.color_mode_cond(
                light="0 8px 24px -4px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.03)",
                dark="0 14px 34px -10px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.10)"
            ),
            _hover={
                "transform": "translateY(-6px)",
                "border_color": f"{theme_color}80",
                "box_shadow": rx.color_mode_cond(
                    light=f"0 20px 35px -8px {theme_color}35",
                    dark=f"0 22px 42px -10px {theme_color}50, inset 0 1px 0 rgba(255,255,255,0.2)"
                ),
            },
        ),
        href=href,
        text_decoration="none",
        width="100%",
        display="block",
    )


# ── Tarjeta Informativa Minimalista ───────────────────────────────────────
def info_card(title: str, desc: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    width="10px",
                    height="10px",
                    border_radius="full",
                    bg=BLUE_ACC,
                    box_shadow=f"0 0 12px {BLUE_ACC}",
                ),
                rx.text(
                    title,
                    font_weight="700",
                    font_size="15px",
                    color=TEXT_MAIN,
                    letter_spacing="-0.01em",
                ),
                spacing="3",
                align_items="center",
            ),
            rx.text(
                desc,
                color=TEXT_SUB,
                font_size="13px",
                line_height="1.6",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        bg=rx.color_mode_cond(light="rgba(255, 255, 255, 0.95)", dark="rgba(30, 41, 59, 0.65)"),
        backdrop_filter="blur(16px)",
        border="1px solid",
        border_color=rx.color_mode_cond(light="#e2e8f0", dark="rgba(255, 255, 255, 0.10)"),
        border_radius="20px",
        p="6",
        width="100%",
        box_shadow=rx.color_mode_cond(
            light="0 4px 16px rgba(0,0,0,0.04)",
            dark="0 8px 24px rgba(0,0,0,0.35)"
        ),
        transition="all 0.25s ease",
        _hover={"transform": "translateY(-3px)", "border_color": BLUE_ACC},
    )


def index() -> rx.Component:
    return rx.box(
        rx.color_mode.button(position="top-right"),
        utility_bar(),
        navbar(),

        # ── HERO SECTION ULTRA PREMIUM ────────────────────────────────────
        rx.box(
            rx.container(
                rx.hstack(
                    # Columna Izquierda: Mensaje institucional y CTAs de impacto
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("sparkles", size=13, color="#60a5fa"),
                                display="flex",
                                align_items="center",
                            ),
                            rx.text(
                                "Plataforma Oficial de Atención Ciudadana",
                                color="#ffffff",
                                font_size="12px",
                                font_weight="600",
                                letter_spacing="0.02em",
                            ),
                            spacing="2",
                            align_items="center",
                            px="3.5",
                            py="1.5",
                            border_radius="full",
                            bg="rgba(255, 255, 255, 0.12)",
                            backdrop_filter="blur(16px)",
                            border="1px solid rgba(255, 255, 255, 0.2)",
                        ),
                        rx.heading(
                            "Atención PQRS",
                            rx.text.span(
                                " • Enlace 1755",
                                color="#93c5fd",
                                font_weight="400",
                            ),
                            size="9",
                            color="#ffffff",
                            line_height="1.08",
                            letter_spacing="-0.03em",
                            font_weight="800",
                        ),
                        rx.text(
                            "Radica, consulta y gestiona tus Peticiones, Quejas, Reclamos y Sugerencias con trazabilidad legal en tiempo real.",
                            color="rgba(255, 255, 255, 0.82)",
                            font_size="16px",
                            max_width="560px",
                            line_height="1.6",
                        ),
                        rx.hstack(
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("send", size=16),
                                        rx.text("Radicar PQRS", font_weight="700"),
                                        spacing="2",
                                        align_items="center",
                                    ),
                                    size="3",
                                    radius="full",
                                    style={
                                        "background": "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
                                        "color": "white",
                                        "padding": "0 26px",
                                        "height": "46px",
                                        "boxShadow": "0 8px 24px -4px rgba(37, 99, 235, 0.65)",
                                        "cursor": "pointer",
                                    },
                                    _hover={"transform": "translateY(-2px)", "boxShadow": "0 12px 28px -4px rgba(37, 99, 235, 0.85)"},
                                    transition="all 0.2s ease",
                                ),
                                href="/solicitudes",
                                text_decoration="none",
                            ),
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("search", size=16),
                                        rx.text("Consultar Estado", font_weight="600"),
                                        spacing="2",
                                        align_items="center",
                                    ),
                                    size="3",
                                    radius="full",
                                    style={
                                        "background": "rgba(255, 255, 255, 0.12)",
                                        "color": "white",
                                        "backdropFilter": "blur(12px)",
                                        "border": "1px solid rgba(255, 255, 255, 0.25)",
                                        "padding": "0 22px",
                                        "height": "46px",
                                        "cursor": "pointer",
                                    },
                                    _hover={"background": "rgba(255, 255, 255, 0.22)", "transform": "translateY(-2px)"},
                                    transition="all 0.2s ease",
                                ),
                                href="/consultar-estado",
                                text_decoration="none",
                            ),
                            spacing="4",
                            pt="2",
                            flex_wrap="wrap",
                        ),
                        spacing="5",
                        align_items="start",
                        width="100%",
                        max_width="620px",
                    ),

                    # Columna Derecha: Card de Accesos Rápidos
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("compass", size=18, color="#60a5fa"),
                                    width="34px",
                                    height="34px",
                                    border_radius="10px",
                                    bg="rgba(37, 99, 235, 0.25)",
                                    border="1px solid rgba(96, 165, 250, 0.3)",
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                ),
                                rx.vstack(
                                    rx.text("Accesos Rápidos", font_size="15px", font_weight="700", color="#ffffff", line_height="1"),
                                    rx.text("Portal de Autogestión", font_size="11px", color="rgba(255,255,255,0.6)", line_height="1"),
                                    spacing="1",
                                    align_items="start",
                                ),
                                width="100%",
                                align_items="center",
                                spacing="3",
                            ),
                            rx.box(width="100%", height="1px", bg="rgba(255,255,255,0.12)", my="1"),

                            rx.link(
                                rx.box(
                                    rx.hstack(
                                        rx.icon("user-plus", size=16, color="#ffffff"),
                                        rx.text("Registrarme", font_size="13px", font_weight="700", color="#ffffff"),
                                        rx.spacer(),
                                        rx.icon("arrow-right", size=14, color="rgba(255,255,255,0.7)"),
                                        width="100%",
                                        align_items="center",
                                    ),
                                    px="4",
                                    height="42px",
                                    border_radius="12px",
                                    bg="linear-gradient(135deg, #2563eb 0%, #1e40af 100%)",
                                    border="1px solid rgba(255,255,255,0.25)",
                                    display="flex",
                                    align_items="center",
                                    box_shadow="0 6px 18px -4px rgba(37,99,235,0.6)",
                                    transition="all 0.2s ease",
                                    _hover={"transform": "translateY(-1px)", "box_shadow": "0 8px 22px -4px rgba(37,99,235,0.85)"},
                                ),
                                href="/registro",
                                width="100%",
                                text_decoration="none",
                            ),

                            rx.link(
                                rx.box(
                                    rx.hstack(
                                        rx.icon("log-in", size=16, color="#e2e8f0"),
                                        rx.text("Iniciar Sesión", font_size="13px", font_weight="600", color="#ffffff"),
                                        rx.spacer(),
                                        rx.icon("arrow-right", size=14, color="rgba(255,255,255,0.5)"),
                                        width="100%",
                                        align_items="center",
                                    ),
                                    px="4",
                                    height="42px",
                                    border_radius="12px",
                                    bg="rgba(255, 255, 255, 0.08)",
                                    border="1px solid rgba(255, 255, 255, 0.16)",
                                    display="flex",
                                    align_items="center",
                                    transition="all 0.2s ease",
                                    _hover={"bg": "rgba(255, 255, 255, 0.16)", "transform": "translateY(-1px)"},
                                ),
                                href="/login",
                                width="100%",
                                text_decoration="none",
                            ),

                            rx.link(
                                rx.box(
                                    rx.hstack(
                                        rx.icon("circle-plus", size=16, color="#93c5fd"),
                                        rx.text("Nueva Solicitud", font_size="13px", font_weight="600", color="#e2e8f0"),
                                        rx.spacer(),
                                        rx.icon("arrow-right", size=14, color="rgba(255,255,255,0.5)"),
                                        width="100%",
                                        align_items="center",
                                    ),
                                    px="4",
                                    height="42px",
                                    border_radius="12px",
                                    bg="rgba(15, 23, 42, 0.45)",
                                    border="1px solid rgba(255, 255, 255, 0.10)",
                                    display="flex",
                                    align_items="center",
                                    transition="all 0.2s ease",
                                    _hover={"bg": "rgba(15, 23, 42, 0.7)", "border_color": "rgba(147,197,253,0.4)"},
                                ),
                                href="/solicitudes",
                                width="100%",
                                text_decoration="none",
                            ),

                            rx.hstack(
                                rx.icon("shield-alert", size=13, color="rgba(255,255,255,0.5)"),
                                rx.text(
                                    "Seguimiento ciudadano con Ley 1755 de 2015.",
                                    font_size="11px",
                                    color="rgba(255, 255, 255, 0.55)",
                                    line_height="1.4",
                                ),
                                spacing="2",
                                align_items="center",
                                pt="1",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        p="6",
                        width="100%",
                        max_width="320px",
                        border_radius="24px",
                        bg="rgba(15, 23, 42, 0.65)",
                        backdrop_filter="blur(24px)",
                        border="1px solid rgba(255, 255, 255, 0.18)",
                        box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.15)",
                    ),
                    spacing="8",
                    align_items="center",
                    justify="between",
                    flex_wrap="wrap",
                ),
                max_width="1200px",
                padding_y="20",
                padding_x="6",
            ),
            width="100%",
            min_height="540px",
            style={
                "backgroundImage": "linear-gradient(90deg, rgba(15,23,42,0.90) 0%, rgba(15,23,42,0.45) 100%), url('/Gemini_Generated_Image_ouyornouyornouyo.png')",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "backgroundRepeat": "no-repeat",
            },
        ),

        # ── SECCIÓN: SERVICIOS / ACCIONES PRINCIPALES (Bento Cards Linear/Stripe) ───────
        rx.box(
            rx.box(
                rx.vstack(
                    rx.vstack(
                        rx.badge(
                            "Servicios Ciudadanos",
                            color_scheme="blue",
                            radius="full",
                            variant="surface",
                            size="1",
                        ),
                        rx.heading(
                            "¿Qué deseas tramitar hoy?",
                            size="8",
                            color=TEXT_MAIN,
                            letter_spacing="-0.03em",
                            font_weight="800",
                        ),
                        rx.text(
                            "Selecciona el servicio correspondiente para radicar o dar seguimiento oportuno.",
                            color=TEXT_SUB,
                            font_size="15px",
                        ),
                        spacing="2",
                        align_items="center",
                        text_align="center",
                    ),
                    rx.grid(
                        quick_action_card(
                            "Radicar PQRS",
                            "Registra peticiones, quejas, reclamos o sugerencias con soporte documental.",
                            "Radicar ahora",
                            "/solicitudes",
                            "blue"
                        ),
                        quick_action_card(
                            "Consultar estado",
                            "Consulta el estado en vivo y respuesta formal con tu código radicado.",
                            "Consultar radicado",
                            "/consultar-estado",
                            "cyan"
                        ),
                        quick_action_card(
                            "Registro ciudadano",
                            "Crea tu expediente digital para historial y notificaciones certificadas.",
                            "Crear cuenta",
                            "/registro",
                            "green"
                        ),
                        quick_action_card(
                            "Iniciar sesión",
                            "Ingresa a tu panel personal de seguimiento y descarga de certificados.",
                            "Ingresar al portal",
                            "/login",
                            "gray"
                        ),
                        columns={"base": "1", "sm": "2", "lg": "4"},
                        spacing={"base": "5", "md": "6"},
                        width="100%",
                    ),
                    spacing="8",
                    align_items="center",
                    width="100%",
                ),
                max_width="1440px",
                width="100%",
                mx="auto",
                py={"base": "12", "md": "20"},
                px={"base": "4", "sm": "6", "md": "8", "xl": "12"},
            ),
            width="100%",
            bg=PAGE_BG,
        ),

        # ── SECCIÓN: TRANSPARENCIA Y GARANTÍAS ────────────────────────────
        rx.box(
            rx.container(
                rx.vstack(
                    rx.vstack(
                        rx.heading(
                            "Gestión Transparente y Oportuna",
                            size="7",
                            color=TEXT_MAIN,
                            letter_spacing="-0.02em",
                            font_weight="800",
                            text_align="center",
                        ),
                        rx.text(
                            "Diseñado bajo los lineamientos de la Ley 1755 de 2015 para garantizar el derecho de petición.",
                            color=TEXT_SUB,
                            font_size="15px",
                            text_align="center",
                            max_width="700px",
                            line_height="1.6",
                        ),
                        spacing="2",
                        align_items="center",
                    ),
                    rx.grid(
                        info_card(
                            "Canal Seguro y Oficial",
                            "Cifrado de datos y resguardo confidencial de anexos bajo política de habeas data."
                        ),
                        info_card(
                            "Trazabilidad Continua",
                            "Histórico auditable paso a paso con fechas límites y funcionario a cargo."
                        ),
                        info_card(
                            "Respuestas Notificadas",
                            "Recepción inmediata vía correo con confirmación de radicado institucional."
                        ),
                        columns={"base": "1", "md": "3"},
                        spacing="6",
                        width="100%",
                    ),
                    spacing="8",
                    align_items="center",
                    width="100%",
                ),
                max_width="1200px",
                padding_y="20",
                padding_x="6",
            ),
            width="100%",
            bg=SECT_BG,
            border_top=f"1px solid",
            border_bottom=f"1px solid",
            border_color=CARD_BDR,
        ),

        # ── SECCIÓN: DEFINICIONES PQRS ───────────────────────────────────
        rx.box(
            rx.container(
                rx.vstack(
                    rx.vstack(
                        rx.badge("Glosario Ciudadano", color_scheme="gray", radius="full", variant="soft", size="1"),
                        rx.heading(
                            "¿Cómo clasificar tu solicitud?",
                            size="7",
                            color=TEXT_MAIN,
                            letter_spacing="-0.02em",
                            font_weight="800",
                        ),
                        spacing="2",
                        align_items="center",
                    ),
                    rx.hstack(
                        pqrs_badge("Petición", "Solicitud formal de información, copias o actuación de la entidad.", BLUE_ACC),
                        pqrs_badge("Queja", "Inconformidad respecto a la conducta de un servidor o atención recibida.", ORANGE),
                        pqrs_badge("Reclamo", "Disconformidad por la prestación indebida o interrupción de un servicio.", RED_ERR),
                        pqrs_badge("Sugerencia", "Aporte o propuesta constructiva para optimizar los procesos de la institución.", GREEN_OK),
                        spacing="4",
                        justify="center",
                        flex_wrap="wrap",
                    ),
                    spacing="6",
                    align_items="center",
                ),
                max_width="1200px",
                padding_y="16",
                padding_x="6",
            ),
            width="100%",
            bg=PAGE_BG,
        ),

        footer(),
        brand_footer(),
        bg=PAGE_BG,
        width="100%",
        min_height="100vh",
    )
