import re
import pandas as pd
from datetime import datetime, timedelta

def parse_date_posted(text: str, now: datetime = None) -> datetime:
    """
    Convierte un string en español del tipo
      'hace 6 horas', 'hace 41 minutos', 'Publicado de nuevo hace 2 horas', etc.
    en un objeto datetime restando el intervalo correspondiente a `now`.

    Parámetros
    ----------
    text : str
        Cadena que contiene 'hace N unidad(es)' posiblemente precedida por
        otros textos.
    now : datetime, opcional
        Fecha y hora de referencia. Por defecto datetime.now().

    Devuelve
    -------
    datetime
        Momento aproximado en que se publicó (now - delta).
    """
    if now is None:
        now = datetime.now()

    # Buscamos "hace N unidad" (minuto(s), hora(s), día(s), semana(s))
    m = re.search(
        r'hace\s+(\d+)\s+'
        r'(minuto|minutos|hora|horas|día|días|semana|semanas)',
        text,
        flags=re.IGNORECASE
    )
    if not m:
        raise ValueError(f"No pude parsear la fecha de: {text!r}")

    cantidad = int(m.group(1))
    unidad = m.group(2).lower()

    if unidad.startswith('minuto'):
        delta = timedelta(minutes=cantidad)
    elif unidad.startswith('hora'):
        delta = timedelta(hours=cantidad)
    elif unidad.startswith('día'):
        delta = timedelta(days=cantidad)
    elif unidad.startswith('semana'):
        delta = timedelta(weeks=cantidad)
    else:
        # por si más adelante quisieras soportar otros periodos
        raise ValueError(f"Unidad no soportada: {unidad!r}")

    return now - delta
