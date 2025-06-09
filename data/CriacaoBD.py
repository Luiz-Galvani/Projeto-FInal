import sqlite3
import pandas as pd

def criarTable():
    df = pd.read_csv("data\\resumo_anual_2025.csv", sep = ';', encoding = 'latin-1')

    conn = sqlite3.connect("data/voos.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voos (
        empresa_sigla TEXT,
        empresa_nome TEXT,
        empresa_nacionalidade TEXT,
        ano INTEGER,
        mes INTEGER,
        origem_sigla TEXT,
        origem_nome TEXT,
        origem_uf TEXT,
        origem_regiao TEXT,
        origem_pais TEXT,
        origem_continente TEXT,
        destino_sigla TEXT,
        destino_nome TEXT,
        destino_uf TEXT,
        destino_regiao TEXT,
        destino_pais TEXT,
        destino_continente TEXT,
        natureza TEXT,
        grupo_voo TEXT,
        passageiros_pagos INTEGER,
        passageiros_gratis INTEGER,
        carga_paga_kg INTEGER,
        carga_gratis_kg INTEGER,
        correio_kg INTEGER,
        ask INTEGER,
        rpk INTEGER,
        atk INTEGER,
        rtk INTEGER,
        combustivel_litros INTEGER,
        distancia_voada_km INTEGER,
        decolagens INTEGER,
        carga_paga_km INTEGER,
        carga_gratis_km INTEGER,
        correio_km INTEGER,
        assentos INTEGER,
        payload INTEGER,
        horas_voadas REAL,
        bagagem_kg INTEGER
    )
    ''')



    df.rename(columns={
        'EMPRESA (SIGLA)': 'empresa_sigla',
        'EMPRESA (NOME)': 'empresa_nome',
        'EMPRESA (NACIONALIDADE)': 'empresa_nacionalidade',
        'ANO': 'ano',
        'MÊS': 'mes',
        'AEROPORTO DE ORIGEM (SIGLA)': 'origem_sigla',
        'AEROPORTO DE ORIGEM (NOME)': 'origem_nome',
        'AEROPORTO DE ORIGEM (UF)': 'origem_uf',
        'AEROPORTO DE ORIGEM (REGIÃO)': 'origem_regiao',
        'AEROPORTO DE ORIGEM (PAÍS)': 'origem_pais',
        'AEROPORTO DE ORIGEM (CONTINENTE)': 'origem_continente',
        'AEROPORTO DE DESTINO (SIGLA)': 'destino_sigla',
        'AEROPORTO DE DESTINO (NOME)': 'destino_nome',
        'AEROPORTO DE DESTINO (UF)': 'destino_uf',
        'AEROPORTO DE DESTINO (REGIÃO)': 'destino_regiao',
        'AEROPORTO DE DESTINO (PAÍS)': 'destino_pais',
        'AEROPORTO DE DESTINO (CONTINENTE)': 'destino_continente',
        'NATUREZA': 'natureza',
        'GRUPO DE VOO': 'grupo_voo',
        'PASSAGEIROS PAGOS': 'passageiros_pagos',
        'PASSAGEIROS GRÁTIS': 'passageiros_gratis',
        'CARGA PAGA (KG)': 'carga_paga_kg',
        'CARGA GRÁTIS (KG)': 'carga_gratis_kg',
        'CORREIO (KG)': 'correio_kg',
        'ASK': 'ask',
        'RPK': 'rpk',
        'ATK': 'atk',
        'RTK': 'rtk',
        'COMBUSTÍVEL (LITROS)': 'combustivel_litros',
        'DISTÂNCIA VOADA (KM)': 'distancia_voada_km',
        'DECOLAGENS': 'decolagens',
        'CARGA PAGA KM': 'carga_paga_km',
        'CARGA GRATIS KM': 'carga_gratis_km',
        'CORREIO KM': 'correio_km',
        'ASSENTOS': 'assentos',
        'PAYLOAD': 'payload',
        'HORAS VOADAS': 'horas_voadas',
        'BAGAGEM (KG)': 'bagagem_kg'
    }, inplace=True)


    df.to_sql("voos", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

    print("Dados inseridos com sucesso!")
