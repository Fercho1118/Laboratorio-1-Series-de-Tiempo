"""Etapa 3: unifica las categorias que el crudo trae escritas de varias formas.

Entrada: data/processed/02_deduplicado.csv
Salida:  data/processed/03_categorias.csv
"""

import pandas as pd

import config
import utils


def unificar_variantes_de_pais(df):
    """Unifica nombres que solo difieren en mayusculas eligiendo la variante mas frecuente.

    El tramo 2020-2021 reescribio varios paises en Title Case ("Federación De Rusia"),
    lo que parte el mismo pais en dos categorias y arruina cualquier ranking.
    """
    conteo = df["pais"].value_counts()
    clave = df["pais"].str.lower()
    canonico = (
        pd.DataFrame({"pais": df["pais"], "clave": clave, "n": df["pais"].map(conteo)})
        .sort_values("n", ascending=False)
        .drop_duplicates("clave")
        .set_index("clave")["pais"]
    )
    unificado = clave.map(canonico)
    cambiadas = int((unificado != df["pais"]).sum())
    variantes = int(df["pais"].nunique() - unificado.nunique())
    utils.paso(f"paises unificados por mayusculas: {variantes} variantes, {cambiadas:,} filas corregidas")
    df["pais"] = unificado
    return df


def separar_codigo_de_frontera(df):
    """'01 La Aurora' -> codigo_frontera='01', frontera='La Aurora'.

    'Cruceros' no trae codigo numerico y se conserva como esta, con codigo nulo.
    """
    extraido = df["frontera"].str.extract(r"^(?P<codigo>\d+)\s+(?P<nombre>.+)$")
    df["codigo_frontera"] = extraido["codigo"]
    df["frontera"] = extraido["nombre"].fillna(df["frontera"])
    sin_codigo = df.loc[df["codigo_frontera"].isna(), "frontera"].unique().tolist()
    utils.paso(f"fronteras sin codigo numerico: {sin_codigo}")
    return df


def unificar_categorias():
    df = utils.cargar_csv(config.SALIDA_02, "etapa 3", dtype=str)
    utils.validar_columnas(df, config.COLUMNAS_02, "etapa 3")

    # Supuesto que deja la etapa 2: ya no hay filas duplicadas exactas.
    utils.exigir(not df.duplicated().any(), "etapa 3: la entrada trae filas duplicadas exactas")

    df = unificar_variantes_de_pais(df)

    for columna, sinonimos in [
        ("agrupacion_residencia", config.SINONIMOS_AGRUPACION),
        ("region_dos", config.SINONIMOS_REGION_DOS),
    ]:
        afectadas = int(df[columna].isin(sinonimos).sum())
        df[columna] = df[columna].replace(sinonimos)
        utils.paso(f"sinonimos unificados en {columna}: {afectadas:,} filas")

    # Codigos que la fuente dejo sin traducir ('0' en region_dos, '0x2a' en region_omt).
    for columna in ["region", "region_dos", "region_omt", "mceo"]:
        invalidas = df[columna].isin(config.CODIGOS_INVALIDOS)
        if invalidas.any():
            utils.paso(f"codigos invalidos en {columna}: {int(invalidas.sum())} filas "
                       f"-> {config.ETIQUETA_SIN_CLASIFICAR}")
            df.loc[invalidas, columna] = config.ETIQUETA_SIN_CLASIFICAR

    df = separar_codigo_de_frontera(df)

    utils.validar_columnas(df, config.COLUMNAS_03, "etapa 3")
    utils.validar_sin_nulos(df, config.COLUMNAS_TEXTO + ["viajeros"], "etapa 3")
    utils.guardar_csv(df[config.COLUMNAS_03], config.SALIDA_03)


if __name__ == "__main__":
    utils.correr("Etapa 3: unificacion de categorias", unificar_categorias)
