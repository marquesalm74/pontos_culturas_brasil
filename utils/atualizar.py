# pages/atualizar.py
import streamlit as st
from services import database as db
import controllers.pontos_controller as PontosController
from utils.create import ESTADIOS, TPSAFRA_OPTS, CULTURAS
from datetime import datetime, date

def atualizar():
    st.title("Atualizar Ponto")

    # ----------------------------------------------------------------------
    # Verifica autenticação
    # ----------------------------------------------------------------------
    if not st.session_state.get("usuario_autenticado", False):
        st.warning("Faça login para atualizar pontos.")
        return

    # ----------------------------------------------------------------------
    # Carrega todos os pontos e IDs disponíveis
    # ----------------------------------------------------------------------
    pontos = PontosController.SelecionarTodos()
    ids_disponiveis = sorted([p["id"] for p in pontos if isinstance(p, dict) and "id" in p])

    # Adiciona opção vazia no início
    ids_options = [""] + [str(i) for i in ids_disponiveis]
    
    # if not ids_disponiveis:
    #     st.error("Nenhum registro encontrado no banco.")
    #     return

    # ----------------------------------------------------------------------
    # Seleção do ID via selectbox
    # ----------------------------------------------------------------------
    selected_id = st.selectbox(
        "Selecione o ID do registro:",
        options=ids_options,
        index = 0,
        #key="selected_id"
    )
    
    # Se nada for selecionado, interrompe a função
    if selected_id == "":
        st.info("Selecione um ID para carregar os dados.")
        return
    
    # Converte para inteiro
    try:
        selected_id_value = int(selected_id)
    except ValueError:
        st.error("ID inválido.")
        return

    # ----------------------------------------------------------------------
    # Recupera o registro correspondente ao ID selecionado
    # ----------------------------------------------------------------------
    registro = next(
        (p for p in pontos if isinstance(p, dict) and p.get("id") == int(selected_id_value)),
        None
    )

    if not registro:
        st.warning("Nenhum registro encontrado para o ID selecionado.")
        return

    # ----------------------------------------------------------------------
    # Sincronização inicial de estado/município/código
    # ----------------------------------------------------------------------
    if st.session_state.get("_upd_loaded_id") != selected_id_value:
        st.session_state["_upd_loaded_id"] = selected_id_value
        st.session_state["estado_edit"] = registro.get("estado", "") or ""
        st.session_state["municipio_edit"] = registro.get("municipio", "") or ""
        st.session_state["code_muni"] = str(registro.get("codigo", "") or "")

    # ----------------------------------------------------------------------
    # Estado e Município
    # ----------------------------------------------------------------------
    estados = db.carregar_estados()
    estados_dict = {e["name_state"]: e["code_state"] for e in estados}

    if "estado_edit" not in st.session_state:
        st.session_state["estado_edit"] = registro.get("estado", "") or ""

    if st.session_state["estado_edit"] not in estados_dict.keys():
        st.session_state["estado_edit"] = ""

    estado = st.selectbox(
        "Selecione o Estado",
        [""] + list(estados_dict.keys()),
        key="estado_edit"
    )

    # Carrega municípios do estado selecionado
    municipios_lista, municipios_obj = [], []
    if estado:
        code_state = estados_dict.get(estado)
        if code_state:
            municipios = db.carregar_municipios(str(code_state).strip())
            municipios_lista = [m["name_muni"] for m in municipios]
            municipios_obj = municipios

    if "municipio_edit" not in st.session_state:
        st.session_state["municipio_edit"] = registro.get("municipio", "") or ""

    if st.session_state["municipio_edit"] not in municipios_lista:
        st.session_state["municipio_edit"] = ""

    municipio = st.selectbox(
        "Município",
        [""] + municipios_lista,
        key="municipio_edit"
    )

    # Código do município
    code_muni = next(
        (m["code_muni"] for m in municipios_obj if m["name_muni"] == st.session_state.get("municipio_edit", "")),
        ""
    )
    st.session_state["code_muni"] = str(code_muni or st.session_state.get("code_muni", ""))
    st.text_input("Código município", st.session_state.get("code_muni", ""), disabled=True)

    # ----------------------------------------------------------------------
    # Formulário de atualização
    # ----------------------------------------------------------------------
    with st.form("form_update"):
        # Normaliza 'data'
        data_valor = registro.get("data")
        if isinstance(data_valor, str):
            try:
                data_valor = datetime.fromisoformat(data_valor.replace("Z", "+00:00")).date()
            except ValueError:
                data_valor = None
        elif isinstance(data_valor, datetime):
            data_valor = data_valor.date()
        elif not isinstance(data_valor, date):
            data_valor = None

        data_input = st.date_input("Data", value=data_valor or date.today())
        latitude = st.number_input("Latitude", value=float(registro.get("latitude") or 0.0), format="%.6f")
        longitude = st.number_input("Longitude", value=float(registro.get("longitude") or 0.0), format="%.6f")

        cultura = st.selectbox(
            "Cultura",
            CULTURAS,
            index=CULTURAS.index(registro.get("cultura")) if registro.get("cultura") in CULTURAS else 0,
        )

        estadio = st.selectbox(
            "Estádio fenológico",
            ESTADIOS,
            index=ESTADIOS.index(registro.get("estadiofenolog")) if registro.get("estadiofenolog") in ESTADIOS else 0,
        )

        tpsafra = st.selectbox(
            "Tipo de Safra",
            TPSAFRA_OPTS,
            index=TPSAFRA_OPTS.index(registro.get("tpsafra")) if registro.get("tpsafra") in TPSAFRA_OPTS else 0,
        )

        altitude = st.number_input("Altitude", value=int(registro.get("altitude") or 0), step=1)
        temperatura = st.number_input("Temperatura", value=float(registro.get("temperatura") or 0.0))
        obs = st.text_area("Observações", registro.get("obs", ""))

        submit = st.form_submit_button("Atualizar")

        if submit:
            payload = {
                "estado": st.session_state.get("estado_edit", ""),
                "municipio": st.session_state.get("municipio_edit", ""),
                "codigo": st.session_state.get("code_muni", ""),
                "data": data_input.isoformat() if hasattr(data_input, "isoformat") else data_input,
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
                PontosController.Atualizar(int(selected_id_value), payload)
                st.success("Registro atualizado com sucesso.")
                st.session_state.pop("df", None)
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
