"""Módulo de servicios de aplicación y adaptadores."""
from .storage_service import (
    sanitizar_nombre_archivo,
    _resolver_ruta_archivo_existente,
    _es_imagen,
    asegurar_espejo_web,
    url_archivo_adjunto,
    construir_metadata_adjunto,
    persistir_archivo_en_uploads,
    UPLOAD_DIR,
    WEB_UPLOAD_DIR,
)
from .email_service import (
    load_email_config,
    save_email_config,
    enviar_correo_bienvenida,
    enviar_correo_notificacion,
    _enviar_notificacion_estado_solicitud,
)
from .report_service import (
    _slug_filtro_excel,
    _nombre_archivo_excel_reporte,
    _valor_celda_excel,
    _sanitizar_datos_exportacion,
    _clasificar_semaforo_solicitud,
    generar_excel_filtrado_con_grafica,
)

__all__ = [
    "sanitizar_nombre_archivo",
    "_resolver_ruta_archivo_existente",
    "_es_imagen",
    "asegurar_espejo_web",
    "url_archivo_adjunto",
    "construir_metadata_adjunto",
    "persistir_archivo_en_uploads",
    "UPLOAD_DIR",
    "WEB_UPLOAD_DIR",
    "load_email_config",
    "save_email_config",
    "enviar_correo_bienvenida",
    "enviar_correo_notificacion",
    "_enviar_notificacion_estado_solicitud",
    "_slug_filtro_excel",
    "_nombre_archivo_excel_reporte",
    "_valor_celda_excel",
    "_sanitizar_datos_exportacion",
    "_clasificar_semaforo_solicitud",
    "generar_excel_filtrado_con_grafica",
]
