"""Etapa 6: particion temporal en entrenamiento y prueba.

Divide las series mensuales en 70% inicial para entrenamiento y 30% final para
prueba. La particion es temporal, no aleatoria: en series de tiempo el conjunto
de prueba debe ser siempre posterior al de entrenamiento, porque el objetivo es
evaluar pronosticos hacia el futuro y una particion aleatoria filtraria
informacion del futuro al modelo.

El corte se hace una sola vez sobre la rejilla mensual y aplica a las siete
series por igual, para que todos los modelos se evaluen sobre el mismo horizonte.
"""

import pandas as pd

import config
import utils


def particionar():
    series = utils.cargar_csv(config.SALIDA_05, "etapa 6", parse_dates=["fecha"])
    utils.exigir(
        series["fecha"].is_monotonic_increasing,
        "etapa 6: las fechas no vienen ordenadas",
    )

    n_total = len(series)
    n_train = round(n_total * config.PROPORCION_ENTRENAMIENTO)
    train, test = series.iloc[:n_train], series.iloc[n_train:]

    utils.paso(f"meses totales: {n_total}")
    utils.paso(
        f"entrenamiento: {len(train)} meses ({len(train) / n_total:.1%}), "
        f"{train['fecha'].min():%Y-%m} a {train['fecha'].max():%Y-%m}"
    )
    utils.paso(
        f"prueba: {len(test)} meses ({len(test) / n_total:.1%}), "
        f"{test['fecha'].min():%Y-%m} a {test['fecha'].max():%Y-%m}"
    )

    utils.exigir(
        train["fecha"].max() < test["fecha"].min(),
        "etapa 6: el entrenamiento invade el periodo de prueba",
    )

    utils.guardar_csv(train, config.SALIDA_06_TRAIN)
    utils.guardar_csv(test, config.SALIDA_06_TEST)


if __name__ == "__main__":
    utils.correr("Etapa 6: particion entrenamiento/prueba", particionar)
