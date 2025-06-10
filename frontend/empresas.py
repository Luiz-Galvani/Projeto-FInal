import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

conn = sqlite3.connect('data/voos.db')

@st.cache_data
def carregar_dados():
    query = """
    SELECT 
        empresa_nome,
        SUM(passageiros_pagos + passageiros_gratis) AS total_passageiros,
        SUM(carga_paga_kg + carga_gratis_kg + correio_kg) AS total_carga_kg,
        SUM(distancia_voada_km) AS total_distancia_km,
        SUM(decolagens) AS total_decolagens,
        SUM(horas_voadas) AS total_horas_voadas
    FROM voos
    GROUP BY empresa_nome
    """
    df = pd.read_sql_query(query, conn)
    return df

@st.cache_data
def carregar_metricas():
    query_base = """
    SELECT 
        empresa_nome,
        SUM(passageiros_pagos + passageiros_gratis) AS total_passageiros,
        SUM(decolagens) AS total_decolagens,
        SUM(horas_voadas) AS total_horas_voadas
    FROM voos
    GROUP BY empresa_nome
    """
    
    # Passageiros
    q1 = query_base + " ORDER BY total_passageiros DESC LIMIT 1"
    r1 = pd.read_sql_query(q1, conn).iloc[0]
    
    # Decolagens
    q2 = query_base + " ORDER BY total_decolagens DESC LIMIT 1"
    r2 = pd.read_sql_query(q2, conn).iloc[0]
  
    # Horas Voadas
    q3 = query_base + " ORDER BY total_horas_voadas DESC LIMIT 1"
    r3 = pd.read_sql_query(q3, conn).iloc[0]
    
    return r1, r2, r3

st.markdown("<h1 style='text-align: center;'>Benchmark entre Empresas Aéreas</h1>", unsafe_allow_html=True)
st.divider()

r1, r2, r3 = carregar_metricas()

c1, c2, c3 = st.columns(3)
c1.metric(
        "✈️ Mais Passageiros",
        f"{int(r1.total_passageiros):,}".replace(",", "."),
        r1.empresa_nome
    )
c2.metric(
        "🛫 Mais Decolagens",
        f"{int(r2.total_decolagens):,}".replace(",", "."),
        r2.empresa_nome
    )
c3.metric(
        "⏱️ Mais Horas Voadas",
        f"{int(r3.total_horas_voadas):,}".replace(",", "."),
        r3.empresa_nome
    )

st.divider()

st.header("Top 10 Empresas")

tab1, tab2, tabs3= st.tabs(["Passageiro", "Carga", "Distância"])

with tab1:
    df = carregar_dados()

    if df.empty:
        st.warning("Nenhum dado encontrado na tabela.")
    else:
        df_passageiros = df.sort_values("total_passageiros", ascending=False).head(10)
        fig_passageiros = px.bar(
            df_passageiros,
            y="empresa_nome",
            x="total_passageiros",
            title="Total de Passageiros por Empresa",
            color="empresa_nome",
            labels={"empresa_nome": "Empresa", "total_passageiros": "Passageiros"},
            orientation="h"
        )
        fig_passageiros.update_layout(
            showlegend=False,
            yaxis={"tickfont": {"size": 10}},
            height=400
        )
        st.plotly_chart(fig_passageiros, use_container_width=True)

with tab2:
    df = carregar_dados()

    if df.empty:
        st.warning("Nenhum dado encontrado na tabela.")
    else:
        df_carga = df.sort_values("total_carga_kg", ascending=False).head(10)
        fig_carga = px.bar(
            df_carga,
            y="empresa_nome",
            x="total_carga_kg",
            title="Total de Carga (kg) por Empresa",
            color="empresa_nome",
            labels={"empresa_nome": "Empresa", "total_carga_kg": "Carga (kg)"},
            orientation="h"
        )
        fig_carga.update_layout(
            showlegend=False,
            yaxis={"tickfont": {"size": 10}},
            height=400
        )
        st.plotly_chart(fig_carga, use_container_width=True)

with tabs3:
    df = carregar_dados()

    if df.empty:
        st.warning("Nenhum dado encontrado na tabela.")
    else:
        df_distancia = df.sort_values("total_distancia_km", ascending=False).head(10)
        fig_distancia = px.bar(
            df_distancia,
            y="empresa_nome",
            x="total_distancia_km",
            title="Total de Distância Voadas (km) por Empresa",
            color="empresa_nome",
            labels={"empresa_nome": "Empresa", "total_distancia_km": "Distância (km)"},
            orientation="h"
        )
        fig_distancia.update_layout(
            showlegend=False,
            yaxis={"tickfont": {"size": 10}},
            height=400
        )
        st.plotly_chart(fig_distancia, use_container_width=True)

st.divider()

st.header("Horas Voadas por Empresa")

conn.close()