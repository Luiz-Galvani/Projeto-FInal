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
col1, col2, col3 = st.columns(3)
# Total de Passageiros
cursor.execute('SELECT SUM(passageiros_pagos + passageiros_gratis) FROM voos')
total_passageiros = cursor.fetchone()[0]

col1.container(border=True).metric('Total de Passageiros', f'{int(total_passageiros)}')

# Total de Carga (Kg)
cursor.execute('SELECT SUM(carga_paga_kg + carga_gratis_kg + correio_kg + bagagem_kg) FROM voos')
carga_total = cursor.fetchone()[0]

col2.container(border=True).metric('Carga Total', f'{carga_total:.2f} Kg')

# Total de Voos (Decolagens)
cursor.execute('SELECT SUM(decolagens) FROM voos')
total_decolagens = cursor.fetchone()[0]

col3.container(border=True).metric('Total de Decolagens', f'{int(total_decolagens)}')

# Total de Distância Percorrida
cursor.execute('SELECT SUM(distancia_voada_km) FROM voos')
distancia_percorrida = cursor.fetchone()[0]

col1, col2 = st.columns(2)

# Média de Ocupação (RPK/ASK)
cursor.execute("SELECT SUM(rpk) / SUM(ask) AS taxa_ocupacao FROM voos")
taxa_ocupacao = cursor.fetchone()[0]

col1.container(border=True).metric('Média de Ocupação (RPK / ASK)', f'{taxa_ocupacao:.2%}')

# Consumo Total de Combustível
cursor.execute('SELECT SUM(combustivel_litros) FROM voos')
combustivel_total = cursor.fetchone()[0]

col2.container(border=True).metric('Consumo Total de Combustível', f'{int(combustivel_total)}')

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
                    labels={'mes_nome': 'Mês', 'total_passageiros': 'Total de Passageiros'})
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
                    labels={'mes_nome': 'Mês', 'total_carga': 'Carga Total (Kg)'}
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
                    labels={'mes_nome': 'Mês', 'total_correio': 'Correio Total (Kg)'}
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
                 values='total_voos'
    )
    st.plotly_chart(fig)

