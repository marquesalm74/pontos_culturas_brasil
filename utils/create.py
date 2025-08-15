# pages/create.py
import streamlit as st
import pandas as pd
from datetime import date
from services import database as db
import controllers.pontos_controller as PontosController

CULTURAS = [
    '', 'Açaí','Algodão', 'Amendoim', 'Arroz','Babaçu','Borracha','Buriti','Cacau',
    'Café Novo', 'Café em Produção', 'Café em Recuperação','Castanha-do-Brasil',
    'Farinha de Mandioca','Feijão 1ª Safra','Feijão 2ª Safra', 'Feijão 3ª Safra',
    'Girassol', 'Laranja','Limão','Macadâmia', 'Mamona','Mexirica','Milho Verão',
    'Milho Safrinha', 'Milho Silagem','Morango','Pequi','Pinhão','Soja','Sorgo',
    'Sorgo Forrageiro','Trigo Sequeiro', 'Trigo Irrigado','Umbu'
]

ESTADIOS = ['', 'Germinação/Emergência', 'Desenvolvimento Vegetativo', 'Floração',
           'Enchimento de Grão', 'Maturação', 'Colheita']

TPSAFRA_OPTS = ["", 'Lavoura Permanente', 'Pastagem', 'Safra Verão', 'Safrinha']


def form_login_cadastro():
    st.header("Login")
    
    st.info("Insira seu e-mail e senha, mas se precisar cadastrar, escolha a opção incluir ao lado.")
    
    email = st.text_input("E-mail", key="login_email")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar"):
        if not email or not senha:
            st.error("Informe e-mail e senha para login.")
            return False
        try:
            user = db.buscar_usuario_por_email(email)
            if user and user.get("senha") == senha:  # ⚠ Ideal: usar hash de senha
                st.success(f"Bem-vindo(a), {user.get('nome') or email}!")
                st.session_state["usuario_autenticado"] = True
                st.session_state["usuario_nome"] = user.get("nome") or email
                st.session_state["email"] = email
                return True
            else:
                st.error("Usuário ou senha inválidos.")
                return False
        except Exception as e:
            st.error(f"Erro ao tentar login: {e}")
            return False

    st.markdown("---")
    st.header("Cadastro")
    nome_cad = st.text_input("Nome completo", key="cad_nome")
    email_cad = st.text_input("E-mail para cadastro", key="cad_email")
    senha_cad = st.text_input("Senha para cadastro", type="password", key="cad_senha")

    if st.button("Cadastrar"):
        if not nome_cad or not email_cad or not senha_cad:
            st.error("Preencha todos os campos para cadastro.")
            return False
        try:
            existing = db.buscar_usuario_por_email(email_cad)
            if existing:
                st.error("E-mail já cadastrado.")
                return False
            db.inserir_usuario({"nome": nome_cad, "email": email_cad, "senha": senha_cad})
            st.success("Cadastro realizado com sucesso! Faça login.")
            return False
        except Exception as e:
            st.error(f"Erro ao cadastrar usuário: {e}")
            return False

    return False


def create():
    st.title("Incluir Ponto")

    col1, col2 = st.columns([1, 2])
    ###########################################################
    # Coluna 1 - Login / Logout
    ###########################################################
    with col1:
        if not st.session_state.get("usuario_autenticado", False):
            if form_login_cadastro():
                st.session_state["refresh_page"] = True
        else:
            st.success(f"Usuário: {st.session_state.get('usuario_nome', '')}")
            
            if st.button("Logout"):
                for k in ["usuario_autenticado", "usuario_nome", "email", "code_muni", "municipios_cache", "estado_cache"]:
                    st.session_state.pop(k, None)
                st.session_state["refresh_page"] = True
                
            # Mensagem informativa
            st.info(
                "Os pontos de culturas permitem mapear e monitorar, com precisão geográfica, "
                "a localização, extensão e condições das lavouras para apoiar o planejamento agrícola, "
                "a gestão da produção e as políticas públicas."
            )

    if st.session_state.get("refresh_page", False):
        st.session_state["refresh_page"] = False
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
            
    #####################################################################
    # Coluna 2 - Formulário
    #####################################################################
    with col2:
        if not st.session_state.get("usuario_autenticado", False):
            st.info("Faça login para acessar o formulário de inclusão.")
            return

        # Carrega lista de estados da view
        try:
            estados = db.carregar_estados()
        except Exception as e:
            st.error(f"Erro ao carregar estados: {e}")
            estados = []

        uf = st.selectbox("Estado (UF)", [""] + estados, key="estado_selecionado")

        # Carrega municípios dinamicamente quando o estado muda
        if uf:
            if "municipios_cache" not in st.session_state or st.session_state.get("estado_cache") != uf:
                try:
                    municipios_df = pd.DataFrame(db.carregar_municipios(uf))
                    st.session_state["municipios_cache"] = municipios_df
                    st.session_state["estado_cache"] = uf
                except Exception as e:
                    st.error(f"Erro ao carregar municípios: {e}")
                    st.session_state["municipios_cache"] = pd.DataFrame()
        else:
            st.session_state["municipios_cache"] = pd.DataFrame()

        municipios_lista = sorted(st.session_state["municipios_cache"]['name_muni'].tolist()) if not st.session_state["municipios_cache"].empty else []
        municipio = st.selectbox("Município", [""] + municipios_lista, key="municipio_selecionado")

        code_muni = ""
        if municipio and not st.session_state["municipios_cache"].empty:
            df = st.session_state["municipios_cache"]
            row = df[df['name_muni'].str.strip().str.lower() == municipio.strip().lower()]
            if not row.empty:
                code_muni = str(row.iloc[0]['code_muni'])
                st.session_state["code_muni"] = code_muni

        with st.form("form_ponto"):
            st.text_input("Código do Município", value=st.session_state.get("code_muni", ""), disabled=True, key="code_muni_display")
            data_reg = st.date_input("Data do registro", value=date.today())
            lat = st.number_input("Latitude: ex. '-19.564568' ", format="%.6f", value=0.0) 
            lon = st.number_input("Longitude: ex. '-46.170056' ", format="%.6f", value=0.0)
            tp_safra = st.selectbox("Tipo de safra", TPSAFRA_OPTS)
            cultura = st.selectbox("Cultura", CULTURAS)
            estadio = st.selectbox("Estádio fenológico", ESTADIOS)
            altitude = st.number_input("Altitude (m)", value=0, step=1)
            temp = st.number_input("Temperatura (°C)", value=0.0, step=0.1)
            informante = st.text_input("Nome do informante", st.session_state.get("usuario_nome", ""))
            emailinfo = st.text_input("E-mail para contato", st.session_state.get("email", ""))
            obs = st.text_area("Observações (opcional)", placeholder='Área Agrícola: ha, alqueire mineiro, alqueire paulista etc.')
            
            # NOVO: opção para já marcar como verificado
            check_point = st.checkbox("Se o ponto está verificado, favor marcar como verificado", value=False)
            
            submit = st.form_submit_button("Enviar")

            if submit:
                if not (uf and municipio and st.session_state.get("code_muni")):
                    st.error("UF, Município e Código do município são obrigatórios.")
                elif not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    st.error("Latitude ou longitude fora do intervalo válido.")
                elif not cultura or cultura.strip() == "":
                    st.error("Cultura é obrigatória.")
                else:
                    payload = {
                        "estado": uf,
                        "codigo": st.session_state.get("code_muni"),
                        "municipio": municipio,
                        "data": data_reg.isoformat(),
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "cultura": cultura,
                        "estadiofenolog": estadio,
                        "altitude": int(altitude),
                        "temperatura": float(temp),
                        "tpsafra": tp_safra,
                        "informante": informante,
                        "emailinfo": emailinfo,
                        "obs": obs or "",
                        "check_point": check_point  # <-- agora pega do checkbox
                    }
                    try:
                        PontosController.Incluir(payload)
                        st.success("Ponto incluído com sucesso.")
                    except Exception as e:
                        st.error(f"Erro ao inserir ponto: {e}")
