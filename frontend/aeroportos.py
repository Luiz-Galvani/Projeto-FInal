import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

st.markdown("<h1 style='text-align: center;'>🛫 ANÁLISE DE DEMANDA E COBERTURA 🛬</h1>", unsafe_allow_html=True)

st.subheader("", divider = True)

DATABASE_PATH = "data/voos.db" 

#Conexão ao Banco de Dados
conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row 
cursor = conn.cursor()

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

totalAeroportos_query = """
    SELECT COUNT(DISTINCT sigla) AS Total_Aeroportos
    FROM (
        SELECT origem_sigla AS sigla FROM voos
        UNION
        SELECT destino_sigla AS sigla FROM voos
    ) AS aeroportos
"""
cursor.execute(totalAeroportos_query)
total = cursor.fetchone()
overview_kpis_query = """
SELECT
    SUM(passageiros_pagos + passageiros_gratis) AS Total_Passageiros,
    SUM(decolagens) AS Total_Decolagens,
    SUM(distancia_voada_km) AS Total_Distancia_Voada_Km
FROM
    voos;
"""
overview_kpis_row = cursor.execute(overview_kpis_query).fetchone()
if overview_kpis_row:
    col1, col2, col3 = st.columns(3) 
    
    with col1.container(border = True):
        st.markdown(kpi_box("Total de Aeroportos",f"{total['Total_Aeroportos']:,.0f}"), unsafe_allow_html=True)
    with col2.container(border = True):
        st.markdown(kpi_box("Total de Decolagens",f"{overview_kpis_row['Total_Decolagens']:,.0f}"), unsafe_allow_html=True)
    with col3.container(border = True):
        st.markdown(kpi_box("Total de Passageiros",f"{overview_kpis_row['Total_Passageiros']:,.0f}"), unsafe_allow_html=True)
        
else:
    st.warning("Não foi possível carregar os KPIs da visão geral.")


st.subheader("", divider = True)

st.markdown(f"<h2 style='text-align: center;'>Destinos Mais Procurados</h2>", unsafe_allow_html=True)
col4,col5 = st.columns(2)
with col4.container(border = True):
    total_passageiros_destino_query = """
    SELECT destino_continente AS Continente,
        SUM(passageiros_pagos) AS Total_Passageiros
    FROM voos
    WHERE destino_continente IS NOT NULL
    GROUP BY destino_continente
    ORDER BY Total_Passageiros DESC
    LIMIT 10;
    """
    df_destino = pd.read_sql_query(total_passageiros_destino_query, conn)
    df_destino["Tipo"] = "Destino"

    total_passageiros_origem_query = """
    SELECT origem_continente AS Continente,
        SUM(passageiros_pagos) AS Total_Passageiros
    FROM voos
    WHERE origem_continente IS NOT NULL
    GROUP BY origem_continente
    ORDER BY Total_Passageiros DESC
    LIMIT 10;
    """
    df_origem = pd.read_sql_query(total_passageiros_origem_query, conn)
    df_origem["Tipo"] = "Origem"

    df_continentes = pd.concat([df_destino, df_origem])
    df_continentes = df_continentes.sort_values(by="Total_Passageiros", ascending=False)

    if not df_continentes.empty:
        fig_continentes = px.bar(
            df_continentes,
            x="Total_Passageiros",
            y="Continente",
            color="Tipo",
            color_discrete_sequence = px.colors.sequential.GnBu_r,
            barmode="group",
            orientation="h",
            text="Total_Passageiros",
            labels={"Total_Passageiros": "Total de Passageiros"}
        )
        fig_continentes.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_continentes.update_layout(
            showlegend=True,
            yaxis=dict(autorange="reversed")
        )
        st.markdown(f"<h3 style='text-align: center;'>Top Continentes (Origem e Destino) </h3>", unsafe_allow_html=True)
        st.plotly_chart(fig_continentes, use_container_width=True)

    with col5.container(border = True):        
        df_destino = pd.read_sql_query("""
            SELECT
                destino_pais AS Pais,
                SUM(passageiros_pagos) AS Total_Passageiros,
                'Destino' AS Tipo
            FROM voos
            WHERE destino_pais IS NOT NULL
            GROUP BY destino_pais
            ORDER BY Total_Passageiros DESC
            LIMIT 10;
        """, conn)

        df_origem = pd.read_sql_query("""
            SELECT
                origem_pais AS Pais,
                SUM(passageiros_pagos) AS Total_Passageiros,
                'Origem' AS Tipo
            FROM voos
            WHERE origem_pais IS NOT NULL
            GROUP BY origem_pais
            ORDER BY Total_Passageiros DESC
            LIMIT 10;
        """, conn)

        df_combinado = pd.concat([df_destino, df_origem])
        df_combinado = df_combinado.sort_values(by='Total_Passageiros', ascending=False)

        fig_combinado = px.bar(
            df_combinado,
            x='Total_Passageiros',
            y='Pais',
            color='Tipo',
            color_discrete_sequence = px.colors.sequential.GnBu_r,
            barmode='group',
            orientation='h',
            labels={'Pais': 'País', 'Total_Passageiros': 'Total de Passageiros'}
        )

        fig_combinado.update_traces(texttemplate='%{x:,}', textposition='outside')

        fig_combinado.update_layout(
            yaxis=dict(autorange="reversed")
        )
        st.markdown(f"<h3 style='text-align: center;'>Top 10 Países de Origem e Destino (Agrupado) </h3>", unsafe_allow_html=True)
        st.plotly_chart(fig_combinado, use_container_width=True)

cursor.execute("SELECT DISTINCT natureza FROM voos ORDER BY natureza")
naturezas = [row[0] for row in cursor.fetchall() if row[0] is not None]

naturezas.insert(0, "Todas")

natureza_escolhida = st.selectbox("**Filtrar por Natureza do Voo:**", naturezas)

destinos_query = """
SELECT
    destino_sigla,
    destino_nome,
    SUM(passageiros_pagos) AS Total_Passageiros_Destino
FROM
    voos
WHERE
    destino_sigla IS NOT NULL AND destino_nome IS NOT NULL
"""

if natureza_escolhida != "Todas":
    destinos_query += f" AND natureza = '{natureza_escolhida}'"

destinos_query += """
GROUP BY
    destino_sigla, destino_nome
ORDER BY
    Total_Passageiros_Destino DESC
LIMIT 11;
"""

df_destinos_mais_procurados = pd.read_sql_query(destinos_query, conn)

if not df_destinos_mais_procurados.empty:
    with st.container(border = True):
        st.markdown(f"<h3 style='text-align: center;'>Top 10 Destinos por Passageiros ({natureza_escolhida})</h3>", unsafe_allow_html=True)
        fig_destinos = px.bar(
            df_destinos_mais_procurados,
            x='destino_nome',
            y='Total_Passageiros_Destino',
            labels={'destino_nome': 'Aeroporto de Destino', 'Total_Passageiros_Destino': 'Total de Passageiros'},
            color='destino_nome',
            color_discrete_sequence=px.colors.sequential.ice,
            text='Total_Passageiros_Destino'

        )
        fig_destinos.update_traces(texttemplate='%{text:.4s}', textposition='outside')
        fig_destinos.update_layout(showlegend=False)
        st.plotly_chart(fig_destinos, use_container_width=True)

st.subheader("", divider = True)
st.markdown("<h2 style='text-align: center;'>Regiões que Mais Movimentam Passageiros</h2>", unsafe_allow_html=True)

tab_Estado, tab_Continente = st.tabs(["País","Continente"])

with tab_Continente:
    cursor.execute("SELECT DISTINCT destino_continente FROM voos WHERE destino_continente IS NOT NULL ORDER BY destino_continente")
    continentes_disponiveis = [row[0] for row in cursor.fetchall() if row[0] is not None]
    continentes_disponiveis.insert(0, "Selecione um Continente")

    continente_selecionado = st.selectbox("**Filtre por continente:** ", continentes_disponiveis)

    if continente_selecionado != "Selecione um Continente":
        
        continent_kpis_query = """
        SELECT
            SUM(passageiros_pagos + passageiros_gratis) AS Total_Passageiros_Continente,
            SUM(decolagens) AS Total_Decolagens_Continente,
            SUM(passageiros_pagos * distancia_voada_km) AS Total_RPK_Continente,
            SUM(assentos * distancia_voada_km) AS Total_ASK_Continente
        FROM voos
        WHERE destino_continente = ?;
        """
        cursor.execute(continent_kpis_query, (continente_selecionado,))

        continent_kpis_row = cursor.fetchone()

        if continent_kpis_row:
            total_pass_continente = continent_kpis_row['Total_Passageiros_Continente'] or 0
            total_decolagens_continente = continent_kpis_row['Total_Decolagens_Continente'] or 0
            rpk_continente = continent_kpis_row['Total_RPK_Continente'] or 0
            ask_continente = continent_kpis_row['Total_ASK_Continente'] or 0

            media_ocupacao_continente = (rpk_continente / ask_continente * 100) if ask_continente > 0 else 0

            col_cont1, col_cont2, col_cont3 = st.columns(3)
            with col_cont1.container(border = True):
                st.markdown(kpi_box("Passageiros",f"{total_pass_continente:,.0f}" ), unsafe_allow_html=True)
            with col_cont2.container(border = True):
                st.markdown(kpi_box("Decolagens",f"{total_decolagens_continente:,.0f}" ), unsafe_allow_html=True)
            with col_cont3.container(border = True):
                st.markdown(kpi_box("Média Ocupação",f"{media_ocupacao_continente:.2f}%" ), unsafe_allow_html=True)
        else:

            st.info(f"Nenhum dado de voo encontrado para o continente selecionado.")
        st.subheader("", divider = True)

        query_decolagens_continente_mensal = """
        SELECT
            ano,
            mes,
            SUM(decolagens) AS Total_Decolagens
        FROM
            voos
        WHERE
            destino_continente = ? OR origem_continente = ?
        GROUP BY
            ano, mes
        ORDER BY
            ano ASC, mes ASC;
        """
        df_decolagens_continente = pd.read_sql_query(
            query_decolagens_continente_mensal,
            conn,
            params=(continente_selecionado, continente_selecionado)
        )

        if not df_decolagens_continente.empty:
            with st.container(border = True):
                st.markdown(f"<h3 style='text-align: center;'>Total de Decolagens por Mês - {continente_selecionado} </h3>", unsafe_allow_html=True)
                df_decolagens_continente['Data'] = pd.to_datetime(df_decolagens_continente['ano'].astype(str) + '-' + df_decolagens_continente['mes'].astype(str) + '-01')
                fig_decolagens_continente = px.line(
                    df_decolagens_continente,
                    x='Data',
                    y='Total_Decolagens',
                    labels={'Data': 'Mês/ano', 'Total_Decolagens': 'Número de Decolagens'},
                    markers=True,
                    line_shape='linear'
                )
                fig_decolagens_continente.update_xaxes(
                    dtick="M1",
                    tickformat="%b\n%Y",
                    ticklabelmode="period"
                )
                st.plotly_chart(fig_decolagens_continente, use_container_width=True)
            

            



        


    
with tab_Estado:
    cursor.execute("SELECT DISTINCT destino_pais FROM voos WHERE destino_pais IS NOT NULL ORDER BY destino_pais")
    paises_disponiveis = [row[0] for row in cursor.fetchall() if row[0] is not None]
    paises_disponiveis.insert(0, "Selecione um País")

    pais_selecionado = st.selectbox("**Escolha um País para ver o Total:**", paises_disponiveis)

    if pais_selecionado != "Selecione um País":
        country_kpis_query = f"""
        SELECT
            SUM(passageiros_pagos + passageiros_gratis) AS Total_Passageiros_Pais,
            SUM(decolagens) AS Total_Decolagens_Pais,
            SUM(passageiros_pagos * distancia_voada_km) AS Total_RPK_Pais,
            SUM(assentos * distancia_voada_km) AS Total_ASK_Pais
        FROM voos
        WHERE destino_pais = ?;
        """
        cursor.execute(country_kpis_query, (pais_selecionado,))
        fetched_kpis = cursor.fetchone()

        if fetched_kpis:
            total_pass_pais = fetched_kpis['Total_Passageiros_Pais'] or 0
            total_decolagens_pais = fetched_kpis['Total_Decolagens_Pais'] or 0
            rpk_pais = fetched_kpis['Total_RPK_Pais'] or 0
            ask_pais = fetched_kpis['Total_ASK_Pais'] or 0

            media_ocupacao_pais = (rpk_pais / ask_pais * 100) if ask_pais > 0 else 0

            col_pais1, col_pais2, col_pais3 = st.columns(3)
            with col_pais1.container(border = True):
                st.markdown(kpi_box("Passageiros",f"{total_pass_pais:,.0f}" ), unsafe_allow_html=True)
            with col_pais2.container(border = True):
                st.markdown(kpi_box("Decolagens",f"{total_decolagens_pais:,.0f}" ), unsafe_allow_html=True)
            with col_pais3.container(border = True):
                st.markdown(kpi_box("Média Ocupação",f"{media_ocupacao_pais:.2f}%" ), unsafe_allow_html=True)
        else:
            st.info(f"Nenhum dado de voo encontrado para {pais_selecionado}.")
            st.subheader(f"Total de Decolagens por Mês - {continente_selecionado}")

        query_decolagens_continente_mensal_pais = """
        SELECT
            ano,
            mes,
            SUM(decolagens) AS Total_Decolagens_pais
        FROM
            voos
        WHERE
            destino_pais = ? OR origem_pais = ?
        GROUP BY
            ano, mes
        ORDER BY
            ano ASC, mes ASC;
        """
        df_decolagens_pais = pd.read_sql_query(
            query_decolagens_continente_mensal_pais,
            conn,
            params=(pais_selecionado,pais_selecionado)
        )
        st.subheader("",divider = True)
        
        
        if not df_decolagens_pais.empty:
            df_decolagens_pais['Data'] = pd.to_datetime(df_decolagens_pais['ano'].astype(str) + '-' + df_decolagens_pais['mes'].astype(str) + '-01')
            fig_decolagens_pais = px.line(
                df_decolagens_pais,
                x='Data',
                y='Total_Decolagens_pais',
                labels={'Data': 'Mês/ano', 'Total_Decolagens': 'Número de Decolagens'},
                markers=True,
                line_shape='linear'
            )
            fig_decolagens_pais.update_xaxes(
                dtick="M1",
                tickformat="%b\n%Y",
                ticklabelmode="period"
            )
            with st.container(border = True):
                st.markdown(f"<h3 style='text-align: center;'>Total de Decolagens por Mês - {pais_selecionado} </h3>", unsafe_allow_html=True)
                st.plotly_chart(fig_decolagens_pais, use_container_width=True)
        
st.subheader("", divider = True)


st.markdown(f"<h2 style='text-align: center;'>Estatísticas Gerais por Aeroporto</h2>", unsafe_allow_html=True)
pais_query = """
    SELECT DISTINCT destino_pais FROM voos
    ORDER BY 1
"""
cursor.execute(pais_query)
paises = cursor.fetchall()
paises_lista = [pais[0] for pais in paises if pais[0] is not None] if paises else []

if paises_lista:
    pais_escolhido = st.selectbox("**Escolha um país:**", paises_lista)
else:
    st.warning("Nenhum país encontrado no banco de dados.")
    pais_escolhido = None

if pais_escolhido:
    aeroportos_query = """
        SELECT DISTINCT origem_sigla, origem_nome
        FROM voos
        WHERE origem_pais = ?
        UNION
        SELECT DISTINCT destino_sigla, destino_nome
        FROM voos
        WHERE destino_pais = ?
        ORDER BY 1
    """
    cursor.execute(aeroportos_query, (pais_escolhido, pais_escolhido))
    aeroportos = cursor.fetchall()
    aeroportos_lista = [f"{a[0]} - {a[1]}" for a in aeroportos if a[0] is not None and a[1] is not None] if aeroportos else []

    if aeroportos_lista:
        aeroporto_escolhido = st.selectbox("**Escolha um aeroporto:**", aeroportos_lista)
        sigla_escolhida = aeroporto_escolhido.split(" - ")[0]

        informacoes_aeroporto_query = """
            SELECT *
            FROM voos
            WHERE origem_sigla = ? OR destino_sigla = ?
        """
        df_aeroporto = pd.read_sql_query(informacoes_aeroporto_query, conn, params=(sigla_escolhida, sigla_escolhida)) # Usa a conexão existente

        if not df_aeroporto.empty:
            st.write(f"### Voos Envolvendo {aeroporto_escolhido}:")
            
            colunas_relevantes = {
                'empresa_nome': 'Empresa',
                'origem_sigla':'Aeroporto de Origem',
                'origem_nome': 'Cidade de Origem',
                'origem_pais': 'País de Origem',
                'destino_sigla':'Aeroporto de Destino',
                'destino_nome':'Cidade de Destino',
                'destino_pais':'País de Destino',
                'passageiros_pagos':'Passageiros Pagantes',
                'distancia_voada_km':'Distância Voada(Km)',
                'decolagens':'Decolagens',
                'horas_voadas':'Horas Voadas'

            }

            colunas_para_exibir = [col for col in colunas_relevantes.keys() if col in df_aeroporto.columns]
            df_aeroporto_display = df_aeroporto[colunas_para_exibir].rename(columns=colunas_relevantes)
            st.dataframe(df_aeroporto_display, use_container_width=True)
        else:
            st.info("Nenhuma informação encontrada para o aeroporto selecionado.")
    else:
        st.warning(f"Nenhum aeroporto encontrado para o país '{pais_escolhido}'.")
else:
    st.info("Nenhum país selecionado para buscar aeroportos.")

conn.close()