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

st.divider()

## Gráficos 
# Evolução mensal de passageiros e carga
cursor.execute("SELECT mes, SUM(passageiros_pagos + passageiros_gratis) AS total_passageiros, SUM(carga_paga_kg + carga_gratis_kg) AS total_carga FROM voos GROUP BY mes ORDER BY mes")
meses = []
passageiros = []
carga = []
for row in cursor.fetchall():
    meses.append(row[0])
    passageiros.append(row[1])
    carga.append(row[2])

data = pd.DataFrame({
    'Mes': meses,
    'Passageiros': passageiros,
    'Carga': carga
})

col1, col2 = st.columns(2)

with col1.container(border=True):
    
    eixo_y = 'Passageiros'
    
    st.markdown("<h3 style='text-align: center;'>Quantidade de Passageiros e Carga x Quantidade</h3>", unsafe_allow_html=True)

    st.line_chart(data,
                  x='Mes',
                  y=['Passageiros', 'Carga'],
                  color=["#FF0000", "#0000FF"],
                  x_label='Meses',
                  y_label='Quantidade',
                  )

# Gráfico de Pizza Doméstico/Internacional
cursor.execute("SELECT tipo_voo, COUNT(*) AS total_voos FROM voos GROUP BY tipo_voo")
tipo_voo = []
total_voos = []
for row in cursor.fetchall():
    tipo_voo.append(row[0])
    total_voos.append(row[1])

st.write(tipo_voo)

data_tipos = pd.DataFrame({
    'Tipo': tipo_voo,
    'Quantidade': total_voos
})

with col2.container(border=True):
    fig = px.pie(
                data_tipos,
                values='Quantidade',
                names='Tipo',
                height=415
            )      
    st.plotly_chart(fig)


# Quais regiões geram mais passageiros
# Gráfico de barras de passageiros por empresa