"""Módulo de utilidades de seguridad, hashing y validaciones de cadenas."""
import re
from typing import Any
import bcrypt


def tiene_password(password: str) -> str:
    """Genera el hash bcrypt de una contraseña en texto plano."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def confirmar_contraseña(contraseña: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    try:
        return bcrypt.checkpw(contraseña.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def normalizar_texto(valor: Any) -> str:
    """Quita espacios sobrantes y aplica formato título para campos de registro."""
    if valor is None:
        return ""
    texto = re.sub(r"\s+", " ", str(valor).strip())
    return texto.title() if texto else ""


def validar_correo(correo: str) -> bool:
    """Valida formato básico de correo electrónico."""
    if "@" not in correo or "." not in correo:
        return False
    partes = correo.split(".")
    if partes[-1].strip() and len(partes[-1].strip()) >= 2:
        return True
    return False


def cantida_minima_contraseña(contraseña: str) -> bool:
    """Valida que la contraseña cumpla los criterios mínimos de robustez."""
    return (
        len(contraseña) >= 8
        and re.search(r"[A-Z]", contraseña) is not None
        and re.search(r"[a-z]", contraseña) is not None
        and re.search(r"[0-9]", contraseña) is not None
        and re.search(r"[^\w\s]", contraseña) is not None
    )

