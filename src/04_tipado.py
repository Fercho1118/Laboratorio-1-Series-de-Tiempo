"""Etapa 4: convierte cada columna a su tipo y dominio validos, y arma la fecha mensual.

Entrada: data/processed/03_categorias.csv
Salida:  data/processed/base_limpia.csv
"""

import pandas as pd

import config
import utils


def validar_cobertura_mensual(df):
    meses = pd.Series(sorted(df["fecha"].unique()))
    esperados = pd.date_range(meses.min(), meses.max(), freq="MS")
    faltantes = sorted(set(esperados) - set(meses))
    utils.exigir(not faltantes, f"etapa 4: faltan meses en la serie: {faltantes[:5]}")
    utils.exigir(
        len(meses) == config.MESES_ESPERADOS,
        f"etapa 4: se esperaban {config.MESES_ESPERADOS} meses y hay {len(meses)}",
    )
    utils.paso(f"cobertura: {len(meses)} meses consecutivos de {meses.min():%Y-%m} a {meses.max():%Y-%m}")


def tipar():
    df = utils.cargar_csv(config.SALIDA_03, "etapa 4", dtype=str)
    utils.validar_columnas(df, config.COLUMNAS_03, "etapa 4")

    # Supuesto que deja la etapa 3: las categorias ya estan unificadas.
    utils.exigir(
        df["pais"].nunique() == df["pais"].str.lower().nunique(),
        "etapa 4: todavia hay paises que solo difieren en mayusculas",
    )

    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")
    df["mes_cod"] = pd.to_numeric(df["mes_cod"], errors="coerce").astype("Int64")
    df["viajeros"] = pd.to_numeric(df["viajeros"], errors="coerce")
    utils.validar_sin_nulos(df, ["anio", "mes_cod", "viajeros"], "etapa 4 (conversion numerica)")

    utils.exigir(
        df["anio"].between(config.ANIO_MIN, config.ANIO_MAX).all(),
        f"etapa 4: hay anios fuera de {config.ANIO_MIN}-{config.ANIO_MAX}",
    )
    utils.exigir(df["mes_cod"].between(1, 12).all(), "etapa 4: hay meses fuera de 1-12")
    utils.exigir(
        (df["mes"].map(config.MES_A_NUMERO) == df["mes_cod"]).all(),
        "etapa 4: el nombre del mes no concuerda con mes_cod",
    )
    utils.exigir((df["viajeros"] >= 0).all(), "etapa 4: hay conteos de viajeros negativos")

    sobran_via = set(df["via"].unique()) - config.DOMINIO_VIA
    sobran_tipo = set(df["tipo_viajero"].unique()) - config.DOMINIO_TIPO_VIAJERO
    utils.exigir(not sobran_via, f"etapa 4: vias fuera de dominio {sobran_via}")
    utils.exigir(not sobran_tipo, f"etapa 4: tipos de viajero fuera de dominio {sobran_tipo}")

    df["fecha"] = pd.to_datetime(dict(year=df["anio"], month=df["mes_cod"], day=1))
    validar_cobertura_mensual(df)

    # Turista + Excursionista es la unica agregacion comparable en todo el rango,
    # porque 'Viajero' cambia de definicion en 2023 y 'Cruceristas' desaparece.
    df["es_visitante"] = df["tipo_viajero"].isin(config.TIPOS_VISITANTE)

    df["anio"] = df["anio"].astype(int)
    df["mes_cod"] = df["mes_cod"].astype(int)
    df = df[config.COLUMNAS_04].sort_values(["fecha", "via", "frontera", "pais", "tipo_viajero"])

    ceros = int((df["viajeros"] == 0).sum())
    utils.paso(f"filas con cero viajeros (se conservan): {ceros:,}")
    utils.paso(f"total de viajeros en la base: {df['viajeros'].sum():,.0f}")

    utils.validar_columnas(df, config.COLUMNAS_04, "etapa 4")
    utils.validar_sin_nulos(df, [c for c in config.COLUMNAS_04 if c != "codigo_frontera"], "etapa 4")
    utils.guardar_csv(df, config.SALIDA_04)


if __name__ == "__main__":
    utils.correr("Etapa 4: tipado y validacion de dominios", tipar)
