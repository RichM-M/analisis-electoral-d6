"""Genera docs/datos_electorales.json, el archivo que consume el tablero web, a partir de
los CSV de data/processed/.

Estructura:
  secciones:     lista de secciones unicas con alcaldia y colonia
  resultados_prep: { anio: { seccion: [ {partido, votos}, ... ] } }
  participacion: { anio: { seccion: {lista_nominal, votantes, no_votantes, pct_part,
                                     genero: {hombres, mujeres, pct_mujeres, no_votantes_hombres, no_votantes_mujeres},
                                     grupos_edad: {jovenes_18_29, adultos_30_64, mayores_65}} } }

El JSON se escribe compacto (sin espacios ni saltos de linea) para que pese menos.
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROCESADOS = RAIZ / "data" / "processed"
PREP_CSV = PROCESADOS / "PREP_PURO_CONSOLIDADO_DISTRITO6.csv"
PARTICIPACION_CSV = PROCESADOS / "PARTICIPACION_HISTORICA_DISTRITO6.csv"
PARTICIPACION_PREP_CSV = PROCESADOS / "PARTICIPACION_PREP_OFICIAL.csv"
SALIDA = RAIZ / "docs" / "datos_electorales.json"

COLUMNAS_DESGLOSE = [
    "Votantes_Hombres", "Votantes_Mujeres",
    "No_Votantes_Hombres", "No_Votantes_Mujeres",
    "Votantes_Jovenes_18_29", "Votantes_Adultos_30_64", "Votantes_Mayores_65",
]


def valor_o_none(valor):
    return None if pd.isna(valor) else valor


def main():
    prep = pd.read_csv(PREP_CSV, encoding="utf-8-sig", keep_default_na=False)
    part = pd.read_csv(PARTICIPACION_CSV, encoding="utf-8-sig")

    # Secciones unicas con su alcaldia y colonia (tomadas de ambos CSV)
    catalogo = pd.concat([
        prep[["SECCION", "ALCALDIA", "COLONIA"]],
        part[["SECCION", "ALCALDIA", "COLONIA"]],
    ]).drop_duplicates("SECCION").sort_values(["ALCALDIA", "SECCION"])
    secciones = [
        {"seccion": int(r.SECCION), "alcaldia": r.ALCALDIA, "colonia": r.COLONIA}
        for r in catalogo.itertuples(index=False)
    ]

    # Resultados PREP: partidos y coaliciones tal cual vienen en el CSV
    resultados_prep = {}
    for (anio, seccion), grupo in prep.groupby(["ANIO", "SECCION"]):
        resultados_prep.setdefault(str(int(anio)), {})[str(int(seccion))] = [
            {"partido": r.PARTIDO_COALICION, "votos": int(r.VOTOS)}
            for r in grupo.itertuples(index=False)
        ]

    # Participacion por seccion y anio, con desglose de genero y grupos de edad
    faltantes = [c for c in COLUMNAS_DESGLOSE if c not in part.columns]
    if faltantes:
        raise KeyError(f"Faltan columnas en {PARTICIPACION_CSV.name}: {faltantes}. "
                       "Vuelve a ejecutar procesar_participacion_historica.py")

    # Lista nominal, votantes y participacion vienen del PREP (actas contabilizadas);
    # el genero y los grupos de edad vienen de las estadisticas de participacion por seccion.
    part_prep = pd.read_csv(PARTICIPACION_PREP_CSV, encoding="utf-8-sig")
    part = part.merge(part_prep, on=["ANIO", "SECCION"], how="left")

    participacion = {}
    for r in part.itertuples(index=False):
        if pd.isna(r.LISTA_NOMINAL_PREP):
            continue  # seccion sin casillas en el PREP: no se muestra participacion
        hombres, mujeres = int(r.Votantes_Hombres), int(r.Votantes_Mujeres)
        ln = int(r.LISTA_NOMINAL_PREP)
        votos = int(r.VOTOS_TOTALES_PREP)
        participacion.setdefault(str(int(r.ANIO)), {})[str(int(r.SECCION))] = {
            "lista_nominal": ln,
            "votantes": votos,
            "no_votantes": ln - votos,
            "pct_part": valor_o_none(r.PARTICIPACION_PREP_PCT),
            "genero": {
                "hombres": hombres,
                "mujeres": mujeres,
                "pct_mujeres": round(mujeres / (hombres + mujeres) * 100, 2) if hombres + mujeres else None,
                "no_votantes_hombres": int(r.No_Votantes_Hombres),
                "no_votantes_mujeres": int(r.No_Votantes_Mujeres),
            },
            "grupos_edad": {
                "jovenes_18_29": int(r.Votantes_Jovenes_18_29),
                "adultos_30_64": int(r.Votantes_Adultos_30_64),
                "mayores_65": int(r.Votantes_Mayores_65),
            },
        }

    datos = {
        "secciones": secciones,
        "resultados_prep": resultados_prep,
        "participacion": participacion,
    }

    with SALIDA.open("w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

    print("datos_electorales.json generado correctamente")
    print(f"  Secciones unicas: {len(secciones)}")
    print(f"  Anios en resultados_prep: {sorted(resultados_prep)}")
    print(f"  Registros de resultados_prep (partido-seccion-anio): {len(prep)}")
    print(f"  Anios en participacion: {sorted(participacion)}")
    print(f"  Registros de participacion (seccion-anio): {len(part)}")
    print(f"  Tamano: {SALIDA.stat().st_size / 1024:.1f} KB")
    print(f"  Archivo: {SALIDA}")


if __name__ == "__main__":
    main()
