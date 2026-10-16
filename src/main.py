"""Punto de entrada: python src/main.py

Carga los datos de la heladería y muestra un menú para consultar el pronóstico.
"""
from pathlib import Path

import pandas as pd

import graficos
from heladeria import Heladeria
from pipeline import guardar_tabla
from pronostico import Pronostico

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_DATOS = RAIZ / "data"
CARPETA_SALIDAS = RAIZ / "outputs"

pd.set_option("display.width", 120)


class App:
    """Menú de consola. Ante una entrada inválida muestra un aviso y vuelve al menú en vez de cortarse."""

    def __init__(self, heladeria, entrada=input, carpeta_salidas=CARPETA_SALIDAS):
        self.heladeria = heladeria
        self.pronostico = Pronostico(heladeria, heladeria.años()[-1])
        self.entrada = entrada
        self.carpeta_salidas = Path(carpeta_salidas)
        self.opciones = {
            "1": ("Ver la carga de datos y las filas rechazadas", self.ver_carga),
            "2": ("Ver la estacionalidad y el ranking de sabores", self.ver_estacionalidad),
            "3": ("Validar el método de pronóstico", self.ver_validacion),
            "4": (f"Producción de cada sabor para un mes de {self.pronostico.año_objetivo}", self.ver_produccion),
            "5": (f"Compras de insumos para un mes de {self.pronostico.año_objetivo}", self.ver_compras),
            "6": ("Exportar resultados y gráficos a outputs/", self.exportar),
        }

    def mostrar_menu(self):
        print("\n" + "=" * 60)
        print(f"  PLANIFICADOR DE PRODUCCIÓN Y COMPRAS — {self.heladeria.nombre}")
        print("=" * 60)
        for clave, (texto, _) in self.opciones.items():
            print(f"  {clave}. {texto}")
        print("  0. Salir")

    def ejecutar(self):
        while True:
            self.mostrar_menu()
            opcion = self.entrada("Elegí una opción: ").strip()
            if opcion == "0":
                print("¡Hasta luego!")
                break
            self.atender(opcion)
            self.entrada("\n(Apretá Enter para volver al menú) ")

    def atender(self, opcion):
        if opcion not in self.opciones:
            print("⚠ Opción inválida: escribí un número del menú.")
            return
        try:
            self.opciones[opcion][1]()
        except ValueError as error:
            print(f"⚠ {error}")

    def pedir_mes(self):
        texto = self.entrada(f"¿Qué mes de {self.pronostico.año_objetivo}? (1 a 12): ").strip()
        if not texto.isdigit():
            raise ValueError("El mes tiene que ser un número del 1 al 12")
        return int(texto)

    def ver_carga(self):
        print(self.heladeria)
        rechazos = self.heladeria.rechazos
        if len(rechazos) == 0:
            print("No se rechazó ninguna fila.")
            return
        print("\nFilas rechazadas:")
        print(rechazos[["tabla", "fecha", "sabor", "kg", "motivo_rechazo"]].to_string(index=False))

    def ver_estacionalidad(self):
        print("Kg vendidos por mes (índice: 1 = mes promedio):")
        print(self.heladeria.estacionalidad().to_string())
        año = self.heladeria.años()[-1]
        print(f"\nRanking de sabores {año}:")
        print(self.heladeria.ranking_sabores(año).to_string())

    def ver_validacion(self):
        tabla, resumen = self.pronostico.validar()
        print(f"Pronóstico de julio a diciembre de {self.pronostico.año_base} usando solo los datos anteriores:")
        print(tabla.to_string())
        print(f"\nError del método: {resumen['error_metodo']:.1%} · "
              f"Error de repetir el año anterior: {resumen['error_ingenuo']:.1%}")

    def ver_produccion(self):
        mes = self.pedir_mes()
        tabla = self.pronostico.produccion(mes)
        print(tabla.to_string())
        print(f"\nTotal a producir: {tabla['produccion'].sum():,.1f} kg")
        sin_historial = self.pronostico.sabores_sin_historial()
        if sin_historial:
            print(f"Sin pronóstico (no vendieron el año anterior): {', '.join(sin_historial)}")
        for sabor, diferencia in self.pronostico.cambios_de_tendencia().items():
            sentido = "cae" if diferencia < 0 else "crece"
            print(f"⚠ {sabor}: en los últimos meses {sentido} más que en el resto del año "
                  f"({abs(diferencia) * 100:.0f} puntos de diferencia). Revisá su producción.")

    def ver_compras(self):
        mes = self.pedir_mes()
        print(self.pronostico.compras_del_mes(mes).to_string())
        print("\npedidos: en cuántas veces conviene comprar en el mes según la vida útil del insumo.")

    def exportar(self):
        año = self.pronostico.año_objetivo
        tabla_validacion, _ = self.pronostico.validar()
        rutas = [
            guardar_tabla(self.heladeria.rechazos, self.carpeta_salidas / "rechazos.csv"),
            guardar_tabla(self.pronostico.produccion_anual(), self.carpeta_salidas / f"produccion_{año}.csv"),
            guardar_tabla(self.pronostico.plan_compras(), self.carpeta_salidas / f"compras_{año}.csv"),
            guardar_tabla(tabla_validacion, self.carpeta_salidas / "validacion.csv"),
            graficos.grafico_lineas(self.heladeria.estacionalidad().drop(columns="indice"),
                                    "Kg vendidos por mes", "kg", self.carpeta_salidas / "estacionalidad.png"),
            graficos.grafico_lineas(self.pronostico.resumen_anual(), f"Ventas {año - 1} y producción pronosticada {año}",
                                    "kg", self.carpeta_salidas / f"pronostico_{año}.png"),
            graficos.grafico_validacion(tabla_validacion, self.carpeta_salidas / "validacion.png"),
        ]
        print("Archivos guardados:")
        for ruta in rutas:
            print(f"  {ruta.relative_to(RAIZ) if ruta.is_relative_to(RAIZ) else ruta}")


def main():
    try:
        heladeria = Heladeria(CARPETA_DATOS)
    except (FileNotFoundError, ValueError) as error:
        print(f"⚠ No se pudieron cargar los datos: {error}")
        return
    print(heladeria)
    guardar_tabla(heladeria.rechazos, CARPETA_SALIDAS / "rechazos.csv")
    App(heladeria).ejecutar()


if __name__ == "__main__":
    main()