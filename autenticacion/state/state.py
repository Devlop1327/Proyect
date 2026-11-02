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
from ..usuario_model import Usuario, Solicitud
from ..solicitud_estado_historial_model import SolicitudEstadoHistorial
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
BASE_DIR = Path(__file__).resolve().parent.parent.parent
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


from ..services.email_service import (
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

from ..core.security import (
    tiene_password,
    confirmar_contraseña,
    normalizar_texto,
    validar_correo,
    cantida_minima_contraseña,
)

from ..services.storage_service import (
    sanitizar_nombre_archivo,
    _resolver_ruta_archivo_existente,
    _es_imagen,
    asegurar_espejo_web,
    url_archivo_adjunto,
    construir_metadata_adjunto,
    persistir_archivo_en_uploads,
)

def _ultimo_adjunto_historial(solicitud_id: int) -> str:
    """último nombre de adjunto registrado en el historial de la solicitud."""
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


from ..services.report_service import (
    _slug_filtro_excel,
    _nombre_archivo_excel_reporte,
    _valor_celda_excel,
    _sanitizar_datos_exportacion,
    _clasificar_semaforo_solicitud,
    generar_excel_filtrado_con_grafica,
)

# quitar prints de prueba

from ..domain.models import AdjuntoMeta, HistorialEvento, HistorialSolicitudEvento


class State(rx.State):
    # --- Modal de Vencimiento de Reportes ---
    vencimiento_modal_abierto: bool = False
    rango_vencimiento_seleccionado: str = ""
    solicitudes_vencimiento_filtradas: list[dict] = []
    detalle_solicitud_modal_abierto: bool = False
    # --- Modal confirmación de cierre de sesión ---
    show_logout_confirm: bool = False

    def abrir_detalle_solicitud(self, solicitud_id: int):
        for s in self.solicitudes:
            if s.get("id") == solicitud_id:
                self.solicitud_consultada = dict(s)
                self.cargar_historial_solicitud(solicitud_id)
                self.detalle_solicitud_modal_abierto = True
                break

    def cerrar_detalle_solicitud(self):
        self.detalle_solicitud_modal_abierto = False

    def abrir_vencimiento_modal(self, data: Any):
        import logging
        print(f"[LOG] abrir_vencimiento_modal llamado con data: {data} (tipo: {type(data)})")
        
        rango = ""
        # 1. Si es un diccionario directo
        if isinstance(data, dict):
            # Podría venir en data['name'] o data['activeLabel']
            rango = data.get("name") or data.get("activeLabel") or ""
        # 2. Si viene de una lista de payload (en algunos charts de Recharts)
        elif isinstance(data, list) and len(data) > 0:
            item = data[0]
            if isinstance(item, dict):
                rango = item.get("name") or item.get("payload", {}).get("name", "")
        # 3. Si es un string directo
        elif isinstance(data, str):
            rango = data
            
        print(f"[LOG] Rango determinado: '{rango}'")
        if not rango:
            print(f"[LOG] Rango vacío, no se hace nada.")
            return

        self.rango_vencimiento_seleccionado = rango
        self.solicitudes_vencimiento_filtradas = []
        
        filtered = []
        for s in (self.solicitudes_filtradas or []):
            rem = s.get("semaforo_remaining")
            
            match = False
            if rem is None:
                if rango == ">10 días":
                    match = True
            else:
                if rango == "Vencidas" and rem <= 0:
                    match = True
                elif rango == "1-5 días" and 1 <= rem <= 5:
                    match = True
                elif rango == "6-10 días" and 6 <= rem <= 10:
                    match = True
                elif rango == ">10 días" and rem > 10:
                    match = True
                
            if match:
                filtered.append({
                    "id": s.get("id"),
                    "radicado": s.get("radicado") or f"ID-{s.get('id')}",
                    "tipo_solicitud": s.get("tipo_solicitud") or s.get("tipo_pqrs") or "N/A",
                    "asunto": s.get("asunto") or "Sin asunto",
                    "creado_por": s.get("creado_por") or "N/A",
                    "estado": s.get("estado") or "Radicada",
                    "area_responsable": s.get("area_responsable") or "N/A",
                    "semaforo_remaining": s.get("semaforo_remaining"),
                    "semaforo_fill": s.get("semaforo_fill") or "gray",
                    "is_expired": bool(rem is not None and rem <= 0),
                    "remaining_str": "Vencida" if (rem is not None and rem <= 0) else (f"{int(rem)} días" if rem is not None else "N/A")
                })
        
        print(f"[LOG] Encontradas {len(filtered)} solicitudes para el rango '{rango}'")
        self.solicitudes_vencimiento_filtradas = filtered
        self.vencimiento_modal_abierto = True

    def abrir_semaforo_activas_modal(self, color: str):
        """Abre el modal de vencimiento filtrando solo solicitudes activas (misma base que Excel)."""
        color = str(color or "").strip()
        labels = {
            "Verde": "Verde (>5 días)",
            "Amarillo": "Amarillo (1-5 días)",
            "Rojo": "Rojo (Vencidas)",
        }
        if color not in labels:
            return

        self.rango_vencimiento_seleccionado = labels[color]
        filtered = []
        for s in (self.solicitudes_abiertas or []):
            if _clasificar_semaforo_solicitud(s) != color:
                continue
            rem = s.get("semaforo_remaining")
            filtered.append({
                "id": s.get("id"),
                "radicado": s.get("radicado") or f"ID-{s.get('id')}",
                "tipo_solicitud": s.get("tipo_solicitud") or s.get("tipo_pqrs") or "N/A",
                "asunto": s.get("asunto") or "Sin asunto",
                "creado_por": s.get("creado_por") or "N/A",
                "estado": s.get("estado") or "Radicada",
                "area_responsable": s.get("area_responsable") or "N/A",
                "semaforo_remaining": rem,
                "semaforo_fill": s.get("semaforo_fill") or "gray",
                "is_expired": bool(rem is not None and rem <= 0),
                "remaining_str": "Vencida" if (rem is not None and rem <= 0) else (f"{int(rem)} días" if rem is not None else "N/A"),
            })

        self.solicitudes_vencimiento_filtradas = filtered
        self.vencimiento_modal_abierto = True

    def cerrar_vencimiento_modal(self):
        self.vencimiento_modal_abierto = False
        self.rango_vencimiento_seleccionado = ""
        self.solicitudes_vencimiento_filtradas = []

    # --- Historial de estados ---
    historial_modal_abierto: bool = False
    historial_solicitud_id: int = 0
    historial_estados: list[HistorialEvento] = []

    def abrir_historial(self, solicitud_id: int):
        """Carga el historial de estados de una solicitud y abre el modal."""
        self.historial_solicitud_id = solicitud_id
        self.historial_estados = []
        from ..solicitud_estado_historial_model import SolicitudEstadoHistorial
        with Session(engine) as session:
            # Cargar la solicitud principal para incluir multimedia/comentarios
            try:
                solicitud_obj = session.get(Solicitud, solicitud_id)
                if solicitud_obj:
                    main = self._solicitud_a_dict(solicitud_obj)
                else:
                    main = {}
            except Exception:
                main = {}
            rows = session.exec(
                select(SolicitudEstadoHistorial)
                .where(SolicitudEstadoHistorial.solicitud_id == solicitud_id)
                .order_by(SolicitudEstadoHistorial.fecha_cambio)
            ).all()
            estados: list[dict[str, Any]] = []
            for h in rows:
                obs_raw = h.observaciones or ""
                doc = h.documento_adjunto or ""
                if not doc:
                    match = re.search(r"\[DOCUMENTO(: ADJUNTO):\s*([^\]\|]+)\]", obs_raw)
                    if match:
                        doc = match.group(1).strip()
                        obs_raw = re.sub(r"\s*\[DOCUMENTO(: ADJUNTO):[^\]]+\]", "", obs_raw).strip()
                
                adjuntos_metas = []
                if doc:
                    parts = [p.strip() for p in doc.split(",") if p.strip()]
                    for p in parts:
                        m = construir_metadata_adjunto(p)
                        adjuntos_metas.append(AdjuntoMeta(
                            documento_adjunto=str(m.get("basename", p)),
                            documento_href=str(m.get("href", "")),
                            documento_preview_src=str(m.get("preview_src", "")),
                            documento_existe=bool(m.get("existe", False)),
                        ))                
                first_meta = adjuntos_metas[0] if adjuntos_metas else None
                estados.append(
                    HistorialEvento(
                        fecha=h.fecha_cambio.strftime("%Y-%m-%d %H:%M"),
                        anterior=str(h.estado_anterior or ""),
                        nuevo=str(h.estado_nuevo or ""),
                        obs=str(obs_raw),
                        documento_adjunto=str(first_meta.documento_adjunto if first_meta else ""),
                        documento_href=str(first_meta.documento_href if first_meta else ""),
                        documento_preview_src=str(first_meta.documento_preview_src if first_meta else ""),
                        documento_existe=bool(first_meta.documento_existe if first_meta else False),
                        adjuntos=adjuntos_metas,
                    )
                )
            # Prepend main solicitud info (multimedia / comentarios) as the first evento
            if main:
                adjuntos_metas = []
                docs = main.get("documento_adjuntos", []) or []
                if isinstance(docs, list):
                    for d in docs:
                        if isinstance(d, dict):
                            adjuntos_metas.append(AdjuntoMeta(
                                documento_adjunto=str(d.get("basename", "")),
                                documento_href=str(d.get("href", "")),
                                documento_preview_src=str(d.get("preview_src", "")),
                                documento_existe=bool(d.get("existe", False)),
                            ))
                first_meta = adjuntos_metas[0] if adjuntos_metas else None

                main_event = HistorialEvento(
                    fecha=str(main.get("fecha") or ""),
                    anterior="",
                    nuevo=str(main.get("estado") or ""),
                    obs=str(main.get("descripcion") or "") + ("\nRespuesta: " + str(main.get("respuesta") or "") if main.get("respuesta") else ""),
                    documento_adjunto=str(first_meta.documento_adjunto if first_meta else ""),
                    documento_href=str(first_meta.documento_href if first_meta else ""),
                    documento_preview_src=str(first_meta.documento_preview_src if first_meta else ""),
                    documento_existe=bool(first_meta.documento_existe if first_meta else False),
                    adjuntos=adjuntos_metas,
                )
                self.historial_estados = [main_event] + estados
            else:
                self.historial_estados = estados
        self.historial_modal_abierto = True

    def cerrar_historial(self):
        self.historial_modal_abierto = False
        self.historial_solicitud_id = 0
        self.historial_estados = []


    # Dentro de class State, agrega estas variables:
    toast_mensaje: str = ""
    toast_tipo: str = ""  # "success" o "error"
    toast_visible: bool = False

    async def clear_mensajes_delay(self):
        import asyncio
        await asyncio.sleep(5)
        self.solicitud_mensaje = ""
        self.mensaje_actualizar_estado = ""
        self.calificacion_mensaje = ""
        self.toast_mensaje = ""
        self.toast_visible = False

    "En esta clase se define el estado de la aplicación, es decir, las variables que se van a usar en la aplicación y sus valores iniciales."
    state_auto_setters = True
    contraseña: str = ""
    confirmar_contraseña: str = ""
    correo: str = ""
    confirmar_correo: str = ""
    # Campos adicionales para registro extendido
    tipo_identificacion: str = ""
    numero_identificacion: str = ""
    apellidos: str = ""
    sexo: str = ""
    direccion: str = ""
    telefono: str = ""
    departamento: str = ""
    ciudad: str = ""
    etnia: str = ""
    persona_vulnerable_registro: str = ""
    # Estados de validación UX
    correo_validado: bool = False
    confirmar_correo_match: bool = False
    numero_identificacion_valid: bool = False
    nombres_valid: bool = False
    apellidos_valid: bool = False
    telefono_valid: bool = False
    departamento_valid: bool = False
    ciudad_valid: bool = False
    
    # Diccionario de departamentos y ciudades para dropdowns dinámicos
    departamentos_ciudades =  {
    "Amazonas": ["Leticia", "Puerto Nariño", "La Chorrera", "Tarapacá", "Puerto Santander", "Mirití-Paraná", "Puerto Alegría", "Puerto Arica", "La Victoria"],
    "Antioquia": ["Medellín", "Envigado", "Sabaneta", "Copacabana", "Girardota", "Barbosa", "Itagüí", "Bello", "Caldas", "La Estrella", "Rionegro", "La Ceja", "Apartadó", "Turbo", "Caucasia", "Santa Rosa de Osos"],
    "Arauca": ["Arauca", "Arauquita", "Cravo Norte", "Saravena", "Tame"],
    "Atlántico": ["Barranquilla", "Soledad", "Malambo", "Puerto Colombia", "Sabanalarga", "Baranoa", "Galapa"],
    "Bogotá D.C.": ["Bogotá D.C."],
    "Bolívar": ["Cartagena", "Turbaco", "Magangué", "Arjona", "El Carmen de Bolívar", "Mompox"],
    "Boyacá": ["Tunja", "Duitama", "Sogamoso", "Paipa", "Chiquinquirá", "Villa de Leyva", "Puerto Boyacá"],
    "Caldas": ["Manizales", "La Dorada", "Riosucio", "Chinchiná", "Villamaría", "Anserma"],
    "Caquetá": ["Florencia", "San Vicente del Caguán", "Puerto Rico", "Currillo"],
    "Casanare": ["Yopal", "Aguazul", "Paz de Ariporo", "Tauramena", "Maní"],
    "Cauca": ["Popayán", "Guachené", "Corinto", "Santander de Quilichao", "Puerto Tejada", "Patía"],
    "Cesar": ["Valledupar", "Aguachica", "Agustín Codazzi", "Bosconia", "Curumaní"],
    "Chocó": ["Quibdó", "Istmina", "Condoto", "Acandí", "Bahía Solano"],
    "Córdoba": ["Montería", "Cereté", "Sahagún", "Lorica", "Montelíbano", "Planeta Rica"],
    "Cundinamarca": ["Soacha", "Chía", "Sopó", "Tausa", "Tenjo", "Tena", "Tocaima", "Tocancipá", "Zipaquirá", "Fúquene", "Pacho", "tica", "Villapinzón", "Villeta", "Facatativá", "Girardot", "Fusagasugá"],
    "Guainía": ["Inírida", "Barrancominas"],
    "Guaviare": ["San José del Guaviare", "Calamar", "El Retorno", "Miraflores"],
    "Huila": ["Neiva", "Pitalito", "Garzón", "La Plata", "Campoalegre", "San Agustín"],
    "La Guajira": ["Riohacha", "Maicao", "Uribia", "San Juan del Cesar", "Fonseca"],
    "Magdalena": ["Santa Marta", "Ciénaga", "Fundación", "El Banco", "Plato"],
    "Meta": ["Villavicencio", "Acacías", "Granada", "Puerto López", "Cumaral"],
    "Nariño": ["Pasto", "Ipiales", "Tumaco", "Sandoná", "Túquerres", "La Unión"],
    "Norte de Santander": ["Cúcuta", "Ocaña", "Pamplona", "Villa del Rosario", "Los Patios", "Tibú"],
    "Putumayo": ["Mocoa", "Puerto Asís", "Orito", "Valle del Guamuez", "Sibundoy"],
    "Quindío": ["Armenia", "Calarcá", "Filandia", "Circasia", "Montenegro", "Quimbaya"],
    "Risaralda": ["Pereira", "Dosquebradas", "Santa Rosa de Cabal", "La Virginia", "Belén de Umbría"],
    "San Andrés y Providencia": ["San Andrés", "Providencia"],
    "Santander": ["Bucaramanga", "Floridablanca", "Girón", "Piedecuesta", "Barrancabermeja", "San Gil", "Socorro"],
    "Sucre": ["Sincelejo", "Corozal", "Tolú", "San Marcos", "Sampués"],
    "Tolima": ["Ibagué", "Espinal", "Melgar", "Mariquita", "Honda", "Líbano"],
    "Valle del Cauca": ["Cali", "Palmira", "Yumbo", "Cartago", "Buenaventura", "Tuluá", "Buga", "Jamundí"],
    "Vaupés": ["Mitú", "Carurú", "Taraira"],
    "Vichada": ["Puerto Carreño", "La Primavera", "Santa Rosalía", "Cumaribo"]
}
    
    # Habeas data / autorizaciones
    acepta_notificaciones: bool = False
    acepta_politica_datos: bool = False
    # Para el formulario de solicitudes
    acepta_politica_solicitud: bool = False
    area_responsable: str = ""
    area_otro: str = ""
    tipo_solicitud: str = ""
    persona_vulnerable: str = ""
    asunto: str = ""
    descripcion: str = ""
    ubicacion: str = ""
    documento: str = ""
    documentos: list[dict[str, str | int]] = []
    documento_nombres: list[str] = []
    documento_nombre: str = ""
    documento_previews: list[dict[str, str]] = []
    descripcion_len: int = 0
    query_solicitud: str = ""
    filter_tipo_solicitud: str = "Todos"
    filter_estado_solicitud: str = "Todos"
    filter_dias_restantes: str = "Todos"
    solicitudes: list[dict[str, Any]] = []
    editar_solicitud_id: int = 0
    eliminar_solicitud_id: int = 0
    solicitud_mensaje: str = ""
    pqrs_contacto_email: str = ""
    mantenimiento_modal_abierto: bool = False

    def abrir_mantenimiento(self):
        self.mantenimiento_modal_abierto = True

    def cerrar_mantenimiento(self):
        self.mantenimiento_modal_abierto = False


    error_de_registro: str = ""
    succes: str = ""
    error_de_contraseña: str = ""
    succes2: str = ""
    
    id_usuario: str = rx.Cookie("0")
    es_autentica: str = rx.Cookie("false")
    email_actual: str = rx.Cookie("")
    correo_usuario: str = rx.Cookie("")
    rol_usuario: str = rx.Cookie("")
    nombres: str = rx.Cookie("")
    show_password: bool = False
    # Campos para cambiar contraseña
    current_password: str = ""
    new_password: str = ""
    confirm_new_password: str = ""
    change_pw_message: str = ""
    # Campos para cambiar rol de ciudadano a funcionario
    cambiar_rol_email: str = ""
    cambiar_rol_mensaje: str = ""
    confirmar_promocion_rol: bool = False
    usuarios_registrados: list[dict[str, Any]] = []
    # Campos para editar estado de solicitud
    editar_estado_id: int = 0
    nuevo_estado: str = ""
    respuesta_solicitud: str = ""
    mensaje_actualizar_estado: str = ""
    respuesta_documento: str = ""
    respuesta_documento_nombre: str = ""
    respuesta_documento_content: str = ""
    respuesta_documento_preview_src: str = ""
    respuesta_documento_es_imagen: bool = False
    respuesta_documento_error: str = ""
    respuesta_documentos: list[dict[str, Any]] = []
    # HU9 y HU11: historial, calificación, estados
    historial_solicitud: list[HistorialSolicitudEvento] = []
    calificacion_seleccionada: int = 0
    calificacion_opcion: str = ""
    comentario_calificacion: str = ""
    calificacion_mensaje: str = ""
    ESTADOS_VALIDOS: list[str] = ["Radicada", "Asignada a Area", "En Gestion de Area", "Solucionada", "Reabierta", "Cerrada"]
    AREAS_DISPONIBLES: list[str] = ["Atención al Ciudadano", "Infraestructura", "Servicios Públicos", "Medio Ambiente", "Salud Pública", "Educación", "Secretaría Jurídica", "Planeación", "Hacienda"]
    area_para_asignar: str = ""
    # Variables para modal de política y validaciones
    modal_politica_visible: bool = False
    archivo_error_mensaje: str = ""
    correo_confirmacion_visible: bool = False
    correo_confirmacion_mensaje: str = ""
    ayuda_seccion_abierta: str = "estados"
    registro_seccion_abierta: str = "cuenta"
    registro_paso_habilitado: int = 1
    
    # Campos para asignación de área con mensaje
    asignar_area_id: int = 0
    asignar_area_mensaje: str = ""
    asignar_area_nombre: str = ""
    asignar_area_seleccionada: str = ""
    mensaje_asignacion: str = ""
    
    # Campos para consultar estado de solicitud
    consulta_radicado: str = ""
    solicitud_consultada: dict[str, Any] = {}
    consulta_mensaje: str = ""
    # Enlace generado tras exportar reportes (archivo descargable)
    export_href: str = ""
    export_filename: str = ""
    mostrar_menu_descarga: bool = False

    @rx.var
    def id_usuario_num(self) -> int:
        """Convierte el id de cookie a entero seguro."""
        try:
            return int(str(self.id_usuario or "0"))
        except Exception:
            return 0

    @rx.var
    def es_autenticada(self) -> bool:
        """Normaliza la cookie de sesión a booleano."""
        return str(self.es_autentica or "").strip().lower() in {"true", "1", "yes", "si", "sí"}

    @rx.var
    def home_url(self) -> str:
        """Retorna la URL de inicio dependiendo del estado de autenticación."""
        if self.es_autenticada:
            if self.rol_usuario == "funcionario":
                return "/dashboard-funcionario"
            return "/dashboard"
        return "/"

    def redirigir_si_autenticado(self):
        """Redirige automáticamente al usuario a su panel si ya tiene una sesión activa."""
        if self.es_autenticada:
            return rx.redirect(self.home_url)

    @rx.var
    def ciudades_disponibles(self) -> list[str]:
        """Retorna las ciudades del departamento seleccionado."""
        if self.departamento in self.departamentos_ciudades:
            return self.departamentos_ciudades[self.departamento]
        return []

    @rx.var
    def data_grafica_tipo(self) -> list[dict]:
        counts = self.estadisticas_por_tipo
        selected = (self.filter_tipo_solicitud or "Todos").strip()
        if selected.lower() in {"todas", "todos"}:
            return [
                {"name": "Petición", "cantidad": counts.get("Petición", 0)},
                {"name": "Queja", "cantidad": counts.get("Queja", 0)},
                {"name": "Reclamo", "cantidad": counts.get("Reclamo", 0)},
                {"name": "Sugerencia", "cantidad": counts.get("Sugerencia", 0)},
            ]

        normalized = self._normalize_tipo_solicitud(selected)
        if normalized:
            return [{"name": normalized, "cantidad": counts.get(normalized, 0)}]

        return []
    
    @rx.var
    def data_grafica_estado(self) -> list[dict]:
        return [
            {"name": "Radicada", "cantidad": int(self.numero_solicitudes_radicadas)},
            {"name": "En Proceso", "cantidad": int(self.numero_solicitudes_actualizadas)},
            {"name": "Cerrada", "cantidad": int(self.numero_solicitudes_cerradas)},
        ]

    def mostrar_toast(self, mensaje: str, tipo: str = "success"):
        self.toast_mensaje = mensaje
        self.toast_tipo = tipo
        self.toast_visible = True
        # Ocultar automáticamente después de 2.5 segundos
        import threading
        threading.Timer(2.5, lambda: setattr(self, 'toast_visible', False)).start()

    def export_reportes_csv(self):
        """Genera un CSV en memoria desde `solicitudes_filtradas` para descarga respetando filtros."""
        try:
            import csv
            import io
            from datetime import datetime

            data = _sanitizar_datos_exportacion(self.solicitudes_filtradas or [])
            if not data:
                self.mostrar_toast("No hay datos para exportar.", "warning")
                self.mostrar_menu_descarga = False
                return
            
            # Generar CSV en memoria
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
            
            # Guardar en almacenamiento temporal
            csv_bytes = output.getvalue().encode('utf-8')
            filename = f"reportes_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
            download_id = str(uuid.uuid4())
            
            TEMP_DOWNLOADS[download_id] = {
                "data": csv_bytes,
                "filename": filename,
                "mime": "text/csv; charset=utf-8"
            }
            
            self.export_filename = filename
            self.mostrar_toast(f" CSV generado. {len(data)} registros. Descargando...", "success")
            self.mostrar_menu_descarga = False
            self.export_href = f"/api/download/{download_id}"
            
        except Exception as e:
            print(f"ERROR en export_reportes_csv: {type(e).__name__}: {e}")
            self.mostrar_toast(f"Error: {str(e)[:100]}", "error")
            self.mostrar_menu_descarga = False

    def descargar_excel_y_abrir(self):
        """Genera Excel en memoria con datos filtrados, gráfica nativa y descarga."""
        try:
            data = _sanitizar_datos_exportacion(self.solicitudes_filtradas or [])
            if not data:
                self.mostrar_toast("No hay datos para exportar.", "warning")
                return

            excel_bytes = generar_excel_filtrado_con_grafica(
                data,
                self.filter_tipo_solicitud,
            )
            filename = _nombre_archivo_excel_reporte(self.filter_tipo_solicitud)
            self.mostrar_menu_descarga = False
            self.mostrar_toast(
                f"Excel con gráfica generado ({len(data)} registros  {self.filter_tipo_solicitud}).",
                "success",
            )
            return rx.download(
                data=excel_bytes,
                filename=filename,
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except (ImportError, ModuleNotFoundError):
            self.mostrar_toast("No se pudo generar Excel. Descargando CSV en su lugar.", "warning")
            return self.descargar_csv_y_abrir()
        except Exception as e:
            print(f"ERROR en descargar_excel_y_abrir: {e}")
            self.mostrar_toast(f"Error exportando Excel: {str(e)[:100]}", "error")

    def descargar_csv_y_abrir(self):
        """Genera CSV en memoria con datos FILTRADOS y dispara la descarga."""
        try:
            import csv
            import io
            from datetime import datetime

            data = _sanitizar_datos_exportacion(self.solicitudes_filtradas or [])
            if not data:
                self.mostrar_toast("No hay datos para exportar.", "warning")
                return

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)

            filename = f"reportes_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
            return rx.download(
                data=output.getvalue().encode('utf-8'),
                filename=filename,
                mime_type="text/csv; charset=utf-8"
            )
        except Exception as e:
            print(f"ERROR en descargar_csv_y_abrir: {e}")
            self.mostrar_toast(f"Error exportando CSV: {str(e)[:100]}", "error")


    def ocultar_toast(self):
        self.toast_visible = False
        self.toast_mensaje = ""

    def toggle_menu_descarga(self):
        """Alterna la visibilidad del menú de descarga."""
        self.mostrar_menu_descarga = not self.mostrar_menu_descarga
        
     
    @rx.var
    def numero_solicitudes(self) -> str:
        return str(len(self.solicitudes_filtradas or []))
    
    @rx.var
    def numero_solicitudes_radicadas(self) -> str:
        return str(sum(1 for solicitud in (self.solicitudes_filtradas or []) if (str(solicitud.get('estado') or '').strip().lower()) == 'radicada'))
    
    @rx.var
    def numero_solicitudes_actualizadas(self) -> str:
        # 'en proceso', 'actualizada', 'asignada' y 'en revisión' representan solicitudes activas / en proceso
        # Tambien se cuentan 'asignada a area' y 'en gestion de area'
        valid_states = ('en proceso', 'actualizada', 'asignada', 'en revisión', 'en revision', 'asignada a area', 'en gestion de area')
        return str(sum(1 for solicitud in (self.solicitudes_filtradas or []) if (str(solicitud.get('estado') or '').strip().lower()) in valid_states))
    
    @rx.var
    def numero_solicitudes_cerradas(self) -> str:
        return str(sum(1 for solicitud in (self.solicitudes_filtradas or []) if (str(solicitud.get('estado') or '').strip().lower()) in ('cerrada', 'finalizada', 'resuelta')))
    
    def _normalize_tipo_solicitud(self, tipo_raw: str) -> str:
        """Normaliza tipos de solicitud a las categorías usadas en los reportes."""
        if not tipo_raw:
            return ""
        tipo = str(tipo_raw).strip().lower()
        if tipo in ("peticion", "petición", "pqr", "solicitud"):
            return "Petición"
        if tipo == "queja":
            return "Queja"
        if tipo == "reclamo":
            return "Reclamo"
        if tipo == "sugerencia":
            return "Sugerencia"
        if "petici" in tipo:
            return "Petición"
        if "queja" in tipo:
            return "Queja"
        if "reclam" in tipo:
            return "Reclamo"
        if "suger" in tipo:
            return "Sugerencia"
        return ""

    @rx.var
    def estadisticas_por_tipo(self) -> dict[str, int]:
        counts = {"Petición": 0, "Queja": 0, "Reclamo": 0, "Sugerencia": 0}
        for solicitud in self.solicitudes_filtradas or []:
            tipo = self._normalize_tipo_solicitud(solicitud.get("tipo_solicitud") or "")
            if tipo in counts:
                counts[tipo] += 1
        return counts

    @rx.var
    def max_registros_tipo(self) -> int:
        values = list(self.estadisticas_por_tipo.values())
        return max(values) if values else 1

    @rx.var
    def monthly_response_times(self) -> list[dict]:
        """Calcula el tiempo promedio de respuesta diario para los últimos 30 días.
        Devuelve lista de dicts: {month: '26 May', dias: float}
        """
        today = date.today()
        start_date = today - timedelta(days=29)
        
        # preparar buckets por día
        buckets: dict[str, list[int]] = {}
        for i in range(30):
            d = start_date + timedelta(days=i)
            buckets[d.strftime("%Y-%m-%d")] = []

        for s in (self.solicitudes_filtradas or []):
            try:
                frp = self._parse_dt(s.get('fecha_respuesta'))
                if not frp:
                    continue
                resp_date = frp.date()
                if resp_date < start_date or resp_date > today:
                    continue
                fr = self._parse_dt(s.get('fecha') or s.get('fecha_radicado'))
                if not fr:
                    continue
                start = fr.date() + timedelta(days=1)
                dias = self._business_days_between(start, resp_date, set())
                
                key = resp_date.strftime("%Y-%m-%d")
                buckets.setdefault(key, []).append(dias)
            except Exception:
                continue

        result = []
        for i in range(30):
            d = start_date + timedelta(days=i)
            key = d.strftime("%Y-%m-%d")
            vals = buckets.get(key, [])
            avg = round(sum(vals) / len(vals), 1) if vals else 0
            label = d.strftime('%d %b')
            result.append({"month": label, "dias": avg})

        return result

    @rx.var
    def compliance_percentage(self) -> int:
        """Calcula cumplimiento: (solicitudes resueltas / total) * 100.
        Resueltas = estado 'Respondida' o 'Cerrada'.
        """
        total = len(self.solicitudes_filtradas or [])
        if total == 0:
            return 0
        closed_states = {"resuelta", "cerrada", "respondida", "finalizada"}
        cerradas = sum(1 for s in (self.solicitudes_filtradas or []) if (s.get('estado') or "").lower() in closed_states)
        return int((cerradas / total) * 100) if total > 0 else 0

    @rx.var
    def compliance_chart_data(self) -> list[dict]:
        total = len(self.solicitudes_filtradas or [])
        closed_states = {"resuelta", "cerrada", "respondida", "finalizada"}
        cerradas = sum(1 for s in (self.solicitudes_filtradas or []) if (s.get('estado') or "").lower() in closed_states)
        no_cerradas = total - cerradas
        return [
            {"name": "Cerradas", "value": cerradas, "fill": "#10b981"},
            {"name": "No cerradas", "value": max(0, no_cerradas), "fill": "#ef4444"},
        ]

    # --- Semáforo: días hábiles y conteos por color ---
    def _parse_dt(self, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        try:
            # ISO format usually works
            return datetime.fromisoformat(v)
        except Exception:
            try:
                from dateutil import parser as _p
                return _p.parse(v)
            except Exception:
                return None

    def _is_business_day(self, d: date, holidays: set):
        return d.weekday() < 5 and d not in holidays

    def _business_days_between(self, start: date, end: date, holidays: set) -> int:
        if end < start:
            return 0
        days = 0
        cur = start
        while cur <= end:
            if self._is_business_day(cur, holidays):
                days += 1
            cur += timedelta(days=1)
        return days

    def _legal_days_for(self, tipo: str, detalle: str | None = None) -> int:
        if not tipo:
            return 15
        t = tipo.lower()
        d = (detalle or "").lower()
        if "consulta" in d or t == "consulta":
            return 30
        if "inform" in d or "copia" in d or "informacion" in d:
            return 10
        if t in ("peticion", "petición", "queja", "reclamo", "sugerencia"):
            return 15
        return 15


    @staticmethod
    def _compute_remaining_for_solicitud(solicitud: dict) -> dict:
        """Computa días restantes y color (fill) para una solicitud dada.
        Usa llaves comunes que retorna `_solicitud_a_dict` como `fecha` y `tipo_solicitud`.
        Retorna dict con `remaining` (int or None) y `fill` (hex color).
        """
        try:
            fecha_raw = solicitud.get("fecha") or solicitud.get("fecha_radicado")
            if not fecha_raw:
                return {"remaining": None, "fill": "gray"}
            # intentar parseo ISO, sino dateutil
            try:
                dt = datetime.fromisoformat(str(fecha_raw))
            except Exception:
                try:
                    from dateutil import parser as _p
                    dt = _p.parse(str(fecha_raw))
                except Exception:
                    return {"remaining": None, "fill": "gray"}

            start = dt.date()
            
            estado_raw = str(solicitud.get("estado") or "").strip().lower()
            closed_states = {"respondida", "respondido", "cerrada", "cerrado", "finalizada", "finalizado", "resuelta", "resuelto"}
            
            ref = date.today()
            if estado_raw in closed_states and solicitud.get("fecha_respuesta"):
                try:
                    ref_dt = datetime.fromisoformat(str(solicitud.get("fecha_respuesta")))
                    ref = ref_dt.date()
                except Exception:
                    try:
                        from dateutil import parser as _p
                        ref = _p.parse(str(solicitud.get("fecha_respuesta"))).date()
                    except Exception:
                        logger.exception("Error parseando fecha_respuesta para solicitud")

            # Contar días calendario desde la fecha de creación hasta la referencia calculada.
            days = max((ref - start).days, 0)

            tipo = (solicitud.get("tipo_solicitud") or solicitud.get("tipo_pqrs") or "").lower()
            if "consulta" in tipo:
                legal = 30
            elif "inform" in tipo or "copia" in tipo or "informacion" in tipo:
                legal = 10
            elif tipo in ("peticion", "petición", "queja", "reclamo", "sugerencia"):
                legal = 15
            else:
                legal = 15

            remaining = legal - days
            if remaining <= 0:
                fill = "#ef4444"
            elif remaining <= 5:
                fill = "#f59e0b"
            else:
                fill = "#10b981"
            # Representar visualmente el avance hacia el vencimiento.
            if legal > 0:
                width = int(min(max((legal - remaining) / legal * 100, 0), 100))
            else:
                width = 0
            return {"remaining": remaining, "fill": fill, "width": width}
        except Exception:
            return {"remaining": None, "fill": "gray", "width": 0}

    @rx.var
    def semaforo_counts(self) -> dict:
        # Lee solicitudes_filtradas y devuelve conteo por color (dinámico por filtros)
        holidays = set()  # puedes poblar con una consulta a festivos si la tienes
        counts = {"verde": 0, "amarillo": 0, "rojo": 0}
        # Estados que consideramos cerrados/resueltos (normalizados en minúsculas)
        closed_states = {"respondida", "respondido", "respondida", "respondida", "cerrada", "cerrado", "finalizada", "finalizado"}
        for s in (self.solicitudes_filtradas or []):
            estado_raw = (s.get("estado") or "").strip().lower()
            # Si el estado está en la lista de cerrados, lo saltamos; así consideramos activo todo lo demás
            if estado_raw in closed_states:
                continue
            fr = self._parse_dt(s.get("fecha") or s.get("fecha_radicado"))
            if not fr:
                # intentar usar la llave 'fecha_radicado' si existe (compatibilidad)
                fr = self._parse_dt(s.get("fecha_radicado"))
            if not fr:
                continue
            start = fr.date() + timedelta(days=1)
            ref = date.today()
            if s.get("fecha_respuesta"):
                resp = self._parse_dt(s.get("fecha_respuesta"))
                if resp:
                    ref = resp.date()
            used = self._business_days_between(start, ref, holidays)
            # usar `tipo_solicitud` por consistencia con `_solicitud_a_dict`
            legal = self._legal_days_for(s.get("tipo_solicitud"), s.get("tipo_detalle") or s.get("asunto"))
            remaining = legal - used
            if remaining <= 0:
                counts["rojo"] += 1
            elif remaining <= 5:
                counts["amarillo"] += 1
            else:
                counts["verde"] += 1
        return counts

    @rx.var
    def semaforo_chart_data(self) -> list[dict]:
        c = self.semaforo_counts
        return [
            {"name": "Verde", "value": c.get("verde", 0), "fill": "#10b981"},
            {"name": "Amarillo", "value": c.get("amarillo", 0), "fill": "#f59e0b"},
            {"name": "Rojo", "value": c.get("rojo", 0), "fill": "#ef4444"},
        ]

    @rx.var
    def semaforo_total(self) -> int:
        c = self.semaforo_counts
        total_from_counts = int(c.get("verde", 0) + c.get("amarillo", 0) + c.get("rojo", 0))
        # Fallback: si no hay conteos, usar data_grafica_tipo (cantidad)
        fallback = 0
        try:
            for it in (self.data_grafica_tipo or []):
                fallback += int(it.get("cantidad", 0))
        except Exception:
            fallback = 0
        return max(total_from_counts, fallback)

    @rx.var
    def semaforo_bar_data(self) -> list[dict]:
        # Devuelve una lista con un único registro que contiene los valores por color
        c = self.semaforo_counts
        total = int(c.get("verde", 0) + c.get("amarillo", 0) + c.get("rojo", 0))
        if total > 0:
            return [{
                "name": "Semáforo",
                "verde": int(c.get("verde", 0)),
                "amarillo": int(c.get("amarillo", 0)),
                "rojo": int(c.get("rojo", 0)),
            }]
        # Fallback a partir de data_grafica_tipo: sumar todas las solicitudes en verde (representación)
        fallback = 0
        try:
            for it in (self.data_grafica_tipo or []):
                fallback += int(it.get("cantidad", 0))
        except Exception:
            fallback = 0
        return [{"name": "Semáforo", "verde": fallback, "amarillo": 0, "rojo": 0}]
    search_area_query: str = ""
    
    @rx.var
    def top_areas(self) -> list[dict]:
        """Devuelve las áreas responsables por cantidad de solicitudes filtradas (de mayor a menor), filtrables por búsqueda.
        """
        counts = {}
        for s in (self.solicitudes_filtradas or []):
            a = s.get('area_responsable') or 'N/A'
            counts[a] = counts.get(a, 0) + 1
        items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        q = self.search_area_query.strip().lower()
        if q:
            items = [item for item in items if q in str(item[0]).lower()]
            
        return [{"name": name, "total": total} for name, total in items]

    @rx.var
    def solicitudes_por_vencer_data(self) -> list[dict]:
        counts = {
            "Vencidas": 0,
            "1-5 días": 0,
            "6-10 días": 0,
            ">10 días": 0,
        }
        for s in (self.solicitudes_filtradas or []):
            rem = s.get("semaforo_remaining")
            if rem is None:
                counts[">10 días"] += 1
                continue
            if rem <= 0:
                counts["Vencidas"] += 1
            elif rem <= 5:
                counts["1-5 días"] += 1
            elif rem <= 10:
                counts["6-10 días"] += 1
            else:
                counts[">10 días"] += 1
        return [{"name": label, "cantidad": total} for label, total in counts.items()]

    @rx.var
    def solicitudes_por_vencer_total(self) -> int:
        return sum(item.get("cantidad", 0) for item in self.solicitudes_por_vencer_data)

    @rx.var
    def kpi_counts(self) -> dict:
        """Devuelve los 3 KPIs: pendientes (>10 días), en proceso (1-10 días), cerradas (estados cerrados).
        Usa solicitudes filtradas para ser dinámico.
        """
        closed_states = {"respondida", "respondido", "cerrada", "cerrado", "finalizada", "finalizado", "resuelta", "resuelto"}
        pendientes = 0
        en_curso = 0
        cerradas = 0
        for s in (self.solicitudes_filtradas or []):
            estado_raw = str(s.get("estado") or "").strip().lower()
            if estado_raw in closed_states:
                cerradas += 1
                continue
            rem = s.get("semaforo_remaining")
            if rem is None:
                continue
            try:
                rem_i = int(rem)
            except Exception:
                continue
            if rem_i > 10:
                pendientes += 1
            elif 1 <= rem_i <= 10:
                en_curso += 1
            # rem_i <= 0 (vencidas) quedan fuera de estos KPIs según definición
        return {"pendientes": pendientes, "en_curso": en_curso, "cerradas": cerradas}

    @rx.var
    def kpi_pendientes_count(self) -> int:
        return int(self.numero_solicitudes_radicadas)

    @rx.var
    def kpi_en_curso_count(self) -> int:
        return int(self.numero_solicitudes_actualizadas)

    @rx.var
    def kpi_cerradas_count(self) -> int:
        return int(self.numero_solicitudes_cerradas)

    @rx.var
    def solicitudes_filtradas(self) -> list[dict]:
        query = (self.query_solicitud or "").strip().lower()
        tipo = (self.filter_tipo_solicitud or "Todos").lower()
        rango = (self.filter_dias_restantes or "Todos").lower()
        resultados = []
        for solicitud in self.solicitudes or []:
            texto = " ".join(
                str(solicitud.get(field, "") or "")
                for field in ("radicado", "asunto", "descripcion", "creado_por")
            ).lower()
            if query and query not in texto:
                continue
            if tipo not in {"todas", "todos"} and self._normalize_tipo_solicitud(solicitud.get("tipo_solicitud", "")).lower() != tipo:
                continue
            if rango not in {"todas", "todos"}:
                expired = bool(solicitud.get("semaforo_expired", False))
                remaining_raw = solicitud.get("semaforo_remaining", 0)
                try:
                    remaining = int(float(str(remaining_raw).strip() or "0"))
                except Exception:
                    remaining = 0
                if rango == "vencidas":
                    if not expired:
                        continue
                elif rango == "0-3":
                    if expired or remaining < 0 or remaining > 3:
                        continue
                elif rango == "4-10":
                    if expired or remaining < 4 or remaining > 10:
                        continue
                elif rango == "11+":
                    if expired or remaining < 11:
                        continue
            resultados.append(solicitud)
        return resultados

    @rx.var
    def solicitudes_abiertas(self) -> list[dict]:
        closed_states = {"cerrada", "resuelta", "finalizada", "respondida"}
        estado_filtro = (self.filter_estado_solicitud or "Todos").lower()
        res = []
        for s in (self.solicitudes_filtradas or []):
            s_est = str(s.get("estado") or "").strip().lower()
            if s_est in closed_states:
                continue
            if estado_filtro not in {"todas", "todos"} and s_est != estado_filtro:
                continue
            res.append(s)
        return res

    @rx.var
    def semaforo_activas_chart_data(self) -> list[dict]:
        """Semáforo Verde/Amarillo/Rojo solo para solicitudes activas (igual que Excel)."""
        counts = {"Verde": 0, "Amarillo": 0, "Rojo": 0}
        for s in (self.solicitudes_abiertas or []):
            color = _clasificar_semaforo_solicitud(s)
            if color in counts:
                counts[color] += 1
        return [
            {"name": "Verde", "cantidad": counts["Verde"], "fill": "#10b981"},
            {"name": "Amarillo", "cantidad": counts["Amarillo"], "fill": "#f59e0b"},
            {"name": "Rojo", "cantidad": counts["Rojo"], "fill": "#ef4444"},
        ]

    @rx.var
    def semaforo_activas_total(self) -> int:
        return sum(int(item.get("cantidad", 0)) for item in self.semaforo_activas_chart_data)

    @rx.var
    def max_semaforo_activas_cantidad(self) -> int:
        valores = [int(item.get("cantidad", 0)) for item in self.semaforo_activas_chart_data]
        maximo = max(valores) if valores else 0
        return max(maximo, 1)

    @rx.var
    def solicitudes_cerradas_lista(self) -> list[dict]:
        closed_states = {"cerrada", "resuelta", "finalizada", "respondida"}
        return [
            s
            for s in (self.solicitudes_filtradas or [])
            if str(s.get("estado") or "").strip().lower() in closed_states
        ]

    @rx.var
    def documento_nombres_joined(self) -> str:
        return ", ".join(self.documento_nombres or [])
    
    @rx.var
    def documento_nombres_count(self) -> str:
        return str(len(self.documento_nombres or []))

    @rx.var
    def documento_tamano_total(self) -> str:
        total = 0
        for item in self.documentos or []:
            if isinstance(item, dict):
                total += int(item.get("size") or 0)
        return f"{total / (1024 * 1024):.2f} MB"
    
    @rx.var
    def usuarios_registrados_count(self) -> int:
        return len(self.usuarios_registrados or [])
    
    @rx.var
    def solicitud_consultada_adjuntos(self) -> list[dict]:
        docs = self.solicitud_consultada.get("documento_adjuntos", [])
        if isinstance(docs, list) and docs:
            return docs
        return []
    
    
    
    def set_query_solicitud(self, value: str):
        self.query_solicitud = value or ""
    
    def set_filter_tipo_solicitud(self, value: str):
        self.filter_tipo_solicitud = value or "Todos"

    def set_filter_estado_solicitud(self, value: str):
        self.filter_estado_solicitud = value or "Todas"

    def set_filter_dias_restantes(self, value: str):
        self.filter_dias_restantes = value or "Todos"

    def buscar_solicitudes(self):
        self.query_solicitud = (self.query_solicitud or "").strip()

    def set_new_password(self, value: str):
        self.new_password = value
    
    def set_confirm_new_password(self, value: str):
        self.confirm_new_password = value
    
    def borrar_mensajes_de_estado(self):
        self.error_de_registro = ""
        self.succes = ""
        self.error_de_contraseña = ""
        self.succes2 = ""
        
    def validacion_de_entradas(self, require_strong_pw: bool = True) -> bool:
        self.correo_confirmacion_visible = False
        self.correo_confirmacion_mensaje = ""

        if not self.correo or not self.correo.strip():
            self.error_de_registro = "El correo electrónico es obligatorio."
            return False

        if not validar_correo(self.correo):
            self.error_de_registro = "Correo no válido."
            self.correo_confirmacion_visible = True
            self.correo_confirmacion_mensaje = "Correo no válido."
            return False

        if not self.confirmar_correo or not self.confirmar_correo.strip():
            self.error_de_registro = "Debes confirmar tu correo electrónico."
            return False

        if self.correo != self.confirmar_correo:
            self.error_de_registro = "Los correos electrónicos no coinciden."
            return False

        self.correo_confirmacion_visible = True
        self.correo_confirmacion_mensaje = "Correo válido."

        if not self.contraseña or not self.contraseña.strip():
            self.error_de_registro = "La contraseña es obligatoria."
            return False

        if not self.confirmar_contraseña or not self.confirmar_contraseña.strip():
            self.error_de_registro = "Debes confirmar tu contraseña."
            return False

        if require_strong_pw and not cantida_minima_contraseña(self.contraseña):
            self.error_de_registro = "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."
            return False
        if require_strong_pw and self.contraseña != self.confirmar_contraseña:
            self.error_de_registro = "Las contraseñas no coinciden."
            return False
        return True

    def set_confirmar_correo_match(self, value: bool):
        self.confirmar_correo_match = bool(value)

    def limpiar_formulario_registro(self):
        """Limpia todos los campos del formulario de registro."""
        self.correo = ""
        self.confirmar_correo = ""
        self.contraseña = ""
        self.confirmar_contraseña = ""
        self.tipo_identificacion = ""
        self.numero_identificacion = ""
        self.nombres = ""
        self.apellidos = ""
        self.sexo = ""
        self.direccion = ""
        self.telefono = ""
        self.departamento = ""
        self.ciudad = ""
        self.etnia = ""
        self.persona_vulnerable_registro = ""
        self.acepta_notificaciones = False
        self.acepta_politica_datos = False
        self.correo_validado = False
        self.confirmar_correo_match = False
        self.numero_identificacion_valid = False
        self.nombres_valid = False
        self.apellidos_valid = False
        self.telefono_valid = False
        self.departamento_valid = False
        self.ciudad_valid = False
        self.error_de_registro = ""
        self.correo_confirmacion_visible = False
        self.correo_confirmacion_mensaje = ""
        self.show_password = False
    def validar_campo_simple(self, campo: str) -> bool:
        """Validaciones simples para mostrar iconos de confirmación. Retorna True si el campo parece correcto."""
        val = getattr(self, campo, "")
        ok = False
        if campo == "telefono":
            ok = isinstance(val, str) and len(val) >= 7
        elif campo == "numero_identificacion":
            ok = isinstance(val, str) and len(val) >= 6
        elif campo == "correo":
            ok = validar_correo(val)
        else:
            ok = bool(val and str(val).strip())
        # set dedicated flags for reactivity
        if campo == "telefono":
            self.telefono_valid = ok
        elif campo == "numero_identificacion":
            self.numero_identificacion_valid = ok
        elif campo == "nombres":
            self.nombres_valid = ok
        elif campo == "apellidos":
            self.apellidos_valid = ok
        elif campo == "departamento":
            self.departamento_valid = ok
        elif campo == "ciudad":
            self.ciudad_valid = ok
        return ok

    def validar_correo_accion(self):
        """Acción invocada por el botón 'Validar' junto al correo."""
        self.correo_validado = validar_correo(self.correo)
        if not self.correo_validado:
            self.error_de_registro = "Correo inválido."
        else:
            self.error_de_registro = ""
        return

    # Setters that also validate so we can show inline icons
    def set_and_validate_nombres(self, val: str):
        self.nombres = val
        self.validar_campo_simple("nombres")

    def set_and_validate_apellidos(self, val: str):
        self.apellidos = val
        self.validar_campo_simple("apellidos")

    def set_and_validate_numero_identificacion(self, val: str):
        self.numero_identificacion = val
        self.validar_campo_simple("numero_identificacion")

    def set_and_validate_telefono(self, val: str):
        self.telefono = val
        self.validar_campo_simple("telefono")

    def set_and_validate_departamento(self, val: str):
        self.departamento = val
        self.ciudad = ""  # Limpia la ciudad cuando cambia el departamento
        self.validar_campo_simple("departamento")

    def set_and_validate_ciudad(self, val: str):
        self.ciudad = val
        self.validar_campo_simple("ciudad")

    def set_and_validate_correo(self, val: str):
        """Valida el correo en tiempo real y borra el mensaje si es válido o vacío."""
        self.correo = val or ""
        
        # Si el correo está vacío, borra el mensaje
        if not self.correo.strip():
            self.correo_confirmacion_visible = False
            self.correo_confirmacion_mensaje = ""
            self.error_de_registro = ""
            self.correo_validado = False
            return
        
        # Si es válido, muestra mensaje verde y borra error
        if validar_correo(self.correo):
            self.correo_confirmacion_visible = True
            self.correo_confirmacion_mensaje = "Correo válido."
            self.error_de_registro = ""
            self.correo_validado = True
        else:
            # Si es inválido, muestra mensaje rojo
            self.correo_confirmacion_visible = True
            self.correo_confirmacion_mensaje = "Correo no válido."
            self.error_de_registro = "Correo no válido."
            self.correo_validado = False

    def set_etnia(self, val: str):
        self.etnia = val or ""

    def set_persona_vulnerable_registro(self, val: str):
        self.persona_vulnerable_registro = val or ""

    def set_etnia(self, val: str):
        self.etnia = val or ""

    def set_modal_politica_visible(self, visible: bool):
        self.modal_politica_visible = bool(visible)

    def set_archivo_error_mensaje(self, mensaje: str):
        self.archivo_error_mensaje = mensaje or ""

    def set_correo_confirmacion_visible(self, visible: bool):
        self.correo_confirmacion_visible = bool(visible)

    def set_correo_confirmacion_mensaje(self, mensaje: str):
        self.correo_confirmacion_mensaje = mensaje or ""

    def validar_email(self):
        if validar_correo(self.correo):
            self.correo_confirmacion_visible = True
            self.correo_confirmacion_mensaje = "Correo válido."
        else:
            self.correo_confirmacion_visible = True
            self.correo_confirmacion_mensaje = "Correo no válido."

    def set_descripcion(self, val: str):
        # Guardar descripción y longitud para el contador de caracteres
        self.descripcion = val if val is not None else ""
        # Limitar a 1000 caracteres en la UI
        if len(self.descripcion) > 1000:
            self.descripcion = self.descripcion[:1000]
        self.descripcion_len = len(self.descripcion)

    def set_tipo_solicitud(self, val: str):
        self.tipo_solicitud = val or ""

    def set_persona_vulnerable(self, val: str):
        self.persona_vulnerable = val or ""

    def set_asunto(self, val: str):
        self.asunto = val or ""

    def set_ubicacion(self, val: str):
        self.ubicacion = val or ""

    def set_acepta_politica_solicitud(self, checked: bool):
        self.acepta_politica_solicitud = bool(checked)

    def preconfirmar_politica(self, checked: bool):
        if checked:
            self.modal_politica_visible = True
        else:
            self.acepta_politica_datos = False

    def confirmar_politica(self):
        self.acepta_politica_datos = True
        self.modal_politica_visible = False

    def cancelar_politica(self):
        self.acepta_politica_datos = False
        self.modal_politica_visible = False

    def set_acepta_notificaciones(self, checked: bool):
        self.acepta_notificaciones = bool(checked)

    def _infer_mime_type(self, name: str) -> str:
        ext = os.path.splitext((name or "").lower())[1].lstrip(".")
        if ext in {"png"}:
            return "image/png"
        if ext in {"jpg", "jpeg"}:
            return "image/jpeg"
        if ext in {"webp"}:
            return "image/webp"
        if ext in {"gif"}:
            return "image/gif"
        if ext in {"pdf"}:
            return "application/pdf"
        return "application/octet-stream"

    def _build_file_preview(self, item: Any) -> dict[str, str]:
        name = "adjunto"
        raw_content = ""
        if isinstance(item, dict):
            name = item.get("name") or item.get("filename") or "adjunto"
            if item.get("src"):
                return {
                    "name": str(name),
                    "src": str(item.get("src") or ""),
                    "mime": str(item.get("mime") or self._infer_mime_type(str(name))),
                }
            path_val = str(item.get("path") or "")
            if path_val and _es_imagen(str(name)):
                meta = construir_metadata_adjunto(path_val, str(name))
                if meta.get("preview_src"):
                    return {
                        "name": str(name),
                        "src": meta["preview_src"],
                        "mime": self._infer_mime_type(str(name)),
                    }
            raw_content = str(item.get("content") or item.get("data") or "")
        elif isinstance(item, str):
            name = os.path.basename(item) or "adjunto"
        else:
            name = (
                getattr(item, "name", None)
                or getattr(item, "filename", None)
                or "adjunto"
            )

        mime = self._infer_mime_type(name)
        es_imagen = mime.startswith("image/")
        src = ""
        if es_imagen and raw_content:
            if raw_content.startswith("data:"):
                src = raw_content
            else:
                src = f"data:{mime};base64,{raw_content}"
        return {"name": name, "src": src, "mime": mime}

    def _upload_to_preview_dict(self, upload: rx.UploadFile) -> dict[str, str | int]:
        name = (
            getattr(upload, "name", None)
            or getattr(upload, "filename", None)
            or "adjunto"
        )
        size = int(getattr(upload, "size", 0) or 0)
        path_raw = getattr(upload, "path", None)
        path_val = str(path_raw) if path_raw else ""
        if path_val and not os.path.isfile(path_val):
            resuelto = _resolver_ruta_archivo_existente(path_val)
            if resuelto:
                path_val = resuelto
        mime = self._infer_mime_type(name)
        src = ""
        content_b64 = ""
        try:
            file_obj = getattr(upload, "file", None)
            if file_obj is not None:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                content_bytes = file_obj.read()
                if content_bytes:
                    content_b64 = base64.b64encode(content_bytes).decode("utf-8")
                    if mime.startswith("image/"):
                        src = f"data:{mime};base64,{content_b64}"
        except Exception:
            content_b64 = ""
        return {"name": str(name), "size": size, "path": path_val, "src": src, "mime": mime, "content": content_b64}

    def set_documento(self, files: list[rx.UploadFile] = None, documento: list[rx.UploadFile] = None, **kwargs):
        """Actualiza adjuntos del ciudadano sin guardar UploadFile en el estado."""
        self.documentos = []
        self.documento_nombres = []
        self.documento = ""
        self.documento_nombre = ""
        self.documento_previews = []
        self.archivo_error_mensaje = ""

        allowed_ext = {"pdf", "png", "jpg", "jpeg"}
        max_files = 3
        max_total_size = 10 * 1024 * 1024
        
        target = files if files is not None else documento
        if target is None:
            return
        archivos = target if isinstance(target, list) else [target]

        if len(archivos) > max_files:
            self.archivo_error_mensaje = "Solo puedes adjuntar hasta 3 archivos."
            return

        normalized: list[dict[str, str | int]] = []
        total_size = 0
        for item in archivos:
            item_data = self._upload_to_preview_dict(item)
            name = str(item_data.get("name") or "adjunto")
            size = int(item_data.get("size") or 0)
            path_val = str(item_data.get("path") or "")
            ext = os.path.splitext(name)[1].lower().lstrip(".")
            if ext not in allowed_ext:
                self.archivo_error_mensaje = "Solo se aceptan archivos PDF, PNG o JPG."
                return
            if size > max_total_size:
                self.archivo_error_mensaje = "Cada archivo no puede superar los 10MB."
                return
            total_size += size

            # Persistir inmediatamente el archivo durante el evento de subida
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            os.makedirs(WEB_UPLOAD_DIR, exist_ok=True)
            nombre_limpio = sanitizar_nombre_archivo(name)
            destino = UPLOAD_DIR / nombre_limpio
            destino_web = WEB_UPLOAD_DIR / nombre_limpio

            guardado_ok = False
            if path_val and os.path.exists(path_val):
                try:
                    shutil.copy2(path_val, destino)
                    shutil.copy2(path_val, destino_web)
                    guardado_ok = True
                except Exception:
                    logger.exception("Error copiando archivo desde path_val: %s", path_val)

            if not guardado_ok:
                content_b64 = item_data.get("content")
                if content_b64:
                    try:
                        data = base64.b64decode(content_b64)
                        with open(destino, "wb") as f:
                            f.write(data)
                        with open(destino_web, "wb") as f:
                            f.write(data)
                        guardado_ok = True
                    except Exception:
                        logger.exception("Error decodificando/guardando contenido base64 para archivo: %s", name)

            if not guardado_ok:
                self.archivo_error_mensaje = f"No se pudo guardar el archivo '{name}' en el servidor."
                return

            item_data["path"] = str(destino.resolve())
            normalized.append(item_data)

        if total_size > max_total_size:
            self.archivo_error_mensaje = "La suma de los archivos no puede superar los 10MB."
            return

        self.documentos = normalized
        self.documento_nombres = [
            os.path.basename(str(item.get("path") or ""))
            or sanitizar_nombre_archivo(str(item.get("name") or "adjunto"))
            for item in normalized
        ]
        self.documento_nombre = ", ".join(self.documento_nombres)
        self.documento_previews = [self._build_file_preview(item) for item in normalized]

    def set_editar_solicitud_id(self, id: int):
        self.editar_solicitud_id = id

    def set_eliminar_solicitud_id(self, id: int):
        self.eliminar_solicitud_id = id

    def eliminar_documento(self, index: int):
        # Reconstruir listas para evitar comportamiento reactivo inesperado
        if not (0 <= index < len(self.documentos)):
            return
        nuevos_docs: list[dict[str, str | int]] = []
        nuevos_nombres: list[str] = []
        for i, item in enumerate(self.documentos):
            if i == index:
                continue
            nuevos_docs.append(item)
        for i, nombre in enumerate(self.documento_nombres):
            if i == index:
                continue
            nuevos_nombres.append(nombre)
        self.documentos = nuevos_docs
        self.documento_nombres = nuevos_nombres
        self.documento_nombre = ", ".join(self.documento_nombres)
        self.documento_previews = [self._build_file_preview(item) for item in self.documentos]
        self.archivo_error_mensaje = ""

    def eliminar_documento_por_nombre(self, nombre: str):
        if nombre in self.documento_nombres:
            index = self.documento_nombres.index(nombre)
            self.eliminar_documento(index)

    def quitar_todos_documentos(self):
        self.documento = ""
        self.documentos = []
        self.documento_nombres = []
        self.documento_nombre = ""
        self.documento_previews = []
        self.archivo_error_mensaje = ""

    def confirmar_editar_solicitud(self):
        if self.editar_solicitud_id:
            self.editar_solicitud(self.editar_solicitud_id)
            self.editar_solicitud_id = 0

    def confirmar_eliminar_solicitud(self):
        if self.eliminar_solicitud_id:
            self.eliminar_solicitud(self.eliminar_solicitud_id)
            self.eliminar_solicitud_id = 0

    def set_area_responsable(self, val: str):
        self.area_responsable = val
        if val != "Otros":
            self.area_otro = ""

    def set_area_otro(self, val: str):
        self.area_otro = val

    def set_nuevo_estado(self, val: str):
        self.nuevo_estado = val
        if val != "Asignada a Area":
            self.area_para_asignar = ""

    def set_area_para_asignar(self, val: str):
        self.area_para_asignar = val


    def set_respuesta_solicitud(self, val: str):
        self.respuesta_solicitud = val

    def _limpiar_campos_respuesta_documento(self) -> None:
        self.respuesta_documento = ""
        self.respuesta_documento_nombre = ""
        self.respuesta_documento_content = ""
        self.respuesta_documento_preview_src = ""
        self.respuesta_documento_es_imagen = False

    def _sincronizar_respuesta_documento_legacy(self) -> None:
        """Mantiene campos legacy alineados con el primer adjunto de la lista."""
        if self.respuesta_documentos:
            primero = self.respuesta_documentos[0]
            self.respuesta_documento = str(primero.get("path") or "")
            self.respuesta_documento_nombre = str(primero.get("nombre") or "")
            self.respuesta_documento_content = str(primero.get("content") or "")
            self.respuesta_documento_preview_src = str(primero.get("preview_src") or "")
            self.respuesta_documento_es_imagen = bool(primero.get("es_imagen"))
        else:
            self._limpiar_campos_respuesta_documento()

    def set_respuesta_documento(self, files: list[rx.UploadFile] = None, documento: list[rx.UploadFile] = None, **kwargs):
        """Agrega adjuntos a la respuesta del funcionario (hasta 3) sin recargar el dashboard."""
        self.mensaje_actualizar_estado = ""
        self.respuesta_documento_error = ""
        max_files = 3
        allowed_ext = {"pdf", "png", "jpg", "jpeg"}

        target = files if files is not None else documento
        if target is None:
            return
        archivos = target if isinstance(target, list) else [target]

        nuevos: list[dict[str, Any]] = list(self.respuesta_documentos or [])
        nombres_actuales = {str(d.get("nombre") or "") for d in nuevos}

        for archivo in archivos:
            if archivo is None:
                continue
            if len(nuevos) >= max_files:
                self.respuesta_documento_error = "Solo puedes adjuntar hasta 3 archivos."
                break

            item_data = self._upload_to_preview_dict(archivo)
            name = str(item_data.get("name") or "respuesta_adjunto")
            ext = os.path.splitext(name)[1].lower().lstrip(".")
            if ext not in allowed_ext:
                self.respuesta_documento_error = (
                    f"Tipo de archivo no permitido: .{ext}. Solo se aceptan PDF, PNG o JPG."
                )
                continue

            ruta_guardada = persistir_archivo_en_uploads(
                archivo,
                nombre_preferido=name,
                prefijo="respuesta",
            )
            if not ruta_guardada and item_data.get("content"):
                ruta_guardada = persistir_archivo_en_uploads(
                    {"name": name, "content": item_data["content"]},
                    nombre_preferido=name,
                    prefijo="respuesta",
                )
            if not ruta_guardada:
                self.respuesta_documento_error = (
                    f"No se pudo guardar el archivo '{name}' en el servidor. Intenta de nuevo."
                )
                continue

            basename = os.path.basename(ruta_guardada)
            if basename in nombres_actuales:
                continue
            asegurar_espejo_web(basename)
            meta = construir_metadata_adjunto(ruta_guardada, basename)
            nuevos.append(
                {
                    "path": ruta_guardada,
                    "nombre": basename,
                    "content": str(item_data.get("content") or ""),
                    "preview_src": str(meta.get("preview_src") or item_data.get("src") or ""),
                    "es_imagen": bool(meta.get("es_imagen")),
                    "href": str(meta.get("href") or ""),
                    "es_pdf": ext == "pdf",
                }
            )
            nombres_actuales.add(basename)

        self.respuesta_documentos = nuevos
        self._sincronizar_respuesta_documento_legacy()

    def quitar_respuesta_documento_por_nombre(self, nombre: str):
        """Quita un adjunto por nombre sin recargar el dashboard."""
        nombre = str(nombre or "").strip()
        if not nombre:
            return rx.clear_selected_files("upload_respuesta")
        self.respuesta_documentos = [
            d for d in self.respuesta_documentos if str(d.get("nombre") or "") != nombre
        ]
        self._sincronizar_respuesta_documento_legacy()
        self.respuesta_documento_error = ""
        return rx.clear_selected_files("upload_respuesta")

    def quitar_todos_respuesta_documentos(self):
        """Quita todos los adjuntos pendientes sin recargar el dashboard."""
        self.respuesta_documentos = []
        self._limpiar_campos_respuesta_documento()
        self.respuesta_documento_error = ""
        return rx.clear_selected_files("upload_respuesta")

    def quitar_respuesta_documento(self):
        """Alias: quitar todos los adjuntos del modal de estado."""
        return self.quitar_todos_respuesta_documentos()

    def set_asignar_area_mensaje(self, val: str):
        self.asignar_area_mensaje = val

    def set_asignar_area_seleccionada(self, val: str):
        self.asignar_area_seleccionada = val or ""

    def set_asignar_area_nombre(self, val: str):
        self.asignar_area_nombre = val or ""

    def cerrar_editor_estado(self):
        self.editar_estado_id = 0
        self.nuevo_estado = ""
        self.respuesta_solicitud = ""
        self.respuesta_documentos = []
        self._limpiar_campos_respuesta_documento()
        self.respuesta_documento_error = ""
        self.mensaje_actualizar_estado = ""
        return rx.clear_selected_files("upload_respuesta")

    def set_consulta_radicado(self, val: str):
        self.consulta_radicado = val

    def toggle_ayuda_seccion(self, seccion: str):
        self.ayuda_seccion_abierta = "" if self.ayuda_seccion_abierta == seccion else seccion

    def set_registro_seccion_abierta(self, seccion: str):
        seccion = seccion or "cuenta"
        paso = {"cuenta": 1, "identidad": 2, "ubicacion": 3}.get(seccion, 1)
        if paso <= self.registro_paso_habilitado:
            self.registro_seccion_abierta = seccion
            return
        self.error_de_registro = "Completa el paso actual para continuar."

    def _validar_paso_cuenta(self) -> bool:
        self.error_de_registro = ""
        correo = str(self.correo or "").strip()
        if not correo:
            self.error_de_registro = "Completa el correo electrónico."
            return False
        if not validar_correo(correo):
            self.error_de_registro = "Correo no válido."
            return False
        if not str(self.contraseña or "").strip():
            self.error_de_registro = "Completa la contraseña."
            return False
        if not cantida_minima_contraseña(self.contraseña):
            self.error_de_registro = "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."
            return False
        if not str(self.confirmar_contraseña or "").strip():
            self.error_de_registro = "Confirma la contraseña."
            return False
        if self.contraseña != self.confirmar_contraseña:
            self.error_de_registro = "Las contraseñas no coinciden."
            return False
        return True

    def _validar_paso_identidad(self) -> bool:
        self.error_de_registro = ""
        if not str(self.nombres or "").strip():
            self.error_de_registro = "Completa el campo Nombres."
            return False
        if not str(self.apellidos or "").strip():
            self.error_de_registro = "Completa el campo Apellidos."
            return False
        if not str(self.sexo or "").strip():
            self.error_de_registro = "Selecciona el sexo."
            return False
        if not str(self.tipo_identificacion or "").strip():
            self.error_de_registro = "Selecciona el tipo de identificación."
            return False
        if len(str(self.numero_identificacion or "").strip()) < 6:
            self.error_de_registro = "El número de identificación debe tener al menos 6 caracteres."
            return False
        if len(re.sub(r"\D", "", str(self.telefono or ""))) < 7:
            self.error_de_registro = "Ingresa un teléfono válido con al menos 7 dígitos."
            return False
        return True

    def continuar_a_identidad(self):
        if not self._validar_paso_cuenta():
            return
        self.registro_paso_habilitado = max(self.registro_paso_habilitado, 2)
        self.registro_seccion_abierta = "identidad"
        self.error_de_registro = ""

    def continuar_a_ubicacion(self):
        if not self._validar_paso_identidad():
            return
        self.registro_paso_habilitado = max(self.registro_paso_habilitado, 3)
        self.registro_seccion_abierta = "ubicacion"
        self.error_de_registro = ""

    async def actualizar_estado_solicitud(self, files: Any = None):
        """Actualiza el estado de una solicitud con validación para cerrada y guarda historial. HU9."""
        self.mensaje_actualizar_estado = ""
        if not self.editar_estado_id or not self.nuevo_estado:
            self.mensaje_actualizar_estado = "Selecciona un estado válido."
            yield State.clear_mensajes_delay
            return
        # HU9: justificación obligatoria para CUALQUIER cambio de estado
        if not str(self.respuesta_solicitud or "").strip():
            self.mensaje_actualizar_estado = "Debes escribir una justificación para el cambio de estado."
            yield State.clear_mensajes_delay
            return
        # Si es Asignada a Area, validar que el area está© seleccionada
        if self.nuevo_estado == "Asignada a Area" and not str(self.area_para_asignar or "").strip():
            self.mensaje_actualizar_estado = "Selecciona el área a la que se va a asignar la solicitud."
            yield State.clear_mensajes_delay
            return
        documentos_respuesta_guardados: list[str] = []
        intento_adjunto = bool(
            self.respuesta_documentos
            or self.respuesta_documento_nombre
            or self.respuesta_documento_content
            or self.respuesta_documento
        )

        def _persistir_fuente(fuente: Any, nombre_preferido: str = "") -> str:
            if not fuente:
                return ""
            try:
                return persistir_archivo_en_uploads(
                    fuente,
                    nombre_preferido=nombre_preferido,
                    prefijo="respuesta",
                ) or ""
            except Exception:
                return ""

        for doc in self.respuesta_documentos or []:
            path = str(doc.get("path") or "")
            nombre_doc = str(doc.get("nombre") or "")
            if path and os.path.isfile(path):
                documentos_respuesta_guardados.append(path)
                asegurar_espejo_web(os.path.basename(path))
                continue
            if doc.get("content") and nombre_doc:
                ruta = _persistir_fuente(
                    {"name": nombre_doc, "content": doc["content"]},
                    nombre_preferido=nombre_doc,
                )
                if ruta:
                    documentos_respuesta_guardados.append(ruta)
                    asegurar_espejo_web(os.path.basename(ruta))

        if not documentos_respuesta_guardados and self.respuesta_documento:
            ruta = _persistir_fuente(
                self.respuesta_documento,
                nombre_preferido=self.respuesta_documento_nombre,
            )
            if ruta:
                documentos_respuesta_guardados.append(ruta)
                asegurar_espejo_web(os.path.basename(ruta))

        if not documentos_respuesta_guardados and files:
            lista = files if isinstance(files, list) else [files]
            for item in lista:
                if hasattr(item, "read"):
                    upload_data = await item.read()
                    ruta = _persistir_fuente({"name": getattr(item, "filename", getattr(item, "name", "adjunto")), "content": upload_data})
                else:
                    ruta = _persistir_fuente(item)
                if ruta:
                    documentos_respuesta_guardados.append(ruta)
                    asegurar_espejo_web(os.path.basename(ruta))

        if (
            not documentos_respuesta_guardados
            and self.respuesta_documento_content
            and self.respuesta_documento_nombre
        ):
            ruta = _persistir_fuente(
                {
                    "name": self.respuesta_documento_nombre,
                    "content": self.respuesta_documento_content,
                },
                nombre_preferido=self.respuesta_documento_nombre,
            )
            if ruta:
                documentos_respuesta_guardados.append(ruta)
                asegurar_espejo_web(os.path.basename(ruta))

        if not documentos_respuesta_guardados and (intento_adjunto or files):
            self.mensaje_actualizar_estado = (
                "No se pudo guardar el documento adjunto. Vuelve a subirlo e intenta de nuevo."
            )
            yield State.clear_mensajes_delay
            return
        nombres_adjuntos = [os.path.basename(p) for p in documentos_respuesta_guardados]
        estado_nuevo = self.nuevo_estado
        # Guardar el área para cualquier estado (no solo "Asignada a Area")
        area_asignada = str(self.area_para_asignar or "").strip()
        respuesta_enviada = self.respuesta_solicitud or ""
        datos_notificacion: dict[str, Any] | None = None
        try:
            with rx.session() as session:
                solicitud_obj = session.get(Solicitud, self.editar_estado_id)
                if not solicitud_obj:
                    self.mensaje_actualizar_estado = "Solicitud no encontrada."
                    yield State.clear_mensajes_delay
                    return
                estado_anterior = solicitud_obj.estado
                solicitud_obj.estado = estado_nuevo
                # Guardar el área seleccionada (si hay una) sin importar el estado
                if area_asignada:
                    solicitud_obj.area_responsable = area_asignada
                if respuesta_enviada:
                    solicitud_obj.respuesta = respuesta_enviada
                closed_states = {"cerrada", "resuelta", "finalizada", "respondida"}
                if str(estado_nuevo or "").strip().lower() in closed_states:
                    solicitud_obj.fecha_respuesta = datetime.now(timezone.utc)
                if documentos_respuesta_guardados:
                    tags = ", ".join(nombres_adjuntos)
                    solicitud_obj.respuesta = (solicitud_obj.respuesta or "") + f"\n\n[DOCUMENTO ADJUNTO: {tags}]"
                session.add(solicitud_obj)
                # Combinar área + observaciones en el historial
                obs_historial = respuesta_enviada or None
                if area_asignada:
                    prefix = f"[ÁREA: {area_asignada}]"
                    obs_historial = prefix + ("\n" + obs_historial if obs_historial else "")
                historial = SolicitudEstadoHistorial(
                    solicitud_id=solicitud_obj.id,
                    estado_anterior=estado_anterior,
                    estado_nuevo=estado_nuevo,
                    fecha_cambio=datetime.now(timezone.utc),
                    observaciones=obs_historial,
                    documento_adjunto=", ".join(nombres_adjuntos) if nombres_adjuntos else None,
                )
                session.add(historial)
                session.commit()

                correo_dest = solicitud_obj.creado_por or ""
                nombre_sol = correo_dest
                if solicitud_obj.usuario_id:
                    usuario = session.get(Usuario, solicitud_obj.usuario_id)
                    if usuario:
                        correo_dest = usuario.email or correo_dest
                        nombre_sol = usuario.nombres or nombre_sol

                solicitud_id_actualizada = solicitud_obj.id
                datos_notificacion = {
                    "correo": correo_dest,
                    "nombre": nombre_sol,
                    "radicado": solicitud_obj.radicado,
                    "tipo": solicitud_obj.tipo_solicitud,
                    "estado_anterior": estado_anterior,
                    "estado_nuevo": estado_nuevo,
                    "respuesta": respuesta_enviada,
                    "area_asignada": area_asignada or (solicitud_obj.area_responsable or ""),
                }

            self.mensaje_actualizar_estado = ""
            self.editar_estado_id = 0
            self.nuevo_estado = ""
            self.area_para_asignar = ""
            self.respuesta_solicitud = ""
            self.respuesta_documentos = []
            self._limpiar_campos_respuesta_documento()
            self._refrescar_solicitud_en_lista(solicitud_id_actualizada)
            self.mostrar_toast(f"Estado actualizado a '{estado_nuevo}' correctamente.", "success")
            
            # Start background thread for email notification
            if datos_notificacion:
                import threading
                threading.Thread(
                    target=_enviar_notificacion_estado_solicitud,
                    args=(dict(datos_notificacion), list(documentos_respuesta_guardados)),
                    daemon=True,
                ).start()
                
            yield State.clear_mensajes_delay

        except Exception as e:
            self.mensaje_actualizar_estado = f"Error actualizando estado: {e}"
            yield State.clear_mensajes_delay



    def abrir_editor_estado(self, solicitud_id: int, estado_actual: str):
        """Abre el editor de estado para una solicitud."""
        self.editar_estado_id = solicitud_id
        self.nuevo_estado = estado_actual
        self.respuesta_solicitud = ""
        self.respuesta_documentos = []
        self._limpiar_campos_respuesta_documento()
        self.respuesta_documento_error = ""
        self.mensaje_actualizar_estado = ""
        
        # Cargar el área responsable actual para persistir en el selector
        with Session(engine) as session:
            sol = session.get(Solicitud, solicitud_id)
            if sol and sol.area_responsable:
                self.area_para_asignar = sol.area_responsable
            else:
                self.area_para_asignar = ""

    def abrir_asignar_area(self, solicitud_id: int, area_actual: str):
        """Abre el diálogo para asignar un área a una solicitud con mensaje."""
        self.asignar_area_id = solicitud_id
        self.asignar_area_nombre = area_actual
        self.asignar_area_seleccionada = area_actual or "Atención al Ciudadano"
        self.asignar_area_mensaje = ""
        self.mensaje_asignacion = ""

    def cerrar_asignar_area(self):
        """Cierra el diálogo de asignación de área."""
        self.asignar_area_id = 0
        self.asignar_area_nombre = ""
        self.asignar_area_seleccionada = ""
        self.asignar_area_mensaje = ""
        self.mensaje_asignacion = ""

    def asignar_area_con_mensaje(self):
        """Asigna un área a una solicitud y envía un mensaje al ciudadano."""
        self.mensaje_asignacion = ""
        
        area_a_asignar = self.asignar_area_seleccionada or self.asignar_area_nombre
        if not self.asignar_area_id or not area_a_asignar:
            self.mensaje_asignacion = "Selecciona un área válida."
            return
        
        if not self.asignar_area_mensaje:
            self.mensaje_asignacion = "Escribe un mensaje para el ciudadano."
            return
        
        try:
            with Session(engine) as session:
                solicitud_obj = session.get(Solicitud, self.asignar_area_id)
                if not solicitud_obj:
                    self.mensaje_asignacion = "Solicitud no encontrada."
                    return
                
                estado_anterior = solicitud_obj.estado
                estado_nuevo = "Asignada a Area" if estado_anterior == "Radicada" else estado_anterior
                
                solicitud_obj.estado = estado_nuevo
                solicitud_obj.area_responsable = area_a_asignar
                session.add(solicitud_obj)
                
                # Crear registro en la bitácora / historial
                prefix = f"[ÁREA: {area_a_asignar}]"
                obs_historial = prefix + ("\n" + self.asignar_area_mensaje if self.asignar_area_mensaje else "")
                
                historial = SolicitudEstadoHistorial(
                    solicitud_id=solicitud_obj.id,
                    estado_anterior=estado_anterior,
                    estado_nuevo=estado_nuevo,
                    fecha_cambio=datetime.now(timezone.utc),
                    observaciones=obs_historial,
                    documento_adjunto=None,
                )
                session.add(historial)
                session.commit()
            
            # Enviar notificación por correo al ciudadano
            solicitud_info = None
            for sol in self.solicitudes:
                if sol['id'] == self.asignar_area_id:
                    solicitud_info = sol
                    break
            
            if solicitud_info:
                area_a_asignar = self.asignar_area_seleccionada or self.asignar_area_nombre
                asunto_email = f"Tu solicitud PQRS ha sido asignada a {area_a_asignar}"
                cuerpo_email = f"""
Estimado ciudadano,

Tu solicitud PQRS con número de radicado {solicitud_info['radicado']} ha sido asignada a {area_a_asignar} para su tratamiento.

Detalles de la solicitud:
- Tipo: {solicitud_info['tipo_solicitud']}
- Asunto: {solicitud_info['asunto']}
- Área responsable: {area_a_asignar}

Mensaje del funcionario:
{self.asignar_area_mensaje}

Puedes consultar el estado completo de tu solicitud en nuestro portal web.

Atentamente,
Equipo de Atención al Ciudadano
Sistema PQRS
"""

                # Enviar correo al ciudadano
                enviar_correo_notificacion(solicitud_info['creado_por'], asunto_email, cuerpo_email)
            
            self.mensaje_asignacion = f"Área asignada a {area_a_asignar} y mensaje enviado correctamente."
            self.cargar_solicitudes()
            self.cerrar_asignar_area()
        except Exception as e:
            self.mensaje_asignacion = f"Error asignando área: {e}"

    def _solicitud_a_dict(self, solicitud: Solicitud) -> dict[str, Any]:
        respuesta_text = solicitud.respuesta or ""
        respuesta_documento_basename = None
        if respuesta_text:
            match = re.search(r"\[DOCUMENTO ADJUNTO:\s*([^\]\|]+)\]", respuesta_text)
            if match:
                respuesta_documento_basename = match.group(1).strip()
                respuesta_text = re.sub(r"\s*\[DOCUMENTO ADJUNTO:[^\]]+\]", "", respuesta_text).strip()

        documento_basenames = []
        if solicitud.documento_basename:
            try:
                parsed_names = json.loads(solicitud.documento_basename)
                if isinstance(parsed_names, list):
                    documento_basenames = parsed_names
                else:
                    documento_basenames = [parsed_names]
            except Exception:
                documento_basenames = [solicitud.documento_basename]

        documento_paths = []
        if solicitud.documento:
            try:
                parsed_paths = json.loads(solicitud.documento)
                if isinstance(parsed_paths, list):
                    documento_paths = parsed_paths
                else:
                    documento_paths = [parsed_paths]
            except Exception:
                documento_paths = [solicitud.documento]

        documento_adjuntos = []
        for idx, path in enumerate(documento_paths):
            basename = documento_basenames[idx] if idx < len(documento_basenames) else os.path.basename(str(path).replace("\\", "/"))
            documento_adjuntos.append(construir_metadata_adjunto(str(path), str(basename)))

        documento_basename = documento_adjuntos[0]["basename"] if documento_adjuntos else ""
        documento_href = documento_adjuntos[0]["href"] if documento_adjuntos else ""

        if not respuesta_documento_basename and solicitud.id:
            fallback_hist = _ultimo_adjunto_historial(solicitud.id)
            if fallback_hist:
                respuesta_documento_basename = fallback_hist

        respuesta_meta = (
            construir_metadata_adjunto(respuesta_documento_basename)
            if respuesta_documento_basename
            else {}
        )
        if respuesta_meta.get("basename"):
            respuesta_documento_basename = respuesta_meta["basename"]

        respuesta_adjuntos = []
        if respuesta_documento_basename:
            for p in respuesta_documento_basename.split(","):
                p = p.strip()
                if p:
                    m = construir_metadata_adjunto(p)
                    respuesta_adjuntos.append({
                        "documento_adjunto": str(m.get("basename", p)),
                        "documento_href": str(m.get("href", "")),
                        "documento_preview_src": str(m.get("preview_src", "")),
                        "documento_existe": bool(m.get("existe", False)),
                        "es_imagen": bool(m.get("es_imagen", False)),
                        "es_pdf": bool(m.get("es_pdf", False)),
                    })

        result: dict[str, Any] = {
            "id": solicitud.id,
            "radicado": solicitud.radicado,
            "tipo_solicitud": solicitud.tipo_solicitud,
            "persona_vulnerable": solicitud.persona_vulnerable,
            "asunto": solicitud.asunto,
            "descripcion": solicitud.descripcion,
            "ubicacion": solicitud.ubicacion,
            "area_responsable": solicitud.area_responsable,
            "documento": solicitud.documento,
            "documento_basename": documento_basename,
            "documento_href": documento_href,
            "documento_adjuntos": documento_adjuntos,
            "documento_adjuntos_json": json.dumps(documento_adjuntos),
            "estado": solicitud.estado,
            "respuesta": respuesta_text,
            "respuesta_documento_basename": respuesta_documento_basename or "",
            "respuesta_documento_href": respuesta_meta.get("href", ""),
            "respuesta_documento_es_imagen": respuesta_meta.get("es_imagen", False),
            "respuesta_documento_preview_src": respuesta_meta.get("preview_src", ""),
            "respuesta_documento_existe": respuesta_meta.get("existe", False),
            "fecha": solicitud.fecha.strftime("%Y-%m-%d %H:%M") if isinstance(solicitud.fecha, datetime) else str(solicitud.fecha),
            "creado_por": solicitud.creado_por,
            "usuario_id": solicitud.usuario_id,
            "calificacion_servicio": solicitud.calificacion_servicio,
            "fecha_consulta_ciudadano": solicitud.fecha_consulta_ciudadano.isoformat() if solicitud.fecha_consulta_ciudadano else None,
            "respuesta_adjuntos": respuesta_adjuntos,
        }

        try:
            if solicitud.documento:
                parsed = json.loads(solicitud.documento)
                if isinstance(parsed, dict):
                    if "tiempo_respuesta_dias" in parsed:
                        result["tiempo_respuesta_dias"] = parsed.get("tiempo_respuesta_dias")
                    if "fecha_respuesta" in parsed:
                        result["fecha_respuesta"] = parsed.get("fecha_respuesta")
                    if "cumple_plazo" in parsed:
                        result["cumple_plazo"] = parsed.get("cumple_plazo")
        except Exception:
            logger.exception("Error parseando campo 'documento' de solicitud %s", getattr(solicitud, 'id', None))

        return result
        
        

    @rx.var
    def solicitud_consultada_adjuntos(self) -> list[dict[str, str]]:
        docs = self.solicitud_consultada.get("documento_adjuntos", [])
        if not isinstance(docs, list):
            return []

        resultado = []
        for doc in docs:
            if isinstance(doc, dict):
                resultado.append({
                    "basename": str(doc.get("basename", "")),
                    "href": str(doc.get("href", "")),
                    "preview_src": str(doc.get("preview_src", "")),
                    "existe": bool(doc.get("existe", False)),
                })
        return resultado

    @rx.var
    def solicitud_consultada_respuesta_adjuntos(self) -> list[AdjuntoMeta]:
        docs = self.solicitud_consultada.get("respuesta_adjuntos", [])
        if not isinstance(docs, list):
            return []

        resultado = []
        for doc in docs:
            if isinstance(doc, dict):
                resultado.append(AdjuntoMeta(
                    documento_adjunto=str(doc.get("documento_adjunto", "")),
                    documento_href=str(doc.get("documento_href", "")),
                    documento_preview_src=str(doc.get("documento_preview_src", "")),
                    documento_existe=bool(doc.get("documento_existe", False)),
                    es_imagen=bool(doc.get("es_imagen", False)),
                    es_pdf=bool(doc.get("es_pdf", False))
                ))
        return resultado

    @rx.var
    def solicitud_consultada_respuesta_documento_href(self) -> str:
        return str(self.solicitud_consultada.get("respuesta_documento_href") or "")

    @rx.var
    def solicitud_consultada_respuesta_documento_basename(self) -> str:
        return str(self.solicitud_consultada.get("respuesta_documento_basename") or "")

    @rx.var
    def solicitud_consultada_respuesta_documento_preview_src(self) -> str:
        return str(self.solicitud_consultada.get("respuesta_documento_preview_src") or "")

    @rx.var
    def solicitud_consultada_tiene_adjunto_respuesta(self) -> bool:
        basename = self.solicitud_consultada.get("respuesta_documento_basename")
        return bool(basename and str(basename).strip())

    @rx.var
    def solicitud_consultada_adjunto_respuesta_existe(self) -> bool:
        return bool(self.solicitud_consultada.get("respuesta_documento_existe"))

    def _enriquecer_solicitud_dict(self, s: dict[str, Any]) -> dict[str, Any]:
        """Normaliza estado, fecha_respuesta y semáforo para una solicitud en memoria."""
        est = s.get("estado", "")
        area = s.get("area_responsable")
        if est not in ["Radicada", "Asignada a Area", "Solucionada", "Cerrada", "Reabierta", "En Gestion de Area"]:
            if area and str(area).strip() != "":
                s["estado"] = "Asignada a Area"
            else:
                s["estado"] = "Radicada"
        try:
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT fecha_respuesta FROM solicitud WHERE id = :id"),
                    {"id": s.get("id")},
                ).fetchone()
                s["fecha_respuesta"] = str(row[0]) if row and row[0] else None
        except Exception:
            s["fecha_respuesta"] = None
        try:
            sem = State._compute_remaining_for_solicitud(s)
            s["semaforo_remaining"] = sem.get("remaining")
            s["semaforo_fill"] = sem.get("fill")
            s["semaforo_width"] = sem.get("width", 0)
            s["semaforo_expired"] = s["semaforo_remaining"] is not None and s["semaforo_remaining"] <= 0
        except Exception:
            s["semaforo_remaining"] = None
            s["semaforo_fill"] = "gray"
            s["semaforo_width"] = 0
            s["semaforo_expired"] = False
        return s

    def _refrescar_solicitud_en_lista(self, solicitud_id: int) -> None:
        """Actualiza solo la solicitud modificada sin recargar todo el dashboard."""
        try:
            with Session(engine) as session:
                obj = session.get(Solicitud, solicitud_id)
                if not obj:
                    return
                actualizado = self._enriquecer_solicitud_dict(self._solicitud_a_dict(obj))
            self.solicitudes = [
                actualizado if s.get("id") == solicitud_id else s
                for s in self.solicitudes
            ]
        except Exception as e:
            print(f"Error refrescando solicitud {solicitud_id}: {e}")

    def cargar_solicitudes(self):
        if not self.es_autenticada:
            self.solicitudes = []
            return
        try:
            with rx.session() as session:
                query = select(Solicitud).order_by(Solicitud.fecha.desc())
                if self.rol_usuario == "ciudadano":
                    # Usar email_actual; si está vacío (sesión antigua) usar correo_usuario como fallback
                    email_filtro = str(self.email_actual or self.correo_usuario or "").strip().lower()
                    if email_filtro:
                        query = query.where(Solicitud.creado_por == email_filtro)
                    else:
                        # Sin email identificado: mostrar lista vacía en lugar de TODAS las solicitudes
                        self.solicitudes = []
                        return
                solicitudes_obj = session.exec(query).all()
                self.solicitudes = [
                    self._enriquecer_solicitud_dict(self._solicitud_a_dict(s))
                    for s in solicitudes_obj
                ]
        except Exception as e:
            print(f"Error cargando solicitudes: {e}")
            self.solicitudes = []

    def hidratar_sesion_ciudadano(self):
        """Sincroniza nombre, email y rol desde BD. Si la sesión es fantasma, hace logout."""
        if not self.es_autenticada:
            self.cargar_solicitudes()
            return

        email = str(self.email_actual or self.correo_usuario or "").strip().lower()
        uid_str = str(self.id_usuario or "0").strip()

        # ── Sesión fantasma: autenticado pero sin ningún identificador ──
        if not email and uid_str in ("0", ""):
            pass  # Sesión fantasma — limpiar y redirigir
            self.es_autentica = "false"
            self.email_actual = ""
            self.correo_usuario = ""
            self.id_usuario = "0"
            self.rol_usuario = ""
            self.nombres = ""
            self.solicitudes = []
            return rx.redirect("/login")

        user = None
        try:
            with rx.session() as session:
                if email:
                    user = session.exec(select(Usuario).where(Usuario.email == email)).first()
                if not user and uid_str not in ("0", ""):
                    try:
                        user = session.exec(select(Usuario).where(Usuario.id == int(uid_str))).first()
                    except Exception:
                        logger.exception("Error buscando usuario por id: %s", uid_str)
                if user:
                    self.email_actual = user.email
                    self.correo_usuario = user.email
                    self.id_usuario = str(user.id)
                    self.rol_usuario = user.rol or "ciudadano"
                    self.nombres = str(user.nombres or "").strip()

                else:
                    # Usuario no encontrado en BD — sesión inválida, forzar logout

                    self.es_autentica = "false"
                    self.email_actual = ""
                    self.correo_usuario = ""
                    self.id_usuario = "0"
                    self.rol_usuario = ""
                    self.nombres = ""
                    self.solicitudes = []
                    return rx.redirect("/login")
        except Exception as e:
            print(f"[HIDRATAR] Error al hidratar sesión: {e}")
        self.cargar_solicitudes()


    def cargar_datos_funcionario(self):
        self.cargar_solicitudes()
        self.cargar_usuarios()

    def export_reportes_excel(self):
        """Genera un Excel en memoria desde `solicitudes_filtradas` con gráfica incluida."""
        try:
            from datetime import datetime

            data = _sanitizar_datos_exportacion(self.solicitudes_filtradas or [])
            if not data:
                self.mostrar_toast("No hay datos para exportar.", "warning")
                self.mostrar_menu_descarga = False
                return

            try:
                excel_bytes = generar_excel_filtrado_con_grafica(
                    data,
                    self.filter_tipo_solicitud,
                )
                filename = _nombre_archivo_excel_reporte(self.filter_tipo_solicitud)
                download_id = str(uuid.uuid4())

                TEMP_DOWNLOADS[download_id] = {
                    "data": excel_bytes,
                    "filename": filename,
                    "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                }

                self.export_filename = filename
                self.mostrar_toast(
                    f"Excel con gráfica generado. {len(data)} registros ({self.filter_tipo_solicitud}).",
                    "success",
                )
                self.mostrar_menu_descarga = False
                self.export_href = f"/api/download/{download_id}"

            except (ImportError, ModuleNotFoundError):
                self.export_reportes_csv()

        except Exception as e:
            print(f"ERROR CRITICO en export_reportes_excel: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_toast(f"Error: {str(e)[:100]}", "error")
            self.mostrar_menu_descarga = False


    def descargar_reporte_excel(self):
        """Descarga el archivo Excel generado"""
        try:
            if not self.export_filename:
                self.mostrar_toast("No hay archivo para descargar.", "warning")
                return
            
            filepath = os.path.join(UPLOAD_DIR, self.export_filename)
            if not os.path.exists(filepath):
                self.mostrar_toast(f"Archivo no encontrado: {self.export_filename}", "error")
                self.export_filename = ""
                self.export_href = ""
                return
            
            # Leer el archivo y preparar para descarga
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Usar rx.download para forzar la descarga
            return rx.download(
                data=content,
                filename=self.export_filename,
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            print(f"ERROR en descargar_reporte_excel: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_toast(f"Error descargando: {str(e)}", "error")

    def _validar_registro_basico(self) -> None:
        self.error_de_registro = ""
        if not self.validacion_de_entradas():
            return
        required_fields = [
            ("nombres", "Nombre"),
            ("apellidos", "Apellido"),
            ("tipo_identificacion", "Tipo de identificación"),
            ("numero_identificacion", "Número de identificación"),
            ("telefono", "Teléfono"),
            ("direccion", "Dirección"),
            ("departamento", "Departamento"),
            ("ciudad", "Ciudad"),
        ]
        for field_name, label in required_fields:
            if not str(getattr(self, field_name, "")).strip():
                self.error_de_registro = f"Completa el campo obligatorio: {label}."
                return

        if len(re.sub(r"\D", "", str(self.telefono))) < 7:
            self.error_de_registro = "Ingresa un teléfono válido con al menos 7 dígitos."
            return

        if len(str(self.numero_identificacion).strip()) < 6:
            self.error_de_registro = "El número de identificación debe tener al menos 6 caracteres."
            return

        if not self.acepta_politica_datos or not self.acepta_notificaciones:
            self.error_de_registro = "Debes aceptar la política de datos y recibir notificaciones para registrarte."
            return

    def _crear_usuario(self, rol: str, éxito_mensaje: str):
        with rx.session() as session:
            correo_normalizado = str(self.correo or "").strip().lower()
            existing_user = session.exec(select(Usuario).where(Usuario.email == correo_normalizado)).first()
            if existing_user:
                self.error_de_registro = "El correo ya está registrado."
                return
            hashed = tiene_password(self.contraseña)
            nuevo_usuario = Usuario(
                email=correo_normalizado,
                Contraseña=hashed,
                rol=rol,
                is_active=True,
                Fecha_de_creacion=datetime.now(timezone.utc),
                tipo_identificacion=str(self.tipo_identificacion or "").strip(),
                numero_identificacion=str(self.numero_identificacion or "").strip(),
                nombres=normalizar_texto(self.nombres),
                apellidos=normalizar_texto(self.apellidos),
                genero=normalizar_texto(self.sexo),
                direccion=str(self.direccion or "").strip(),
                telefono=str(self.telefono or "").strip(),
                departamento=str(self.departamento or "").strip(),
                ciudad=str(self.ciudad or "").strip(),
                etnia=normalizar_texto(self.etnia),
                persona_vulnerable=normalizar_texto(self.persona_vulnerable_registro),
                acepta_notificaciones=bool(self.acepta_notificaciones),
                acepta_politica_datos=bool(self.acepta_politica_datos),
            )
            session.add(nuevo_usuario)
            session.commit()
        print(f"Usuario registrado: {self.correo}")
        # Dispara el correo de bienvenida inmediatamente después del registro.
        enviar_correo_bienvenida(self.correo, self.correo)
        self.succes = éxito_mensaje
        self.mostrar_toast("¡Registro exitoso! Bienvenido al sistema.", "success")
        # Obtener el id del usuario recién creado para completar la sesión
        correo_registrado = str(self.correo or "").strip().lower()
        try:
            with rx.session() as session:
                nuevo = session.exec(select(Usuario).where(Usuario.email == correo_registrado)).first()
                if nuevo:
                    self.id_usuario = str(nuevo.id)
                    self.nombres = getattr(nuevo, "nombres", "") or ""
        except Exception as e:
            print(f"No se pudo cargar el id del nuevo usuario: {e}")
        self.limpiar_formulario_registro()
        # Login automático después del registro — asignar TODAS las cookies de sesión
        # igual que en login() para que el filtro de solicitudes funcione correctamente
        self.es_autentica = "true"
        self.email_actual = correo_registrado   # ← clave: el filtro WHERE usa esta cookie
        self.correo_usuario = correo_registrado
        self.rol_usuario = rol
        self.cargar_solicitudes()   # ahora filtra solo las del ciudadano (ninguna por ser nuevo)
        self.cargar_usuarios()

    def signup(self):
        self.borrar_mensajes_de_estado()
        self._validar_registro_basico()
        if self.error_de_registro:
            return
        self._crear_usuario(
            rol="ciudadano",
            éxito_mensaje="Registro exitoso. Revisa tu correo para confirmar. Ahora el funcionario puede iniciar sesión.",
        )
        # Redirigir al dashboard del ciudadano después del registro
        if not self.error_de_registro:
            return rx.redirect("/dashboard")

    def signup_funcionario(self):
        self.borrar_mensajes_de_estado()
        if not self.es_autenticada or self.rol_usuario != "funcionario":
            self.error_de_registro = "Solo los funcionarios autenticados pueden registrar nuevos funcionarios."
            return
        self._validar_registro_basico()
        if self.error_de_registro:
            return
        return self._crear_usuario(
            rol="funcionario",
            éxito_mensaje="Funcionario registrado con ééxito. Ahora puede iniciar sesión con su correo institucional.",
        )

    def login(self, form_data: dict | None = None):
        self.borrar_mensajes_de_estado()
        if form_data:
            self.correo = str(form_data.get("correo") or self.correo or "").strip().lower()
            self.contraseña = str(form_data.get("contraseña") or self.contraseña or "")
        else:
            self.correo = str(self.correo or "").strip().lower()
        if not self.correo or not self.correo.strip():
            self.succes2 = ""
            self.error_de_contraseña = "El correo electrónico es obligatorio."
            return
            
        if not self.contraseña or not self.contraseña.strip():
            self.succes2 = ""
            self.error_de_contraseña = "La contraseña es obligatoria."
            return
        with Session(engine) as session:
            user = session.exec(select(Usuario).where(Usuario.email == self.correo)).first()
            pw_ok = False
            try:
                pw_ok = confirmar_contraseña(self.contraseña, user.Contraseña) if user else False
            except Exception:
                pw_ok = False
            if not user or not pw_ok:
                self.error_de_contraseña = "Correo o contraseña incorrectos."
                color="red"
                self.succes2 = ""
                return
            if not user.is_active:
                self.error_de_contraseña = "La cuenta no está activa."
                color="red"
                self.succes2 = ""
                return
            self.id_usuario = str(user.id)
            self.rol_usuario = user.rol
            self.email_actual = user.email
            self.nombres = getattr(user, 'nombres', 'Ciudadano')  # Extraer nombre si existe en DB
            self.es_autentica = "true"
            self.cargar_solicitudes()
            self.cargar_usuarios()
            self.error_de_contraseña = ""
            self.contraseña = ""
            self.confirmar_contraseña = ""
            self.show_password = False
            self.mostrar_toast("Inicio de sesión exitoso! Redirigiendo automáticamente...", "success")
            # Redirigir después de mostrar el toast
            if self.rol_usuario == "funcionario":
                return rx.redirect("/dashboard-funcionario")
            else:
                return rx.redirect("/dashboard")
        

    def redirect_after_login(self):
        if self.rol_usuario == "funcionario":
            return rx.redirect("/dashboard-funcionario")
        return rx.redirect("/dashboard")

    def abrir_logout_confirm(self):
        """Muestra el modal de confirmación de cierre de sesión."""
        self.show_logout_confirm = True

    def cerrar_logout_confirm(self):
        """Cierra el modal de confirmación sin hacer logout."""
        self.show_logout_confirm = False

    def logout(self):
        "cerrar sesion de usuario"
        self.show_logout_confirm = False
        self.id_usuario = "0"
        self.correo = ""
        self.contraseña = ""
        self.confirmar_contraseña = ""
        self.rol_usuario = ""
        self.email_actual = ""
        self.es_autentica = "false"
        self.nombres = ""
        self.show_password = False
        self.succes2 = "Has cerrado sesión éxitosamente."
        self.error_de_contraseña = ""
        return rx.redirect("/")

    def change_password(self):
        """Cambiar la contraseña usuario autenticado"""
        self.change_pw_message = ""
        if not self.es_autenticada or not self.id_usuario_num:
            self.change_pw_message = "Debes iniciar sesión para cambiar la contraseña."
            return
        # Validaciones básicas
        if not self.current_password or not self.new_password or not self.confirm_new_password:
            self.change_pw_message = "Completa todos los campos."
            return
        if self.new_password != self.confirm_new_password:
            self.change_pw_message = "La nueva contraseña y su confirmación no coinciden."
            return
        if not cantida_minima_contraseña(self.new_password):
            self.change_pw_message = "La nueva contraseña no cumple los requisitos de seguridad."
            return
        with Session(engine) as session:
            user = session.exec(select(Usuario).where(Usuario.id == self.id_usuario_num)).first()
            if not user:
                self.change_pw_message = "Usuario no encontrado."
                return
            try:
                if not confirmar_contraseña(self.current_password, user.Contraseña):
                    self.change_pw_message = "La contraseña actual es incorrecta."
                    return
            except Exception as e:
                self.change_pw_message = f"Error comprobando contraseña: {e}"
                return
            # Actualizar contraseña
            user.Contraseña = tiene_password(self.new_password)
            session.add(user)
            session.commit()
            self.change_pw_message = "Contraseña cambiada correctamente."
            # Limpiar campos
            self.current_password = ""
            self.new_password = ""
            self.confirm_new_password = ""

    def toggle_show_password(self):
        self.show_password = not self.show_password

    def limpiar_formulario_solicitud(self, keep_message: bool = False):
        self.tipo_solicitud = ""
        self.persona_vulnerable = ""
        self.asunto = ""
        self.descripcion = ""
        self.ubicacion = ""
        self.documento = ""
        self.documentos = []
        self.documento_nombres = []
        self.documento_nombre = ""
        self.documento_previews = []
        self.area_responsable = ""
        self.area_otro = ""
        self.descripcion_len = 0
        self.editar_solicitud_id = 0
        self.pqrs_contacto_email = ""
        self.acepta_politica_solicitud = False
        if not keep_message:
            self.solicitud_mensaje = ""

    async def crear_solicitud(self, files: list[rx.UploadFile] = None):
        self.solicitud_mensaje = ""
        if not self.tipo_solicitud or not self.asunto or not self.descripcion:
            self.solicitud_mensaje = "Completa los campos obligatorios antes de enviar."
            yield State.clear_mensajes_delay
            return

        # Validación de correo para usuarios no registrados
        if not self.es_autenticada:
            if not self.pqrs_contacto_email:
                self.solicitud_mensaje = "Por favor ingresa un correo electrónico para recibir respuesta."
                yield State.clear_mensajes_delay
                return
            if not validar_correo(self.pqrs_contacto_email):
                self.solicitud_mensaje = "El correo electrónico ingresado no es válido."
                yield State.clear_mensajes_delay
                return
        if not self.area_responsable:
            self.solicitud_mensaje = "Selecciona el área responsable."
            yield State.clear_mensajes_delay
            return
        if self.area_responsable == "Otros" and not self.area_otro:
            self.solicitud_mensaje = "Por favor indica el área responsable cuando eliges Otros."
            yield State.clear_mensajes_delay
            return
        # Verificar aceptación de política de tratamiento de datos
        if not self.acepta_politica_solicitud:
            self.solicitud_mensaje = "Debes aceptar la Política de Tratamiento de Datos Personales antes de enviar."
            yield State.clear_mensajes_delay
            return

        documentos_guardados: list[str] = []
        documento_basenames_guardados: list[str] = []

        def guardar_archivo(item: Any) -> None:
            nombre_pref = ""
            if isinstance(item, dict):
                nombre_pref = str(item.get("name") or item.get("filename") or "")
            ruta = persistir_archivo_en_uploads(
                item,
                nombre_preferido=nombre_pref,
                prefijo="solicitud",
            )
            if not ruta:
                etiqueta = nombre_pref or "adjunto"
                raise ValueError(f"No se pudo guardar el archivo '{etiqueta}' en el servidor.")
            basename = os.path.basename(ruta)
            documentos_guardados.append(basename)
            documento_basenames_guardados.append(basename)

        if files:
            try:
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                os.makedirs(WEB_UPLOAD_DIR, exist_ok=True)
                for item in files:
                    if hasattr(item, "read"):
                        upload_data = await item.read()
                        guardar_archivo({"name": getattr(item, "filename", getattr(item, "name", "adjunto")), "content": upload_data})
                    else:
                        guardar_archivo(item)
            except Exception as e:
                self.solicitud_mensaje = f"Error guardando documento: {e}"
                yield State.clear_mensajes_delay
                return
        elif self.documentos:
            try:
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                os.makedirs(WEB_UPLOAD_DIR, exist_ok=True)
                for item in self.documentos:
                    guardar_archivo(item)
            except Exception as e:
                self.solicitud_mensaje = f"Error guardando documento: {e}"
                yield State.clear_mensajes_delay
                return
        elif self.documento:
            try:
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                os.makedirs(WEB_UPLOAD_DIR, exist_ok=True)
                guardar_archivo(self.documento)
            except Exception as e:

                self.solicitud_mensaje = f"Error guardando documento: {e}"
                yield State.clear_mensajes_delay
                return

        if self.editar_solicitud_id:
            try:
                with rx.session() as session:
                    solicitud_obj = session.get(Solicitud, self.editar_solicitud_id)
                    if not solicitud_obj:
                        self.solicitud_mensaje = "Solicitud no encontrada para editar."
                        yield State.clear_mensajes_delay
                        return
                    # Obtener persona_vulnerable del usuario autenticado
                    usuario = session.get(Usuario, self.id_usuario_num)
                    persona_vulnerable_valor = usuario.persona_vulnerable if usuario else None
                    
                    solicitud_obj.tipo_solicitud = self.tipo_solicitud
                    solicitud_obj.persona_vulnerable = persona_vulnerable_valor or None
                    solicitud_obj.asunto = self.asunto
                    solicitud_obj.descripcion = self.descripcion
                    solicitud_obj.ubicacion = self.ubicacion or None
                    solicitud_obj.area_responsable = self.area_otro if self.area_responsable == "Otros" else self.area_responsable
                    if documentos_guardados:
                        solicitud_obj.documento = json.dumps(documentos_guardados)
                        solicitud_obj.documento_basename = json.dumps(documento_basenames_guardados)
                    solicitud_obj.estado = "Actualizada"
                    session.add(solicitud_obj)
                    session.commit()
                # Enviar notificación de cambio de estado (si hay correo disponible)
                try:
                    correo_dest = self.email_actual or self.correo
                    if correo_dest and isinstance(correo_dest, str) and "@" in correo_dest:
                        fecha_cambio = datetime.now().strftime("%d/%m/%Y %H:%M")
                        notificar_cambio_estado(
                            nombre_solicitante=getattr(self, 'nombres', correo_dest) or correo_dest,
                            correo_solicitante=correo_dest,
                            numero_solicitud=solicitud_obj.radicado,
                            estado_anterior="(anterior)",
                            estado_nuevo=solicitud_obj.estado,
                            fecha_cambio=fecha_cambio,
                            observaciones="Actualizada desde interfaz",
                            correos_adicionales=None
                        )
                except Exception:
                    logger.exception("Error enviando notificación de cambio de estado para solicitud %s", getattr(solicitud_obj, 'id', None))

                self.solicitud_mensaje = "Solicitud actualizada con ééxito."
                self.editar_solicitud_id = 0
                self.limpiar_formulario_solicitud(keep_message=True)
                self.cargar_solicitudes()
                yield State.clear_mensajes_delay
                return
            except Exception as e:
                self.solicitud_mensaje = f"Error actualizando solicitud: {e}"
                yield State.clear_mensajes_delay
                return

        try:
            with rx.session() as session:
                # Obtener persona_vulnerable del usuario autenticado
                usuario = session.get(Usuario, self.id_usuario_num)
                persona_vulnerable_valor = usuario.persona_vulnerable if usuario else None
                
                solicitud_obj = Solicitud(
                    radicado=f"PQRS-{datetime.now().year}-{uuid.uuid4().hex[:8]}".upper(),
                    tipo_solicitud=self.tipo_solicitud,
                    persona_vulnerable=persona_vulnerable_valor or None,
                    asunto=self.asunto,
                    descripcion=self.descripcion,
                    ubicacion=self.ubicacion or None,
                    area_responsable=self.area_otro if self.area_responsable == "Otros" else self.area_responsable,
                    documento=json.dumps(documentos_guardados) if documentos_guardados else None,
                    documento_basename=json.dumps(documento_basenames_guardados) if documento_basenames_guardados else None,
                    estado="Radicada",
                    fecha=datetime.now(timezone.utc),
                    creado_por=self.email_actual if self.es_autenticada else self.pqrs_contacto_email,
                    usuario_id=self.id_usuario_num if self.id_usuario_num else None,
                )
                session.add(solicitud_obj)
                session.commit()
                # Crear registro de historial inicial persistente si la solicitud incluye adjuntos
                try:
                    session.refresh(solicitud_obj)
                    if documentos_guardados:
                        h_init = SolicitudEstadoHistorial(
                            solicitud_id=solicitud_obj.id,
                            estado_anterior="",
                            estado_nuevo=solicitud_obj.estado or "Radicada",
                            fecha_cambio=solicitud_obj.fecha or datetime.now(timezone.utc),
                            observaciones="Solicitud inicial (documentos adjuntos)",
                            documento_adjunto=", ".join(documentos_guardados) if documentos_guardados else None,
                        )
                        session.add(h_init)
                        session.commit()
                except Exception:
                    logger.exception("Error creando historial inicial persistente para solicitud %s", getattr(solicitud_obj, 'id', None))
                radicado_generado = solicitud_obj.radicado
            # Enviar notificación de creación (si hay correo disponible)
            try:
                correo_dest = self.email_actual if self.es_autenticada else self.pqrs_contacto_email
                if correo_dest and isinstance(correo_dest, str) and "@" in correo_dest:
                    fecha_creacion = solicitud_obj.fecha.strftime("%d/%m/%Y %H:%M")
                    fecha_vencimiento = (solicitud_obj.fecha + timedelta(days=15)).strftime("%d/%m/%Y")
                    notificar_solicitud_creada(
                        nombre_solicitante=getattr(self, 'nombres', correo_dest) or correo_dest,
                        correo_solicitante=correo_dest,
                        numero_solicitud=solicitud_obj.radicado,
                        tipo_pqrs=solicitud_obj.tipo_solicitud,
                        fecha_creacion=fecha_creacion,
                        fecha_vencimiento=fecha_vencimiento,
                        correos_adicionales=None
                    )
            except Exception:
                logger.exception("Error enviando notificación de creación de solicitud para %s", getattr(solicitud_obj, 'id', None))

            self.solicitud_mensaje = f"✅ Solicitud enviada con éxito. Radicado: {radicado_generado}"
            self.limpiar_formulario_solicitud(keep_message=True)
            self.cargar_solicitudes()
            yield rx.clear_selected_files("upload_solicitud")
            yield rx.call_script("if(window.__pqrsClear) window.__pqrsClear();")
            yield State.clear_mensajes_delay
        except Exception as e:
            self.solicitud_mensaje = f"Error guardando solicitud: {e}"
            yield rx.clear_selected_files("upload_solicitud")
            yield rx.call_script("if(window.__pqrsClear) window.__pqrsClear();")
            yield State.clear_mensajes_delay

    def editar_solicitud(self, solicitud_id: int):
        try:
            with Session(engine) as session:
                solicitud_obj = session.get(Solicitud, solicitud_id)
                if solicitud_obj:
                    self.editar_solicitud_id = solicitud_id
                    self.tipo_solicitud = solicitud_obj.tipo_solicitud
                    self.asunto = solicitud_obj.asunto
                    self.descripcion = solicitud_obj.descripcion
                    self.ubicacion = solicitud_obj.ubicacion or ""
                    self.area_responsable = solicitud_obj.area_responsable or ""
                    self.area_otro = solicitud_obj.area_responsable if solicitud_obj.area_responsable and solicitud_obj.area_responsable not in ["Secretaría", "Contabilidad", "Bienestar", "Tesorería", "Atención al Ciudadano"] else ""
                    self.persona_vulnerable = solicitud_obj.persona_vulnerable or ""
                    self.documento = solicitud_obj.documento or ""
                    self.solicitud_mensaje = "Editando solicitud. Actualiza los campos y guarda cambios."
                else:
                    self.solicitud_mensaje = "Solicitud no encontrada."
        except Exception as e:
            self.solicitud_mensaje = f"Error cargando solicitud: {e}"

    mostrar_rastreador: bool = False

    def toggle_rastreador(self):
        """Muestra u oculta el campo de rastreo en el dashboard."""
        self.mostrar_rastreador = not self.mostrar_rastreador

    def consultar_desde_dashboard(self):
        """Ejecuta la consulta y redirige a la página de consulta para ver los resultados."""
        self.consultar_estado_solicitud()
        return rx.redirect("/consultar-estado")

    def cerrar_consulta(self):
        """Limpia los campos de consulta y regresa al inicio."""
        self.consulta_radicado = ""
        self.solicitud_consultada = {}
        self.historial_solicitud = []
        if self.es_autentica:
            return rx.redirect("/dashboard")
        return rx.redirect("/")

    def consultar_estado_solicitud(self):
        """Consulta el estado de una solicitud por número de radicado"""
        self.consulta_mensaje = ""
        self.solicitud_consultada = {}
        
        if not self.consulta_radicado:
            self.consulta_mensaje = "Ingresa un número de radicado válido."
            return
        
        try:
            with Session(engine) as session:
                solicitud = session.exec(
                    select(Solicitud).where(Solicitud.radicado == self.consulta_radicado)
                ).first()
                
                if not solicitud:
                    self.consulta_mensaje = "No se encontró una solicitud con ese número de radicado."
                    return
                
                # HU11: registrar fecha_consulta_ciudadano si la solicitud es Solucionada y aún no se registró
                if str(solicitud.estado or "").strip().lower() == "solucionada" and not solicitud.fecha_consulta_ciudadano:
                    solicitud.fecha_consulta_ciudadano = datetime.now(timezone.utc)
                    session.add(solicitud)
                    session.commit()
                    session.refresh(solicitud)

                self.solicitud_consultada = self._solicitud_a_dict(solicitud)
                # HU11: cargar historial de cambios
                self.cargar_historial_solicitud(solicitud.id, session)
                self.consulta_mensaje = "Solicitud encontrada."
                
        except Exception as e:
            self.consulta_mensaje = f"Error consultando solicitud: {e}"

    def cargar_historial_solicitud(self, solicitud_id: int, session=None):
        """Carga el historial de cambios de estado de una solicitud. HU11."""
        try:
            def _query(s):
                items = s.exec(
                    select(SolicitudEstadoHistorial)
                    .where(SolicitudEstadoHistorial.solicitud_id == solicitud_id)
                    .order_by(SolicitudEstadoHistorial.fecha_cambio.desc())
                ).all()
                def _parse_historial(h):
                    obs_raw = h.observaciones or ""
                    area_h = ""
                    obs_clean = obs_raw
                    if obs_raw.startswith("[ÁREA:"):
                        end = obs_raw.find("]")
                        if end != -1:
                            area_h = obs_raw[7:end].strip()
                            obs_clean = obs_raw[end + 1:].lstrip("\n").strip()
                    
                    doc = h.documento_adjunto or ""
                    if not doc:
                        match = re.search(r"\[DOCUMENTO(: ADJUNTO):\s*([^\]\|]+)\]", obs_clean)
                        if match:
                            doc = match.group(1).strip()
                            obs_clean = re.sub(r"\s*\[DOCUMENTO(: ADJUNTO):[^\]]+\]", "", obs_clean).strip()

                    # Construir lista completa de adjuntos (soporta lista separada por comas)
                    documento_adjuntos_list = []
                    if doc:
                        parts = [p.strip() for p in str(doc).split(",") if p and str(p).strip()]
                        for p in parts:
                            try:
                                m = construir_metadata_adjunto(p)
                                documento_adjuntos_list.append(AdjuntoMeta(
                                    documento_adjunto=str(m.get("basename", str(p))),
                                    documento_href=str(m.get("href", "")),
                                    documento_preview_src=str(m.get("preview_src", "")),
                                    documento_existe=bool(m.get("existe", False)),
                                ))
                            except Exception:
                                logger.exception("Error construyendo metadata para adjunto del historial: %s", p)

                    doc_meta = construir_metadata_adjunto(doc) if doc else {}

                    return HistorialSolicitudEvento(
                        estado_anterior=str(h.estado_anterior or ""),
                        estado_nuevo=str(h.estado_nuevo or ""),
                        fecha_cambio=h.fecha_cambio.strftime("%d/%m/%Y %H:%M") if isinstance(h.fecha_cambio, datetime) else str(h.fecha_cambio),
                        observaciones=str(obs_clean or ""),
                        area_asignada=str(area_h or ""),
                        documento_adjunto=str(doc_meta.get("basename", doc) or ""),
                        documento_href=str(doc_meta.get("href", "") or ""),
                        documento_preview_src=str(doc_meta.get("preview_src", "") or ""),
                        documento_existe=bool(doc_meta.get("existe", False)),
                        adjuntos=documento_adjuntos_list,
                    )
                self.historial_solicitud = [_parse_historial(h) for h in items]
                # Añadir una entrada inicial basada en los adjuntos de la solicitud (si existen)
                try:
                    sol = s.get(Solicitud, solicitud_id)
                    if sol and (sol.documento or sol.documento_basename):
                        documento_basenames = []
                        if sol.documento_basename:
                            try:
                                parsed_names = json.loads(sol.documento_basename)
                                documento_basenames = parsed_names if isinstance(parsed_names, list) else [parsed_names]
                            except Exception:
                                documento_basenames = [sol.documento_basename]

                        documento_paths = []
                        if sol.documento:
                            try:
                                parsed_paths = json.loads(sol.documento)
                                documento_paths = parsed_paths if isinstance(parsed_paths, list) else [parsed_paths]
                            except Exception:
                                documento_paths = [sol.documento]

                        nombres = [os.path.basename(p) for p in documento_paths] if documento_paths else documento_basenames
                        primero = nombres[0] if nombres else ""
                        if primero:
                            doc_meta = construir_metadata_adjunto(primero)
                            existe = bool(doc_meta.get("basename") or primero)
                            # Evitar duplicados: si ya hay una entrada en el historial con este basename, no la añadimos
                            ya_presente = any(
                                str(h.get("documento_adjunto", "")) == (doc_meta.get("basename") or primero)
                                for h in self.historial_solicitud
                            )
                            if not ya_presente:
                                entrada_inicial = HistorialSolicitudEvento(
                                    estado_anterior="",
                                    estado_nuevo=str(sol.estado or "Radicada"),
                                    fecha_cambio=sol.fecha.strftime("%d/%m/%Y %H:%M") if isinstance(sol.fecha, datetime) else str(sol.fecha),
                                    observaciones="Solicitud inicial (documento adjunto)",
                                    area_asignada="",
                                    documento_adjunto=str(doc_meta.get("basename", primero) or ""),
                                    documento_href=str(doc_meta.get("href", "") or ""),
                                    documento_preview_src=str(doc_meta.get("preview_src", "") or ""),
                                    documento_existe=bool(doc_meta.get("existe", False)),
                                    adjuntos=[],
                                )
                                # Añadir al final (será la entrada más antigua)
                                self.historial_solicitud.append(entrada_inicial)
                except Exception:
                    logger.exception("Error cargando historial para solicitud %s", solicitud_id)
            if session:
                _query(session)
            else:
                with Session(engine) as s:
                    _query(s)
        except Exception as e:
            logger.exception("Error cargando historial: %s", e)
            self.historial_solicitud = []

    def enviar_calificacion(self):
        self.calificar_solicitud(self.calificacion_opcion)

    def calificar_solicitud(self, estrellas_str: str):
        """Registra la calificación del ciudadano para una solicitud solucionada. HU11."""
        self.calificacion_mensaje = ""
        try:
            if not estrellas_str:
                self.calificacion_mensaje = "Selecciona una calificación."
                return
            estrellas = int(str(estrellas_str).split(" - ")[0])
        except Exception:
            self.calificacion_mensaje = "Calificación inválida."
            return
        radicado = self.solicitud_consultada.get("radicado", "")
        if not radicado:
            self.calificacion_mensaje = "Primero consulta una solicitud."
            return
        if estrellas < 1 or estrellas > 5:
            self.calificacion_mensaje = "Calificación inválida."
            return
        try:
            with Session(engine) as session:
                sol = session.exec(
                    select(Solicitud).where(Solicitud.radicado == radicado)
                ).first()
                if not sol:
                    self.calificacion_mensaje = "Solicitud no encontrada."
                    return
                if sol.calificacion_servicio is not None:
                    self.calificacion_mensaje = "Ya has calificado este servicio."
                    return
                sol.calificacion_servicio = estrellas
                sol.estado = "Cerrada"
                # Guardar el registro en historial
                observacion_texto = f"Ciudadano calificó el servicio con {estrellas} estrella(s)."
                if self.comentario_calificacion.strip():
                    observacion_texto += f" Comentario: {self.comentario_calificacion.strip()}"
                
                h = SolicitudEstadoHistorial(
                    solicitud_id=sol.id,
                    estado_anterior="Solucionada",
                    estado_nuevo="Cerrada",
                    fecha_cambio=datetime.now(timezone.utc),
                    observaciones=observacion_texto,
                )
                session.add(sol)
                session.add(h)
                session.commit()
            self.calificacion_seleccionada = estrellas
            self.solicitud_consultada = {**self.solicitud_consultada, "calificacion_servicio": estrellas, "estado": "Cerrada"}
            self.cargar_historial_solicitud(self.solicitud_consultada.get("id", 0))
            self.calificacion_mensaje = f"¡Gracias! Has calificado el servicio con {estrellas} estrella(s)."
        except Exception as e:
            self.calificacion_mensaje = f"Error al calificar: {e}"

    def auto_cerrar_solucionadas(self):
        """Cierra automáticamente con calificación 5 las PQRS 'Solucionadas' con >5 días hábiles sin evaluar. HU11."""
        from datetime import date, timedelta
        try:
            with Session(engine) as session:
                solucionadas = session.exec(
                    select(Solicitud)
                    .where(Solicitud.estado == "Solucionada")
                    .where(Solicitud.calificacion_servicio == None)
                    .where(Solicitud.fecha_consulta_ciudadano != None)
                ).all()
                hoy = date.today()
                for sol in solucionadas:
                    fecha_consulta = sol.fecha_consulta_ciudadano.date() if sol.fecha_consulta_ciudadano else None
                    if not fecha_consulta:
                        continue
                    # Calcular días hábiles desde consulta
                    dias_habiles = 0
                    cur = fecha_consulta + timedelta(days=1)
                    while cur <= hoy:
                        if cur.weekday() < 5:  # Lunes a viernes
                            dias_habiles += 1
                        cur += timedelta(days=1)
                    if dias_habiles >= 5:
                        sol.calificacion_servicio = 5
                        sol.estado = "Cerrada"
                        h = SolicitudEstadoHistorial(
                            solicitud_id=sol.id,
                            estado_anterior="Solucionada",
                            estado_nuevo="Cerrada",
                            fecha_cambio=datetime.now(timezone.utc),
                            observaciones="Cierre automático: ciudadano no evaluó en 5 días hábiles. Calificación asignada: 5.",
                        )
                        session.add(sol)
                        session.add(h)
                session.commit()
        except Exception as e:
            print(f"Error en auto_cerrar_solucionadas: {e}")


    def cargar_usuarios(self):
        """Carga la lista de usuarios registrados en el sistema"""
        try:
            with rx.session() as session:
                usuarios = session.exec(select(Usuario)).all()
                self.usuarios_registrados = [
                    {
                        "id": u.id,
                        "email": u.email,
                        "nombres": u.nombres or "",
                        "apellidos": u.apellidos or "",
                        "rol": u.rol,
                        "fecha_creacion": u.Fecha_de_creacion.strftime("%Y-%m-%d") if isinstance(u.Fecha_de_creacion, datetime) else str(u.Fecha_de_creacion),
                        "is_active": "Activo" if u.is_active else "Inactivo",
                    }
                    for u in usuarios
                ]
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
            self.usuarios_registrados = []

    def cambiar_rol_ciudadano_a_funcionario(self):
        """Cambia el rol de un ciudadano a funcionario"""
        self.cambiar_rol_mensaje = ""
        
        if not self.cambiar_rol_email:
            self.cambiar_rol_mensaje = "Ingresa el correo del usuario."
            return
        if not self.confirmar_promocion_rol:
            self.cambiar_rol_mensaje = "Debes confirmar la validación del usuario antes de promover el rol."
            return
        
        try:
            with rx.session() as session:
                usuario = session.exec(
                    select(Usuario).where(Usuario.email == self.cambiar_rol_email)
                ).first()
                
                if not usuario:
                    self.cambiar_rol_mensaje = f"No se encontró usuario con el correo {self.cambiar_rol_email}."
                    return
                
                if usuario.rol == "funcionario":
                    self.cambiar_rol_mensaje = f"El usuario ya es funcionario."
                    return
                
                usuario.rol = "funcionario"
                session.add(usuario)
                session.commit()
                
                # Enviar notificación
                try:
                    asunto = "Rol actualizado - Has sido promovido a Funcionario"
                    cuerpo = """
Estimado usuario,

Te informamos que tu rol en el sistema ha sido actualizado.

Tu nuevo rol: FUNCIONARIO

Con este rol podrás:
- Gestionar solicitudes PQRS
- Asignar áreas responsables
- Actualizar estados de solicitudes
- Ver reportes del sistema

Accede al Dashboard Funcionario con tu correo y contraseña.

Atentamente,
Sistema PQRS
"""
                    enviar_correo_notificacion(self.cambiar_rol_email, asunto, cuerpo)
                except:
                    pass  # No fallar si no se envía el correo
                
                self.cambiar_rol_mensaje = f" Rol del usuario {self.cambiar_rol_email} actualizado a funcionario."
                self.cambiar_rol_email = ""
                self.confirmar_promocion_rol = False
                self.cargar_usuarios()
        except Exception as e:
            self.cambiar_rol_mensaje = f"Error al cambiar rol: {e}"

    def degradar_funcionario_a_ciudadano(self, email: str):
        """Cambia el rol de un funcionario a ciudadano (solo funcionarios autenticados)."""
        self.cambiar_rol_mensaje = ""
        if not self.es_autenticada or self.rol_usuario != "funcionario":
            self.cambiar_rol_mensaje = "Solo funcionarios autenticados pueden cambiar roles."
            return
        email_norm = str(email or "").strip().lower()
        if not email_norm:
            self.cambiar_rol_mensaje = "Correo inválido."
            return
        if self.email_actual and str(self.email_actual).strip().lower() == email_norm:
            self.cambiar_rol_mensaje = "No puedes degradarte a ti mismo."
            return

        try:
            with rx.session() as session:
                usuario = session.exec(select(Usuario).where(Usuario.email == email_norm)).first()
                if not usuario:
                    self.cambiar_rol_mensaje = f"No se encontró usuario con el correo {email_norm}."
                    return
                if usuario.rol != "funcionario":
                    self.cambiar_rol_mensaje = f"El usuario {email_norm} no es funcionario."
                    return

                usuario.rol = "ciudadano"
                session.add(usuario)
                session.commit()

            # Notificación (no bloquear si falla)
            try:
                asunto = "Rol actualizado - Has sido asignado como Ciudadano"
                cuerpo = f"""\
Estimado usuario,

Te informamos que tu rol en el sistema ha sido actualizado.

Tu nuevo rol: CIUDADANO

Atentamente,
Sistema PQRS
"""
                enviar_correo_notificacion(email_norm, asunto, cuerpo)
            except Exception:
                pass

            self.cambiar_rol_mensaje = f" Rol del usuario {email_norm} actualizado a ciudadano."
            self.cargar_usuarios()
        except Exception as e:
            self.cambiar_rol_mensaje = f"Error al cambiar rol: {e}"

    def set_cambiar_rol_email(self, value: str):
        self.cambiar_rol_email = str(value or "").strip().lower()
        self.cambiar_rol_mensaje = ""
        self.confirmar_promocion_rol = False

    def set_confirmar_promocion_rol(self, value: bool):
        self.confirmar_promocion_rol = bool(value)

    def limpiar_form_promocion_rol(self):
        self.cambiar_rol_email = ""
        self.confirmar_promocion_rol = False
        self.cambiar_rol_mensaje = ""


    def set_confirmar_contraseña(self, value: str):
        self.confirmar_contraseña = value

    def set_correo(self, value: str):
        self.correo = value

    def set_contraseña(self, value: str):
        self.contraseña = value

    def set_tipo_identificacion(self, value: str):
        self.tipo_identificacion = value

    def set_genero(self, value: str):
        self.genero = value

    def set_sexo(self, value: str):
        self.sexo = value

    def set_direccion(self, value: str):
        self.direccion = value

    def set_current_password(self, value: str):
        self.current_password = value


