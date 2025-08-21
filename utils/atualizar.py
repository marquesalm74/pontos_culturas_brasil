# pages/atualizar.py
import streamlit as st
from services import database as db
import controllers.pontos_controller as PontosController
from utils.create import ESTADIOS, TPSAFRA_OPTS, CULTURAS
from datetime import datetime, date   # ✅ IMPORTADO para conversão


def atualizar():
    st.title("Atualizar Ponto")

    if not st.session_state.get("usuario_autenticado", False):
        st.warning("Faça login para atualizar pontos.")
        return

    # Seleção do ID
    selected_id = st.session_state.get("selected_id", None)
    if not selected_id:
        selected_id = st.number_input(
            "Digite o ID do registro para atualizar", min_value=1, value=1, step=1
        )

    # Busca registro no banco
    pontos = PontosController.SelecionarTodos()
    registro = next(
        (p for p in pontos if isinstance(p, dict) and p.get("id") == int(selected_id)),
        None,
    )

    if registro is None:
        st.error("Registro não encontrado.")
        return

    # 🔸 NOVO: inicializa/ressincroniza estado/município/código ao trocar o ID
    if st.session_state.get("_upd_loaded_id") != int(selected_id):
        st.session_state["_upd_loaded_id"] = int(selected_id)
        st.session_state["estado_edit"] = registro.get("estado", "")
        st.session_state["municipio_edit"] = registro.get("municipio", "")
        st.session_state["code_muni"] = str(registro.get("codigo", ""))

    # ---------- ESTADO E MUNICÍPIO ----------
    estados = db.carregar_estados()
    estados_dict = {e["name_state"]: e["code_state"] for e in estados}

    # 🔹 ALTERADO - conflito session_state: inicializa apenas se não existir
    if "estado_edit" not in st.session_state:
        st.session_state["estado_edit"] = registro.get("estado", "")

    estado_options = [""] + list(estados_dict.keys())
    estado_index = (
        estado_options.index(st.session_state["estado_edit"])
        if st.session_state["estado_edit"] in estado_options
        else 0
    )

    estado = st.selectbox(
        "Selecione o Estado",
        estado_options,
        index=estado_index,
        key="estado_edit",
    )

    # Carrega municípios do estado selecionado
    municipios_lista, municipios_obj = [], []
    if estado:
        code_state = estados_dict.get(estado)
        if code_state:
            municipios = db.carregar_municipios(str(code_state).strip())
            municipios_lista = [m["name_muni"] for m in municipios]
            municipios_obj = municipios

    # 🔹 ALTERADO - conflito session_state: inicializa apenas se não existir
    if "municipio_edit" not in st.session_state:
        st.session_state["municipio_edit"] = registro.get("municipio", "")

    if st.session_state.get("municipio_edit") and st.session_state["municipio_edit"] not in municipios_lista:
        st.session_state["municipio_edit"] = ""

    municipio_options = [""] + municipios_lista
    municipio_index = (
        municipio_options.index(st.session_state["municipio_edit"])
        if st.session_state["municipio_edit"] in municipio_options
        else 0
    )

    municipio = st.selectbox(
        "Município",
        municipio_options,
        index=municipio_index,
        key="municipio_edit",
    )

    # 🔹 ALTERADO: Código do município recalculado a cada troca e mostrado fora do form
    code_muni = next(
        (m["code_muni"] for m in municipios_obj if m["name_muni"] == st.session_state.get("municipio_edit", "")),
        "",
    )
    st.session_state["code_muni"] = str(code_muni or st.session_state.get("code_muni", ""))

    # 🔹 ALTERADO: campo exibido fora do form para refletir troca imediata
    st.text_input("Código município", st.session_state.get("code_muni", ""), disabled=True)

    with st.form("form_update"):
        # ---------- OUTROS CAMPOS ----------

        # ✅ CORRIGIDO: garantir que 'data' seja datetime.date
        data_valor = registro.get("data")
        if isinstance(data_valor, str):
            try:
                data_valor = datetime.fromisoformat(data_valor.replace("Z", "+00:00")).date()
            except ValueError:
                data_valor = None
        elif isinstance(data_valor, datetime):
            data_valor = data_valor.date()
        elif isinstance(data_valor, date):
            pass
        else:
            data_valor = None

        data = st.date_input("Data", value=data_valor)

        latitude = st.number_input(
            "Latitude", value=float(registro.get("latitude") or 0.0), format="%.6f"
        )
        longitude = st.number_input(
            "Longitude", value=float(registro.get("longitude") or 0.0), format="%.6f"
        )

        cultura = st.selectbox(
            "Cultura",
            CULTURAS,
            index=CULTURAS.index(registro.get("cultura", CULTURAS[0]))
            if registro.get("cultura") in CULTURAS
            else 0,
        )

        estadio = st.selectbox(
            "Estádio fenológico",
            ESTADIOS,
            index=ESTADIOS.index(registro.get("estadiofenolog", ESTADIOS[0]))
            if registro.get("estadiofenolog") in ESTADIOS
            else 0,
        )

        tpsafra = st.selectbox(
            "Tipo de Safra",
            TPSAFRA_OPTS,
            index=TPSAFRA_OPTS.index(registro.get("tpsafra", TPSAFRA_OPTS[0]))
            if registro.get("tpsafra") in TPSAFRA_OPTS
            else 0,
        )

        altitude = st.number_input(
            "Altitude", value=int(registro.get("altitude") or 0), step=1
        )
        temperatura = st.number_input(
            "Temperatura", value=float(registro.get("temperatura") or 0.0)
        )
        obs = st.text_area("Observações", registro.get("obs", ""))

        # ---------- BOTÃO ----------
        submit = st.form_submit_button("Atualizar")

        if submit:
            payload = {
                "estado": st.session_state.get("estado_edit", ""),
                "municipio": st.session_state.get("municipio_edit", ""),
                "codigo": st.session_state.get("code_muni", ""),
                "data": data.isoformat() if hasattr(data, "isoformat") else data,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "cultura": cultura,
                "estadiofenolog": estadio,
                "tpsafra": tpsafra,
                "altitude": int(altitude),
                "temperatura": float(temperatura),
                "obs": obs,
            }
            try:
                PontosController.Atualizar(int(selected_id), payload)
                st.success("Registro atualizado com sucesso.")
                st.session_state.pop("df", None)  # limpa cache
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
