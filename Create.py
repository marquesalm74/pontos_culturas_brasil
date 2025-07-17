import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import Controllers.PontosController as PontosController
import models.Pontos as pts

# Conexão com o banco MySQL via SQLAlchemy
engine = create_engine("mysql+pymysql://root:495499@localhost/db_gedesmg")

# Leitura de municípios
query = "SELECT name_state, code_muni, name_muni, name_intermediate, name_immediate FROM tbl_municipiobr"
#cidades = pd.read_sql(query, con=engine)
try:
    cidades = pd.read_sql(query, con=engine)
except Exception as e:
    st.error(f"Erro ao carregar municípios: {e}")
    cidades = pd.DataFrame()

#################### FUNÇÕES DE USUÁRIO ####################

def salvar_usuario(email, senha, nome, empresa, cidade):
    query = """
        INSERT INTO usuarios (email, senha, nome, empresa, cidade)
        VALUES (:email, :senha, :nome, :empresa, :cidade)
    """
    with engine.connect() as connection:
        connection.execute(
            text(query),
            {"email": email, "senha": senha, "nome": nome, "empresa": empresa, "cidade": cidade}
        )
        connection.commit()

def buscar_usuario(email):
    query = "SELECT * FROM usuarios WHERE email = :email"
    with engine.connect() as connection:
        result = connection.execute(text(query), {"email": email}).fetchone()
    return result

#################### INTERFACE PRINCIPAL ####################

def Incluir():
    st.title('INCLUIR PONTOS')

    col1, col2 = st.columns([1, 2])

    with col1:

        if "usuario_autenticado" not in st.session_state:
            st.session_state.usuario_autenticado = False
        if "modo_cadastro" not in st.session_state:
            st.session_state.modo_cadastro = False
        if "email" not in st.session_state:
            st.session_state.email = ""
        if "senha" not in st.session_state:
            st.session_state.senha = ""

        st.subheader("🔐 Login / Cadastro")

        st.write('Se esqueceu a senha, favor solicitar no e-mail: mg.segeo@conab.gov.br')

        with st.form("form_login"):
            # Campos controlados por session_state
            email = st.text_input("E-mail *", value=st.session_state.email)
            senha = st.text_input("Senha *", type="password", value=st.session_state.senha)

            if st.session_state.modo_cadastro:
                nome = st.text_input("Nome e Sobrenome *")
                empresa = st.text_input("Empresa *")
                cidade_cliente = st.text_input("Cidade *")
            else:
                nome = ""
                empresa = ""
                cidade_cliente = ""

            col_botao_login, col_botao_sair = st.columns([2, 1])

            with col_botao_login:
                botao_login = st.form_submit_button("Cadastrar / Login")

            with col_botao_sair:
                botao_sair = st.form_submit_button('🚪 Sair')

            if botao_login:
                if email.strip() and senha.strip():
                    usuario = buscar_usuario(email)
                    if usuario:
                        if usuario[2] == senha:
                            st.success(f"Bem-vindo de volta, {usuario[3]}!")
                            st.session_state.usuario_autenticado = True
                            st.session_state.usuario_nome = usuario[3]
                            st.session_state.usuario_empresa = usuario[4]
                            st.session_state.usuario_cidade = usuario[5]
                            st.session_state.email = usuario[1]  # Armazena o e-mail no estado
                            st.session_state.senha = senha
                        else:
                            st.error("Senha incorreta.")
                    else:
                        if not st.session_state.modo_cadastro:
                            st.info("Usuário não encontrado. Preencha os campos para realizar o cadastro.")
                            st.session_state.modo_cadastro = True
                            st.session_state.email = email  # Guarda o e-mail digitado
                            st.session_state.senha = senha
                        else:
                            if nome.strip() and empresa.strip() and cidade_cliente.strip():
                                try:
                                    salvar_usuario(email, senha, nome, empresa, cidade_cliente)
                                    st.success(f"Bem-vindo, {nome}! Cadastro realizado com sucesso.")
                                    st.session_state.usuario_autenticado = True
                                    st.session_state.usuario_nome = nome
                                    st.session_state.usuario_empresa = empresa
                                    st.session_state.usuario_cidade = cidade_cliente
                                    st.session_state.email = email
                                    st.session_state.senha = senha
                                except Exception as e:
                                    st.error(f"Erro ao cadastrar: {e}")
                            else:
                                st.error("Por favor, preencha todos os campos para cadastro.")
                else:
                    st.error("Por favor, preencha o e-mail e a senha.")

            if botao_sair:
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        if st.session_state.get('usuario_autenticado', False):
            st.subheader(f"Usuário: {st.session_state.usuario_nome} - {st.session_state.usuario_empresa} ({st.session_state.usuario_cidade})")

            st.info("Apresento uma rede colaborativa com os profissionais da Agricultura e áreas afins.")

            st.info('Todos estão convidados a compartilhar Pontos de Lavouras que são cultivadas.')

            st.info('Você ao preencher o cadastro irá contribuir com a coleta de informações agrícolas e terá disponível uma planilha dos pontos coletados do município de interesse, no Menu -> Consultas.')

            st.info('Para contato, envie um email para mg.segeo@conab.gov.br')

    #################### FORMULÁRIO DE INCLUSÃO DE PONTOS ####################

    with col2:
        if st.session_state.get('usuario_autenticado', False):

            dados_municipios = cidades

            input_uf = st.selectbox('Selecione o Estado (UF)', [""] + sorted(dados_municipios['name_state'].unique()))
            municipios_filtrados = dados_municipios[dados_municipios['name_state'] == input_uf].sort_values("name_muni")
            nome_municipios = municipios_filtrados['name_muni'].tolist()
            
            input_name = st.selectbox('Selecione o Município', [""] + nome_municipios)

            municipio_selecionado = input_name
            input_code = ""

            if input_name:
                input_name_normalizado = input_name.strip().lower()
                municipios_filtrados = municipios_filtrados.copy()
                municipios_filtrados['name_normalizado'] = municipios_filtrados['name_muni'].str.strip().str.lower()
                linha_filtrada = municipios_filtrados[municipios_filtrados['name_normalizado'] == input_name_normalizado]

                if not linha_filtrada.empty:
                    input_code = str(linha_filtrada['code_muni'].values[0])
                    st.success(f"Código do município: {input_code}")
                    st.text_input(label='Código do Município', value=input_code, disabled=True)
                else:
                    st.warning("Município não encontrado para o estado selecionado. Verifique o nome digitado.")

            with st.form(key="include_pontos"):
                input_date = st.date_input(label="Insira a Data do Registro", format="DD/MM/YYYY")
                input_lat = st.number_input(label="Insira a Latitude do PONTO DA CULTURA. ( Ex. -19.819723) *", format='%6f')
                input_long = st.number_input(label="Insira a Longitude do PONTO DA CULTURA. ( Ex. -43.938665) *", format='%6f')
                input_tpsafra = st.selectbox("Selecione o Tipo de Safra *", [" ", 'Lavoura Permanente', 'Pastagem', 'Safra Verão', 'Safrinha'])

                input_cultura = st.selectbox("Selecione a Cultura *", ['', 'Açaí','Algodão', 'Amendoim', 'Arroz','Babaçu','Borracha','Buriti','Cacau',
                                                                      'Café Novo Plantio < 2 anos', 'Café em Produção > 2 anos',
                                                                      'Café em Recuperação < 2 anos','Castanha-do-Brasil','Farinha de Mandioca','Feijão 1ª Safra',
                                                                      'Feijão 2ª Safra', 'Feijão 3ª Safra',
                                                                      'Girassol', 'Laranja', 'Mamona','Mexirica','Milho Verão', 'Milho Safrinha',
                                                                      'Milho Silagem','Morango','Pequi','Pinhão','Soja', 'Sorgo', 'Sorgo Forrageiro',
                                                                      'Trigo Sequeiro', 'Trigo Irrigado','Umbu'])

                input_estadiofen = st.selectbox("Selecione o Estádio Fenológico da Cultura *",
                                                ['', 'Germinação/Emergência', 'Desenvolvimento Vegetativo', 'Floração',
                                                 'Enchimento de Grão', 'Maturação', 'Colheita'])

                input_altitude = st.number_input("Insira a Altitude", format='%d', step=1)
                input_temp = st.number_input("Digite a Temperatura Celsius")
                input_informante = st.text_input('Digite seu Nome *', st.session_state.usuario_nome)
                input_emailinfor = st.text_input('Digite seu E-mail para contato *', st.session_state.email)
                #input_emailinfor = st.text_input('Digite seu E-mail para contato *', email)

                input_button_submit = st.form_submit_button('Enviar Dados')

                if input_button_submit:
                    lat_ok = input_lat is not None and -90 <= input_lat <= 90
                    long_ok = input_long is not None and -180 <= input_long <= 180

                    campos_obrigatorios_preenchidos = all([
                        input_code not in [None, ""],
                        input_uf not in [None, ""],
                        municipio_selecionado not in [None, ""],
                        input_date is not None,
                        lat_ok,
                        long_ok,
                        input_cultura.strip() != "",
                        input_temp is not None,
                        input_tpsafra.strip() != "",
                        input_estadiofen.strip() != "",
                        input_informante.strip() != "",
                        input_emailinfor.strip() != ""
                    ])

                    if campos_obrigatorios_preenchidos:
                        ponto = pts.Pontos(
                            id=0,
                            estado=input_uf,
                            codigo=input_code,
                            municipio=municipio_selecionado,
                            data=input_date,
                            latitude=input_lat,
                            longitude=input_long,
                            cultura=input_cultura,
                            estadiofenolog=input_estadiofen,
                            altitude=input_altitude,
                            temperatura=input_temp,
                            tpsafra=input_tpsafra,
                            informante=input_informante,
                            emailinfo=input_emailinfor
                        )
                        PontosController.Incluir(ponto)
                        st.success(f"Ponto incluído com sucesso para {municipio_selecionado} - {input_code} ({input_uf})!")
                    else:
                        st.error("Por favor, preencha todos os campos obrigatórios marcados com (*).")

