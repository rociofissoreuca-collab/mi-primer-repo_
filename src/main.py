"""Punto de entrada: python src/main.py

Por ahora: lee los datos, los valida y limpia, y guarda las filas rechazadas.
"""
from pathlib import Path

from pipeline import guardar_tabla, preparar_datos

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_DATOS = RAIZ / "data"
CARPETA_SALIDAS = RAIZ / "outputs"


def main():
    try:
        tablas, rechazos = preparar_datos(CARPETA_DATOS)
    except (FileNotFoundError, ValueError) as error:
        print(f"⚠ No se pudieron cargar los datos: {error}")
        return

    print("Registros válidos:")
    for nombre, tabla in tablas.items():
        print(f"  {nombre}: {len(tabla)}")

    print(f"\nFilas rechazadas: {len(rechazos)}")
    print(rechazos[["tabla", "fecha", "sabor", "kg", "motivo_rechazo"]].to_string(index=False))

    ruta = guardar_tabla(rechazos, CARPETA_SALIDAS / "rechazos.csv")
    print(f"\nSe guardaron en {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()