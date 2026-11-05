"""Modelos de dominio y estructuras de datos auxiliares para el módulo de autenticación."""
from pydantic import BaseModel


class AdjuntoMeta(BaseModel):
    documento_adjunto: str
    documento_href: str
    documento_preview_src: str
    documento_existe: bool


class HistorialEvento(BaseModel):
    fecha: str
    anterior: str
    nuevo: str
    obs: str
    documento_adjunto: str
    documento_href: str
    documento_preview_src: str
    documento_existe: bool
    adjuntos: list[AdjuntoMeta]


class HistorialSolicitudEvento(BaseModel):
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
