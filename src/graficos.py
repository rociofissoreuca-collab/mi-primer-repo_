"""Gráficos de la aplicación. Se guardan como PNG en la carpeta outputs/."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORES = ["#2a78d6", "#eb6834"]
TEXTO = "#52514e"


def preparar_ejes(titulo, etiqueta_y):
    figura, ejes = plt.subplots(figsize=(9, 5))
    ejes.set_title(titulo, loc="left", fontsize=13)
    ejes.set_ylabel(etiqueta_y, color=TEXTO)
    ejes.grid(axis="y", alpha=0.25)
    ejes.spines[["top", "right"]].set_visible(False)
    ejes.tick_params(colors=TEXTO)
    return figura, ejes


def guardar(figura, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    figura.tight_layout()
    figura.savefig(ruta, dpi=120)
    plt.close(figura)
    return ruta


def grafico_lineas(tabla, titulo, etiqueta_y, ruta):
    """Una línea por columna de la tabla, con los meses en el eje horizontal."""
    figura, ejes = preparar_ejes(titulo, etiqueta_y)
    meses = [mes[:3] for mes in tabla.index]
    for numero, columna in enumerate(tabla.columns):
        ejes.plot(meses, tabla[columna], color=COLORES[numero % len(COLORES)], linewidth=2,
                  marker="o", markersize=5, label=str(columna))
    ejes.set_ylim(bottom=0)
    ejes.legend(frameon=False)
    return guardar(figura, ruta)


def grafico_validacion(tabla, ruta):
    """Error del pronóstico por sabor, comparado con el método ingenuo (repetir el año anterior)."""
    tabla = tabla.sort_values("error")
    figura, ejes = preparar_ejes("Error del pronóstico por sabor (2.º semestre 2025)", "")
    posiciones = range(len(tabla))
    ejes.barh([p + 0.2 for p in posiciones], tabla["error"] * 100, height=0.4, color=COLORES[0], label="método con crecimiento")
    ejes.barh([p - 0.2 for p in posiciones], tabla["error_ingenuo"] * 100, height=0.4, color=COLORES[1], label="repetir el año anterior")
    ejes.set_yticks(list(posiciones), tabla.index)
    ejes.set_xlabel("error (% de lo vendido)", color=TEXTO)
    ejes.grid(axis="y", alpha=0)
    ejes.grid(axis="x", alpha=0.25)
    ejes.legend(frameon=False, loc="lower right")
    return guardar(figura, ruta)