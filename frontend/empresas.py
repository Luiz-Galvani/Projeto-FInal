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

st.header("📊 Top 10 Empresas")

tab1, tab2, tabs3= st.tabs([
    "🧑‍🤝‍🧑 Top 10 Passageiros",
    "📦 Top 10 Carga (kg)",
    "🛫 Top 10 Distância (km)"
])

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
            orientation="h",
            color_discrete_sequence=px.colors.qualitative.Plotly
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
            orientation="h",
            color_discrete_sequence=px.colors.qualitative.Plotly
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
            orientation="h",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_distancia.update_layout(
            showlegend=False,
            yaxis={"tickfont": {"size": 10}},
            height=400
        )
        st.plotly_chart(fig_distancia, use_container_width=True)

st.divider()

@st.cache_data
def load_ranking_horas(top_n: int = 5):
    query = """
    SELECT 
      empresa_nome,
      SUM(horas_voadas) AS total_horas_voadas
    FROM voos
    GROUP BY empresa_nome
    ORDER BY total_horas_voadas DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(top_n,))

@st.cache_data
def load_horas_temporal_empresa(empresa: str):
    query = """
        SELECT 
          empresa_nome,
          ano,
          mes,
          SUM(horas_voadas) AS horas_voadas
        FROM voos
        WHERE empresa_nome = ?
        GROUP BY empresa_nome, ano, mes
        ORDER BY ano, mes
    """
    return pd.read_sql_query(query, conn, params=(empresa,))

@st.cache_data
def load_duracao_voos(empresa: str | None = None):
    if empresa and empresa != "Todas":
        query = "SELECT horas_voadas FROM voos WHERE empresa_nome = ?"
        return pd.read_sql_query(query, conn, params=(empresa,))
    else:
        query = "SELECT empresa_nome, horas_voadas FROM voos"
        return pd.read_sql_query(query, conn)

@st.cache_data
def load_empresas() -> list[str]:
    df = pd.read_sql_query("SELECT DISTINCT empresa_nome FROM voos ORDER BY empresa_nome", conn)
    return df['empresa_nome'].tolist()

st.header("⏱️ Horas Voadas por Empresa")

tabs = st.tabs([
    "🏆 Ranking Top-5",
    "📈 Evolução Mensal",
])

with tabs[0]:
    st.subheader("Top-5 Empresas por Horas Voadas")
    top5 = load_ranking_horas(5)
    if top5.empty:
        st.warning("Nenhum dado encontrado para as empresas.")
    else:
        fig_rank = px.bar(
            top5,
            x='total_horas_voadas',
            y='empresa_nome',
            orientation='h',
            labels={'empresa_nome': 'Empresa', 'total_horas_voadas': 'Horas Voadas'},
            title="Ranking: Horas Voadas",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_rank.update_layout(
            yaxis={'categoryorder': 'total ascending', 'tickfont': {'size': 10}},
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_rank, use_container_width=True)

        st.dataframe(top5, use_container_width=True, height=220)

with tabs[1]:
    st.subheader("📈 Evolução Mensal de Horas Voadas")

    empresa_selecionada = st.selectbox(
        "Selecione a Empresa",
        options=load_empresas()
    )
    df_temp = load_horas_temporal_empresa(empresa_selecionada)

    if df_temp.empty:
        st.warning("Não há registros para a empresa selecionada.")
    else:
        df_temp['data'] = pd.to_datetime({
            'year':  df_temp['ano'],
            'month': df_temp['mes'],
            'day':   1
        })

        fig_time = px.line(
            df_temp,
            x='data',
            y='horas_voadas',
            title=f"Evolução Mensal – {empresa_selecionada}",
            labels={'data':'Data','horas_voadas':'Horas Voadas'},
            markers=True
        )
        fig_time.update_layout(
            xaxis=dict(dtick="M1", tickformat="%b/%Y"),
            yaxis_tickformat=".0f"
        )
        st.plotly_chart(fig_time, use_container_width=True)

st.divider()
st.header("🚀 Decolagens vs Distância Voada")
    
# --- Fim da Seção ---
conn.close()