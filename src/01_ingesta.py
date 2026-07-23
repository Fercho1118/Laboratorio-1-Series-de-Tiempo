"""Etapa 1: trae la hoja Datos del Excel a texto uniforme y unifica los marcadores de nulo.

Entrada: data/raw/Base_Migracion_2009-2026jun.xlsx (hoja Datos)
Salida:  data/processed/01_ingesta.csv
"""

import pandas as pd

import config
import utils


def ingestar():
    utils.exigir(
        config.CRUDO.exists(),
        f"no se encuentra el crudo en {config.CRUDO}",
    )

    df = pd.read_excel(
        config.CRUDO,
        sheet_name=config.HOJA_DATOS,
        dtype=str,
        na_values=config.MARCADORES_NULOS,
        keep_default_na=True,
    )
    utils.paso(f"leido {config.CRUDO.name}: {df.shape[0]:,} filas x {df.shape[1]} columnas")

    utils.validar_columnas(df, config.COLUMNAS_CRUDO, "etapa 1")
    df = df.rename(columns=config.RENOMBRE_COLUMNAS)[config.COLUMNAS_01]

    # El crudo llega como texto: los espacios sobrantes se quitan aqui para que
    # ninguna etapa posterior compare categorias contra un valor con espacios.
    for columna in df.columns:
        df[columna] = df[columna].str.strip()
    df = df.replace({c: {"": None} for c in df.columns})

    nulos = df.isna().sum()
    con_nulos = nulos[nulos > 0]
    if len(con_nulos):
        utils.paso(f"nulos tras unificar marcadores: {con_nulos.to_dict()}")
    else:
        utils.paso("nulos tras unificar marcadores: ninguno")

    utils.exigir(len(df) > 0, "etapa 1: el crudo llego vacio")
    utils.guardar_csv(df, config.SALIDA_01)


if __name__ == "__main__":
    utils.correr("Etapa 1: ingesta", ingestar)
