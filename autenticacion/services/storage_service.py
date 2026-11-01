"""Servicio de gestión y almacenamiento de archivos y adjuntos."""
import base64
import logging
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import quote

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploaded_files"
WEB_UPLOAD_DIR = BASE_DIR / ".web" / "public" / "uploads"

REFLEX_UPLOAD_DIRS = (
    BASE_DIR / ".web" / "uploaded_files",
    BASE_DIR / ".web" / "backend" / "uploaded_files",
    BASE_DIR / "uploaded_files",
)

EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def sanitizar_nombre_archivo(nombre: str) -> str:
    """Sanitiza un nombre de archivo para evitar problemas de seguridad."""
    nombre = re.sub(r"[^\w\s\-\.]", "", nombre)
    nombre = nombre[:255]
    return nombre or "archivo"


def _resolver_ruta_archivo_existente(ruta: str) -> str:
    """Devuelve ruta absoluta si el archivo existe en disco."""
    if not ruta:
        return ""
    candidato = Path(ruta)
    if candidato.is_file():
        return str(candidato.resolve())

    candidatos_busqueda = [
        candidato,
        BASE_DIR / ruta,
        BASE_DIR / ".web" / ruta,
        BASE_DIR / ".web" / "uploaded_files" / candidato.name,
    ]
    for base in REFLEX_UPLOAD_DIRS:
        candidatos_busqueda.extend([base / candidato.name, base / ruta.lstrip("/\\")])
    candidatos_busqueda.append(UPLOAD_DIR / candidato.name)

    for path in candidatos_busqueda:
        if path.is_file():
            return str(path.resolve())
    return ""


def _es_imagen(nombre: str) -> bool:
    return Path(str(nombre or "")).suffix.lower() in EXTENSIONES_IMAGEN


def asegurar_espejo_web(nombre_archivo: str) -> None:
    """Copia el archivo a .web/public/uploads para servirlo en /uploads/ del frontend."""
    if not nombre_archivo:
        return
    nombre = sanitizar_nombre_archivo(os.path.basename(str(nombre_archivo).replace("\\", "/")))
    origen = UPLOAD_DIR / nombre
    if not origen.is_file():
        resuelto = _resolver_ruta_archivo_existente(nombre_archivo)
        if not resuelto:
            return
        origen = Path(resuelto)
        nombre = origen.name
    os.makedirs(WEB_UPLOAD_DIR, exist_ok=True)
    destino = WEB_UPLOAD_DIR / nombre
    try:
        if not destino.is_file() or destino.stat().st_mtime < origen.stat().st_mtime:
            shutil.copy2(origen, destino)
    except Exception:
        logger.exception("Error copiando archivo a espejo web: %s -> %s", origen, destino)


def url_archivo_adjunto(nombre_archivo: str) -> str:
    """URL relativa para ver o descargar un adjunto persistido."""
    nombre = sanitizar_nombre_archivo(os.path.basename(str(nombre_archivo or "").replace("\\", "/")))
    if not nombre:
        return ""
    asegurar_espejo_web(nombre)
    return f"/uploads/{quote(nombre)}"


def construir_metadata_adjunto(path_o_nombre: str, basename: str = "") -> dict[str, Any]:
    """Metadatos de adjunto para enlaces y vista previa en la UI."""
    raw = str(path_o_nombre or "").replace("\\", "/")
    nombre = sanitizar_nombre_archivo(basename or os.path.basename(raw))
    if not nombre:
        nombre = sanitizar_nombre_archivo(raw)
    ruta_resuelta = _resolver_ruta_archivo_existente(raw) or _resolver_ruta_archivo_existente(nombre)
    if ruta_resuelta:
        nombre = Path(ruta_resuelta).name
        asegurar_espejo_web(nombre)
    href = url_archivo_adjunto(nombre) if nombre and ruta_resuelta else ""
    es_imagen = _es_imagen(nombre)
    return {
        "basename": nombre,
        "href": href,
        "es_imagen": es_imagen,
        "preview_src": href if es_imagen and href else "",
        "existe": bool(ruta_resuelta),
    }


def persistir_archivo_en_uploads(
    item: Any,
    nombre_preferido: str = "",
    prefijo: str = "adjunto",
) -> str:
    """Guarda un archivo subido en UPLOAD_DIR y devuelve la ruta absoluta."""
    if item is None:
        return ""

    if isinstance(item, list):
        if not item:
            return ""
        item = item[0]

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(WEB_UPLOAD_DIR, exist_ok=True)

    def _guardar_bytes(data: bytes, nombre: str) -> str:
        nombre_limpio = sanitizar_nombre_archivo(nombre)
        destino = UPLOAD_DIR / nombre_limpio
        with open(destino, "wb") as f:
            f.write(data)
        destino_web = WEB_UPLOAD_DIR / nombre_limpio
        with open(destino_web, "wb") as f:
            f.write(data)
        return str(destino.resolve())

    if isinstance(item, str):
        if item.startswith("data:"):
            header, b64 = item.split(",", 1)
            mime = header.split(";")[0].split(":")[1] if ":" in header else ""
            ext = mime.split("/")[-1] if "/" in mime else "bin"
            nombre = nombre_preferido or f"{prefijo}_{uuid.uuid4().hex}.{ext}"
            if not os.path.splitext(nombre)[1] and ext not in ("", "bin"):
                nombre = f"{nombre}.{ext}"
            return _guardar_bytes(base64.b64decode(b64), nombre)

        existente = _resolver_ruta_archivo_existente(item)
        if existente:
            destino = UPLOAD_DIR / Path(existente).name
            if Path(existente).resolve() != destino.resolve():
                shutil.copy2(existente, destino)
            destino_web = WEB_UPLOAD_DIR / Path(existente).name
            shutil.copy2(str(destino), str(destino_web))
            return str(destino.resolve())
        return ""

    if isinstance(item, dict):
        nombre = sanitizar_nombre_archivo(
            item.get("name") or item.get("filename") or nombre_preferido or f"{prefijo}_{uuid.uuid4().hex}"
        )
        contenido = item.get("content") or item.get("data") or item.get("file")
        if contenido:
            if isinstance(contenido, str) and contenido.startswith("data:"):
                _, b64 = contenido.split(",", 1)
                data = base64.b64decode(b64)
            elif isinstance(contenido, str):
                data = base64.b64decode(contenido)
            else:
                data = bytes(contenido)
            return _guardar_bytes(data, nombre)

        for clave in ("path", "filepath", "full_path", "tmp_path", "file_path"):
            existente = _resolver_ruta_archivo_existente(str(item.get(clave) or ""))
            if existente:
                destino = UPLOAD_DIR / Path(existente).name
                if Path(existente).resolve() != destino.resolve():
                    shutil.copy2(existente, destino)
                destino_web = WEB_UPLOAD_DIR / Path(existente).name
                shutil.copy2(str(destino), str(destino_web))
                return str(destino.resolve())
        return ""

    nombre_obj = (
        nombre_preferido
        or getattr(item, "filename", None)
        or getattr(item, "name", None)
        or f"{prefijo}_{uuid.uuid4().hex}"
    )
    nombre_final = sanitizar_nombre_archivo(str(nombre_obj))
    for attr in ("path", "file_path", "filepath", "full_path"):
        existente = _resolver_ruta_archivo_existente(str(getattr(item, attr, "") or ""))
        if existente:
            destino = UPLOAD_DIR / nombre_final
            if Path(existente).resolve() != destino.resolve():
                shutil.copy2(existente, destino)
            destino_web = WEB_UPLOAD_DIR / nombre_final
            shutil.copy2(str(destino), str(destino_web))
            return str(destino.resolve())

    file_obj = getattr(item, "file", None)
    if file_obj is not None:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            data = file_obj.read()
            if data:
                return _guardar_bytes(data, nombre_final)
        except Exception:
            logger.exception("Error leyendo objeto archivo en persistir_archivo_en_uploads")

    return ""

