import streamlit as st
import sqlite3
import pandas as pd

st.markdown("<h1 style='text-align: center;'>✈️ Análise por Empresa</h1>", unsafe_allow_html=True)
st.divider()

# Conexão
conn = sqlite3.connect('data/voos.db')

q1 = """
SELECT empresa_nome,
       SUM(passageiros_pagos + passageiros_gratis) AS total_passageiros
FROM voos
GROUP BY empresa_nome
ORDER BY total_passageiros DESC
LIMIT 1
"""
r1 = pd.read_sql_query(q1, conn).iloc[0]

q2 = """
SELECT empresa_nome,
       SUM(decolagens) AS total_decolagens
FROM voos
GROUP BY empresa_nome
ORDER BY total_decolagens DESC
LIMIT 1
"""
r2 = pd.read_sql_query(q2, conn).iloc[0]

q3 = """
SELECT empresa_nome,
       SUM(horas_voadas) AS total_horas_voadas
FROM voos
GROUP BY empresa_nome
ORDER BY total_horas_voadas DESC
LIMIT 1
"""
r3 = pd.read_sql_query(q3, conn).iloc[0]

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

st.subheader("📊 KPIs da Empresa")
empresas = pd.read_sql_query(
    "SELECT DISTINCT empresa_nome FROM voos ORDER BY empresa_nome", conn
)
empresa = st.selectbox("Selecione a Empresa", empresas['empresa_nome'])

query = f"""
SELECT
  SUM(passageiros_pagos + passageiros_gratis) AS total_passageiros,
  SUM(decolagens)                     AS total_decolagens,
  SUM(horas_voadas)                   AS total_horas_voadas,
  ROUND(
    SUM(combustivel_litros)*1.0
    / NULLIF(SUM(horas_voadas),0)
  , 2) AS consumo_medio_l_por_hora
FROM voos
WHERE empresa_nome = ?
"""
kpis = pd.read_sql_query(query, conn, params=(empresa,)).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("✈️ Passageiros Totais",    f"{int(kpis.total_passageiros):,}".replace(",", "."))
col2.metric("🛫 Decolagens Totais",     f"{int(kpis.total_decolagens):,}".replace(",", "."))
col3.metric("⏱️ Horas Voadas Totais",   f"{int(kpis.total_horas_voadas):,}".replace(",", "."))

st.divider()
