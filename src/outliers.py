import pandas as pd
import numpy as np


def detectar_outliers_iqr(
    df: pd.DataFrame,
    coluna: str,
    agrupar_por: list[str] | None = None,
    multiplicador: float = 1.5
) -> pd.Series:
    """
    Retorna uma máscara booleana: True = outlier, False = valor normal.
    Se `agrupar_por` for fornecido, calcula IQR dentro de cada grupo.
    Robusto a DataFrame vazio ou com apenas 1 grupo.
    """
    # Caso 1: DataFrame vazio → retorna máscara vazia
    if df.empty:
        return pd.Series([], dtype=bool, index=df.index)

    # Caso 2: sem agrupamento → aplica IQR global
    if not agrupar_por:
        q1, q3 = df[coluna].quantile([0.25, 0.75])
        iqr = q3 - q1
        li, ls = q1 - multiplicador * iqr, q3 + multiplicador * iqr
        return (df[coluna] < li) | (df[coluna] > ls)

    # Caso 3: agrupado — calcula limites por grupo e mapeia de volta
    limites = (
        df.groupby(agrupar_por)[coluna]
        .quantile([0.25, 0.75])
        .unstack()
        .rename(columns={0.25: 'q1', 0.75: 'q3'})
    )
    limites['iqr'] = limites['q3'] - limites['q1']
    limites['li'] = limites['q1'] - multiplicador * limites['iqr']
    limites['ls'] = limites['q3'] + multiplicador * limites['iqr']

    # Merge dos limites de volta ao df original
    df_lim = df.merge(
        limites[['li', 'ls']],
        left_on=agrupar_por,
        right_index=True,
        how='left'
    )

    # Se o grupo tiver 1 único registro, IQR = 0 → tudo seria outlier.
    # Nesse caso, marcamos como NÃO outlier (valor único não é anômalo).
    mascara = (
        (df_lim[coluna] < df_lim['li']) |
        (df_lim[coluna] > df_lim['ls'])
    )
    # Onde li == ls (grupo com 1 registro), força False
    mascara = mascara & (df_lim['li'] != df_lim['ls'])

    return mascara


def resumo_outliers(df: pd.DataFrame, coluna: str, mascara: pd.Series) -> dict:
    """Retorna estatísticas comparativas antes/depois da remoção."""
    total = len(df)
    if total == 0:
        return {
            "total_registros": 0,
            "n_outliers": 0,
            "pct_outliers": 0,
            "media_com_outliers": 0,
            "media_sem_outliers": 0,
            "mediana": 0,
            "mediana_sem_outliers": 0,
            "max_com_outliers": 0,
            "max_sem_outliers": 0,
            "min_com_outliers": 0,
            "min_sem_outliers": 0,
        }

    # Garantir que a máscara é booleana e alinhada ao índice
    mascara = mascara.reindex(df.index, fill_value=False).astype(bool)
    n_out = int(mascara.sum())
    df_sem = df.loc[~mascara]

    return {
        "total_registros": total,
        "n_outliers": n_out,
        "pct_outliers": round(100 * n_out / total, 2) if total else 0,
        "media_com_outliers": df[coluna].mean(),
        "media_sem_outliers": df_sem[coluna].mean() if len(df_sem) > 0 else 0,
        "mediana": df[coluna].median(),
        "mediana_sem_outliers": df_sem[coluna].median() if len(df_sem) > 0 else 0,
        "max_com_outliers": df[coluna].max(),
        "max_sem_outliers": df_sem[coluna].max() if len(df_sem) > 0 else 0,
        "min_com_outliers": df[coluna].min(),
        "min_sem_outliers": df_sem[coluna].min() if len(df_sem) > 0 else 0,
    }