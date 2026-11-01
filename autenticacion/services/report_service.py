"""Servicio de generación de reportes y exportación en formato Excel con gráficos."""
import io
import logging
from collections import Counter
from datetime import date, datetime
from typing import Any

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.styles import Font

logger = logging.getLogger(__name__)


def _slug_filtro_excel(filtro_tipo: str) -> str:
    """Normaliza el nombre del filtro para usarlo como identificador en archivos."""
    slug = (filtro_tipo or "todos").strip().lower()
    slug = (
        slug.replace("ó", "o")
        .replace("í", "i")
        .replace("é", "e")
        .replace(" ", "_")
    )
    if slug in {"todos", "todas"}:
        return "general"
    return slug


def _nombre_archivo_excel_reporte(filtro_tipo: str) -> str:
    """Genera un nombre de archivo dinámico con timestamp para el reporte."""
    return f"reporte_pqrs_{_slug_filtro_excel(filtro_tipo)}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"


def _valor_celda_excel(valor: Any) -> Any:
    """Convierte valores de estado Reflex (MutableProxy, listas, fechas, etc.) a tipos compatibles con Excel."""
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        return valor
    if isinstance(valor, str):
        return valor
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(valor, date):
        return valor.isoformat()

    tipo = type(valor).__name__
    if "Proxy" in tipo:
        try:
            if hasattr(valor, "keys"):
                valor = dict(valor)
            else:
                valor = list(valor)
        except Exception:
            return str(valor)

    if isinstance(valor, dict):
        if not valor:
            return ""
        return ", ".join(f"{k}: {_valor_celda_excel(v)}" for k, v in valor.items())

    if isinstance(valor, (list, tuple, set)):
        if not valor:
            return ""
        return ", ".join(str(_valor_celda_excel(v)) for v in valor)

    return str(valor)


def _sanitizar_datos_exportacion(data: list[Any]) -> list[dict[str, Any]]:
    """Convierte solicitudes del estado Reflex a dicts limpios con valores nativos para exportación."""
    limpios: list[dict[str, Any]] = []
    for item in data or []:
        try:
            if hasattr(item, "keys"):
                raw = dict(item)
            elif isinstance(item, dict):
                raw = item
            else:
                continue
        except Exception:
            continue
        limpios.append({str(k): _valor_celda_excel(v) for k, v in raw.items()})
    return limpios


def _clasificar_semaforo_solicitud(solicitud: dict[str, Any]) -> str | None:
    """Devuelve 'Verde', 'Amarillo', 'Rojo' para solicitudes activas, o None si está cerrada."""
    closed_states = {
        "resuelta", "cerrada", "respondida", "finalizada",
        "respondido", "cerrado", "finalizado",
    }
    if str(solicitud.get("estado") or "").strip().lower() in closed_states:
        return None
    if solicitud.get("semaforo_expired"):
        return "Rojo"
    fill = str(solicitud.get("semaforo_fill") or "").lower()
    if fill in {"#ef4444", "red", "rojo"}:
        return "Rojo"
    if fill in {"#f59e0b", "orange", "yellow", "amarillo", "#eab308"}:
        return "Amarillo"
    if fill in {"#10b981", "green", "verde"}:
        return "Verde"
    remaining = solicitud.get("semaforo_remaining")
    if remaining is not None:
        try:
            rem = int(float(str(remaining)))
            if rem <= 0:
                return "Rojo"
            if rem <= 5:
                return "Amarillo"
            return "Verde"
        except Exception:
            logger.exception("Error calculando semáforo restante")
    return None


def generar_excel_filtrado_con_grafica(
    data: list[dict[str, Any]],
    filtro_tipo: str = "Todos",
) -> bytes:
    """Genera un archivo Excel con hoja de datos y hoja de 'Gráfica' con visualizaciones nativas."""
    data = _sanitizar_datos_exportacion(list(data or []))

    wb = Workbook()
    ws_graf = wb.active
    ws_graf.title = "Gráfica"
    ws_data = wb.create_sheet("Solicitudes")

    if data:
        cols_preferidas = [
            "radicado", "tipo_solicitud", "estado", "asunto", "descripcion",
            "creado_por", "fecha", "area_responsable", "fecha_respuesta",
        ]
        todas = list(data[0].keys())
        cols = [c for c in cols_preferidas if c in todas] + [c for c in todas if c not in cols_preferidas]
        ws_data.append(cols)
        for fila in data:
            ws_data.append([fila.get(c, "") for c in cols])
    else:
        ws_data.append(["Sin registros"])

    closed_states = {
        "resuelta", "cerrada", "respondida", "finalizada",
        "respondido", "cerrado", "finalizado",
    }
    estados_counter: Counter[str] = Counter()
    semaforo = {"Verde": 0, "Amarillo": 0, "Rojo": 0}
    for solicitud in data or []:
        est = str(solicitud.get("estado") or "Sin estado").strip()
        estados_counter[est] += 1
        color = _clasificar_semaforo_solicitud(solicitud)
        if color:
            semaforo[color] += 1

    filtro_label = (filtro_tipo or "Todos").strip()
    total = len(data or [])
    cerradas = sum(
        c for e, c in estados_counter.items()
        if e.lower() in closed_states
    )
    no_cerradas = max(0, total - cerradas)
    pct = int((cerradas / total) * 100) if total else 0

    ws_graf["A1"] = f"Reporte PQRS – Filtro: {filtro_label}"
    ws_graf["A1"].font = Font(bold=True, size=16, color="1E3A8A")
    ws_graf.merge_cells("A1:H1")
    ws_graf["A2"] = f"Registros exportados: {total}  |  Cumplimiento: {pct}%"
    ws_graf["A2"].font = Font(size=11, color="475569")

    ws_graf["A4"] = "Estado"
    ws_graf["B4"] = "Cantidad"
    for celda in ("A4", "B4"):
        ws_graf[celda].font = Font(bold=True)

    fila = 5
    for estado, cantidad in sorted(estados_counter.items(), key=lambda x: (-x[1], x[0])):
        ws_graf[f"A{fila}"] = estado
        ws_graf[f"B{fila}"] = cantidad
        fila += 1
    fin_estados = fila - 1

    if fin_estados >= 5:
        bar_estados = BarChart()
        bar_estados.type = "col"
        bar_estados.title = f"Distribución por estado – {filtro_label}"
        bar_estados.y_axis.title = "Cantidad"
        bar_estados.style = 10
        bar_estados.height = 14
        bar_estados.width = 24
        bar_estados.add_data(
            Reference(ws_graf, min_col=2, min_row=4, max_row=fin_estados),
            titles_from_data=True,
        )
        bar_estados.set_categories(
            Reference(ws_graf, min_col=1, min_row=5, max_row=fin_estados)
        )
        ws_graf.add_chart(bar_estados, "D4")

    fila_pie = max(fila + 2, 4)
    ws_graf[f"A{fila_pie}"] = "Nivel de cumplimiento"
    ws_graf[f"A{fila_pie}"].font = Font(bold=True, size=12)
    hdr = fila_pie + 1
    ws_graf[f"A{hdr}"] = "Categoría"
    ws_graf[f"B{hdr}"] = "Cantidad"
    ws_graf[f"A{hdr}"].font = Font(bold=True)
    ws_graf[f"B{hdr}"].font = Font(bold=True)
    ws_graf[f"A{hdr + 1}"] = "Cerradas / Resueltas"
    ws_graf[f"B{hdr + 1}"] = cerradas
    ws_graf[f"A{hdr + 2}"] = "Pendientes"
    ws_graf[f"B{hdr + 2}"] = no_cerradas

    if total > 0 and (cerradas > 0 or no_cerradas > 0):
        pie = PieChart()
        pie.title = f"Cumplimiento: {pct}%"
        pie.height = 12
        pie.width = 16
        pie.add_data(
            Reference(ws_graf, min_col=2, min_row=hdr + 1, max_row=hdr + 2)
        )
        pie.set_categories(
            Reference(ws_graf, min_col=1, min_row=hdr + 1, max_row=hdr + 2)
        )
        ws_graf.add_chart(pie, f"D{fila_pie}")

    sem_total = sum(semaforo.values())
    if sem_total > 0:
        fila_sem = hdr + 5
        ws_graf[f"A{fila_sem}"] = "Semáforo de vencimiento (activas)"
        ws_graf[f"A{fila_sem}"].font = Font(bold=True, size=12)
        sh = fila_sem + 1
        ws_graf[f"A{sh}"] = "Estado"
        ws_graf[f"B{sh}"] = "Cantidad"
        ws_graf[f"A{sh + 1}"] = "Verde"
        ws_graf[f"B{sh + 1}"] = semaforo["Verde"]
        ws_graf[f"A{sh + 2}"] = "Amarillo"
        ws_graf[f"B{sh + 2}"] = semaforo["Amarillo"]
        ws_graf[f"A{sh + 3}"] = "Rojo"
        ws_graf[f"B{sh + 3}"] = semaforo["Rojo"]
        bar_sem = BarChart()
        bar_sem.type = "col"
        bar_sem.title = "Estado de vencimiento"
        bar_sem.height = 12
        bar_sem.width = 18
        bar_sem.add_data(
            Reference(ws_graf, min_col=2, min_row=sh + 1, max_row=sh + 3)
        )
        bar_sem.set_categories(
            Reference(ws_graf, min_col=1, min_row=sh + 1, max_row=sh + 3)
        )
        ws_graf.add_chart(bar_sem, "G4")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

