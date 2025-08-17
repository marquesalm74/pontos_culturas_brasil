import streamlit as st 
import sys
import importlib

from utils import create as PageCreate
from utils import list as PageList
from utils import atualizar as PageUpdate
from utils import deletar as PageDelete

################### Reinicia automaticamente o Streamlit
#
# Lista de módulos que você quer sempre recarregar
MODULES_TO_RELOAD = [
    "controllers.pontos_controller",
    "models.model_serietemp",
    "ai",
    "helper"
]

for module_name in MODULES_TO_RELOAD:
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])

# Limpa cache do Streamlit para garantir que funções atualizadas rodem
st.cache_data.clear()
st.cache_resource.clear()
#
###########################################################################################

st.set_page_config(layout="wide", page_title="Pontos Culturas")

# --- Sidebar ---
with st.sidebar:
    st.title("MENU")
    st.image("img/RCA.png", use_container_width=True)
    page = st.selectbox("PONTOS", ["Incluir", "Consultar", "Atualizar", "Deletar"])
    st.info("Você profissional do campo, pode contribuir com a coleta de informações de culturas no território brasileiro.")
    
    st.info("Para contato e/ou solicitação de outros municípios: alessandro.alm74@gmail.com")

###################################################################
# Incluir ponto
###################################################################
if page == "Incluir":
    # o controle de login está dentro do create.py
    PageCreate.create()

###################################################################
# Consultar pontos
###################################################################
elif page == "Consultar":
    PageList.list_pontos()
    
###################################################################
# Atualizar ponto
###################################################################
elif page == "Atualizar":
    PageUpdate.atualizar()

###################################################################
# Deletar ponto
###################################################################
elif page == "Deletar":
    PageDelete.deletar()
