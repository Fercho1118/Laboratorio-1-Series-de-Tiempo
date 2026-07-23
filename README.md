# Laboratorio 1. Series de Tiempo

CC3084 Data Science, Universidad del Valle de Guatemala, Semestre II 2026.

Fernando Rueda - 23748
Fernando Hernández - 23645

Analisis de los datos historicos de ingreso de viajeros internacionales a Guatemala,
de enero 2009 a junio 2026. El conjunto viene en formato largo, una fila por
combinacion de mes, via, frontera, pais y tipo de viajero, y trae los quiebres
tipicos de una base armada de tres fuentes distintas: categorias escritas de varias
formas, codigos sin traducir y un cambio de metodologia a mitad del periodo.

Igual que en la practica de limpieza, la preparacion de los datos esta organizada
como un pipeline de etapas en lugar de un solo script. Cada etapa hace una sola
cosa, lee la salida de la anterior, la valida, la transforma y escribe su propio
dataset.

## El pipeline

```
data/raw/Base_Migracion_2009-2026jun.xlsx
        │
        ▼
┌─────────────────────┐
│ 01_ingesta.py       │  trae la hoja Datos a texto y unifica los nulos
└─────────────────────┘
        │  data/processed/01_ingesta.csv
        ▼
┌─────────────────────┐
│ 02_deduplicacion.py │  quita duplicados y verifica la llave de negocio
└─────────────────────┘
        │  data/processed/02_deduplicado.csv
        ▼
┌─────────────────────┐
│ 03_categorias.py    │  unifica las categorias escritas de varias formas
└─────────────────────┘
        │  data/processed/03_categorias.csv
        ▼
┌─────────────────────┐
│ 04_tipado.py        │  tipa cada columna, arma la fecha y valida dominios
└─────────────────────┘
        │
        ▼
data/processed/base_limpia.csv   ← dataset final (ver codebook.md)
```

| Etapa | Archivo | Responsabilidad | Entrada | Salida |
|-------|---------|-----------------|---------|--------|
| 1 | `src/01_ingesta.py` | Leer la hoja `Datos`, normalizar los nombres de columna a snake_case y unificar los marcadores de nulo (`""`, `NA`, `N/A`, `null`, `-`, `?`...) a `NaN` | `data/raw/Base_Migracion_2009-2026jun.xlsx` | `data/processed/01_ingesta.csv` |
| 2 | `src/02_deduplicacion.py` | Eliminar filas duplicadas exactas y verificar la llave de negocio del formato largo | `01_ingesta.csv` | `data/processed/02_deduplicado.csv` |
| 3 | `src/03_categorias.py` | Unificar las categorias que el crudo trae escritas de varias formas y separar el codigo de la frontera de su nombre | `02_deduplicado.csv` | `data/processed/03_categorias.csv` |
| 4 | `src/04_tipado.py` | Convertir cada columna a su tipo y dominio validos, armar la fecha mensual y verificar que los 210 meses esten consecutivos | `03_categorias.csv` | `data/processed/base_limpia.csv` |

Sobre la etapa 2: en este conjunto no elimina nada, el crudo llega sin filas
duplicadas exactas. Se mantiene como etapa propia porque el supuesto hay que
verificarlo antes de unificar categorias — si la fusion de nombres de pais se
corriera sobre filas repetidas, duplicaria viajeros — y porque dejarlo explicito
documenta que la ausencia de duplicados se comprobo y no se asumio.

Archivos de apoyo:

- `src/00_init.py` — prepara el entorno: crea el venv e instala dependencias.
- `src/config.py` — rutas de cada etapa y el "contrato" de columnas y dominios.
- `src/utils.py` — funciones compartidas de carga, guardado y validacion.
- `src/run_pipeline.py` — corre las etapas en orden.
- `requirements.txt` — dependencias del proyecto.
- `codebook.md` — definicion de cada variable del dataset limpio.

Analisis:

- `notebooks/eda-general.ipynb` — analisis exploratorio general (punto 1 del enunciado).
- `reports/figuras/` — figuras que exporta el notebook al ejecutarlo, para usarlas en el informe. No se versionan, ya van embebidas en el notebook.
- `docs/` — enunciado del laboratorio.

## Como correrlo

1. Preparar el entorno (una sola vez). Se corre con el python del sistema; crea un
entorno virtual en `.venv/` e instala las dependencias de `requirements.txt`:

```
python src/00_init.py
```

2. Activar el venv (una vez por terminal):

```
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

3. Correr el pipeline completo:

```
python src/run_pipeline.py
```

O correr una etapa a la vez (cada script es independiente y se ejecuta solo):

```
python src/01_ingesta.py
python src/02_deduplicacion.py
python src/03_categorias.py
python src/04_tipado.py
```

Siempre desde la raiz del proyecto, con el venv activado. Despues del pipeline,
el notebook del analisis exploratorio se abre con:

```
jupyter notebook notebooks/eda-general.ipynb
```

## Que corrige la limpieza

El diagnostico del crudo encontro cuatro problemas de consistencia. Ninguno se
resuelve borrando filas, las 161,036 filas originales sobreviven completas al
pipeline:

- **Paises duplicados por mayusculas.** Trece paises venian escritos de dos formas
  que solo difieren en el uso de mayusculas (`Federación de Rusia` y
  `Federación De Rusia`). Sin unificarlos, pandas los cuenta como paises distintos
  y el ranking de paises queda partido. La etapa 3 los fusiona eligiendo la
  variante mas frecuente como forma canonica.
- **Codigos sin traducir.** Un `0` en `region_dos` y un `0x2a` en `region_omt`, que
  entre los dos afectan 13 filas y 821 viajeros. Se reetiquetan como
  `Sin clasificar` en vez de descartarse, porque son viajeros reales.
- **Sinonimos de categoria.** `Resto de mundo` contra `Resto del Mundo`, y
  `Cruceros` contra `Cruceristas` dentro de `region_dos`.
- **Codigo y nombre mezclados.** La frontera venia como `01 La Aurora`; la etapa 3
  separa el codigo en su propia columna.

Las filas que repiten la combinacion de mes, via, frontera, pais y tipo de viajero
**no** son duplicados: difieren en la agrupacion de residencia y cada una aporta
viajeros distintos, asi que se conservan y se suman.

## Por que un pipeline y no un solo script

- **Una responsabilidad por archivo.** Si algo sale mal en la unificacion de
  categorias, se sabe exactamente que archivo mirar.
- **Datasets intermedios auditables.** El notebook compara `01_ingesta.csv` contra
  `base_limpia.csv` para mostrar exactamente que cambio la limpieza. Ese estado
  intermedio existe en disco justamente porque el pipeline lo escribe.
- **Validacion entre etapas.** Cada etapa empieza validando la salida de la
  anterior: la etapa 2 confirma que ya no hay espacios ni cadenas vacias, la etapa
  3 confirma que ya no hay filas duplicadas, y la etapa 4 confirma que ya no hay
  paises que solo difieran en mayusculas y que los 210 meses estan consecutivos.
  Si un supuesto no se cumple, el pipeline falla ahi mismo (fail-fast) con un
  mensaje claro.
- **Reejecucion parcial.** Si cambia solo la logica de tipado, se corre la etapa 4
  sobre `03_categorias.csv` sin volver a leer el Excel, que es la parte lenta.
- **Extensible.** Las etapas de construccion de series y de particion en
  entrenamiento y prueba se encadenan despues como `05_series.py` y `06_split.py`,
  leyendo `base_limpia.csv`, sin tocar el codigo que ya funciona.
- **Datos crudos intactos.** El Excel en `data/raw/` nunca se modifica. Todo lo
  generado vive en `data/processed/` y se puede regenerar corriendo el pipeline.
