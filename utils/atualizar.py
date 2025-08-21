# pages/atualizar.py
import streamlit as st
from services import database as db
import controllers.pontos_controller as PontosController
from utils.create import ESTADIOS, TPSAFRA_OPTS, CULTURAS
from datetime import datetime, date

def atualizar():
    st.title("Atualizar Ponto")

    if not st.session_state.get("usuario_autenticado", False):
        st.warning("Faça login para atualizar pontos")
        return

    # Seleciona ID do ponto para atualizar
    pontos = PontosController.SelecionarTodos()
    if not pontos:
        st.info("Nenhum ponto cadastrado.")
        return

    ponto_ids = [p['id'] for p in pontos]
    id_selecionado = st.selectbox("Selecione o ID do ponto", ponto_ids, key="id_ponto_edit")

    # Obtém os dados do ponto selecionado
    ponto = next((p for p in pontos if p['id'] == id_selecionado), None)
    if not ponto:
        st.error("Ponto não encontrado.")
        return

    # Inicializa session_state para cada campo se ainda não existir
    campos = {
        "estado_edit": ponto.get("estado", ""),
        "municipio_edit": ponto.get("municipio", ""),
        "cultura_edit": ponto.get("cultura", ""),
        "tpsafra_edit": ponto.get("tipo_safra", ""),
        "estadio_edit": ponto.get("estadio", ""),
        "data_plantio_edit": ponto.get("data_plantio", ""),
        "observacao_edit": ponto.get("observacao", "")
    }

    for chave, valor in campos.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

    # Campos do formulário
    estado = st.selectbox("Estado", sorted(list(db.listar_estados())), key="estado_edit")
    
    # Municípios filtrados pelo estado selecionado
    municipios = db.listar_municipios(estado)
    municipio = st.selectbox("Município", municipios, key="municipio_edit")

    cultura = st.selectbox("Cultura", CULTURAS, key="cultura_edit")
    tpsafra = st.selectbox("Tipo de Safra", TPSAFRA_OPTS, key="tpsafra_edit")
    estadio = st.selectbox("Estádio de desenvolvimento", ESTADIOS, key="estadio_edit")

    # Data de plantio
    if st.session_state["data_plantio_edit"]:
        try:
            data_plantio_default = datetime.strptime(st.session_state["data_plantio_edit"], "%Y-%m-%d").date()
        except:
            data_plantio_default = date.today()
    else:
        data_plantio_default = date.today()

    data_plantio = st.date_input("Data de Plantio", value=data_plantio_default, key="data_plantio_edit")

    observacao = st.text_area("Observação", value=st.session_state["observacao_edit"], key="observacao_edit")

    # Botão para atualizar
    if st.button("Atualizar Ponto"):
        novos_dados = {
            "estado": estado,
            "municipio": municipio,
            "cultura": cultura,
            "tipo_safra": tpsafra,
            "estadio": estadio,
            "data_plantio": data_plantio.strftime("%Y-%m-%d"),
            "observacao": observacao
        }

        sucesso = PontosController.Atualizar(id_selecionado, novos_dados)
        if sucesso:
            st.success("Ponto atualizado com sucesso!")
        else:
            st.error("Erro ao atualizar o ponto.")
