import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium

from controllers import pontos_controller as PontosController
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from geobr import read_municipality
from matplotlib.colors import to_hex

#################################################################

def List():
    if not st.session_state.get('usuario_autenticado', False):
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()

    st.title("Pontos Cadastrados")

    # Carregar dados
    if "df" not in st.session_state or st.button("🔄 Atualizar Lista"):
        data = PontosController.SelecionarTodos()
        if not data:
            st.session_state['df'] = pd.DataFrame()
        else:
            rows = []
            for item in data:
                if isinstance(item, dict):
                    rows.append([
                        item.get('id'), item.get('estado'), item.get('codigo'),
                        item.get('municipio'), item.get('data'),
                        item.get('latitude'), item.get('longitude'),
                        item.get('cultura'), item.get('estadiofenolog'),
                        item.get('altitude'), item.get('temperatura'),
                        item.get('tpsafra'), item.get('check_point')  # Corrigido aqui
                    ])
                else:
                    rows.append([
                        getattr(item, 'id', None), getattr(item, 'estado', None),
                        getattr(item, 'codigo', None), getattr(item, 'municipio', None),
                        getattr(item, 'data', None), getattr(item, 'latitude', None),
                        getattr(item, 'longitude', None), getattr(item, 'cultura', None),
                        getattr(item, 'estadiofenolog', None), getattr(item, 'altitude', None),
                        getattr(item, 'temperatura', None), getattr(item, 'tpsafra', None),
                        getattr(item, 'check_point', None)  # Corrigido aqui
                    ])
            st.session_state['df'] = pd.DataFrame(rows, columns=[
                'id', 'estado', 'codigo', 'municipio', 'data',
                'latitude', 'longitude', 'cultura', 'estadiofenolog',
                'altitude', 'temperatura', 'tp_safra', 'check_point'  # Corrigido aqui
            ])

    df = st.session_state.get('df', pd.DataFrame())

    if df.empty:
        st.info("Nenhum ponto cadastrado.")

    col1, col2 = st.columns([1, 1])

    with col1:
        estados = sorted(df['estado'].dropna().unique().tolist()) if not df.empty else []
        estado = st.selectbox("Estado", [""] + estados)

        cidades = []
        if estado:
            cidades = sorted(df[df['estado'] == estado]['municipio'].dropna().unique().tolist())
        municipio = st.selectbox("Município", [""] + cidades)

        # Filtrar df conforme seleção
        if municipio:
            df_filtrado = df[df['municipio'] == municipio].copy()
        elif estado:
            df_filtrado = df[df['estado'] == estado].copy()
        else:
            df_filtrado = df.iloc[0:0].copy()

        st.write(f"Total registros: {len(df_filtrado)}")

        if estado and municipio:
            if not df_filtrado.empty:
                st.dataframe(df_filtrado.sort_values(by='data', ascending=True))
            else:
                st.info("Nenhum registro encontrado para esta seleção.")
        else:
            st.info("Selecione um estado e um município para visualizar os registros.")

        ###################################################################################
        # Inicializa variáveis de sessão
        if 'modo_edicao' not in st.session_state:
            st.session_state['modo_edicao'] = False
        if 'selected_id' not in st.session_state:
            st.session_state['selected_id'] = None
        if 'id_selecao' not in st.session_state:
            st.session_state['id_selecao'] = 0

        # Entrada do ID para edição
        id_sel = st.number_input(
            "ID do registro para editar (digite o id) - Após digitar o ID, click enter ou no espaço fora da caixa.",
            min_value=0,
            step=1,
            key="id_selecao"
        )

        # Botão para entrar no modo edição
        if id_sel > 0 and st.button("Editar este registro"):
            if not df_filtrado.empty and 'id' in df_filtrado.columns and not df_filtrado[df_filtrado['id'] == id_sel].empty:
                st.session_state['modo_edicao'] = True
                st.session_state['selected_id'] = int(id_sel)
                st.rerun()
            else:
                st.error("Registro não encontrado no filtro atual.")

        # --- FORMULÁRIO DE EDIÇÃO ---
        if st.session_state.get('modo_edicao') and st.session_state.get('selected_id') is not None:

            id_edit = st.session_state['selected_id']

            if not df_filtrado.empty and 'id' in df_filtrado.columns:
                registro = df_filtrado[df_filtrado['id'] == id_edit]
            else:
                registro = pd.DataFrame()

            if registro.empty:
                st.error("Registro não encontrado para edição.")
            else:
                # Lista de municípios do estado com "0" no topo
                lista_municipios = ["0"] + sorted(
                    df.loc[df['estado'] == estado, 'municipio'].dropna().unique().tolist()
                )

                municipio_atual = registro.iloc[0].get('municipio', '')
                codigo_atual = registro.iloc[0].get('codigo', '')
                lat_atual = float(registro.iloc[0].get('latitude', 0))
                lon_atual = float(registro.iloc[0].get('longitude', 0))
                check_atual = bool(registro.iloc[0].get('check_point', False)) if 'check_point' in registro.columns else False

                st.markdown(f"## Editando registro ID {id_edit}")

                novo_municipio = st.selectbox(
                    "Selecione o Município",
                    options=lista_municipios,
                    index=lista_municipios.index(municipio_atual) if municipio_atual in lista_municipios else 0,
                    key="edit_municipio"
                )

                if novo_municipio != "0":
                    cod_match = df.loc[
                        (df['estado'] == estado) & (df['municipio'] == novo_municipio),
                        'codigo'
                    ]
                    codigo_municipio = cod_match.iloc[0] if not cod_match.empty else codigo_atual
                else:
                    codigo_municipio = codigo_atual

                st.text_input("Código do Município", value=str(codigo_municipio), disabled=True, key="edit_codigo")

                nova_lat = st.number_input(
                    "Latitude",
                    value=float(lat_atual),
                    format="%.6f",
                    key="edit_lat"
                )
                nova_lon = st.number_input(
                    "Longitude",
                    value=float(lon_atual),
                    format="%.6f",
                    key="edit_lon"
                )
                novo_check = st.checkbox(
                    "Marcar como verificado",
                    value=check_atual,
                    key="edit_check"
                )

                # ---- Callback seguro para salvar e resetar seleção ----
                def salvar_alteracoes(id_edit, municipio_atual, codigo_municipio, nova_lat, nova_lon, novo_check, novo_municipio):
                    try:
                        novos_dados = {
                            "municipio": novo_municipio if novo_municipio != "0" else municipio_atual,
                            "codigo": codigo_municipio,
                            "latitude": float(nova_lat),
                            "longitude": float(nova_lon),
                            "check_point": bool(novo_check)
                        }
                        PontosController.Atualizar(id_edit, novos_dados)

                        # Mensagem de sucesso para exibir após o rerun automático
                        st.session_state['sucesso_msg'] = f"Registro {id_edit} atualizado com sucesso!"

                        # Importante: atualizar a seleção via callback (sem violar a regra do Streamlit)
                        st.session_state['id_selecao'] = 0
                        st.session_state['modo_edicao'] = False
                        st.session_state['selected_id'] = None

                    except Exception as e:
                        st.session_state['erro_atualizar'] = f"Erro ao atualizar registro: {e}"

                st.button(
                    "Salvar alterações",
                    key="btn_salvar_edicao",
                    on_click=salvar_alteracoes,
                    args=(id_edit, municipio_atual, codigo_municipio, nova_lat, nova_lon, novo_check, novo_municipio),
                )

                # Exibe mensagens após o rerun automático acionado pelo clique do botão
                if st.session_state.get('sucesso_msg'):
                    st.success(st.session_state.pop('sucesso_msg'))
                if st.session_state.get('erro_atualizar'):
                    st.error(st.session_state.pop('erro_atualizar'))

    #############################################################################
    # GERAR O MAPA NO FOLIUM
    ############################################################################
    
    # Coluna 2 - Mapa (sem alterações, você pode manter seu código original)
    with col2:
        st.subheader("🗺️ Mapa dos Pontos")

        if not df_filtrado.empty:
            m = folium.Map(
                location=[df_filtrado['latitude'].mean(), df_filtrado['longitude'].mean()],
                zoom_start=10,
                min_zoom=5,
                max_zoom=20,
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri'
            )

            Fullscreen().add_to(m)

            try:
                if df_filtrado['codigo'].notnull().any():
                    codigo_ibge = int(df_filtrado['codigo'].iloc[0])
                    municipio_gdf = read_municipality(code_muni=codigo_ibge, year=2022)

                    if not municipio_gdf.empty:
                        folium.GeoJson(
                            municipio_gdf.__geo_interface__,
                            name='Limite Município',
                            style_function=lambda feature: {
                                'color': 'blue',
                                'weight': 3,
                                'fillColor': 'blue',
                                'fillOpacity': 0.1,
                            }
                        ).add_to(m)
            except Exception as e:
                st.error(f"Erro ao carregar o município via geobr: {e}")

            culturas_unicas = df_filtrado['cultura'].unique()
            cmap = plt.cm.get_cmap('tab20', len(culturas_unicas))
            cores_culturas = {cultura: to_hex(cmap(i)) for i, cultura in enumerate(culturas_unicas)}

            for _, row in df_filtrado.iterrows():
                cor_marcador = cores_culturas.get(row['cultura'], '#808080')
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=7,
                    color=cor_marcador,
                    fill=True,
                    fill_color=cor_marcador,
                    fill_opacity=0.7,
                    popup=f"ID: {row['id']}<br>Cultura: {row['cultura']}<br>Data: {row['data']}"
                ).add_to(m)

            folium.LatLngPopup().add_to(m)

            st_folium(m, width=700, height=500)
        else:
            st.warning("Nenhum ponto encontrado para o município selecionado.")
