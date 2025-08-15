import streamlit as st
import qrcode
import io
import sys
import importlib

from utils import create as PageCreate
from utils import list as PageList
from utils import atualizar as PageUpdate
from utils import deletar as PageDelete
from PIL import Image

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
    st.image("img/ponto_brasil.png" if st.query_params.get("dev") else "img/RCA.png", use_container_width=True)
    page = st.selectbox("PONTOS", ["Incluir", "Consultar", "Atualizar", "Deletar"])
    st.info("Você profissional do campo, pode contribuir com a coleta de informações de culturas no território brasileiro.")

    # # --- Função de QR Code ---
    # def gerar_qrcode(data: str):
    #     qr = qrcode.QRCode(version=1, box_size=10, border=5)
    #     qr.add_data(data)
    #     qr.make(fit=True)
    #     img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    #     buf = io.BytesIO()
    #     img.save(buf, format="PNG")
    #     buf.seek(0)
    #     return buf

    # # --- Gerar e exibir QR Code ---
    # dados_pix = "00020126480014br.gov.bcb.pix0126alessandro.alm74@gmail.com5204000053039865802BR5924Alessandro Lucio Marques6014Belo Horizonte62070503***6304C139"
    # img_qr = gerar_qrcode(dados_pix)
    # st.image(img_qr, use_container_width=True)
    # st.info("Se quiser apoiar a manutenção da aplicação, contribua com qualquer valor via QR Code.")

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
    PageList.List()
    
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
