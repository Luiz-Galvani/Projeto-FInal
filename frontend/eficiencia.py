import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt

# Inject Font Awesome CSS: Isso permite que você use os ícones do Font Awesome.
# 'all.min.css' inclui todos os estilos (sólido, regular, light, etc.).
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)

# Conecta ao banco de dados SQLite
conn = sqlite3.connect("data/voos.db", check_same_thread=False)
# Carrega os dados da tabela 'voos' para um DataFrame
df = pd.read_sql_query("SELECT * FROM voos;", conn)
 

# Título principal do aplicativo
st.title("Análise de Desempenho Operacional")

# Cria 3 colunas para exibir as métricas (2 linhas de 3)
c1, c2, c3 = st.columns(3)

# Calcula as métricas principais
mediacombustivel = df['combustivel_litros'].mean().round(2)
psgt = df['passageiros_pagos'].sum()
combustivel = df['combustivel_litros'].sum()
km = df['distancia_voada_km'].sum()

# Eficiência por Distância: Relação combustível/distância (litros por km)
kmcomb = (combustivel / km).round(2)

passtotal = df['passageiros_pagos'].sum() + df['passageiros_gratis'].sum()
# Passageiros transportados por litro
passcomb = (passtotal / combustivel).round(2)

qtdvoos = df['decolagens'].sum()

# Novo KPI: Total de Empresas
total_empresas = df['empresa_nome'].nunique()

# Exibe as métricas nas colunas com o novo estilo (sem ícones do Font Awesome)
# Primeira linha de métricas
c1.metric('Total de Empresas', int(total_empresas), border=True)
c2.metric( 'Passageiros Transportados', int(passtotal), border=True)
c3.metric( 'Total de Voos', int(qtdvoos), border=True)

# Segunda linha de métricas
c1.metric('Litros consumidos por KM', kmcomb, border=True)
c2.metric('Eficiência por Passageiro (Passageiros/Litro)', passcomb, border=True)
c3.metric( 'Consumo Médio de Combustível', mediacombustivel, border=True)


# Título da seção de análise de consumo por empresa

st.markdown("---")
st.subheader("Consumo Médio de Combustível")

# Seleção do tipo de análise: por Empresa ou País/Continente
analise = st.radio(
    "Agrupar por:",
    ("Empresa", "País/Continente"),
    horizontal=True
)

if analise == "Empresa":
    # Input para pesquisar empresas
    empresa_pesquisa = st.text_input(
        "🔍 Pesquisar empresa (digite a sigla ou parte do nome):",
        placeholder="Ex: GOL, LATAM, AZUL..."
    )

    # Filtra as empresas com base na pesquisa (case-insensitive)
    if empresa_pesquisa:
        df_filtrado = df[
            df["empresa_sigla"].str.contains(empresa_pesquisa, case=False) |
            df["empresa_nome"].str.contains(empresa_pesquisa, case=False)
        ]
    else:
        df_filtrado = df   # Se não houver pesquisa, mostra todas as empresas

    # Título da tabela de consumo médio por empresa
    st.subheader("📊 Consumo Médio de Combustível e Eficiência por Empresa")

    # Agrupa por empresa e calcula as métricas agregadas
    tabela_empresas = df_filtrado.groupby(["empresa_sigla", "empresa_nome"]).agg(
        combustivel_litros_total=('combustivel_litros', 'sum'),
        passageiros_pagos_total=('passageiros_pagos', 'sum'),
        passageiros_gratis_total=('passageiros_gratis', 'sum'),
        distancia_voada_km_total=('distancia_voada_km', 'sum'),
        decolagens=('decolagens', 'sum'),
    ).round(2).reset_index()

    # Calcula as novas métricas de eficiência por empresa
    # Correção: o nome da variável estava incorreto (tabela_emprescas para tabela_empresas)
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
        "Passageiros Grátis (Total)" # Keep all columns for completeness
    ]]

    # Substitui NaNs ou infs por 0 ou um valor adequado para visualização
    tabela_empresas = tabela_empresas.fillna(0)
    tabela_empresas = tabela_empresas.replace([float('inf'), -float('inf')], 0)


    # Mostra a tabela
    st.dataframe(
        tabela_empresas,
        height=500,
        use_container_width=True
    )

    # Benchmark: Gráficos de barras para eficiência entre empresas
    st.subheader("🏆 Benchmark de Eficiência entre Empresas")

    # Top 10 empresas por Litros por KM (menor é melhor)
    st.write("#### Top 10 Empresas - Mais Eficientes (Litros por KM)")
    # Filtra empresas onde o consumo total de combustível é maior que 0 antes de classificar
    eficiencia_km = tabela_empresas[tabela_empresas['Combustível Total (L)'] > 0].sort_values(by="Litros por KM (Empresa)", ascending=True).head(10)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x="Litros por KM (Empresa)", y="Empresa", data=eficiencia_km, palette="viridis", ax=ax1)
    ax1.set_xlabel("Litros por KM")
    ax1.set_ylabel("Empresa")
    st.pyplot(fig1)

    # Top 10 empresas por Passageiros por Litro (maior é melhor)
    st.write("#### Top 10 Empresas - Mais Eficientes (Passageiros por Litro)")
    eficiencia_passageiro = tabela_empresas.sort_values(by="Passageiros por Litro (Empresa)", ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(x="Passageiros por Litro (Empresa)", y="Empresa", data=eficiencia_passageiro, palette="magma", ax=ax2)
    ax2.set_xlabel("Passageiros por Litro")
    ax2.set_ylabel("Empresa")
    st.pyplot(fig2)


    # Tabela Detalhada (se uma empresa específica for selecionada)
    if empresa_pesquisa and not df_filtrado.empty:
        st.subheader(f"✈️ Voos da Empresa: {df_filtrado['empresa_nome'].iloc[0]}")

        # Seleciona apenas colunas relevantes
        cols_detalhes = [
            "ano", "mes", "origem_sigla", "destino_sigla",
            "combustivel_litros", "passageiros_pagos", "distancia_voada_km"
        ]
        
        st.dataframe(
            df_filtrado[cols_detalhes].rename(columns={
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
    elif empresa_pesquisa and df_filtrado.empty:
        st.warning("⚠️ Nenhuma empresa encontrada com esse nome!")

else:
    # Se a análise for por País/Continente
    st.write("### Consumo Médio por País (Litros por Voo)")
    col_pais_chart, col_pais_table = st.columns(2)
    # Consumo médio por país (origem)
    consumo_pais = df.groupby('origem_pais')['combustivel_litros'].mean().round(2).sort_values(ascending=False)
    
    with col_pais_chart:
        fig_pais, ax_pais = plt.subplots(figsize=(10, 6))
        # Eixos invertidos para gráfico vertical, nova paleta para países
        sns.barplot(x=consumo_pais.head(10).index, y=consumo_pais.head(10).values, palette="Set2", ax=ax_pais)
        ax_pais.set_xlabel("País")
        ax_pais.set_ylabel("Consumo Médio (L)")
        plt.xticks(rotation=45, ha='right') # Rotaciona rótulos do eixo X para melhor visualização
        st.pyplot(fig_pais)
    with col_pais_table:
        st.dataframe(consumo_pais.reset_index().rename(columns={"combustivel_litros": "Consumo Médio (L)"}), use_container_width=True)

    st.write("### Consumo Médio por Continente (Litros por Voo)")
    col_cont_chart, col_cont_table = st.columns(2)
    # Consumo médio por continente (origem)
    consumo_continente = df.groupby('origem_continente')['combustivel_litros'].mean().round(2).sort_values(ascending=False)
    
    with col_cont_chart:
        fig_cont, ax_cont = plt.subplots(figsize=(10, 6))
        # Eixos invertidos para gráfico vertical, nova paleta para continentes
        sns.barplot(x=consumo_continente.index, y=consumo_continente.values, palette="plasma", ax=ax_cont)
        ax_cont.set_xlabel("Continente")
        ax_cont.set_ylabel("Consumo Médio (L)")
        plt.xticks(rotation=45, ha='right') # Rotaciona rótulos do eixo X para melhor visualização
        st.pyplot(fig_cont)
    with col_cont_table:
        st.dataframe(consumo_continente.reset_index().rename(columns={"combustivel_litros": "Consumo Médio (L)"}), use_container_width=True)

# --- Nova Seção: Variação Mensal da Eficiência ---
st.markdown("---")
st.title("Variação Mensal da Eficiência")

# Cria uma coluna 'ano_mes' para agrupar por ano e mês
df['ano_mes'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)

# Agrupa por ano_mes e calcula os totais necessários para eficiência
eficiencia_mensal = df.groupby('ano_mes').agg(
    combustivel_total=('combustivel_litros', 'sum'),
    passageiros_total=('passageiros_pagos', 'sum'), # Considera apenas passageiros pagos para esta análise, pode ajustar se quiser incluir grátis
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

with col_litros_km:
    st.subheader("Litros por KM ao longo dos Meses")
    st.line_chart(eficiencia_mensal.set_index('ano_mes')['Litros por KM Mensal'])

with col_passageiros_litro:
    st.subheader("Passageiros por Litro ao longo dos Meses")
    st.line_chart(eficiencia_mensal.set_index('ano_mes')['Passageiros por Litro Mensal'])

st.write("Tabela de Variação Mensal da Eficiência:")
st.dataframe(eficiencia_mensal.round(2), use_container_width=True)


# --- Nova Seção: Aeroportos Mais Estratégicos (Carga por KM) ---
st.markdown("---")
st.title("Aeroportos Mais Estratégicos (Carga por KM)")

# Agrupa por aeroporto de origem e destino para calcular a carga total e distância
carga_por_aeroporto = df.groupby(['origem_sigla', 'origem_nome']).agg(
    carga_total_kg=('carga_paga_kg', 'sum'),
    distancia_total_km=('distancia_voada_km', 'sum')
).reset_index()

# Calcula a métrica de Carga por KM
carga_por_aeroporto['Carga por KM'] = (carga_por_aeroporto['carga_total_kg'] / carga_por_aeroporto['distancia_total_km']).round(2)

# Substitui NaNs ou infs por 0 ou um valor adequado para visualização
carga_por_aeroporto = carga_por_aeroporto.fillna(0)
carga_por_aeroporto = carga_por_aeroporto.replace([float('inf'), -float('inf')], 0)

# Remove linhas onde a distância total é zero para evitar divisão por zero, se houver
carga_por_aeroporto = carga_por_aeroporto[carga_por_aeroporto['distancia_total_km'] > 0]

st.subheader("Ranking de Aeroportos por Carga por KM (Origem)")

# Ordena pelo "Carga por KM" em ordem decrescente (maior é melhor)
ranking_carga_aeroporto = carga_por_aeroporto.sort_values(by="Carga por KM", ascending=False)

# Renomeia colunas para melhor visualização e consistência antes de usar no gráfico
ranking_carga_aeroporto_display = ranking_carga_aeroporto.rename(columns={
    'origem_sigla': 'Sigla do Aeroporto',
    'origem_nome': 'Nome do Aeroporto',
    'carga_total_kg': 'Carga Total (KG)',
    'distancia_total_km': 'Distância Total Voada (KM)'
})

# Exibe o ranking em um DataFrame
st.dataframe(
    ranking_carga_aeroporto_display,
    height=500,
    use_container_width=True
)

# Gráfico de barras para os Top 10 Aeroportos por Carga por KM
st.write("#### Top 10 Aeroportos - Carga por KM")
# Agora, pega o head(10) do DataFrame *já renomeado* para o gráfico
top_10_carga_aeroporto = ranking_carga_aeroporto_display.head(10)
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.barplot(x="Carga por KM", y="Nome do Aeroporto", data=top_10_carga_aeroporto, palette="cividis", ax=ax3)
ax3.set_xlabel("Carga por KM (KG/KM)")
ax3.set_ylabel("Aeroporto")
st.pyplot(fig3)
