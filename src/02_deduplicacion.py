"""Etapa 2: elimina filas duplicadas y verifica la llave de negocio del formato largo.

Entrada: data/processed/01_ingesta.csv
Salida:  data/processed/02_deduplicado.csv
"""

import config
import utils


def deduplicar():
    df = utils.cargar_csv(config.SALIDA_01, "etapa 2", dtype=str)
    utils.validar_columnas(df, config.COLUMNAS_01, "etapa 2")

    # Supuesto que deja la etapa 1: no quedan cadenas vacias ni espacios sobrantes,
    # porque una categoria con espacios se veria como un duplicado distinto.
    for columna in config.COLUMNAS_TEXTO:
        valores = df[columna].dropna()
        utils.exigir(
            (valores == valores.str.strip()).all() and not (valores == "").any(),
            f"etapa 2: la columna {columna} todavia trae espacios o cadenas vacias",
        )

    antes = len(df)
    df = df.drop_duplicates()
    utils.paso(f"duplicados exactos eliminados: {antes - len(df):,}")

    # Repetir la llave de negocio no implica duplicado: estas filas difieren en
    # otra columna y cada una aporta viajeros distintos, asi que se conservan.
    repetidas = int(df.duplicated(subset=config.LLAVE_NEGOCIO).sum())
    utils.paso(f"filas que repiten la llave de negocio (se conservan): {repetidas:,}")
    if repetidas:
        ejemplo = df[df.duplicated(subset=config.LLAVE_NEGOCIO, keep=False)].head(2)
        utils.paso(f"ejemplo de esas filas:\n{ejemplo.to_string(index=False)}")

    utils.exigir(not df.duplicated().any(), "etapa 2: todavia quedan filas duplicadas exactas")
    utils.validar_columnas(df, config.COLUMNAS_02, "etapa 2")
    utils.guardar_csv(df[config.COLUMNAS_02], config.SALIDA_02)


if __name__ == "__main__":
    utils.correr("Etapa 2: deduplicacion", deduplicar)
