import sqlite3
import pandas as pd

def criarTable():

    df = pd.read_csv("data\\resumo_anual_2025.csv", sep=';', encoding='latin-1')

    columns_to_drop = [
        'AEROPORTO DE ORIGEM (UF)',
        'AEROPORTO DE ORIGEM (REGIÃO)',
        'AEROPORTO DE DESTINO (UF)',
        'AEROPORTO DE DESTINO (REGIÃO)'
    ]

    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    if existing_columns_to_drop:
        df.drop(columns=existing_columns_to_drop, inplace=True)
        print(f"Colunas {existing_columns_to_drop} removidas do DataFrame.")
    else:
        print("Nenhuma das colunas de UF/Região especificadas foi encontrada no DataFrame.")

    df.rename(columns={
        'EMPRESA (SIGLA)': 'empresa_sigla',
        'EMPRESA (NOME)': 'empresa_nome',
        'EMPRESA (NACIONALIDADE)': 'empresa_nacionalidade',
        'ANO': 'ano',
        'MÊS': 'mes',
        'AEROPORTO DE ORIGEM (SIGLA)': 'origem_sigla',
        'AEROPORTO DE ORIGEM (NOME)': 'origem_nome',
        'AEROPORTO DE ORIGEM (PAÍS)': 'origem_pais',
        'AEROPORTO DE ORIGEM (CONTINENTE)': 'origem_continente',
        'AEROPORTO DE DESTINO (SIGLA)': 'destino_sigla',
        'AEROPORTO DE DESTINO (NOME)': 'destino_nome',
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
    print("Colunas renomeadas para o formato do banco de dados.")

    df.dropna(inplace=True)
    print(f"Linhas com valores nulos removidas. Restam {len(df)} linhas.")

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
        origem_pais TEXT,
        origem_continente TEXT,
        destino_sigla TEXT,
        destino_nome TEXT,
        destino_pais TEXT,
        destino_continente TEXT,
        natureza TEXT,
        grupo_voo TEXT,
        passageiros_pagos INTEGER,
        passageiros_gratis INTEGER,
        carga_paga_kg REAL, -- Alterado para REAL caso haja valores decimais
        carga_gratis_kg REAL, -- Alterado para REAL
        correio_kg REAL, -- Alterado para REAL
        ask REAL, -- ASK, RPK, ATK, RTK geralmente são reais
        rpk REAL,
        atk REAL,
        rtk REAL,
        combustivel_litros REAL, -- Alterado para REAL
        distancia_voada_km REAL, -- Alterado para REAL
        decolagens INTEGER,
        carga_paga_km REAL, -- Alterado para REAL
        carga_gratis_km REAL, -- Alterado para REAL
        correio_km REAL, -- Alterado para REAL
        assentos INTEGER,
        payload REAL, -- PAYLOAD geralmente é REAL
        horas_voadas REAL,
        bagagem_kg REAL -- BAGAGEM (KG) pode ser real
    )
    ''')
    conn.commit()


    df.to_sql("voos", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

    print("Dados do CSV carregados e inseridos no banco de dados 'voos.db' com sucesso!")