import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.subheader("Análise de Consumo por Empresa")
st.write("## Tabela Completa com Estatísticas de Consumo")

# Preparar dados de consumo
df_consumo = df.groupby(['empresa_nome', 'mes']).agg({
    'combustivel_litros': 'sum',
    'distancia_voada_km': 'sum'
}).reset_index()

# Calcular consumo médio (tratar divisão por zero)
df_consumo['consumo_medio'] = np.where(
    df_consumo['distancia_voada_km'] > 0,
    df_consumo['combustivel_litros'] / df_consumo['distancia_voada_km'],
    0
)

# ANÁLISE COMPLETA POR EMPRESA
stats_por_empresa = df_consumo.groupby('empresa_nome').agg({
    'consumo_medio': ['count', 'mean', 'std', 'min', 'max'],
    'combustivel_litros': 'sum',
    'distancia_voada_km': 'sum'
}).round(4)

# Flatten column names
stats_por_empresa.columns = [
    'total_registros', 'consumo_medio_geral', 'desvio_padrao', 'consumo_min', 'consumo_max',
    'total_combustivel', 'total_distancia'
]

# Adicionar análises adicionais
stats_por_empresa['registros_zerados'] = df_consumo.groupby('empresa_nome')['consumo_medio'].apply(lambda x: (x == 0).sum())
stats_por_empresa['registros_validos'] = stats_por_empresa['total_registros'] - stats_por_empresa['registros_zerados']
stats_por_empresa['percentual_validos'] = (stats_por_empresa['registros_validos'] / stats_por_empresa['total_registros'] * 100).round(2)

# Calcular consumo médio geral real (considerando apenas registros válidos)
stats_por_empresa['consumo_medio_geral_real'] = df_consumo[df_consumo['consumo_medio'] > 0].groupby('empresa_nome')['consumo_medio'].mean().round(4)
stats_por_empresa['consumo_medio_geral_real'] = stats_por_empresa['consumo_medio_geral_real'].fillna(0)

# Reset index para ter empresa_nome como coluna
stats_por_empresa.reset_index(inplace=True)

# Reordenar colunas para melhor visualização
colunas_ordenadas = [
    'empresa_nome', 
    'consumo_medio_geral_real',
    'total_registros', 
    'registros_validos', 
    'registros_zerados',
    'percentual_validos',
    'consumo_min', 
    'consumo_max', 
    'desvio_padrao',
    'total_combustivel', 
    'total_distancia'
]

stats_final = stats_por_empresa[colunas_ordenadas].copy()

# MÉTRICAS GERAIS
st.write("### 📈 Resumo Geral")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Empresas", len(stats_final))

with col2:
    consumo_medio_overall = stats_final[stats_final['consumo_medio_geral_real'] > 0]['consumo_medio_geral_real'].mean()
    st.metric("Consumo Médio Geral", f"{consumo_medio_overall:.4f} L/km")

with col3:
    empresas_com_dados = len(stats_final[stats_final['registros_validos'] > 0])
    st.metric("Empresas com Dados Válidos", f"{empresas_com_dados}")

with col4:
    registros_totais = stats_final['total_registros'].sum()
    st.metric("Total de Registros", f"{registros_totais:,}")

# GRÁFICO DE DISTRIBUIÇÃO
st.write("### 📊 Distribuição do Consumo Médio")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)

# Histograma do consumo médio (apenas valores > 0)
consumos_validos = stats_final[stats_final['consumo_medio_geral_real'] > 0]['consumo_medio_geral_real']
if len(consumos_validos) > 0:
    ax1.hist(consumos_validos, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
    ax1.set_xlabel('Consumo Médio Geral (L/km)', fontsize=12)
    ax1.set_ylabel('Número de Empresas', fontsize=12)
    ax1.set_title('Distribuição do Consumo Médio', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

# Gráfico de barras: Top 10 maiores e menores consumos
top_10_maior = stats_final[stats_final['consumo_medio_geral_real'] > 0].nlargest(10, 'consumo_medio_geral_real')
top_10_menor = stats_final[stats_final['consumo_medio_geral_real'] > 0].nsmallest(10, 'consumo_medio_geral_real')

# Combinar e plotar
top_consumos = pd.concat([top_10_menor, top_10_maior]).drop_duplicates()
colors = ['red' if x in top_10_maior['consumo_medio_geral_real'].values else 'green' 
          for x in top_consumos['consumo_medio_geral_real']]

bars = ax2.barh(range(len(top_consumos)), top_consumos['consumo_medio_geral_real'], color=colors, alpha=0.7)
ax2.set_yticks(range(len(top_consumos)))
ax2.set_yticklabels(top_consumos['empresa_nome'], fontsize=8)
ax2.set_xlabel('Consumo Médio Geral (L/km)', fontsize=12)
ax2.set_title('Top Empresas: Maior e Menor Consumo', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

st.pyplot(fig)

# TABELA PRINCIPAL
st.write("### 📋 Tabela Completa - Todas as Empresas")


# Aplicar formatação e cores condicionais
styled_df = stats_por_empresa.copy().style.format({
    'consumo_medio_geral_real': '{:.4f}',
    'consumo_min': '{:.4f}',
    'consumo_max': '{:.4f}',
    'desvio_padrao': '{:.4f}',
    'percentual_validos': '{:.1f}%',
    'total_combustivel': '{:,.0f}',
    'total_distancia': '{:,.0f}'
}).background_gradient(
    subset=['consumo_medio_geral_real'], 
    cmap='RdYlGn_r',
    vmin=0, 
    vmax=stats_por_empresa['consumo_medio_geral_real'].max()
).background_gradient(
    subset=['percentual_validos'], 
    cmap='RdYlGn',
    vmin=0, 
    vmax=100
)

# Exibir tabela
st.dataframe(styled_df, use_container_width=True, height=600)
