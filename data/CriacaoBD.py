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

    df.dropna(inplace=True)

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
