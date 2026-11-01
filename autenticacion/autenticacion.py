"""Sistema de Gestión de PQRS para Empresas Públicas - Sprint 1: Registro de Ciudadanos"""
import re
from datetime import datetime, date, timedelta, timezone
import random
import bcrypt
import base64
import json
import uuid
import os
import shutil
from pathlib import Path
from urllib.parse import quote
import reflex as rx
from .usuario_model import Usuario, Solicitud
from .solicitud_estado_historial_model import SolicitudEstadoHistorial
from sqlmodel import select, SQLModel, create_engine, text, Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv
from reflex.components import recharts as rc
from notificaciones import (
    notificar_solicitud_creada,
    notificar_cambio_estado,
    notificar_respuesta_final,
    enviar_correo_smtp,
    formatear_nota_documento,
    get_app_base_url,
)
import logging

# Logger para el módulo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carpeta donde se guardarán los archivos subidos por los usuarios
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploaded_files"

WEB_UPLOAD_DIR = BASE_DIR / ".web" / "public" / "uploads"
WEB_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
from typing import Any

# Almacenamiento temporal para descargas (limpieza automática después de acceso)
TEMP_DOWNLOADS = {}

# Cargar variables de entorno
load_dotenv()
# Ruta para configuración de correo almacenada por la app (opcional)
EMAIL_CONFIG_PATH = BASE_DIR / "email_config.json"


from .services.email_service import (
    load_email_config,
    save_email_config,
    enviar_correo_bienvenida,
    enviar_correo_notificacion,
    _enviar_notificacion_estado_solicitud,
)

# Load persisted email config on startup (if any)
_EMAIL_CONFIG_CACHE = load_email_config()
DEFAULT_DATABASE_PATH = BASE_DIR / "reflex.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)

# Asegura que las columnas necesarias existan en la tabla usuario
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info('usuario')"))
    columnas = [row[1] for row in result]
    if 'etnia' not in columnas:
        conn.execute(text("ALTER TABLE usuario ADD COLUMN etnia TEXT"))
    if 'persona_vulnerable' not in columnas:
        conn.execute(text("ALTER TABLE usuario ADD COLUMN persona_vulnerable TEXT"))
    if 'acepta_notificaciones' not in columnas:
        conn.execute(text("ALTER TABLE usuario ADD COLUMN acepta_notificaciones INTEGER DEFAULT 0"))
    if 'acepta_politica_datos' not in columnas:
        conn.execute(text("ALTER TABLE usuario ADD COLUMN acepta_politica_datos INTEGER DEFAULT 0"))
    conn.commit()

# Asegura que la columna persona_vulnerable exista en la tabla solicitud cuando se añada al modelo
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info('solicitud')"))
    columnas = [row[1] for row in result]
    if 'persona_vulnerable' not in columnas:
        conn.execute(text("ALTER TABLE solicitud ADD COLUMN persona_vulnerable TEXT"))
    if 'fecha_respuesta' not in columnas:
        conn.execute(text("ALTER TABLE solicitud ADD COLUMN fecha_respuesta TIMESTAMP"))
    # Backfill: si una solicitud ya está cerrada, usar el último cambio de estado como fecha_respuesta.
    try:
        conn.execute(
            text(
                """
                UPDATE solicitud
                SET fecha_respuesta = (
                    SELECT MAX(h.fecha_cambio)
                    FROM solicitudestadohistorial AS h
                    WHERE h.solicitud_id = solicitud.id
                      AND lower(coalesce(h.estado_nuevo,'')) IN ('cerrada','resuelta','finalizada','respondida')
                )
                WHERE fecha_respuesta IS NULL
                  AND lower(coalesce(estado,'')) IN ('cerrada','resuelta','finalizada','respondida')
                """
            )
        )
    except Exception as e:
        print("No se pudo backfillear fecha_respuesta:", e)
    conn.commit()

from .core.security import (
    tiene_password,
    confirmar_contraseña,
    normalizar_texto,
    validar_correo,
    cantida_minima_contraseña,
)

from .services.storage_service import (
    sanitizar_nombre_archivo,
    _resolver_ruta_archivo_existente,
    _es_imagen,
    asegurar_espejo_web,
    url_archivo_adjunto,
    construir_metadata_adjunto,
    persistir_archivo_en_uploads,
)

def _ultimo_adjunto_historial(solicitud_id: int) -> str:
    """�?ltimo nombre de adjunto registrado en el historial de la solicitud."""
    if not solicitud_id:
        return ""
    try:
        with Session(engine) as session:
            rows = session.exec(
                select(SolicitudEstadoHistorial)
                .where(SolicitudEstadoHistorial.solicitud_id == solicitud_id)
                .where(SolicitudEstadoHistorial.documento_adjunto.isnot(None))
                .order_by(SolicitudEstadoHistorial.fecha_cambio.desc())
            ).all()
        for row in rows:
            nombre = str(row.documento_adjunto or "").strip()
            if nombre:
                return nombre
    except Exception:
        logger.exception("Error obteniendo último adjunto del historial para solicitud %s", solicitud_id)
    return ""


from .services.report_service import (
    _slug_filtro_excel,
    _nombre_archivo_excel_reporte,
    _valor_celda_excel,
    _sanitizar_datos_exportacion,
    _clasificar_semaforo_solicitud,
    generar_excel_filtrado_con_grafica,
)

# quitar prints de prueba

from .domain.models import AdjuntoMeta, HistorialEvento, HistorialSolicitudEvento

from .state.state import State

from .ui.pages.auth_pages import (
    auth_card,
    login_page,
    change_password_page,
)
from .ui.pages.register_pages import (
    registro_page,
    registro_funcionario_page,
)
from .ui.pages.index_page import (
    index,
    quick_action_card,
    info_card,
)

from .ui.pages.privacy_page import (
    politica_privacidad_page,
)
from .ui.pages.dashboard_page import (
    dashboard,
)

from .ui.components.attachments import (
    ui_boton_descargar_adjunto,
    ui_enlace_archivo,
    ui_tarjeta_adjunto,
    ui_fila_adjunto_respuesta_modal,
    ui_tarjeta_adjunto_historial,
)

from .ui.components.kpi import (
    kpi_metric_card,
    dashboard_chart_card,
    action_icon_button,
    modal_vencimiento_solicitudes,
)
from .ui.pages.funcionario_dashboard_page import (
    funcionario_dashboard,
    funcionario_cerradas_dashboard,
)

from .ui.pages.solicitudes_page import (
    solicitudes_page,
    consultar_estado_page,
)

from .ui.pages.reportes_page import (
    reportes_page,
)
from .ui.pages.admin_pages import (
    usuarios_page,
    cambiar_rol_page,
)
from .ui.pages.ayuda_page import (
    ayuda_funcionario_page,
)

app = rx.App()
app.add_page(index, route="/", title="Inicio - Sistema PQRS", on_load=State.redirigir_si_autenticado)
app.add_page(registro_page, route="/registro", title="Registro de Ciudadano", on_load=State.redirigir_si_autenticado)
app.add_page(registro_funcionario_page, route="/registro-funcionario", title="Registro de Funcionario")
app.add_page(login_page, route="/login", title="Iniciar Sesión", on_load=State.redirigir_si_autenticado)
app.add_page(solicitudes_page, route="/solicitudes", title="Nueva Solicitud PQRS")
app.add_page(change_password_page, route="/cambiar-contrasena", title="Cambiar Contraseña")
app.add_page(dashboard, route="/dashboard", title="Panel de Ciudadano", on_load=State.hidratar_sesion_ciudadano)
app.add_page(funcionario_dashboard, route="/dashboard-funcionario", title="Panel de Funcionario", on_load=State.cargar_datos_funcionario)
app.add_page(funcionario_cerradas_dashboard, route="/dashboard-funcionario-cerradas", title="Solicitudes Cerradas", on_load=State.cargar_datos_funcionario)
app.add_page(usuarios_page, route="/usuarios", title="Gestión de Usuarios", on_load=State.cargar_usuarios)
app.add_page(cambiar_rol_page, route="/cambiar-rol", title="Cambiar Rol de Usuario")
app.add_page(ayuda_funcionario_page, route="/ayuda-funcionario", title="Ayuda para Funcionarios")
app.add_page(consultar_estado_page, route="/consultar-estado", title="Consultar Estado de Solicitud")
app.add_page(politica_privacidad_page, route="/politica-privacidad", title="Política de Privacidad")
app.add_page(reportes_page, route="/reportes", title="Reportes PQRS", on_load=State.cargar_solicitudes)

if app._api is not None:
    app._api.mount(
        "/assets/uploads",
        StaticFiles(directory=str(UPLOAD_DIR), check_dir=False),
        name="assets_uploads",
    )
    app._api.mount(
        "/uploads",
        StaticFiles(directory=str(UPLOAD_DIR), check_dir=False),
        name="uploads",
    )

    from starlette.responses import FileResponse, Response

    async def serve_uploaded_file(filename: str):
        nombre = sanitizar_nombre_archivo(filename)
        ruta = _resolver_ruta_archivo_existente(nombre)
        if not ruta:
            return Response(
                content=b"Archivo no encontrado",
                status_code=404,
                media_type="text/plain",
            )
        asegurar_espejo_web(nombre)
        return FileResponse(ruta, filename=Path(ruta).name)

    async def download_file(download_id: str):
        try:
            if download_id not in TEMP_DOWNLOADS:
                return Response(
                    content=b"Archivo no encontrado o expirado",
                    status_code=404,
                    media_type="text/plain",
                )

            file_data = TEMP_DOWNLOADS[download_id]
            filename = file_data.get("filename", "descargar.bin")
            data = file_data.get("data", b"")
            mime = file_data.get("mime", "application/octet-stream")

            del TEMP_DOWNLOADS[download_id]

            return Response(
                content=data,
                media_type=mime,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        except Exception as e:
            print(f"Error en download_file: {e}")
            return Response(
                content=b"Error al descargar el archivo",
                status_code=500,
                media_type="text/plain",
            )

    for _path, _handler in (
        ("/download/{download_id}", download_file),
        ("/api/download/{download_id}", download_file),
        ("/uploads/{filename}", serve_uploaded_file),
        ("/assets/uploads/{filename}", serve_uploaded_file),
    ):
        try:
            app._api.add_api_route(_path, _handler, methods=["GET"])
        except Exception:
            try:
                from starlette.routing import Route
                app._api.routes.insert(0, Route(_path, endpoint=_handler, methods=["GET"]))
            except Exception as route_err:
                print(f"No se pudo registrar ruta {_path}: {route_err}")


