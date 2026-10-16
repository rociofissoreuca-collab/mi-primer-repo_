import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from heladeria import Heladeria


class TestHeladeria(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.heladeria = Heladeria(RAIZ / "data")

    def test_caso_normal_dos_años_de_ventas(self):
        self.assertEqual(self.heladeria.años(), [2024, 2025])
        tabla = self.heladeria.kg_por_mes(2025)
        self.assertEqual(list(tabla.index), list(range(1, 13)))

    def test_el_verano_vende_mas_que_el_invierno(self):
        indice = self.heladeria.estacionalidad()["indice"]
        self.assertGreater(indice["diciembre"], 1)
        self.assertLess(indice["julio"], 1)
        self.assertAlmostEqual(indice.mean(), 1, places=2)

    def test_la_participacion_del_ranking_suma_uno(self):
        ranking = self.heladeria.ranking_sabores(2025)
        self.assertAlmostEqual(ranking["participacion"].sum(), 1, places=2)

    def test_los_cortes_de_luz_no_cuentan_en_la_tasa_de_merma(self):
        tasa = self.heladeria.tasa_merma()
        self.assertTrue(((tasa >= 0) & (tasa < 1)).all())
        self.assertEqual(tasa.idxmax(), "menta granizada")

    def test_año_sin_datos(self):
        with self.assertRaises(ValueError):
            self.heladeria.kg_por_mes(2023)

    def test_modificar_la_copia_no_cambia_la_heladeria(self):
        copia = self.heladeria.ventas
        copia["kg"] = 0
        self.assertGreater(self.heladeria.ventas["kg"].sum(), 0)


if __name__ == "__main__":
    unittest.main()