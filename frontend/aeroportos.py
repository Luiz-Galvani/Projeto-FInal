import sqlite3
import pandas as pd
import streamlit as st

st.markdown("<h1 style='text-align: center;'>🛫 Aeroportos 🛬</h1>", unsafe_allow_html=True)

st.divider()

conn = sqlite3.connect("data/voos.db")
cursor = conn.cursor()



#calculo total de aeroportos de origem
numAeroportosOrigem = """
                SELECT COUNT(DISTINCT origem_sigla)
                FROM voos """

cursor.execute(numAeroportosOrigem)
resultadoOrigem = cursor.fetchone()

#calculo total de aeroportos de destino
numAeroportosDestino = """
                SELECT COUNT(DISTINCT destino_sigla)
                FROM voos """
cursor.execute(numAeroportosDestino)
resultadoDestino = cursor.fetchone()

#Calculo total de aeroportos distintos
totalAeroportos="""
                SELECT COUNT(DISTINCT sigla)
                FROM (
                    SELECT origem_sigla AS sigla FROM voos
                    UNION
                    SELECT destino_sigla AS sigla FROM voos
                ) AS aeroportos
                """
cursor.execute(totalAeroportos)
total = cursor.fetchone()


#Criação dos big numbers
col1, col2, col3= st.columns(3)

with col1:
    st.markdown(f"<h3 style='text-align: center;'>Aeroportos de Origem Distintos:<br> {resultadoOrigem[0]}</h3>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<h3 style='text-align: center;'>Aeroportos de Destino Distintos:<br> {resultadoDestino[0]}</h3>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<h3 style='text-align: center;'>Total de Aeroportos Distintos:<br> {total[0]}</h3>", unsafe_allow_html=True)


st.subheader("", divider = True)

st.subheader("Filtro por Aeroportos: ")
pais_query = """
                SELECT DISTINCT origem_pais FROM voos
                UNION
                SELECT DISTINCT destino_pais FROM voos
"""
cursor.execute(pais_query)
paises = cursor.fetchall()

# Criando a lista de países
paises_lista = [pais[0] for pais in paises]

# Filtro para escolher o País
pais_escolhido = st.selectbox("**Escolha um país:**", paises_lista)

aeroportos_query = """
                SELECT DISTINCT origem_sigla, origem_nome 
                FROM voos
                WHERE origem_pais = ?
                UNION
                SELECT DISTINCT destino_sigla, destino_nome 
                FROM voos
                WHERE destino_pais = ?
"""
cursor.execute(aeroportos_query, (pais_escolhido, pais_escolhido))
aeroportos = cursor.fetchall()

aeroportos_lista = [f"{aeroporto[0]} - {aeroporto[1]}" for aeroporto in aeroportos]


aeroporto_escolhido = st.selectbox("**Escolha um aeroporto:**", aeroportos_lista)

sigla_escolhida = aeroporto_escolhido.split(" - ")[0]

informacoes_aeroporto = """
    SELECT *
    FROM voos
    WHERE origem_sigla = ? OR destino_sigla = ?
"""

cursor.execute(informacoes_aeroporto, (sigla_escolhida, sigla_escolhida))
dados_aeroporto = cursor.fetchall()

if dados_aeroporto:
    colunas = [description[0] for description in cursor.description]
    df_aeroporto = pd.DataFrame(dados_aeroporto, columns=colunas)
    colunas_relevantes = [
            'origem_sigla', 'origem_nome',  'origem_pais', 'destino_sigla', 'destino_nome', 
            'destino_pais', 'passageiros_pagos', 'passageiros_gratis', 'carga_paga_kg', 
            'carga_gratis_kg', 'combustivel_litros', 'distancia_voada_km', 'decolagens', 'horas_voadas'
        ]

    df_aeroporto = df_aeroporto[[col for col in colunas_relevantes if col in df_aeroporto.columns]]

    st.dataframe(df_aeroporto)
else:
    st.write("Nenhuma informação encontrada para o aeroporto selecionado.")

conn.close() 
