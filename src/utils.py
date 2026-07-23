"""Funciones compartidas de carga, guardado y validacion entre etapas."""

import sys

import pandas as pd

import config


class ErrorDeEtapa(Exception):
    """Falla de validacion que corta el pipeline en la etapa donde ocurre."""


def titulo(texto):
    print(f"\n{'=' * 70}\n{texto}\n{'=' * 70}")


def paso(texto):
    print(f"  - {texto}")


def exigir(condicion, mensaje):
    """Fail-fast: si el supuesto no se cumple, la etapa termina aqui."""
    if not condicion:
        raise ErrorDeEtapa(mensaje)


def validar_columnas(df, esperadas, origen):
    faltan = [c for c in esperadas if c not in df.columns]
    sobran = [c for c in df.columns if c not in esperadas]
    exigir(not faltan, f"{origen}: faltan columnas {faltan}")
    exigir(not sobran, f"{origen}: columnas inesperadas {sobran}")


def validar_sin_nulos(df, columnas, origen):
    nulos = df[columnas].isna().sum()
    con_nulos = nulos[nulos > 0].to_dict()
    exigir(not con_nulos, f"{origen}: hay nulos en {con_nulos}")


def cargar_csv(ruta, origen, **kwargs):
    exigir(
        ruta.exists(),
        f"{origen}: no existe {ruta.name}. Corre la etapa anterior primero.",
    )
    df = pd.read_csv(ruta, **kwargs)
    paso(f"leido {ruta.name}: {df.shape[0]:,} filas x {df.shape[1]} columnas")
    return df


def guardar_csv(df, ruta):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    paso(f"escrito {ruta.name}: {df.shape[0]:,} filas x {df.shape[1]} columnas")


def correr(etapa, funcion):
    """Envuelve una etapa para que falle con un mensaje claro y codigo distinto de cero."""
    titulo(etapa)
    try:
        funcion()
    except ErrorDeEtapa as error:
        print(f"\nFALLO en {etapa}: {error}", file=sys.stderr)
        sys.exit(1)
    print(f"  OK {etapa}")
