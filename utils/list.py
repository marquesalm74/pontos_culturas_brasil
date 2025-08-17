# list_pontos.py
import streamlit as st
import pandas as pd
import folium
import controllers.pontos_controller as PontosController

from shapely import wkt
from services.database import supabase, carregar_municipios, carregar_limite_municipio, carregar_estados
from matplotlib.colors import to_hex
from streamlit_folium import st_folium
from folium.plugins import Fullscreen

def list_pontos():
    if not st.session_state.get('usuario_autenticado', False):
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()

    st.title("Pontos Cadastrados")

    # --- CARREGAR DADOS ---
    if "df" not in st.session_state or st.button("🔄 Atualizar Lista"):
        data = PontosController.SelecionarTodos()
        if not data:
            st.session_state['df'] = pd.DataFrame()
        else:
            rows = []
            for item in data:
                rows.append([
                    item.get('id'),
                    item.get('estado'),
                    item.get('codigo'),
                    item.get('municipio'),
                    item.get('data'),
                    item.get('latitude'),
                    item.get('longitude'),
                    item.get('cultura'),
                    item.get('estadiofenolog'),
                    item.get('altitude'),
                    item.get('temperatura'),
                    item.get('tpsafra'),
                    item.get('check_point')
                ])
            st.session_state['df'] = pd.DataFrame(rows, columns=[
                'id', 'estado', 'codigo', 'municipio', 'data',
                'latitude', 'longitude', 'cultura', 'estadiofenolog',
                'altitude', 'temperatura', 'tpsafra', 'check_point'
            ])

    df = st.session_state.get('df', pd.DataFrame())
    if df.empty:
        st.info("Nenhum ponto cadastrado.")

    col1, col2 = st.columns([1, 1], gap="large")

    # ---------------- COLUNA ESQUERDA ----------------
    with col1:
        estados = sorted(df['estado'].dropna().unique().tolist()) if not df.empty else []
        estado = st.selectbox("Estado", [""] + estados)

        cidades = sorted(df[df['estado'] == estado]['municipio'].dropna().unique().tolist()) if estado else []
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

        st.divider()
        st.session_state.setdefault('modo_edicao', False)
        st.session_state.setdefault('selected_id', None)
        st.session_state.setdefault('id_selecao', 0)
        st.session_state.setdefault('sucesso_msg', "")
        st.session_state.setdefault('erro_atualizar', "")

        id_sel = st.number_input(
            "ID do registro para editar (digite o id) - Após digitar o ID, clique Enter ou fora da caixa.",
            min_value=0,
            step=1,
            key="id_selecao"
        )

        if id_sel > 0 and st.button("Editar este registro"):
            if not df_filtrado.empty and 'id' in df_filtrado.columns and not df_filtrado[df_filtrado['id'] == id_sel].empty:
                st.session_state['modo_edicao'] = True
                st.session_state['selected_id'] = int(id_sel)
                st.rerun()
            else:
                st.error("Registro não encontrado no filtro atual.")

        if st.session_state['modo_edicao'] and st.session_state['selected_id'] is not None:
            id_edit = st.session_state['selected_id']
            registro = df_filtrado[df_filtrado['id'] == id_edit] if not df_filtrado.empty else pd.DataFrame()

            if registro.empty:
                st.error("Registro não encontrado para edição.")
            else:
                municipio_atual = registro.iloc[0]['municipio']
                codigo_atual = registro.iloc[0]['codigo']
                lat_atual = float(registro.iloc[0]['latitude'])
                lon_atual = float(registro.iloc[0]['longitude'])
                check_atual = bool(registro.iloc[0]['check_point']) if 'check_point' in registro.columns else False
                
                #########################################################
                
                estados_info = carregar_estados()
                df_estados = pd.DataFrame(estados_info)
                df_estados.rename(columns={'name_state': 'estado'}, inplace=True)
                
                # 1️⃣ Recupera code_state do estado atual do registro
                estado_nome = registro.iloc[0]['estado']
                # Supondo que você tenha um dataframe ou dict com mapeamento estado -> code_state
                # Exemplo: df_estados = pd.DataFrame({'estado': [...], 'code_state': [...]})
                code_state = df_estados.loc[df_estados['estado'] == estado_nome, 'code_state'].values
                code_state = str(code_state[0]) if len(code_state) > 0 else None

                lista_municipios_info = carregar_municipios(code_state) if code_state else []
                lista_municipios = [""] + sorted([m['name_muni'] for m in lista_municipios_info])


                ###################################################################################
                
                st.markdown(f"### Editando registro ID {id_edit}")
                novo_municipio = st.selectbox(
                    "Selecione o Município",
                    options=lista_municipios,
                    index=lista_municipios.index(municipio_atual) if municipio_atual in lista_municipios else 0,
                    key="edit_municipio"
                )

                cod_match = df.loc[
                    (df['estado'] == estado) & (df['municipio'] == novo_municipio), 'codigo'
                ]
                codigo_municipio = cod_match.iloc[0] if not cod_match.empty else codigo_atual

                st.text_input("Código do Município", value=str(codigo_municipio), disabled=True, key="edit_codigo")
                nova_lat = st.number_input("Latitude", value=float(lat_atual), format="%.6f", key="edit_lat")
                nova_lon = st.number_input("Longitude", value=float(lon_atual), format="%.6f", key="edit_lon")
                novo_check = st.checkbox("Marcar como verificado", value=check_atual, key="edit_check")

                def salvar_alteracoes(id_edit, municipio_atual, codigo_municipio, nova_lat, nova_lon, novo_check, novo_municipio):
                    try:
                        novos_dados = {
                            "municipio": novo_municipio if novo_municipio != "0" else municipio_atual,
                            "codigo": codigo_municipio,
                            "latitude": float(nova_lat),
                            "longitude": float(nova_lon),
                            "check_point": bool(novo_check),
                        }
                        PontosController.Atualizar(id_edit, novos_dados)
                        st.session_state['sucesso_msg'] = f"Registro {id_edit} atualizado com sucesso!"
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

                if st.session_state['sucesso_msg']:
                    st.success(st.session_state.pop('sucesso_msg'))
                if st.session_state['erro_atualizar']:
                    st.error(st.session_state.pop('erro_atualizar'))

    # ---------------- COLUNA DIREITA ----------------
    with col2:
        st.subheader("🗺️ Mapa dos Pontos")
        if df_filtrado.empty:
            st.warning("Nenhum ponto encontrado para o município selecionado.")
            return

        # Centraliza mapa
        m = folium.Map(
            location=[df_filtrado['latitude'].mean(), df_filtrado['longitude'].mean()],
            zoom_start=10,
            min_zoom=5,
            max_zoom=20,
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri'
        )
        Fullscreen().add_to(m)

        # ------------------ Limite do município ------------------
        code_muni_sel = df_filtrado.iloc[0]['codigo']
        geom_wkt = carregar_limite_municipio(code_muni_sel)
        #st.write(f"WKT carregado para code_muni={code_muni_sel}: {geom_wkt}")  # DEBUG

        if geom_wkt:
            try:
                geom_obj = wkt.loads(geom_wkt)
                folium.GeoJson(
                    geom_obj.__geo_interface__,
                    name="Limite do Município",
                    style_function=lambda x: {"fillColor": "#00000000", "color": "#0000FF", "weight": 2}
                ).add_to(m)
            except Exception as e:
                st.error(f"Erro ao desenhar limite do município: {e}")
        else:
            st.warning("Nenhum limite encontrado para o município selecionado.")

        # ------------------ Pontos ------------------
        culturas_unicas = df_filtrado['cultura'].unique()
        import matplotlib.pyplot as plt
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
