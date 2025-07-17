from dataclasses import dataclass

@dataclass
class Pontos:
    id: int
    estado: str
    codigo: str
    municipio: str
    data: str
    latitude: float
    longitude: float
    cultura: str
    estadiofenolog: str
    altitude: int
    temperatura: float
    tpsafra: str
    informante: str
    emailinfo: str