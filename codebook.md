# Codebook — `data/processed/base_limpia.csv`

Dataset final que produce el pipeline. Formato largo: **161,036 filas x 16 columnas**,
una fila por combinacion de mes, via, frontera, pais, agrupacion de residencia y
tipo de viajero. Cobertura de **enero 2009 a junio 2026**, 210 meses consecutivos
sin huecos. Sin valores faltantes salvo `codigo_frontera`, que es nulo por diseno.

La medida es `viajeros`; el resto de columnas son dimensiones por las que agregarla.
No hay filas de total ni doble conteo, asi que sumar `viajeros` sobre cualquier
subconjunto da el total de ese subconjunto.

## Variables

| Columna | Tipo | Descripcion | Valores |
|---------|------|-------------|---------|
| `fecha` | fecha | Primer dia del mes de ingreso. Derivada de `anio` y `mes_cod`, es la que se usa como indice temporal | 2009-01-01 a 2026-06-01, frecuencia mensual |
| `anio` | entero | Ano de ingreso al pais | 2009 a 2026 (2026 solo llega a junio) |
| `mes_cod` | entero | Codificacion del mes | 1 a 12 |
| `mes` | texto | Nombre abreviado del mes | Ene, Feb, Mar, ... Dic |
| `via` | texto | Via de entrada | Aerea, Terrestre, Maritima |
| `frontera` | texto | Nombre del puesto de ingreso, sin el codigo | 22 valores (La Aurora, Valle Nuevo, San Cristobal, ...) |
| `codigo_frontera` | texto | Codigo del puesto segun la nomenclatura historica. **Unica columna con nulos**: vacio para `Cruceros`, que no es una frontera fisica | 01 a 20, 22, o nulo |
| `pais` | texto | Pais de procedencia hasta 2022; desde 2023 es una agrupacion de mercado | 222 valores tras unificar variantes |
| `region` | texto | Clasificacion usada para reportes nacionales | 17 valores |
| `region_dos` | texto | Agrupa varias categorias de `region` en continentes o grandes areas | 10 valores |
| `region_omt` | texto | Subregion de la Organizacion Mundial del Turismo | 26 valores |
| `mceo` | texto | Mercado o agrupacion comercial estrategica | 8 valores |
| `agrupacion_residencia` | texto | Region donde reside el viajero. **Poco confiable en 2021 y 2022** (ver notas) | 32 valores |
| `tipo_viajero` | texto | Categoria del viajero | Turista, Excursionista, Viajero, Cruceristas |
| `viajeros` | decimal | Cantidad de viajeros. Es la medida del conjunto | >= 0. Admite decimales |
| `es_visitante` | booleano | Derivada: `True` si `tipo_viajero` es Turista o Excursionista | True / False |

## Definicion de `tipo_viajero`

- **Turista**: pernocta al menos una noche en el pais.
- **Excursionista**: visita sin pernoctar, entra y sale el mismo dia.
- **Viajero**: cruza la frontera sin calificar como visitante (trabajo fronterizo,
  transito, carga, tripulacion, comercio de alta frecuencia). No se contabiliza
  como visitante.
- **Cruceristas**: pasajeros de crucero. Solo existen hasta 2022; desde 2023 los
  cruceros se miden por una fuente portuaria externa y no aparecen aqui.

## `es_visitante`, la unica medida comparable en todo el periodo

`es_visitante` marca Turista + Excursionista, y es la agregacion que hay que usar
para comparar a lo largo de los 210 meses. Las otras dos categorias no son
comparables consigo mismas:

- `Viajero` cambia de definicion en 2023, cuando la metodologia depurada excluye a
  los compradores fronterizos frecuentes. Cae de 1.06 millones en 2022 a 331 mil en
  2023 sin que eso corresponda a un cambio real de comportamiento.
- `Cruceristas` desaparece de la base en 2023.

## Advertencias de la fuente

Los datos son de uso exclusivamente academico y no corresponden a cifras oficiales
del INGUAT ni del Instituto Guatemalteco de Migracion. La base se armo de tres
tramos: 2009-2020 de respaldos historicos, 2021-2022 de una entrega del IGM, y
2023-2026 del sistema depurado de conteos del INGUAT. De ahi salen los quiebres:

1. **Quiebre metodologico 2022 → 2023.** El tramo desde 2023 viene del sistema
   depurado y excluye compradores fronterizos frecuentes, entre otros criterios.
   Los niveles no son perfectamente comparables hacia atras.
2. **Granularidad de `pais`.** De 2009 a 2021 la fuente reporta alrededor de 200
   paises individuales, en 2022 baja a 109 y desde 2023 reporta 26 agrupaciones de
   mercado. Los mercados principales (El Salvador, Estados Unidos, Honduras,
   Mexico) siguen siendo comparables como serie; los paises pequenos quedan dentro
   de su agrupacion.
3. **`Guatemala` desaparece como pais de residencia desde 2023.** Aportaba 1.42
   millones de visitantes en 2022 y cero desde 2023. No es una caida, es que la
   nueva metodologia dejo de contar a los residentes del propio pais. Explica buena
   parte de la brecha aparente del total frente a 2019.
4. **Via maritima.** Desde 2017 no registra **ningun** visitante: todo su flujo
   queda clasificado como `Cruceristas`, que no es turista ni excursionista. Y como
   los cruceristas terminan en 2022, la via maritima queda en un residuo de unas
   6,000 personas al ano. No es una serie modelable.
5. **Decimales en `viajeros`.** Son estimaciones expandidas de encuesta, no conteos
   exactos. Un 32% de las filas los trae. No se redondean, porque redondear
   introduce un sesgo sistematico al agregar.
6. **`agrupacion_residencia` es ruidosa en 2021 y 2022.** Aparecen combinaciones
   imposibles, como viajeros de Japon clasificados en `Otros Europa`. No conviene
   usarla como variable de analisis.
7. **2026 esta incompleto**, cubre solo enero a junio. Cualquier corte anual que la
   incluya se lee como una caida artificial.

## Transformaciones que aplico el pipeline

Ninguna descarta filas. El conteo entra y sale en 161,036.

| Transformacion | Etapa | Alcance |
|----------------|-------|---------|
| Nombres de columna a snake_case | 1 | 13 columnas |
| Unificacion de marcadores de nulo a `NaN` | 1 | todas |
| Recorte de espacios sobrantes | 1 | columnas de texto |
| Eliminacion de filas duplicadas exactas | 2 | 0 filas (el crudo no traia) |
| Fusion de paises que solo difieren en mayusculas | 3 | 13 paises, 51 filas |
| `Resto de mundo` → `Resto del Mundo` | 3 | 630 filas |
| `Cruceros` → `Cruceristas` en `region_dos` | 3 | 8 filas |
| Codigos `0` y `0x2a` → `Sin clasificar` | 3 | 18 filas, 821 viajeros |
| Separacion de `codigo_frontera` del nombre | 3 | 161,036 filas |
| Tipado numerico y validacion de dominios | 4 | todas |
| Construccion de `fecha` y `es_visitante` | 4 | 161,036 filas |
