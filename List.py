import streamlit as st
import pandas as pd
import folium
import geopandas as gpd
import matplotlib.pyplot as plt

from matplotlib.colors import to_hex
from Controllers import PontosController
from geobr import read_municipality
from folium.plugins import Fullscreen
from streamlit_folium import folium_static
from streamlit_folium import st_folium

def List():
    if not st.session_state.get('usuario_autenticado', False):
        st.warning("Você precisa estar logado e incluir ao menos um ponto para acessar esta página.")
        st.stop()

    st.title('PONTOS')

    col1, col2 = st.columns([1, 1])
    
    # Inicializa variáveis globais
    #lat_valor = ""
    #lon_valor = ""
    #map_data = {}

    with col1:
        if st.button("🔄 Atualizar Lista", key="botao_atualizar") or "df" not in st.session_state:
            consultaList = []
            for item in PontosController.SelecionarTodos():
                consultaList.append([
                    item.id, item.estado, item.codigo, item.municipio, item.data,
                    item.latitude, item.longitude, item.cultura, item.estadiofenolog,
                    item.altitude, item.temperatura, item.tpsafra, item.informante, item.emailinfo
                ])
            df = pd.DataFrame(consultaList, columns=[
                'id', 'estado', 'codigo', 'municipio', 'data', 'latitude', 'longitude',
                'cultura', 'estadiofenolog', 'altitude', 'temperatura', 'tp_safra',
                'informante', 'emailinfo'
            ])
            st.session_state['df'] = df

        st.info("Selecione o Estado e o Município para Carregar a tabela com os dados.")

        df = st.session_state['df']
        df_exibicao = df.drop(columns=["informante", "emailinfo"])

        estados_disponiveis = sorted(df['estado'].dropna().unique())
        estado_selecionado = st.selectbox("Selecione o Estado:", [""] + estados_disponiveis)

        #cidades_disponiveis = sorted(df['municipio'].dropna().unique())
        if estado_selecionado:
            cidades_disponiveis = sorted(df[df['estado'] == estado_selecionado]['municipio'].dropna().unique())
        else:
            cidades_disponiveis = []

        cidade = st.selectbox("Selecione o município:", [""] + cidades_disponiveis)

        df_filtrado = df_exibicao[df_exibicao['municipio'] == cidade].copy()

        st.write('Lista com os registros por Município inseridos no Banco de Dados')
        st.dataframe(df_filtrado.sort_values(by='data', ascending=True))
        st.write('O total de Registros para o município acima é:', df_filtrado.shape[0])

        st.download_button(
            label="⬇️ Download CSV",
            data=df_filtrado.to_csv(index=False).encode("utf-8"), # df_exibicao (todas as culturas) ou df_filtrado (só as culturas do municipio selecionado)
            file_name="pontos_culturas.csv",
            mime="text/csv"
        )

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

            # Adicionando botão de tela cheia
            Fullscreen().add_to(m)

            # Delimitação do município usando geobr
            try:
                if df_filtrado['codigo'].notnull().any():
                    codigo_ibge = int(df_filtrado['codigo'].iloc[0])
                    municipio_gdf = read_municipality(code_muni=codigo_ibge, year=2022)

                    if not municipio_gdf.empty:
                        folium.GeoJson(municipio_gdf.__geo_interface__).add_to(m)
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

            # Renderiza o mapa
            map_data = st_folium(m, width=900, height=700)

            # Captura clique do usuário
            #clicked_coords = map_data.get("last_clicked")
        else:
            st.warning("Nenhum ponto encontrado para o município selecionado.")
            #clicked_coords = None  # Garante que essa variável sempre exista

