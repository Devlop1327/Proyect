"""Modelos de dominio y estructuras de datos auxiliares para el módulo de autenticación."""
import reflex as rx


class AdjuntoMeta(rx.Base):
    documento_adjunto: str
    documento_href: str
    documento_preview_src: str
    documento_existe: bool


class HistorialEvento(rx.Base):
    fecha: str
    anterior: str
    nuevo: str
    obs: str
    documento_adjunto: str
    documento_href: str
    documento_preview_src: str
    documento_existe: bool
    adjuntos: list[AdjuntoMeta]


class HistorialSolicitudEvento(rx.Base):
    estado_anterior: str
    estado_nuevo: str
    fecha_cambio: str
    observaciones: str
    area_asignada: str
    documento_adjunto: str
    documento_href: str
    documento_preview_src: str
    documento_existe: bool
    adjuntos: list[AdjuntoMeta]

