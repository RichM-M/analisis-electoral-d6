"""Ejecuta el procesamiento completo en orden:

1. procesar_participacion_historica.py  -> data/processed/PARTICIPACION_HISTORICA_DISTRITO6.csv
2. procesar_prep_puro.py                -> data/processed/PREP_PURO_CONSOLIDADO_DISTRITO6.csv
                                           data/processed/PARTICIPACION_PREP_OFICIAL.csv
3. generar_json_web.py                  -> docs/datos_electorales.json
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
PASOS = [
    "procesar_participacion_historica.py",
    "procesar_prep_puro.py",
    "generar_json_web.py",
]


def main():
    for paso in PASOS:
        print(f"\n=== {paso} ===", flush=True)
        resultado = subprocess.run([sys.executable, str(SCRIPTS / paso)])
        if resultado.returncode != 0:
            sys.exit(f"El paso {paso} termino con error ({resultado.returncode}).")
    print("\nProcesamiento completo.")


if __name__ == "__main__":
    main()
