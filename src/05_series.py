"""Etapa 5: construccion de las series de tiempo mensuales.

Lee base_limpia.csv y arma las siete series mensuales del laboratorio:

- total: total mensual de visitantes internacionales (serie obligatoria)
- las tres regiones de region_dos con mayor acumulado en todo el periodo
- las tres fronteras con mayor acumulado en todo el periodo

La medida en todas es visitantes (Turista + Excursionista), la unica agregacion
comparable en los 210 meses: 'Viajero' cambia de definicion en 2023 y
'Cruceristas' desaparece ese anio. Las categorias (regiones y fronteras) salen
del diagnostico de viabilidad de la seccion 11 del EDA: son las unicas dos
opciones del enunciado cuyas tres series principales cubren todo el periodo sin
meses en cero.

El ranking usa el total acumulado de todo el periodo, como exige el enunciado,
no un anio especifico.
"""

import pandas as pd

import config
import utils


def _serie_mensual(df, rejilla, etiqueta):
    serie = df.groupby("fecha")["viajeros"].sum().reindex(rejilla, fill_value=0)
    # Los unicos meses en cero admisibles son los del cierre de fronteras por la
    # pandemia (abril-agosto 2020): son ceros reales, no huecos de datos. Un cero
    # fuera de esa ventana si indicaria una serie no modelable.
    ceros = serie[serie == 0].index
    fuera = ceros[(ceros < config.INICIO_CIERRE_PANDEMIA) | (ceros > config.FIN_CIERRE_PANDEMIA)]
    utils.exigir(
        fuera.empty,
        f"etapa 5: la serie '{etiqueta}' tiene meses sin visitantes fuera del "
        f"cierre pandemico ({[f'{d:%Y-%m}' for d in fuera]}); no es modelable",
    )
    if not ceros.empty:
        utils.paso(f"'{etiqueta}': {len(ceros)} meses en cero por el cierre pandemico")
    return serie


def construir_series():
    df = utils.cargar_csv(
        config.SALIDA_04, "etapa 5", parse_dates=["fecha"]
    )
    utils.validar_columnas(df, config.COLUMNAS_04, "etapa 5")

    visitantes = df[df["es_visitante"]]
    rejilla = pd.date_range(df["fecha"].min(), df["fecha"].max(), freq="MS")
    utils.exigir(
        len(rejilla) == config.MESES_ESPERADOS,
        f"etapa 5: se esperaban {config.MESES_ESPERADOS} meses y hay {len(rejilla)}",
    )

    series = {"total": _serie_mensual(visitantes, rejilla, "total")}

    for columna, prefijo in config.CATEGORIAS_SERIES.items():
        top = (
            visitantes.groupby(columna)["viajeros"]
            .sum()
            .nlargest(config.TOP_N_SERIES)
        )
        utils.paso(f"top {config.TOP_N_SERIES} de {columna} por acumulado: "
                   + ", ".join(f"{v} ({t:,.0f})" for v, t in top.items()))
        for valor in top.index:
            etiqueta = f"{prefijo}: {valor}"
            series[etiqueta] = _serie_mensual(
                visitantes[visitantes[columna] == valor], rejilla, etiqueta
            )

    salida = pd.DataFrame(series)
    salida.index.name = "fecha"

    utils.exigir(
        salida.notna().all().all(), "etapa 5: quedaron nulos en las series"
    )
    utils.paso(f"series construidas: {list(salida.columns)}")
    utils.paso(f"periodo: {salida.index.min():%Y-%m} a {salida.index.max():%Y-%m}")
    utils.guardar_csv(salida.reset_index(), config.SALIDA_05)


if __name__ == "__main__":
    utils.correr("Etapa 5: construccion de series mensuales", construir_series)
