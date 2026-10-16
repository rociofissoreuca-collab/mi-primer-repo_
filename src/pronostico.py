"""Pronóstico de producción y plan de compras de insumos para el año siguiente al último con datos."""
import calendar
import math

import pandas as pd

from heladeria import MESES

MARGEN_SEGURIDAD_DIAS = 2
MESES_PARA_VALIDAR = range(7, 13)
MESES_RECIENTES = range(10, 13)
UMBRAL_CAMBIO_TENDENCIA = 0.05


def calcular_crecimiento(kg_actual, kg_anterior):
    """Crecimiento de cada sabor entre dos períodos equivalentes. Sin ventas en el anterior no se puede medir (NaN)."""
    anterior = kg_anterior.sum()
    return kg_actual.sum() / anterior.where(anterior > 0) - 1


def error_porcentual(pronostico, real):
    """De cada 100 kg vendidos, cuántos kg se equivocó el pronóstico (en más o en menos)."""
    return float((pronostico - real).abs().to_numpy().sum() / real.to_numpy().sum())


def validar_mes(mes):
    if not isinstance(mes, int) or not 1 <= mes <= 12:
        raise ValueError("El mes tiene que ser un número entero entre 1 y 12")


class Pronostico:
    """Pronostica el año siguiente a año_base: mismo mes de año_base × (1 + crecimiento del sabor)."""

    def __init__(self, heladeria, año_base):
        if año_base not in heladeria.años() or año_base - 1 not in heladeria.años():
            raise ValueError(f"Para pronosticar desde {año_base} se necesitan ventas de {año_base - 1} y {año_base}")
        self.heladeria = heladeria
        self.año_base = año_base
        self.año_objetivo = año_base + 1
        self._kg_base = heladeria.kg_por_mes(año_base)
        self._kg_anterior = heladeria.kg_por_mes(año_base - 1)
        self._crecimiento = calcular_crecimiento(self._kg_base, self._kg_anterior)

    def crecimiento(self):
        """Crecimiento de cada sabor de un año al otro (solo los sabores con historial)."""
        return self._crecimiento.dropna().sort_values(ascending=False).round(3)

    def sabores_sin_historial(self):
        """Sabores que no vendieron en el año anterior: no se pueden pronosticar con este método."""
        return list(self._crecimiento[self._crecimiento.isna()].index)

    def cambios_de_tendencia(self):
        """Sabores cuyo crecimiento de los últimos meses se aleja del crecimiento del año.

        El pronóstico supone que la tendencia del año se mantiene; si en los últimos meses cambió,
        conviene revisar esos sabores a mano. Devuelve la diferencia (ej.: -0.06 = cae 6 puntos más).
        """
        meses = list(MESES_RECIENTES)
        reciente = calcular_crecimiento(self._kg_base.loc[meses], self._kg_anterior.loc[meses])
        diferencia = (reciente - self._crecimiento).dropna()
        return diferencia[diferencia.abs() > UMBRAL_CAMBIO_TENDENCIA].sort_values().round(3)

    def demanda(self, mes):
        """Kg que se espera vender de cada sabor en ese mes del año objetivo."""
        validar_mes(mes)
        crecimiento = self.crecimiento()
        return (self._kg_base.loc[mes, crecimiento.index] * (1 + crecimiento)).round(1)

    def produccion(self, mes):
        """Kg a producir de cada sabor: lo que se espera vender más lo que se suele tirar."""
        demanda = self.demanda(mes)
        merma = demanda * self.heladeria.tasa_merma().reindex(demanda.index, fill_value=0)
        tabla = pd.DataFrame({"demanda": demanda, "merma_esperada": merma.round(1)})
        tabla["produccion"] = tabla["demanda"] + tabla["merma_esperada"]
        tabla.index.name = "sabor"
        return tabla.sort_values("produccion", ascending=False)

    def consumo_insumos(self, mes):
        """Cantidad de cada insumo que necesita la producción del mes (producción × receta)."""
        produccion = self.produccion(mes)["produccion"].reset_index()
        detalle = produccion.merge(self.heladeria.recetas, on="sabor")
        detalle["cantidad"] = detalle["produccion"] * detalle["cantidad_por_kg"]
        return detalle.groupby("insumo")["cantidad"].sum().round(2)

    def plan_compras(self):
        """Compras de cada insumo mes a mes, partiendo del stock actual.

        Cada mes se compra lo que falta para cubrir el consumo y dejar un stock de seguridad
        (los días que tarda el proveedor más un margen). Los perecederos se piden en varias veces.
        """
        insumos = self.heladeria.insumos
        stock = insumos["stock_actual"].astype(float)
        filas = []
        for mes in range(1, 13):
            dias = calendar.monthrange(self.año_objetivo, mes)[1]
            consumo = self.consumo_insumos(mes).reindex(insumos.index, fill_value=0)
            seguridad = consumo / dias * (insumos["dias_entrega"] + MARGEN_SEGURIDAD_DIAS)
            for insumo in insumos.index:
                stock_inicial = stock[insumo]
                compra = max(consumo[insumo] + seguridad[insumo] - stock_inicial, 0)
                stock[insumo] = stock_inicial + compra - consumo[insumo]
                filas.append({
                    "mes": mes,
                    "insumo": insumo,
                    "unidad": insumos.loc[insumo, "unidad"],
                    "stock_inicial": stock_inicial,
                    "consumo": consumo[insumo],
                    "compra": compra,
                    "stock_final": stock[insumo],
                    "pedidos": math.ceil(dias / min(insumos.loc[insumo, "vida_util_dias"], dias)) if compra > 0 else 0,
                })
        plan = pd.DataFrame(filas)
        if (plan["stock_final"] < -1e-9).any():
            raise ValueError("El plan de compras dejó stock negativo: revisar los datos de insumos")
        return plan.round(2)

    def compras_del_mes(self, mes):
        validar_mes(mes)
        plan = self.plan_compras()
        del_mes = plan[(plan["mes"] == mes) & (plan["compra"] > 0)].set_index("insumo")
        return del_mes[["unidad", "consumo", "stock_inicial", "compra", "pedidos"]].sort_values("compra", ascending=False)

    def validar(self):
        """Prueba el método en el 2.º semestre de año_base, como si todavía no hubiera pasado.

        El crecimiento se mide con el 1.er semestre (año_base contra el anterior). Se compara mes a mes
        contra lo que realmente se vendió y contra un método ingenuo que repite el año anterior.
        """
        meses = list(MESES_PARA_VALIDAR)
        crecimiento = calcular_crecimiento(self._kg_base.loc[1:6], self._kg_anterior.loc[1:6]).dropna()
        real = self._kg_base.loc[meses, crecimiento.index]
        ingenuo = self._kg_anterior.loc[meses, crecimiento.index]
        pronostico = ingenuo * (1 + crecimiento)
        tabla = pd.DataFrame({
            "real": real.sum(),
            "pronostico": pronostico.sum(),
            "error": (pronostico - real).abs().sum() / real.sum(),
            "error_ingenuo": (ingenuo - real).abs().sum() / real.sum(),
        })
        tabla.index.name = "sabor"
        resumen = {"error_metodo": error_porcentual(pronostico, real), "error_ingenuo": error_porcentual(ingenuo, real)}
        return tabla.sort_values("error", ascending=False).round(3), resumen

    def produccion_anual(self):
        """Kg a producir de cada sabor (filas) en cada mes del año objetivo (columnas)."""
        tabla = pd.DataFrame({MESES[mes - 1]: self.produccion(mes)["produccion"] for mes in range(1, 13)})
        tabla.index.name = "sabor"
        return tabla.round(1)

    def resumen_anual(self):
        """Kg a producir por mes en el año objetivo, junto a lo vendido en el año base."""
        return pd.DataFrame({f"vendido {self.año_base}": self._kg_base.sum(axis=1).values,
                             f"producción {self.año_objetivo}": self.produccion_anual().sum().values},
                            index=MESES).round(1)

    def __str__(self):
        return f"Pronóstico {self.año_objetivo} de {self.heladeria.nombre}, a partir de las ventas de {self.año_base}"