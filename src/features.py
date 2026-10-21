
import pandas as pd
import numpy as np

def generar_features_demanda(df, col_target, lags=[1,2,7,14,21,28],ventanas_moviles=[7,14]):
    df_feat = df.copy()

    for lag in lags:
        df_feat[f'lag_{lag}'] = df_feat[col_target].shift(lag)

    for window in ventanas_moviles:
        df_feat[f'rolling_mean:{window}'] = df_feat[col_target].shift(1).rolling(window=window).mean()
        df_feat[f'rolling_std:{window}'] = df_feat[col_target].shift(1).rolling(window=window).std()

    df_feat['dias_semana'] = df_feat.index.dayofweek
    df_feat['dia_mes'] = df_feat.index.day
    df_feat['mes'] = df_feat.index.month
    df_feat['es_finde_semana'] = (df_feat['dias_semana'] >=5).astype(int)

    return df_feat
