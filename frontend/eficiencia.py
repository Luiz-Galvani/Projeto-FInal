import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# ====================================
# Configuração da Página Streamlit e CSS
# ====================================
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)

# ====================================
# Conexão ao Banco de Dados e Carregamento de Dados
# ====================================
conn = sqlite3.connect("data/voos.db", check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM voos;", conn)

# ====================================
# Título Principal e Subtítulo
# ====================================
st.markdown("<h1 style='text-align: center;'>📈 Análise de Desempenho Operacional </h1>", unsafe_allow_html=True)
st.subheader('', divider=True)

# ====================================
# Cálculo dos KPIs
# ====================================
mediacombustivel = df['combustivel_litros'].mean().round(2)
# A variável 'psgt' é calculada, mas não é usada nas métricas abaixo.
psgt = df['passageiros_pagos'].sum()
combustivel = df['combustivel_litros'].sum()
km = df['distancia_voada_km'].sum()

kmcomb = (combustivel / km).round(2)
passtotal = df['passageiros_pagos'].sum() + df['passageiros_gratis'].sum()
passcomb = (passtotal / combustivel).round(2)
qtdvoos = df['decolagens'].sum()
total_empresas = df['empresa_nome'].nunique()


# ====================================
# Exibição dos KPIs
# ====================================
c1, c2, c3 = st.columns(3)

# Segunda linha de métricas
def kpi_box(title, value):
    return f"""
    <div style="
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-family: Arial, sans-serif;
        margin-bottom: 10px;
    ">
        <div style="font-size: 18px; font-weight: 500; color: #333;">{title}</div>
        <p style='font-size: 24px; margin: 5px 0 0 0; font-weight: bold;'>{value}</p>
    </div>
    """
with c1.container(border = True):
    st.markdown(kpi_box('Litros consumidos por KM', kmcomb), unsafe_allow_html=True)

with c2.container(border = True):
    st.markdown(kpi_box('Eficiência por Passageiro (Passageiros/Litro)', passcomb), unsafe_allow_html=True)

with c3.container(border = True):
    st.markdown(kpi_box('Consumo Médio de Combustível', mediacombustivel), unsafe_allow_html=True)

st.subheader("", divider = True)
# Análise de Consumo de Combustível por Empresa ou Região
st.markdown("<h2 style='text-align: center;'>Variação Mensal da Eficiência</h2>", unsafe_allow_html=True)


# Cria uma coluna 'ano_mes' para agrupar por ano e mês
df['ano_mes'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)

# Agrupa por ano_mes e calcula os totais necessários para eficiência
eficiencia_mensal = df.groupby('ano_mes').agg(
    combustivel_total=('combustivel_litros', 'sum'),
    passageiros_total=('passageiros_pagos', 'sum'),  # Considera apenas passageiros pagos para esta análise
    distancia_total=('distancia_voada_km', 'sum')
).reset_index()

# Calcula as métricas de eficiência mensal
eficiencia_mensal['Litros por KM Mensal'] = (eficiencia_mensal['combustivel_total'] / eficiencia_mensal['distancia_total']).round(2)
eficiencia_mensal['Passageiros por Litro Mensal'] = (eficiencia_mensal['passageiros_total'] / eficiencia_mensal['combustivel_total']).round(2)

# Substitui NaNs ou infs por 0 ou um valor adequado para visualização
eficiencia_mensal = eficiencia_mensal.fillna(0)
eficiencia_mensal = eficiencia_mensal.replace([float('inf'), -float('inf')], 0)

# Cria as colunas para os gráficos de variação mensal
col_litros_km, col_passageiros_litro = st.columns(2)

with col_litros_km.container(border = True):
    st.markdown("<h3 style='text-align: center;'>Litros por KM ao longo dos Meses</h3>", unsafe_allow_html=True)
    fig = px.line(
        eficiencia_mensal,
        x='ano_mes',
        y='Litros por KM Mensal',
        markers=True,
        labels={"ano_mes": "Mês", "Litros por KM Mensal": "Litros/KM"},
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

with col_passageiros_litro.container(border = True):
    st.markdown("<h3 style='text-align: center;'>Passageiros por Litro ao longo dos Meses</h3>", unsafe_allow_html=True)
    fig = px.line(
        eficiencia_mensal,
        x='ano_mes',
        y='Passageiros por Litro Mensal',
        markers=True,
        labels={"ano_mes": "Mês", "Passageiros por Litro Mensal": "Litros/KM"},
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)
st.write("Tabela de Variação Mensal da Eficiência:")
st.dataframe(eficiencia_mensal.round(2), use_container_width=True)
st.subheader("", divider = True)
st.markdown("<h2 style='text-align: center;'>Consumo Médio de Combustível</h2>", unsafe_allow_html=True)
tab_empresa, tab_continente_pais = st.tabs(["Empresa","País/Continente"])

with tab_empresa:
    # --- Cálculos para os gráficos Top 10 (USANDO O DATAFRAME ORIGINAL 'df') ---
    # Estes cálculos usam o DataFrame 'df' completo para que os gráficos Top 10 não sejam afetados pela pesquisa.
    tabela_empresas_total = df.groupby(["empresa_sigla", "empresa_nome"]).agg(
        combustivel_litros_total=('combustivel_litros', 'sum'),
        passageiros_pagos_total=('passageiros_pagos', 'sum'),
        passageiros_gratis_total=('passageiros_gratis', 'sum'),
        distancia_voada_km_total=('distancia_voada_km', 'sum'),
        decolagens=('decolagens', 'sum'),
    ).round(2).reset_index()

    tabela_empresas_total['Litros por KM (Empresa)'] = (tabela_empresas_total['combustivel_litros_total'] / tabela_empresas_total['distancia_voada_km_total']).round(2)
    tabela_empresas_total['Passageiros por Litro (Empresa)'] = ((tabela_empresas_total['passageiros_pagos_total'] + tabela_empresas_total['passageiros_gratis_total']) / tabela_empresas_total['combustivel_litros_total']).round(2)
    tabela_empresas_total['Consumo Médio (L)'] = (tabela_empresas_total['combustivel_litros_total'] / tabela_empresas_total['decolagens']).round(2)

    tabela_empresas_total.columns = [
        "Sigla", "Empresa", "Combustível Total (L)", "Passageiros Pagos (Total)",
        "Passageiros Grátis (Total)", "Distância Total (KM)", "Voos (Total)",
        "Litros por KM (Empresa)", "Passageiros por Litro (Empresa)", "Consumo Médio por Voo (L)"
    ]
    tabela_empresas_total = tabela_empresas_total.fillna(0).replace([float('inf'), -float('inf')], 0)
    # --- Fim dos cálculos para os gráficos Top 10 ---

    col1, col2 = st.columns(2)

    # Benchmark: Gráficos de barras para eficiência entre empresas
    # Top 10 empresas por Litros por KM (menor é melhor) - USANDO tabela_empresas_total (dados globais)
    with col1.container(border = True):
        st.markdown("<h4 style='text-align: center;'> Top 10 Empresas - Mais Eficientes (Litros por KM)</h4>", unsafe_allow_html=True)
        eficiencia_km = tabela_empresas_total[tabela_empresas_total['Combustível Total (L)'] > 0].sort_values(by="Litros por KM (Empresa)", ascending=True).head(10)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.barplot(x="Litros por KM (Empresa)", y="Empresa", data=eficiencia_km, palette="viridis", ax=ax1)
        ax1.set_xlabel("Litros por KM")
        ax1.set_ylabel("Empresa")
        st.pyplot(fig1)

    # Top 10 empresas por Passageiros por Litro (maior é melhor) - USANDO tabela_empresas_total (dados globais)
    with col2.container(border = True):
        st.markdown("<h4 style='text-align: center;'>Top 10 Empresas - Mais Eficientes (Passageiros por Litro)</h4>", unsafe_allow_html=True)
        eficiencia_passageiro = tabela_empresas_total.sort_values(by="Passageiros por Litro (Empresa)", ascending=False).head(10)
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.barplot(x="Passageiros por Litro (Empresa)", y="Empresa", data=eficiencia_passageiro, palette="magma", ax=ax2)
        ax2.set_xlabel("Passageiros por Litro")
        ax2.set_ylabel("Empresa")
        st.pyplot(fig2)

    st.subheader("",divider = True)
    st.markdown("<h2 style='text-align: center;'>📊 Consumo Médio de Combustível e Eficiência por Empresa</h2>", unsafe_allow_html=True)
    # Input para pesquisar empresas
    empresa_pesquisa = st.text_input(
        "🔍 Pesquisar empresa (digite a sigla ou parte do nome):",
        placeholder="Ex: GOL, LATAM, AZUL..."
    )

    # Filtra as empresas com base na pesquisa para a tabela principal
    if empresa_pesquisa:
        df_filtrado_para_tabela = df[
            df["empresa_sigla"].str.contains(empresa_pesquisa, case=False) |
            df["empresa_nome"].str.contains(empresa_pesquisa, case=False)
        ]
    else:
        df_filtrado_para_tabela = df  # Se não houver pesquisa, mostra todas as empresas
    # Tabela de consumo médio por empresa (calculada com df_filtrado_para_tabela)
    
    tabela_empresas = df_filtrado_para_tabela.groupby(["empresa_sigla", "empresa_nome"]).agg(
        combustivel_litros_total=('combustivel_litros', 'sum'),
        passageiros_pagos_total=('passageiros_pagos', 'sum'),
        passageiros_gratis_total=('passageiros_gratis', 'sum'),
        distancia_voada_km_total=('distancia_voada_km', 'sum'),
        decolagens=('decolagens', 'sum'),
    ).round(2).reset_index()

    # Calcula as novas métricas de eficiência por empresa
    tabela_empresas['Litros por KM (Empresa)'] = (tabela_empresas['combustivel_litros_total'] / tabela_empresas['distancia_voada_km_total']).round(2)
    tabela_empresas['Passageiros por Litro (Empresa)'] = ((tabela_empresas['passageiros_pagos_total'] + tabela_empresas['passageiros_gratis_total']) / tabela_empresas['combustivel_litros_total']).round(2)
    tabela_empresas['Consumo Médio (L)'] = (tabela_empresas['combustivel_litros_total'] / tabela_empresas['decolagens']).round(2)

    # Renomeia colunas para melhor visualização
    tabela_empresas.columns = [
        "Sigla", "Empresa", "Combustível Total (L)", "Passageiros Pagos (Total)",
        "Passageiros Grátis (Total)", "Distância Total (KM)", "Voos (Total)",
        "Litros por KM (Empresa)", "Passageiros por Litro (Empresa)", "Consumo Médio por Voo (L)"
    ]

    # Reordena as colunas para melhor visualização
    tabela_empresas = tabela_empresas[[
        "Sigla", "Empresa", "Consumo Médio por Voo (L)", "Litros por KM (Empresa)",
        "Passageiros por Litro (Empresa)", "Passageiros Pagos (Total)",
        "Distância Total (KM)", "Voos (Total)", "Combustível Total (L)",
        "Passageiros Grátis (Total)"
    ]]

    # Substitui NaNs ou infs por 0 ou um valor adequado para visualização
    tabela_empresas = tabela_empresas.fillna(0)
    tabela_empresas = tabela_empresas.replace([float('inf'), -float('inf')], 0)

    # Mostra a tabela (esta tabela será filtrada pela pesquisa)
    st.dataframe(
        tabela_empresas,
        height=500,
        use_container_width=True
    )

    # Tabela Detalhada (se uma empresa específica for selecionada na pesquisa)
    # Usa df_filtrado_para_tabela para esta tabela de detalhes
    if empresa_pesquisa and not df_filtrado_para_tabela.empty:
        st.subheader(f"✈️ Voos da Empresa: {df_filtrado_para_tabela['empresa_nome'].iloc[0]}")

        # Seleciona apenas colunas relevantes
        cols_detalhes = [
            "ano", "mes", "origem_sigla", "destino_sigla",
            "combustivel_litros", "passageiros_pagos", "distancia_voada_km"
        ]

        st.dataframe(
            df_filtrado_para_tabela[cols_detalhes].rename(columns={
                "ano": "Ano", "mes": "Mês",
                "origem_sigla": "Origem",
                "destino_sigla": "Destino",
                "combustivel_litros": "Combustível (L)",
                "passageiros_pagos": "Passageiros",
                "distancia_voada_km": "Distância (KM)"
            }),
            height=400,
            use_container_width=True
        )
    elif empresa_pesquisa and df_filtrado_para_tabela.empty:
        st.warning("⚠️ Nenhuma empresa encontrada com esse nome!")


with tab_continente_pais:
    # Se a análise for por País/Continente
    st.markdown("<h3 style='text-align: center;'>Consumo Médio por País (Litros por Voo)</h3>", unsafe_allow_html=True)
    col_pais_chart, col_pais_table = st.columns(2)
    # Consumo médio por país (origem)
    consumo_pais = df.groupby('origem_pais')['combustivel_litros'].mean().round(2).sort_values(ascending=False)

    with col_pais_chart.container(border = True):
        fig_pais, ax_pais = plt.subplots(figsize=(10, 6))
        # Eixos invertidos para gráfico vertical, nova paleta para países
        sns.barplot(x=consumo_pais.head(10).index, y=consumo_pais.head(10).values, palette="viridis", ax=ax_pais)
        ax_pais.set_xlabel("País")
        ax_pais.set_ylabel("Consumo Médio (L)")
        plt.xticks(rotation=45, ha='right')  # Rotaciona rótulos do eixo X para melhor visualização
        st.pyplot(fig_pais)
    with col_pais_table:
        st.dataframe(consumo_pais.reset_index().rename(columns={"combustivel_litros": "Consumo Médio (L)"}), use_container_width=True)

    st.subheader("", divider = True)
    st.markdown("<h3 style='text-align: center;'>Consumo Médio por Continente (Litros por Voo)</h3>", unsafe_allow_html=True)
    col_cont_chart, col_cont_table = st.columns(2)
    # Consumo médio por continente (origem)
    consumo_continente = df.groupby('origem_continente')['combustivel_litros'].mean().round(2).sort_values(ascending=False)

    with col_cont_chart.container(border = True):
        fig_cont, ax_cont = plt.subplots(figsize=(10, 6))
        # Eixos invertidos para gráfico vertical, nova paleta para continentes
        sns.barplot(x=consumo_continente.index, y=consumo_continente.values, palette="viridis", ax=ax_cont)
        ax_cont.set_xlabel("Continente")
        ax_cont.set_ylabel("Consumo Médio (L)")
        plt.xticks(rotation=45, ha='right')  # Rotaciona rótulos do eixo X para melhor visualização
        st.pyplot(fig_cont)
    with col_cont_table:
        st.dataframe(consumo_continente.reset_index().rename(columns={"combustivel_litros": "Consumo Médio (L)"}), use_container_width=True)

# Variação Mensal da Eficiência

