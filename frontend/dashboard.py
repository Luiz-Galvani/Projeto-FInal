import streamlit as st  
import sqlite3

st.markdown("<h1 style='text-align: center;'>Dashboard</h1>", unsafe_allow_html=True)

st.divider()

conn = sqlite3.connect("data/voos.db")
cursor = conn.cursor()

## Big Numbers
# Total de Passageiros
cursor.execute("SELECT SUM(passageiros_pagos + passageiros_gratis) FROM voos")
total_passageiros = cursor.fetchone()[0]

col1, col2, col3, col4 = st.columns(4)

col1.container(border=True).metric("Total de Passageiros:", f"{int(total_passageiros)}")

# Destino Mais Procurado
cursor.execute("SELECT destino_nome, SUM(passageiros_pagos + passageiros_gratis) AS total_passageiros FROM voos GROUP BY destino_nome ORDER BY total_passageiros DESC LIMIT 1")
destino_procurado = cursor.fetchone()[0]

col2.container(border=True).metric("Destino Mais Procurado: ", f'{destino_procurado}')

# RPK/ASK -> Taxa de Ocupação
cursor.execute("SELECT SUM(rpk) / SUM(ask) AS taxa_ocupacao FROM voos")
taxa_ocupacao = cursor.fetchone()[0]

col3.container(border=True).metric("Taxa de Ocupação:", f"{taxa_ocupacao:.2%}")

# Empresa com mais voos/volumes de passageiros
cursor.execute("SELECT empresa_nome, COUNT(*) AS total_voos FROM voos GROUP BY empresa_nome ORDER BY total_voos DESC LIMIT 1")
empresa_mais_voos = cursor.fetchone()[0]

col4.container(border=True).metric("Empresa com mais voos:", f'{empresa_mais_voos}')

## Gráficos 
# Evolução mensal de passageiros e carga
# Gráfico de Pizza Doméstico/Internacional
# Quais regiões geram mais passageiros
# Gráfico de barras de passageiros por empresa