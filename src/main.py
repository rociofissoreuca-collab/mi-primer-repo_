"""Punto de entrada: python src/main.py

Por ahora: carga y limpia los datos, guarda las filas rechazadas y muestra la estacionalidad y el ranking.
"""
from pathlib import Path

import pandas as pd

from heladeria import Heladeria
from pipeline import guardar_tabla

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_DATOS = RAIZ / "data"
CARPETA_SALIDAS = RAIZ / "outputs"

pd.set_option("display.width", 120)


def main():
    try:
        heladeria = Heladeria(CARPETA_DATOS)
    except (FileNotFoundError, ValueError) as error:
        print(f"⚠ No se pudieron cargar los datos: {error}")
        return

    print(heladeria)
    guardar_tabla(heladeria.rechazos, CARPETA_SALIDAS / "rechazos.csv")
    print("Las filas rechazadas se guardaron en outputs/rechazos.csv")

    print("\nKg vendidos por mes (índice: 1 = mes promedio):")
    print(heladeria.estacionalidad().to_string())

    año = heladeria.años()[-1]
    print(f"\nRanking de sabores {año}:")
    print(heladeria.ranking_sabores(año).to_string())


if __name__ == "__main__":
    main()