# pages/update.py
import streamlit as st
from services import database as db
import controllers.pontos_controller as PontosController

def atualizar():
    st.title("Atualizar Ponto")

    if not st.session_state.get('usuario_autenticado', False):
        st.warning("Faça login para atualizar pontos.")
        return

    selected_id = st.session_state.get('selected_id', None)
    if not selected_id:
        selected_id = st.number_input("Digite o ID do registro para atualizar", min_value=1, value=1, step=1)
        # if selected_id == 0:
        #     st.info("Selecione um ID válido para atualizar.")
        #     return

    # busca registro no supabase
    pontos = PontosController.SelecionarTodos()
    registro = None
    for p in pontos:
        if isinstance(p, dict) and p.get("id") == int(selected_id):
            registro = p
            break
    if registro is None:
        st.error("Registro não encontrado.")
        return

    with st.form("form_update"):
        estado = st.text_input("Estado", registro.get("estado",""))
        municipio = st.text_input("Município", registro.get("municipio",""))
        codigo = st.text_input("Código município", str(registro.get("codigo","")), disabled=True)
        data = st.date_input("Data", value=registro.get("data") if isinstance(registro.get("data"), str) else registro.get("data"))
        latitude = st.number_input("Latitude", value=float(registro.get("latitude") or 0.0), format="%.6f")
        longitude = st.number_input("Longitude", value=float(registro.get("longitude") or 0.0), format="%.6f")
        cultura = st.text_input("Cultura", registro.get("cultura",""))
        estadio = st.text_input("Estádio fenológico", registro.get("estadiofenolog",""))
        altitude = st.number_input("Altitude", value=int(registro.get("altitude") or 0), step=1)
        temperatura = st.number_input("Temperatura", value=float(registro.get("temperatura") or 0.0))
        obs = st.text_area("Observações", registro.get("obs",""))
        submit = st.form_submit_button("Atualizar")

        if submit:
            payload = {
                "estado": estado,
                "municipio": municipio,
                "data": data.isoformat() if hasattr(data, "isoformat") else data,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "cultura": cultura,
                "estadiofenolog": estadio,
                "altitude": int(altitude),
                "temperatura": float(temperatura),
                "obs": obs
            }
            try:
                PontosController.Atualizar(int(selected_id), payload)
                st.success("Registro atualizado com sucesso.")
                # limpa caches
                st.session_state.pop("df", None)
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
