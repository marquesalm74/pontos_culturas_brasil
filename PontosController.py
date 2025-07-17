from typing import List
from sqlalchemy import text
import services.database as db
import models.Pontos as pts
import pandas as pd

def Incluir(ponto: pts.Pontos) -> int:
    query = """
        INSERT INTO tbl_ponto(
            name_state, code_muni, name_muni, data, latitude, longitude,
            cultura, estadiofenolog, altitude, temp_celsius, tp_safra, informante, emailinfo
        )
        VALUES (:name_state, :code_muni, :name_muni, :data, :latitude, :longitude,
                :cultura, :estadiofenolog, :altitude, :temp_celsius, :tp_safra, :informante, :emailinfo)
    """
    with db.engine.connect() as connection:
        connection.execute(
            text(query),
            {
                "name_state": ponto.estado,
                "code_muni": ponto.codigo,
                "name_muni": ponto.municipio,
                "data": ponto.data,
                "latitude": ponto.latitude,
                "longitude": ponto.longitude,
                "cultura": ponto.cultura,
                "estadiofenolog": ponto.estadiofenolog,
                "altitude": ponto.altitude,
                "temp_celsius": ponto.temperatura,
                "tp_safra": ponto.tpsafra,
                "informante": ponto.informante,
                "emailinfo": ponto.emailinfo
            }
        )
        connection.commit()
    return 1  # Retorna sucesso (você pode melhorar isso retornando ID se quiser)

def SelecionarTodos() -> List[pts.Pontos]:
    query = "SELECT * FROM tbl_ponto"
    with db.engine.connect() as connection:
        result = connection.execute(text(query))
        consultaList = []

        for row in result.fetchall():
            consultaList.append(pts.Pontos(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                row[7], row[8], row[9], row[10], row[11], row[12], row[13]
            ))

    return consultaList
