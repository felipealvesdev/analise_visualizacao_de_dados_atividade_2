import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def load_data(path: str = "data/dados_desenrola.csv") -> pd.DataFrame:
    """Carrega e pré-processa o dataset Desenrola Brasil."""
    df = pd.read_csv(path, sep=';', decimal=',', encoding='utf-8')

    # Converter DATA_BASE (AAAAMM) para datetime
    df['DATA_BASE'] = pd.to_datetime(df['DATA_BASE'].astype(str), format='%Y%m')

    # Normalizar nomes de colunas
    df = df.rename(columns={
        'DATA_BASE': 'data',
        'TIPO_DESENROLA': 'tipo',
        'UNIDADE_FEDERACAO': 'uf',
        'COD_CONGLOMERADO_FINANCEIRO': 'cod_banco',
        'NOME_CONGLOMERADO_FINANCEIRO': 'banco',
        'NUMERO_OPERACOES': 'operacoes',
        'VOLUME_OPERACOES': 'volume'
    })

    # Flag: banco "PRUDENCIAL" (nova fase do programa a partir de 2025)
    df['is_prudencial'] = df['banco'].str.contains('PRUDENCIAL', case=False, na=False)

    # Nome limpo do banco (sem sufixo "- PRUDENCIAL")
    df['banco_limpo'] = (
        df['banco']
        .str.replace(r'\s*-\s*PRUDENCIAL$', '', regex=True)
        .str.strip()
    )

    # Remover linhas sem volume ou com volume zero
    df = df[df['volume'] > 0].copy()

    return df