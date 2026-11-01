"""Servicio de correo electrónico y notificaciones."""
import json
import logging
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from notificaciones import (
    enviar_correo_smtp,
    formatear_nota_documento,
    get_app_base_url,
    notificar_cambio_estado,
    notificar_respuesta_final,
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EMAIL_CONFIG_PATH = BASE_DIR / "email_config.json"


def load_email_config() -> dict:
    """Carga configuración de correo desde email_config.json si existe y
    aplica valores a os.environ cuando sea apropiado.
    """
    try:
        if EMAIL_CONFIG_PATH.exists():
            with open(EMAIL_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in cfg.items():
                if v is None:
                    continue
                os.environ.setdefault(k, str(v))
            return cfg
    except Exception as e:
        logger.warning("No se pudo cargar email_config.json: %s", e)
    return {}


def save_email_config(cfg: dict) -> None:
    """Guarda configuración de correo en email_config.json y actualiza os.environ."""
    try:
        with open(EMAIL_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
        for k, v in cfg.items():
            if v is None:
                continue
            os.environ[k] = str(v)
    except Exception as e:
        logger.warning("No se pudo guardar email_config.json: %s", e)


def enviar_correo_bienvenida(email_destinatario: str, email_usuario: str) -> bool:
    """Envía un correo de bienvenida después de un registro exitoso."""
    try:
        email_sender = os.getenv("EMAIL_SENDER", "enlacepqrs1755@gmail.com")
        empresa_nombre = os.getenv("EMPRESA_NOMBRE", "Sistema de Gestión de PQRS")

        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = f"¡Bienvenido a {empresa_nombre}!"
        mensaje["From"] = email_sender
        mensaje["To"] = email_destinatario

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h1 style="color: #1e40af; text-align: center;">¡Bienvenido!</h1>
                    <p style="color: #333; font-size: 16px;">Hola,</p>
                    <p style="color: #333; font-size: 16px;">Tu registro en <strong>{empresa_nombre}</strong> ha sido exitoso. A continuación, encontrarás tus datos de acceso:</p>
                    
                    <div style="background-color: #f0f7ff; padding: 15px; border-left: 4px solid #1e40af; margin: 20px 0; border-radius: 5px;">
                        <p style="margin: 5px 0;"><strong>📧 Correo:</strong> <code>{email_usuario}</code></p>
                    </div>
                    
                    <p style="color: #333; font-size: 16px;">Para iniciar sesión, ingresa a:</p>
                    <p style="text-align: center; margin: 20px 0;">
                        <a href="{get_app_base_url() or 'http://localhost:3000'}/login" style="background-color: #1e40af; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Ir a Iniciar Sesión</a>
                    </p>
                    
                    <hr style="border: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #666; font-size: 14px;"><strong>Recuerda:</strong> Nunca compartas tu contraseña con terceros. El equipo de soporte nunca te pedirá tu contraseña.</p>
                    <p style="color: #666; font-size: 14px;">Si tienes preguntas o problemas, contacta a nuestro equipo de soporte.</p>
                    <p style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">© 2026 {empresa_nombre}. Todos los derechos reservados.</p>
                </div>
            </body>
        </html>
        """

        if enviar_correo_smtp(email_destinatario, mensaje["Subject"], html):
            logger.info("Correo enviado exitosamente a %s vía SMTP", email_destinatario)
            return True

        logger.warning("No se pudo enviar el correo de bienvenida por SMTP a %s", email_destinatario)
        failed_path = BASE_DIR / "failed_emails.log"
        try:
            with open(failed_path, "a", encoding="utf-8") as f:
                f.write(
                    f"{datetime.utcnow().isoformat()} | {email_destinatario} | subject: {mensaje['Subject']}\n{html}\n\n---\n"
                )
        except Exception as e:
            logger.error("No se pudo guardar el correo fallido: %s", e)

        return False
    except Exception as e:
        logger.exception("Error inesperado al preparar correo: %s", e)
        return False


def enviar_correo_notificacion(email_destinatario: str, asunto: str, cuerpo: str) -> bool:
    """Envía una notificación por correo electrónico al ciudadano sobre actualizaciones en su solicitud."""
    try:
        empresa_nombre = os.getenv("EMPRESA_NOMBRE", "Sistema de Gestión de PQRS")
        html = (
            f"<html><body>"
            f"<pre style='font-family:Arial,sans-serif'>{cuerpo}</pre>"
            f"<p style='color:#666;font-size:12px'>© 2026 {empresa_nombre}</p>"
            f"</body></html>"
        )
        if enviar_correo_smtp(email_destinatario, asunto, html):
            logger.info("Notificación enviada a %s (SMTP)", email_destinatario)
            return True
        logger.warning("No se pudo enviar notificación a %s", email_destinatario)
        return False
    except Exception as e:
        logger.exception("Error inesperado al enviar notificación: %s", e)
        return False


def _enviar_notificacion_estado_solicitud(
    datos_notificacion: dict[str, Any],
    documentos_respuesta: list[str],
) -> None:
    """Envía correo de cambio de estado en segundo plano (no bloquear la UI)."""
    if not datos_notificacion or not datos_notificacion.get("correo"):
        return
    try:
        adjuntos_correo: list[str] = []
        notas_documento: list[str] = []
        for doc_path in documentos_respuesta or []:
            if not doc_path:
                continue
            doc_name = os.path.basename(doc_path)
            nota_doc, adj = formatear_nota_documento(doc_name, doc_path)
            if nota_doc:
                notas_documento.append(nota_doc)
            adjuntos_correo.extend(adj)
        nota_total = "".join(notas_documento)
        if datos_notificacion["estado_nuevo"].lower() == "cerrada":
            descripcion_respuesta = datos_notificacion["respuesta"] or "Su solicitud ha sido cerrada."
            descripcion_respuesta += nota_total
            notificar_respuesta_final(
                nombre_solicitante=datos_notificacion["nombre"],
                correo_solicitante=datos_notificacion["correo"],
                numero_solicitud=datos_notificacion["radicado"],
                tipo_pqrs=datos_notificacion["tipo"],
                fecha_respuesta=datetime.now().strftime("%d/%m/%Y %H:%M"),
                descripcion_respuesta=descripcion_respuesta,
                adjuntos=adjuntos_correo or None,
            )
        else:
            area_en_obs = datos_notificacion.get("area_asignada", "")
            observaciones = datos_notificacion["respuesta"] or None
            if nota_total:
                observaciones = (observaciones or "") + nota_total
            notificar_cambio_estado(
                nombre_solicitante=datos_notificacion["nombre"],
                correo_solicitante=datos_notificacion["correo"],
                numero_solicitud=datos_notificacion["radicado"],
                estado_anterior=datos_notificacion["estado_anterior"],
                estado_nuevo=datos_notificacion["estado_nuevo"],
                fecha_cambio=datetime.now().strftime("%d/%m/%Y %H:%M"),
                observaciones=observaciones,
                adjuntos=adjuntos_correo or None,
                area_asignada=area_en_obs or None,
            )
    except Exception as e:
        logger.exception("Error enviando notificación: %s", e)

