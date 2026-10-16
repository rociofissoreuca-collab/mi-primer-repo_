import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from heladeria import Heladeria
from main import App


class TestMenu(unittest.TestCase):

    def test_una_sesion_con_entradas_invalidas_no_rompe_la_app(self):
        respuestas = iter(["9", "1", "2", "3", "4", "13", "4", "abc", "4", "12", "5", "1", "6", "0"])
        with tempfile.TemporaryDirectory() as carpeta:
            app = App(Heladeria(RAIZ / "data"), entrada=lambda mensaje: "" if "Enter" in mensaje else next(respuestas),
                      carpeta_salidas=carpeta)
            salida = io.StringIO()
            with redirect_stdout(salida):
                app.ejecutar()
            archivos = sorted(ruta.name for ruta in Path(carpeta).iterdir())
        texto = salida.getvalue()
        self.assertIn("Opción inválida", texto)
        self.assertIn("El mes tiene que ser", texto)
        self.assertIn("¡Hasta luego!", texto)
        self.assertEqual(len(archivos), 7)


if __name__ == "__main__":
    unittest.main()