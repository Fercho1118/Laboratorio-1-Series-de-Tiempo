"""Corre las etapas del pipeline en orden. Si una falla, no se ejecutan las siguientes."""

import importlib
import sys

import utils

ETAPAS = [
    ("01_ingesta", "ingestar", "Etapa 1: ingesta"),
    ("02_deduplicacion", "deduplicar", "Etapa 2: deduplicacion"),
    ("03_categorias", "unificar_categorias", "Etapa 3: unificacion de categorias"),
    ("04_tipado", "tipar", "Etapa 4: tipado y validacion de dominios"),
]


def main():
    for modulo, funcion, titulo in ETAPAS:
        utils.correr(titulo, getattr(importlib.import_module(modulo), funcion))
    print("\nPipeline completo. Dataset final en data/processed/base_limpia.csv")


if __name__ == "__main__":
    sys.exit(main())
