from ...domain.models import HistorialEvento
import reflex as rx
from ...state import State

def ui_boton_descargar_adjunto(href, filename, color_scheme: str = "blue") -> rx.Component:
    """Botón que fuerza la descarga del adjunto al disco local."""
    return rx.cond(
        href != "",
        rx.button(
            rx.hstack(
                rx.icon("download", size=14),
                rx.text("Descargar", font_size="xs", font_weight="medium"),
                spacing="1",
                align_items="center",
            ),
            on_click=rx.download(url=href, filename=filename),
            size="2",
            variant="soft",
            color_scheme=color_scheme,
            cursor="pointer",
        ),
        rx.box(),
    )


def ui_enlace_archivo(href, *children, **props) -> rx.Component:
    """Enlace HTML para ver/descargar adjuntos (no usar rx.link: interpreta /uploads como ruta SPA)."""
    return rx.el.a(
        *children,
        href=href,
        target="_blank",
        rel="noopener noreferrer",
        text_decoration="none",
        **props,
    )


def ui_tarjeta_adjunto(doc) -> rx.Component:
    """Muestra un adjunto con vista previa (imagen) y enlace de descarga."""
    return rx.cond(
        doc["basename"] != "",
        rx.vstack(
            rx.cond(
                doc["preview_src"] != "",
                rx.image(
                    src=doc["preview_src"],
                    alt=doc["basename"],
                    width="100%",
                    max_height="120px",
                    object_fit="contain",
                    border_radius="lg",
                    border="1px solid #bfdbfe",
                ),
                rx.box(),
            ),
            rx.cond(
                doc["href"] != "",
                rx.vstack(
                    rx.text(doc["basename"], font_size="xs", color="#64748b"),
                    ui_boton_descargar_adjunto(doc["href"], doc["basename"]),
                    spacing="1",
                    width="100%",
                    align_items="start",
                ),
                rx.text(
                    "El archivo ya no está en el servidor",
                    font_size="xs",
                    color="#ef4444",
                ),
            ),
            spacing="2",
            width="100%",
            align_items="start",
            p="2",
            bg=rx.color_mode_cond(light="#eff6ff", dark="rgba(59,130,246,0.1)"),
            border="1px solid #bfdbfe",
            border_radius="lg",
        ),
        rx.box(),
    )


def ui_fila_adjunto_respuesta_modal(doc) -> rx.Component:
    """Fila de adjunto en el modal de actualizar estado (funcionario)."""
    return rx.hstack(
        rx.cond(
            doc["es_imagen"] & (doc["preview_src"] != ""),
            rx.image(
                src=doc["preview_src"],
                alt=doc["nombre"],
                width="56px",
                height="56px",
                object_fit="cover",
                border_radius="10px",
                flex_shrink="0",
            ),
            rx.cond(
                doc.get("es_pdf") & (doc.get("href") != ""),
                rx.el.object(data=doc["href"], type="application/pdf", width="56px", height="56px"),
                rx.icon("file-check-2", size=18, color="#2563eb"),
            ),
        ),
        rx.text(
            doc["nombre"],
            font_size="sm",
            color=rx.color_mode_cond(light="#1d4ed8", dark="#93c5fd"),
            font_weight="600",
            max_width="220px",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.button(
            rx.icon("trash-2", size=14),
            type="button",
            size="2",
            variant="soft",
            color_scheme="red",
            on_click=State.quitar_respuesta_documento_por_nombre(doc["nombre"]),
        ),
        spacing="3",
        align_items="center",
        width="100%",
        p="2",
    )


def ui_tarjeta_adjunto_historial(h: HistorialEvento) -> rx.Component:
    """Adjunto en una entrada de bitácora / historial."""
    return rx.cond(
        h.adjuntos.length() > 0,
        rx.vstack(
            rx.foreach(
                h.adjuntos,
                lambda doc: rx.vstack(
                    rx.cond(
                        doc.documento_preview_src != "",
                        rx.image(
                            src=doc.documento_preview_src,
                            alt=doc.documento_adjunto,
                            width="100%",
                            max_height="120px",
                            object_fit="contain",
                            border_radius="md",
                            border="1px solid #bfdbfe",
                            margin_top="1",
                        ),
                        rx.cond(
                            doc.documento_href != "",
                            rx.box(),
                            rx.box(
                                rx.icon("file", size=28, color="#3b82f6"),
                                display="flex", align_items="center",
                            ),
                        ),
                    ),
                    rx.cond(
                        doc.documento_href != "",
                        ui_boton_descargar_adjunto(doc.documento_href, doc.documento_adjunto),
                        ui_boton_descargar_adjunto(f"/uploads/{doc.documento_adjunto}", doc.documento_adjunto),
                    ),
                    spacing="1",
                    width="100%",
                    align_items="start",
                    margin_bottom="2",
                )
            ),
            spacing="2",
            width="100%",
            align_items="start",
        ),
        rx.box(),
    )


