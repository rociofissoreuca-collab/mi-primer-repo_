"""Punto de entrada: python src/main.py

Por ahora: carga los datos, valida el método de pronóstico y muestra la producción y las compras de un mes.
"""
from pathlib import Path

import pandas as pd

from heladeria import Heladeria
from pipeline import guardar_tabla
from pronostico import Pronostico

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

    pronostico = Pronostico(heladeria, heladeria.años()[-1])
    print(f"\n{pronostico}")

    tabla, resumen = pronostico.validar()
    print(f"\nValidación (julio a diciembre de {pronostico.año_base}):")
    print(tabla.to_string())
    print(f"Error del método: {resumen['error_metodo']:.1%} · "
          f"Error de repetir el año anterior: {resumen['error_ingenuo']:.1%}")

    print(f"\nProducción de diciembre de {pronostico.año_objetivo}:")
    print(pronostico.produccion(12).to_string())

    print(f"\nCompras de enero de {pronostico.año_objetivo}:")
    print(pronostico.compras_del_mes(1).to_string())


if __name__ == "__main__":
    main()