# Planificador de producción y compras para una heladería

**Autora:** Rocío Fissore · Programación Orientada a Datos · UCA · Trabajo Práctico 2

## Problema

Una heladería artesanal decide cuánto helado producir y cuántos insumos comprar a partir de la experiencia del encargado. La demanda es muy estacional y muchos insumos son perecederos: si se produce o se compra de más, la mercadería se pierde; si se produce de menos, faltan sabores.

**Usuario:** el dueño o encargado de producción, que planifica cada mes qué producir y qué pedir a los proveedores.

**Pregunta:** ¿cuántos kilos de cada sabor conviene producir y cuánto de cada insumo conviene comprar en cada mes de 2026, según las ventas de 2024 y 2025, el consumo de insumos y la estacionalidad de la demanda?

## Solución propuesta

Una aplicación de consola en Python que:

1. Lee y valida los datos de ventas, merma, recetas e insumos (CSV y JSON) y registra las filas rechazadas.
2. Muestra la estacionalidad de la demanda y el ranking de sabores.
3. Valida el método de pronóstico contra datos reales.
4. Pronostica la producción de cada sabor para un mes de 2026.
5. Calcula el plan de compras de insumos según el stock, los días de entrega y la vida útil.
6. Exporta los resultados y gráficos.

## Alcance

Primera versión: una heladería, pronóstico mensual y sabores con historial de ventas. Quedan fuera los precios y costos, el clima, los sabores nuevos y el pronóstico diario.

## Estado

En desarrollo.