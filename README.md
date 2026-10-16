# Planificador de producción y compras para una heladería

**Autora:** Rocío Fissore · Programación Orientada a Datos · UCA · Trabajo Práctico 2

## Problema, usuario y solución

Una heladería artesanal decide cuánto helado producir y cuántos insumos comprar a partir de la experiencia del encargado. La demanda es muy estacional (en diciembre se vende unas cinco veces lo de julio) y muchos insumos son perecederos: si se produce o se compra de más, la mercadería se pierde; si se produce de menos, faltan sabores.

**Usuario:** el dueño o encargado de producción, que planifica cada mes qué producir y qué pedir a los proveedores.

**Pregunta que responde:** ¿cuántos kilos de cada sabor conviene producir y cuánto de cada insumo conviene comprar en cada mes de 2026, según las ventas de 2024 y 2025, el consumo de insumos y la estacionalidad de la demanda?

**Solución:** una aplicación de consola que lee y limpia los datos de la heladería y calcula:

1. **Demanda** de cada sabor = kg vendidos en el mismo mes de 2025 × (1 + crecimiento del sabor entre 2024 y 2025).
2. **Producción** = demanda + merma habitual del sabor.
3. **Consumo de insumos** = producción × receta.
4. **Compras** = consumo + stock de seguridad − stock disponible. El stock de seguridad cubre los días que tarda el proveedor más 2 días de margen. Los insumos perecederos se piden en varias veces dentro del mes, según su vida útil.

## Instalación y uso

Se necesita Python 3. Desde la carpeta del proyecto:

```bash
pip install -r requirements.txt
python src/main.py                     # abre el menú
python -m unittest discover tests      # corre las pruebas
python data/generar_datos.py           # (opcional) vuelve a generar los datos
```

Opciones del menú:

1. Ver la carga de datos y las filas rechazadas.
2. Ver la estacionalidad y el ranking de sabores.
3. Validar el método de pronóstico.
4. Producción de cada sabor para un mes de 2026.
5. Compras de insumos para un mes de 2026.
6. Exportar resultados y gráficos a `outputs/`.
0. Salir.

Al iniciar, la aplicación guarda las filas rechazadas en `outputs/rechazos.csv`. Si se escribe una opción o un mes inválido, muestra un aviso y vuelve al menú.

## Datos

Los datos son **simulados** con `data/generar_datos.py`, con semilla fija, así que se obtienen siempre los mismos archivos. Representan dos años (2024 y 2025) de una heladería con 14 sabores y 14 insumos. Licencia CC BY 4.0, sin información personal.

- `ventas.csv` (unidad de análisis: los kg vendidos de un sabor en un día, 9.763 filas)
- `merma.csv` (helado que se tiró y el motivo)
- `recetas.json` (insumos de cada sabor por kg de helado)
- `insumos.json` (stock, días de entrega y vida útil de cada insumo)
- `muestra_ventas.csv` y `muestra_ventas.json` (las mismas 60 ventas en los dos formatos)

La procedencia, las variables y las limitaciones de los datos están en [`data/README.md`](data/README.md).

## Organización del código

```
src/
  main.py        menú de consola (clase App)
  fuentes.py     FuenteDatos con cargar(), y sus implementaciones FuenteCSV y FuenteJSON
  pipeline.py    leer, validar el esquema, normalizar, limpiar y registrar rechazos
  heladeria.py   clase Heladeria: datos limpios, estacionalidad, ranking y tasa de merma
  pronostico.py  clase Pronostico: demanda, producción, insumos, compras y validación
  graficos.py    gráficos con matplotlib
tests/           pruebas con unittest
data/            datos, generador y documentación de los datos
outputs/         resultados (no se suben: se generan con la opción 6)
```

- **Herencia:** `FuenteCSV` y `FuenteJSON` heredan de la clase abstracta `FuenteDatos` y cada una implementa `cargar()` para su formato. `fuente_para(ruta)` elige la clase según la extensión, así el resto del programa no depende del formato del archivo.
- **Expresión regular:** `PATRON_FECHA = r"\d{4}-\d{2}-\d{2}"` valida que la fecha tenga el formato AAAA-MM-DD. Como acepta fechas imposibles como `2025-02-30`, se complementa con `datetime` para comprobar que la fecha exista en el calendario.
- **Encapsulamiento:** los datos de `Heladeria` se guardan con guion bajo (`_ventas`) y se leen con `@property`, que devuelve una copia.

## Decisiones de limpieza

Las ventas y la merma pasan por estas reglas en orden. Cada fila rechazada se guarda con su motivo en `outputs/rechazos.csv`:

1. Faltan la fecha, el sabor o los kg.
2. La fecha no tiene el formato AAAA-MM-DD (expresión regular).
3. La fecha no existe en el calendario.
4. Los kg no son un número mayor que 0.
5. Más de 100 kg de un sabor en un día (fuera de rango).
6. El sabor no tiene receta.
7. Fila repetida para la misma fecha y sabor (se conserva la primera).

Antes de validar, los textos se pasan a minúscula y sin espacios en los extremos. Los catálogos (recetas e insumos) no se limpian: si tienen un error, la carga se frena con un mensaje, porque sin ellos no se puede calcular el pronóstico. Los días sin ventas no se completan con cero. La merma por corte de luz no se cuenta en la merma de cada sabor, porque es un accidente.

Con los datos del repositorio se rechazan 8 filas, una por cada tipo de error incluido a propósito.

## Ejemplo de resultado

**Validación (opción 3).** Se pronosticó julio a diciembre de 2025 usando solo los datos anteriores y se comparó con lo vendido. El método se equivocó un **3,9 %**; repetir el año anterior se equivocaba un **8,6 %**.

**Producción de diciembre de 2026 (opción 4), primeros sabores:**

```
                          demanda  merma_esperada  produccion
dulce de leche granizado    513.2            15.4       528.6
dulce de leche              472.4             9.4       481.8
tramontana                  336.4            10.1       346.5
...
Total a producir: 3,625.8 kg
⚠ menta granizada: en los últimos meses cae más que en el resto del año (6 puntos de diferencia). Revisá su producción.
```

**Compras de enero de 2026 (opción 5), primeros insumos:**

```
          unidad  consumo  stock_inicial   compra  pedidos
leche     litros  1405.52           60.0  1481.54        4
crema     litros   585.24           25.0   616.88        3
frutilla      kg   175.94            6.0   186.97        8
...
```

## Interpretación

En enero conviene comprar unos 1.480 litros de leche repartidos en 4 pedidos, porque dura 10 días, y unos 187 kg de frutilla en 8 pedidos, porque dura 4. El error de validación indica cuánto confiar en estos números: en promedio, el pronóstico se aleja un 4 % de lo que se vende. Los resultados son una guía para decidir, no una decisión automática.

## Limitaciones

- El método supone que la tendencia de cada sabor se mantiene. Si cambia, el error aumenta: la menta granizada, cuya caída se aceleró en el segundo semestre de 2025, tuvo un error del 14,7 %. Para esos casos la aplicación muestra un aviso, y conviene volver a correr el pronóstico cada mes con los datos nuevos.
- Los sabores sin ventas en el año anterior (el maracuyá, que empezó en 2025) quedan fuera del pronóstico.
- Con dos años de datos, el crecimiento se mide con una sola comparación entre años.
- Los datos son simulados: muestran el método, no una heladería real. Con datos reales el error probablemente sería mayor.
- Fuera del alcance de esta versión: precios y costos, clima, sabores nuevos y pronóstico diario.