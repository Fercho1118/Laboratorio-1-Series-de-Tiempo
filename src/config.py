"""Rutas de cada etapa y contrato de columnas del pipeline."""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "data" / "raw"
DATA_PROCESSED = RAIZ / "data" / "processed"
FIGURAS = RAIZ / "reports" / "figuras"

# Entradas y salidas de cada etapa
CRUDO = DATA_RAW / "Base_Migracion_2009-2026jun.xlsx"
HOJA_DATOS = "Datos"
HOJA_NOTAS = "Notas"

SALIDA_01 = DATA_PROCESSED / "01_ingesta.csv"
SALIDA_02 = DATA_PROCESSED / "02_deduplicado.csv"
SALIDA_03 = DATA_PROCESSED / "03_categorias.csv"
SALIDA_04 = DATA_PROCESSED / "base_limpia.csv"

SALIDA_05 = DATA_PROCESSED / "series_mensuales.csv"
SALIDA_06_TRAIN = DATA_PROCESSED / "series_train.csv"
SALIDA_06_TEST = DATA_PROCESSED / "series_test.csv"

# Construccion de series (etapa 5): categorias elegidas segun el diagnostico de
# viabilidad de la seccion 11 del EDA. Regiones y fronteras son las unicas dos
# categorias cuyas tres series principales cubren los 210 meses sin huecos.
CATEGORIAS_SERIES = {"region_dos": "region", "frontera": "frontera"}
TOP_N_SERIES = 3

# Ventana del cierre de fronteras por la pandemia: unicos meses donde una serie
# puede valer cero sin ser un hueco de datos.
INICIO_CIERRE_PANDEMIA = pd.Timestamp("2020-03-01")
FIN_CIERRE_PANDEMIA = pd.Timestamp("2020-09-01")

# Particion temporal (etapa 6): 70% inicial para entrenamiento, 30% final para prueba
PROPORCION_ENTRENAMIENTO = 0.70

# Contrato: nombres originales del Excel -> nombres normalizados
RENOMBRE_COLUMNAS = {
    "Año": "anio",
    "Mes cod": "mes_cod",
    "Mes": "mes",
    "Vía": "via",
    "Frontera": "frontera",
    "País": "pais",
    "Región": "region",
    "Región dos": "region_dos",
    "Regiones OMT": "region_omt",
    "MCEO": "mceo",
    "Agrupación Residencia": "agrupacion_residencia",
    "Tipo de Viajero": "tipo_viajero",
    "Viajero": "viajeros",
}

COLUMNAS_CRUDO = list(RENOMBRE_COLUMNAS.keys())
COLUMNAS_01 = list(RENOMBRE_COLUMNAS.values())

# Columnas que agrega cada etapa posterior
COLUMNAS_02 = COLUMNAS_01  # la deduplicacion quita filas, no cambia el esquema
COLUMNAS_03 = COLUMNAS_02 + ["codigo_frontera"]
COLUMNAS_04 = ["fecha"] + COLUMNAS_03 + ["es_visitante"]

# Combinacion que identifica una fila en el formato largo. No es una llave unica:
# la fuente puede reportar la misma combinacion con agrupaciones de residencia
# distintas, y cada una aporta viajeros propios.
LLAVE_NEGOCIO = ["anio", "mes_cod", "via", "frontera", "pais",
                 "agrupacion_residencia", "tipo_viajero"]

COLUMNAS_TEXTO = [
    "mes", "via", "frontera", "pais", "region", "region_dos",
    "region_omt", "mceo", "agrupacion_residencia", "tipo_viajero",
]

# Marcadores de nulo que puede traer el crudo
MARCADORES_NULOS = ["", " ", "NA", "N/A", "n/a", "null", "NULL", "None", "-", "--", "?", "#N/A", "nan"]

# Dominios validos esperados al terminar el tipado
DOMINIO_VIA = {"Aérea", "Terrestre", "Marítima"}
DOMINIO_TIPO_VIAJERO = {"Turista", "Excursionista", "Viajero", "Cruceristas"}
TIPOS_VISITANTE = {"Turista", "Excursionista"}

ANIO_MIN, ANIO_MAX = 2009, 2026
MESES_ESPERADOS = 210  # enero 2009 a junio 2026, consecutivos

# Correcciones de categoria detectadas en el diagnostico del crudo
SINONIMOS_AGRUPACION = {"Resto de mundo": "Resto del Mundo"}
SINONIMOS_REGION_DOS = {"Cruceros": "Cruceristas"}
CODIGOS_INVALIDOS = {"0", "0x2a"}
ETIQUETA_SIN_CLASIFICAR = "Sin clasificar"

ORDEN_MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MES_A_NUMERO = {nombre: i + 1 for i, nombre in enumerate(ORDEN_MESES)}
