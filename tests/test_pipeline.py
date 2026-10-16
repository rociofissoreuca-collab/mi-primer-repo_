import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from fuentes import FuenteCSV
from pipeline import (es_fecha_existente, leer_tablas, limpiar_registros, normalizar_campos, preparar_datos,
                      tiene_formato_fecha, validar_esquema, verificar_catalogos)

DATOS = RAIZ / "data"


class TestFechas(unittest.TestCase):

    def test_la_regex_controla_solo_el_formato(self):
        self.assertTrue(tiene_formato_fecha("2025-12-31"))
        self.assertTrue(tiene_formato_fecha("2025-02-30"))
        self.assertFalse(tiene_formato_fecha("15/03/2024"))
        self.assertFalse(tiene_formato_fecha("2025-1-5"))

    def test_el_calendario_completa_lo_que_la_regex_no_ve(self):
        self.assertTrue(es_fecha_existente("2024-02-29"))
        self.assertFalse(es_fecha_existente("2025-02-29"))
        self.assertFalse(es_fecha_existente("2025-02-30"))
        self.assertFalse(es_fecha_existente("2024-13-05"))


class TestLimpieza(unittest.TestCase):

    def setUp(self):
        self.tabla = pd.DataFrame({
            "fecha": ["2025-01-10", "2025-01-10", "2025-02-30", "2025-01-11", "2025-01-12", "2025-01-13", None],
            "sabor": ["limón", "limón", "limón", "limón", "chocolate suizo", "limón", "limón"],
            "kg": [3.0, 3.0, 2.0, -1.0, 2.0, 500.0, 1.0],
        })

    def test_cada_fila_invalida_se_rechaza_con_su_motivo(self):
        validas, rechazos = limpiar_registros(self.tabla, {"limón"}, ["fecha", "sabor"])
        self.assertEqual(len(validas), 1)
        self.assertEqual(sorted(rechazos["motivo_rechazo"]), sorted([
            "registro duplicado", "fecha inexistente", "kg no numérico o no positivo",
            "sabor sin receta", "kg fuera de rango (más de 100)", "dato faltante",
        ]))

    def test_no_se_pierden_filas(self):
        validas, rechazos = limpiar_registros(self.tabla, {"limón"}, ["fecha", "sabor"])
        self.assertEqual(len(validas) + len(rechazos), len(self.tabla))

    def test_normalizar_no_modifica_la_tabla_original(self):
        original = pd.DataFrame({"sabor": ["  Dulce de LECHE "]})
        normalizada = normalizar_campos(original, ["sabor"])
        self.assertEqual(normalizada["sabor"][0], "dulce de leche")
        self.assertEqual(original["sabor"][0], "  Dulce de LECHE ")

    def test_esquema_con_columnas_faltantes(self):
        with self.assertRaises(ValueError):
            validar_esquema(pd.DataFrame({"fecha": ["2025-01-01"]}), "ventas")


class TestFlujoCompleto(unittest.TestCase):

    def test_caso_normal_con_los_datos_del_repositorio(self):
        tablas, rechazos = preparar_datos(DATOS)
        crudas = FuenteCSV(DATOS / "ventas.csv").cargar()
        self.assertEqual(len(tablas["ventas"]) + (rechazos["tabla"] == "ventas").sum(), len(crudas))
        self.assertEqual(len(rechazos), 8)
        self.assertTrue((tablas["ventas"]["kg"] > 0).all())
        self.assertFalse(tablas["ventas"].duplicated(["fecha", "sabor"]).any())
        self.assertIn("dulce de leche", set(tablas["ventas"]["sabor"]))

    def test_carpeta_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            leer_tablas(DATOS / "no_existe")

    def test_receta_con_insumo_desconocido(self):
        tablas = leer_tablas(DATOS)
        recetas = pd.concat([tablas["recetas"], pd.DataFrame([{"sabor": "limón", "insumo": "kiwi", "cantidad_por_kg": 0.1}])])
        with self.assertRaises(ValueError):
            verificar_catalogos(recetas, tablas["insumos"])

    def test_carpeta_a_la_que_le_falta_un_archivo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            (Path(carpeta) / "ventas.csv").write_text("fecha,sabor,kg\n", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                leer_tablas(carpeta)


if __name__ == "__main__":
    unittest.main()