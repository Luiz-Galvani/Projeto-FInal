import streamlit as st  
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.markdown("<h1 style='text-align: center;'>Dashboard</h1>", unsafe_allow_html=True)

st.divider()

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

st.divider()

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

