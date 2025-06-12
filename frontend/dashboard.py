import streamlit as st  
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import airportsdata
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.markdown("<h1 style='text-align: center;'>📊 Dashboard </h1>", unsafe_allow_html=True)

st.subheader('', divider=True)

conn = sqlite3.connect("data/voos.db")
cursor = conn.cursor()

## Big Numbers
col1, col2, col3, col4 = st.columns(4)

# Total de Passageiros
cursor.execute('SELECT SUM(passageiros_pagos + passageiros_gratis) FROM voos')
total_passageiros = cursor.fetchone()[0]

with col1.container(border=True):
    st.markdown(f"<h4 style='text-align: center;'> Total de Passageiros <br> {total_passageiros} </h4>", unsafe_allow_html=True)

# Total de Carga (Kg)
cursor.execute('SELECT SUM(carga_paga_kg + carga_gratis_kg) FROM voos')
carga_total = cursor.fetchone()[0]

with col2.container(border=True):
    st.markdown(f"<h4 style='text-align: center;'> Carga Total <br> {carga_total} Kg</h4>", unsafe_allow_html=True)

# Total de Correio
cursor.execute('SELECT SUM(correio_kg) FROM voos')
correio_total = cursor.fetchone()[0]

with col3.container(border=True):
    st.markdown(f"<h4 style='text-align: center;'> Total de Correios <br> {correio_total} Kg</h4>", unsafe_allow_html=True)

# Total de Voos (Decolagens)
cursor.execute('SELECT SUM(decolagens) FROM voos')
total_decolagens = cursor.fetchone()[0]

with col4.container(border=True):
    st.markdown(f"<h4 style='text-align: center;'> Total de Decolagens <br> {int(total_decolagens)}</h4>", unsafe_allow_html=True)

# Total de Distância Percorrida
cursor.execute('SELECT SUM(distancia_voada_km) FROM voos')
distancia_percorrida = cursor.fetchone()[0]

col1, col2 = st.columns(2)

# Média de Ocupação (RPK/ASK)
cursor.execute("SELECT SUM(rpk) / SUM(ask) AS taxa_ocupacao FROM voos")
taxa_ocupacao = cursor.fetchone()[0]

with col1.container(border=True):
    st.markdown(f"<h4 style='text-align: center;'> Média de Ocupação (RPK / ASK) <br> {taxa_ocupacao:.2%}</h4>", unsafe_allow_html=True)

# Consumo Total de Combustível
cursor.execute('SELECT SUM(combustivel_litros) FROM voos')
combustivel_total = cursor.fetchone()[0]

with col2.container(border=True):
    st.markdown(f"<h4 style='text-align: center;'> Consumo Total de Combustível <br> {combustivel_total}</h4>", unsafe_allow_html=True)

st.subheader('', divider=True)

## Evolução Temporal (Gráfico de Linhas)
# Passageiros pagantes e gratuitos

col1, col2 = st.columns(2)
meses = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}

with col1.container(border=True):
    tab1, tab2, tab3 = st.tabs(['Passageiros x Mês', 'Carga x Mês', 'Correio x Mês'])
    with tab1:
        cursor.execute(''' 
            CREATE VIEW IF NOT EXISTS passageiros_por_mes AS
                SELECT
                    mes,
                    SUM(passageiros_pagos + passageiros_gratis) AS total_passageiros
                FROM
                    voos
                GROUP BY
                    mes
                ORDER BY
                    mes
        ''')
        cursor.execute('SELECT * FROM passageiros_por_mes')
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        df_pass = pd.DataFrame(rows, columns=column_names)
        df_pass['mes_nome'] = df_pass['mes'].map(meses)
        fig = px.line(df_pass,
                    x='mes_nome',
                    y='total_passageiros',
                    labels={'mes_nome': 'Mês', 'total_passageiros': 'Total de Passageiros'},
                    title='Desempenho Operacional: Volume de Passageiros Transportados por Mês'
                    )
        fig.update_layout(
            margin=dict(l=10, r=30, t=50, b=0),  # Margens para evitar cortes
            title_x=0.1  # Centraliza o título
        )
        st.plotly_chart(fig)

    with tab2:
        # Carga paga e correio
        cursor.execute('''
                        CREATE VIEW IF NOT EXISTS carga_correio AS
                            SELECT
                                mes,
                                SUM(carga_paga_kg) AS total_carga
                            FROM
                                voos
                            GROUP BY
                                mes
                            ORDER BY
                                mes               
        ''')
        cursor.execute('SELECT * FROM carga_correio')
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        df_carga = pd.DataFrame(rows, columns=column_names)
        df_carga['mes_nome'] = df_carga['mes'].map(meses)

        fig = px.line(df_carga,
                    x='mes_nome',
                    y='total_carga',
                    labels={'mes_nome': 'Mês', 'total_carga': 'Carga Total (Kg)'},
                    title='Desempenho Mensal de Carga Aérea: Volume Transportado em kg'
                    )
        fig.update_layout(
            margin=dict(l=10, r=30, t=50, b=0),  # Margens para evitar cortes
            title_x=0.15  # Centraliza o título
        )
        st.plotly_chart(fig)
    
    with tab3:
        cursor.execute('''
                        CREATE VIEW IF NOT EXISTS correio AS
                            SELECT
                                mes,
                                SUM(correio_kg) AS total_correio
                            FROM
                                voos
                            GROUP BY
                                mes
                            ORDER BY
                                mes               
        ''')   
        cursor.execute('SELECT * FROM correio')
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        df_correio = pd.DataFrame(rows, columns=column_names)
        df_correio['mes_nome'] = df_correio['mes'].map(meses)     

        fig = px.line(df_correio,
                    x='mes_nome',
                    y='total_correio',
                    labels={'mes_nome': 'Mês', 'total_correio': 'Correio Total (Kg)'},
                    title='Volume de Correio Aéreo: Tendências Mensais em kg'
                    )
        fig.update_layout(
            margin=dict(l=10, r=30, t=50, b=0),  # Margens para evitar cortes
            title_x=0.23  # Centraliza o título
        )
        st.plotly_chart(fig)

    
## Dristribuição de Natures dos Voos (Gráfico de Pizza)
# Doméstico vs Internacional 
with col2.container(border=True):
    cursor.execute('SELECT natureza, COUNT(decolagens) AS total_voos FROM voos GROUP BY natureza')
    column_names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    df_natureza = pd.DataFrame(rows, columns=column_names)

    fig = px.pie(df_natureza,
                 names='natureza',
                 values='total_voos',
                 title='Distribuição de Voos: Domésticos vs. Internacionais'
    )
    fig.update_layout(
    height=508,  # Altura do gráfico
    margin=dict(l=10, r=30, t=50, b=0),  # Margens para evitar cortes
    title_x=0.23  # Centraliza o título
    )
    st.plotly_chart(fig)

st.subheader('', divider=True)
st.subheader('🌍 Mapa de Conexões Aéreas')

# Carregar dados de aeroportos
airports = airportsdata.load('ICAO')  # Usa códigos ICAO (4 letras)

# Consulta para obter rotas únicas com nomes
cursor.execute('''
    CREATE VIEW IF NOT EXISTS aeroportos AS
        SELECT DISTINCT
            origem_sigla,
            destino_sigla,
            origem_nome,
            destino_nome
        FROM
            voos
        WHERE
            origem_sigla != '' AND destino_sigla != '' AND origem_nome != '' AND destino_nome != ''
''')

# Criar dois seletores: origem e destino
col1, col2 = st.columns(2)

# Obter lista completa de aeroportos
cursor.execute('''
    SELECT DISTINCT origem_nome FROM aeroportos
    UNION
    SELECT DISTINCT destino_nome FROM aeroportos
    ORDER BY origem_nome
''')
nomes_aeroportos = [row[0] for row in cursor.fetchall()]

# Seletor de Origem
with col1:
    # Adicionar opção "Todos" no início
    origens = ["Todos"] + nomes_aeroportos
    origem_selecionada = st.selectbox('Selecione a Origem:', origens)

# Seletor de Destino
with col2:
    destinos = ["Todos"]
    
    # Se uma origem foi selecionada, buscar destinos correspondentes
    if origem_selecionada != "Todos":
        cursor.execute('''
            SELECT DISTINCT destino_nome 
            FROM aeroportos 
            WHERE origem_nome = ?
            ORDER BY destino_nome
        ''', (origem_selecionada,))
        destinos += [row[0] for row in cursor.fetchall()]
    
    destino_selecionado = st.selectbox('Selecione o Destino:', destinos, 
                                      disabled=(origem_selecionada == "Todos"))

# Consulta para obter rotas de acordo com os filtros
if origem_selecionada == "Todos":
    # Mostrar todas as rotas
    cursor.execute('''
        SELECT origem_sigla, destino_sigla
        FROM aeroportos
    ''')
    rotas_filtradas = cursor.fetchall()
    
elif destino_selecionado == "Todos":
    # Mostrar todos os destinos da origem selecionada
    cursor.execute('''
        SELECT origem_sigla, destino_sigla
        FROM aeroportos
        WHERE origem_nome = ?
    ''', (origem_selecionada,))
    rotas_filtradas = cursor.fetchall()
    
else:
    # Mostrar rota específica
    cursor.execute('''
        SELECT origem_sigla, destino_sigla
        FROM aeroportos
        WHERE origem_nome = ? AND destino_nome = ?
    ''', (origem_selecionada, destino_selecionado))
    rotas_filtradas = cursor.fetchall()

# Converter para DataFrame
df_rotas_filtradas = pd.DataFrame(rotas_filtradas, columns=['origem_sigla', 'destino_sigla'])

# Preparar dados para o mapa
fig = go.Figure()

if not df_rotas_filtradas.empty:
    # Listas para armazenar todas as coordenadas
    all_lons = []
    all_lats = []
    
    # Processar cada rota
    for _, rota in df_rotas_filtradas.iterrows():
        origem_sigla = rota['origem_sigla']
        destino_sigla = rota['destino_sigla']
        
        if origem_sigla in airports and destino_sigla in airports:
            # Obter coordenadas
            orig_coords = airports[origem_sigla]
            dest_coords = airports[destino_sigla]
            
            # Adicionar coordenadas para cálculo de limites
            all_lons += [orig_coords['lon'], dest_coords['lon']]
            all_lats += [orig_coords['lat'], dest_coords['lat']]
            
            # Adicionar linha da rota
            fig.add_trace(go.Scattergeo(
                lon = [orig_coords['lon'], dest_coords['lon']],
                lat = [orig_coords['lat'], dest_coords['lat']],
                text = f"{origem_sigla} → {destino_sigla}",
                line = dict(width=1, color='blue'),
                mode = 'lines',
                showlegend = False
            ))
            
            # Adicionar ponto de origem (verde)
            fig.add_trace(go.Scattergeo(
                lon = [orig_coords['lon']],
                lat = [orig_coords['lat']],
                text = f"Origem: {origem_sigla}",
                marker = dict(size=10, color='green'),
                mode = 'markers',
                showlegend = False
            ))
            
            # Adicionar ponto de destino (vermelho)
            fig.add_trace(go.Scattergeo(
                lon = [dest_coords['lon']],
                lat = [dest_coords['lat']],
                text = f"Destino: {destino_sigla}",
                marker = dict(size=10, color='red'),
                mode = 'markers',
                showlegend = False
            ))
    
    # Configurar layout do mapa
    if all_lons and all_lats:
        fig.update_layout(
            title_text = f'Rotas Aéreas: {len(rotas_filtradas)} conexões',
            showlegend = False,
            geo = dict(
                scope = 'world',
                projection_type = 'equirectangular',
                showland = True,
                landcolor = 'rgb(243, 243, 243)',
                countrycolor = 'rgb(204, 204, 204)',
                coastlinewidth = 1,
                coastlinecolor = 'rgb(204, 204, 204)',
            ),
            height = 600,
            margin = {"r":0,"t":40,"l":0,"b":0}
        )
        
        # Ajustar zoom com margem
        fig.update_geos(
            lataxis_range = [min(all_lats) - 5, max(all_lats) + 5],
            lonaxis_range = [min(all_lons) - 10, max(all_lons) + 10]
        )
    else:
        st.warning("Nenhuma rota válida encontrada com os filtros selecionados.")
else:
    if origem_selecionada != "Todos":
        st.warning("Nenhuma rota encontrada com os filtros selecionados.")
    else:
        st.info("Selecione uma origem para visualizar as rotas aéreas")

# Mostrar o gráfico
st.plotly_chart(fig)

# Mostrar tabela com rotas filtradas
if not df_rotas_filtradas.empty:
    with st.expander("Ver detalhes das rotas"):
        # Adicionar nomes completos
        df_exibir = df_rotas_filtradas.copy()
        
        # Obter nomes dos aeroportos
        nomes_dict = {}
        cursor.execute("SELECT origem_sigla, origem_nome FROM aeroportos")
        for sigla, nome in cursor.fetchall():
            nomes_dict[sigla] = nome
        
        df_exibir['origem_nome'] = df_exibir['origem_sigla'].map(nomes_dict)
        df_exibir['destino_nome'] = df_exibir['destino_sigla'].map(nomes_dict)
        
        st.dataframe(df_exibir[['origem_sigla', 'origem_nome', 'destino_sigla', 'destino_nome']])
conn.close()