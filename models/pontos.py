# models/pontos.py
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Pontos:
    id: Optional[int]
    estado: str
    codigo: str
    municipio: str
    data: date
    latitude: float
    longitude: float
    cultura: str
    estadiofenolog: str
    altitude: Optional[int] = None
    temperatura: Optional[float] = None
    tpsafra: Optional[str] = None
    informante: Optional[str] = None
    emailinfo: Optional[str] = None
    obs: Optional[str] = None
    check_point: Optional[bool] = False
