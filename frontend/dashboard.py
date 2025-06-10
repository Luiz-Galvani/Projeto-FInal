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

# Carga paga e correio

## Dristribuição de Natures dos Voos (Gráfico de Pizza)
# Doméstico vs Internacional 


# col1.container(border=True).metric("Total de Passageiros:", f"{int(total_passageiros)}")

# col2.container(border=True).metric("Destino Mais Procurado: ", f'{destino_procurado}')

# col3.container(border=True).metric("Taxa de Ocupação:", f"{taxa_ocupacao:.2%}")

# col4.container(border=True).metric("Empresa com mais voos:", f'{empresa_mais_voos}')

# st.divider()

# col1, col2 = st.columns(2)