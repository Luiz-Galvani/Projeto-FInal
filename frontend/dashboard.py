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

# Consulta para obter os nomes distintos de aeroportos
cursor.execute('''
    SELECT DISTINCT origem_nome FROM aeroportos
    UNION
    SELECT DISTINCT destino_nome FROM aeroportos
    ORDER BY origem_nome
''')


nomes_aeroportos = [row[0] for row in cursor.fetchall()]

# Selecionador de aeroporto pelo nome
aeroporto_selecionado = st.selectbox('Selecione o aeroporto:', nomes_aeroportos)

# Consulta para obter TODAS as rotas associadas ao aeroporto selecionado
cursor.execute('''
    SELECT 
        origem_sigla,
        destino_sigla
    FROM
        aeroportos
    WHERE
        origem_nome = ? OR destino_nome = ?
''', (aeroporto_selecionado, aeroporto_selecionado))

rotas_filtradas = cursor.fetchall()

# Converter para DataFrame
df_rotas_filtradas = pd.DataFrame(rotas_filtradas, columns=['origem_sigla', 'destino_sigla'])

# Preparar dados para o mapa
fig = go.Figure()

# Obter sigla do aeroporto selecionado
sigla_origem = None
if not df_rotas_filtradas.empty:
    # Encontrar a sigla do aeroporto selecionado
    origem_rows = df_rotas_filtradas[df_rotas_filtradas['origem_sigla'] != '']
    if not origem_rows.empty:
        sigla_origem = origem_rows.iloc[0]['origem_sigla']
    else:
        destino_rows = df_rotas_filtradas[df_rotas_filtradas['destino_sigla'] != '']
        if not destino_rows.empty:
            sigla_origem = destino_rows.iloc[0]['destino_sigla']

# Se encontramos a sigla do aeroporto e ela está na base
if sigla_origem and sigla_origem in airports:
    origem_data = airports[sigla_origem]
    
    # Adicionar aeroporto central (ponto vermelho)
    fig.add_trace(go.Scattergeo(
        lon = [origem_data['lon']],
        lat = [origem_data['lat']],
        text = [f"Aeroporto: {aeroporto_selecionado} ({sigla_origem})"],
        marker = dict(size=15, color='red'),
        name = aeroporto_selecionado,
        mode = 'markers'
    ))
    
    # Listas para cálculo de limites do mapa
    all_lons = [origem_data['lon']]
    all_lats = [origem_data['lat']]
    
    # Contador de rotas plotadas
    rotas_plotadas = 0
    
    # Processar TODAS as rotas associadas
    for index, rota in df_rotas_filtradas.iterrows():
        # Determinar qual é o aeroporto de destino para esta rota
        if rota['origem_sigla'] == sigla_origem:
            sigla_destino = rota['destino_sigla']
            tipo_rota = "Saída"
            cor_linha = 'blue'
        else:
            sigla_destino = rota['origem_sigla']
            tipo_rota = "Chegada"
            cor_linha = 'green'
        
        if sigla_destino in airports:
            dest_data = airports[sigla_destino]
            rotas_plotadas += 1
            
            # Adicionar coordenadas para cálculo de limites
            all_lons.append(dest_data['lon'])
            all_lats.append(dest_data['lat'])
            
            # Adicionar linha da rota
            fig.add_trace(go.Scattergeo(
                lon = [origem_data['lon'], dest_data['lon']],
                lat = [origem_data['lat'], dest_data['lat']],
                text = f"{tipo_rota}: {sigla_origem} ↔ {sigla_destino}",
                line = dict(width=1, color=cor_linha),
                mode = 'lines',
                showlegend = False
            ))
            
            # Adicionar ponto do aeroporto conectado
            fig.add_trace(go.Scattergeo(
                lon = [dest_data['lon']],
                lat = [dest_data['lat']],
                text = f"Aeroporto: {sigla_destino}",
                marker = dict(size=8, color='orange'),
                mode = 'markers',
                showlegend = False
            ))
    
    # Configurar layout do mapa apenas se houver rotas plotadas
    if rotas_plotadas > 0:
        fig.update_layout(
            title_text = f'Conexões de {aeroporto_selecionado} ({rotas_plotadas} rotas)',
            showlegend = True,
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
        
        # Calcular limites do mapa
        min_lon, max_lon = min(all_lons), max(all_lons)
        min_lat, max_lat = min(all_lats), max(all_lats)
        
        # Ajustar o zoom com uma margem
        fig.update_geos(
            lataxis_range = [min_lat - 5, max_lat + 5],
            lonaxis_range = [min_lon - 10, max_lon + 10]
        )
    else:
        st.warning("Nenhuma rota válida encontrada para este aeroporto.")
else:
    st.error(f"Dados do aeroporto {aeroporto_selecionado} (sigla: {sigla_origem}) não encontrados!")

# Mostrar o gráfico
st.plotly_chart(fig)

# Mostrar tabela com todas as rotas
with st.expander("Ver detalhes das conexões"):
    # Adicionar coluna de tipo de rota
    df_exibir = df_rotas_filtradas.copy()
    df_exibir['tipo'] = df_exibir.apply(
        lambda row: "Saída" if row['origem_sigla'] == sigla_origem else "Chegada",
        axis=1
    )
    df_exibir['aeroporto_conectado'] = df_exibir.apply(
        lambda row: row['destino_sigla'] if row['tipo'] == "Saída" else row['origem_sigla'],
        axis=1
    )
    
    st.dataframe(df_exibir[['tipo', 'aeroporto_conectado']].reset_index(drop=True))
    
    # Mostrar informações sobre o aeroporto selecionado
    st.subheader(f"Informações sobre {aeroporto_selecionado}")
    st.write(f"**Sigla:** {sigla_origem}")
    
    # Verificar se a sigla está na base de aeroportos
    if sigla_origem and sigla_origem in airports:
        info = airports[sigla_origem]
        st.write(f"**Nome completo:** {info.get('name', 'N/A')}")
        st.write(f"**Cidade:** {info.get('city', 'N/A')}")
        st.write(f"**País:** {info.get('country', 'N/A')}")
        st.write(f"**Coordenadas:** {info['lat']}, {info['lon']}")
    else:
        st.warning("Informações adicionais não disponíveis")

conn.close()