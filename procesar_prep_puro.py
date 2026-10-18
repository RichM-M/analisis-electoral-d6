"""Consolida los resultados del PREP (diputaciones federales 2015, 2018, 2021 y 2024)
a nivel SECCION ELECTORAL para LA MAGDALENA CONTRERAS y ALVARO OBREGON.

Los votos de partidos, coaliciones, candidaturas independientes, nulos y no registrados
se conservan tal cual vienen en cada PREP (sin agrupar en bloques politicos).
"""

import io
import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DESCARGAS = Path.home() / "Downloads"

CATALOGO_PATH = DESCARGAS / "listado_colonias_secciones_alcaldia.csv"
CATALOGO_INE_PATH = BASE_DIR / "catalogo_ine" / "20240503_CORTE_CASILLAS_PEF24.xlsx"
COLONIAS_EXTRA_PATH = BASE_DIR / "colonias_secciones_faltantes.csv"  # secciones sin colonia en el listado
PREP_PATHS = {
    2015: DESCARGAS / "DIP_FED_2015.csv",
    2018: DESCARGAS / "DIP_FED_2018.csv",
    2021: DESCARGAS / "DIP_FED_2021.csv",
    2024: BASE_DIR / "prep_2024_nuevo" / "DIP_FED_2024.csv",  # descarga oficial del 20240603_2005
}
SALIDA = BASE_DIR / "PREP_PURO_CONSOLIDADO_DISTRITO6.csv"
PARTICIPACION_SALIDA = BASE_DIR / "PARTICIPACION_PREP_OFICIAL.csv"

# Columna de total de votos calculados en cada PREP (incluye nulos y no registradas)
TOTAL_COL = {
    2015: "TOTAL_VOTOS",
    2018: "TOTAL_VOTOS_CALCULADO",
    2021: "TOTAL_VOTOS_CALCULADOS",
    2024: "TOTAL_VOTOS_CALCULADO",
}

ALCALDIAS_OBJETIVO = ["LA MAGDALENA CONTRERAS", "ALVARO OBREGON"]
# Columna y valor que identifican a la Ciudad de Mexico en cada PREP.
# En 2015 la columna ID_ESTADO trae el nombre del estado, no la clave.
FILTRO_ENTIDAD = {
    2015: ("ESTADO", "DISTRITO FEDERAL"),
    2018: ("ID_ESTADO", "9"),
    2021: ("ID_ESTADO", "9"),
    2024: ("ID_ENTIDAD", "9"),
}

# Etiquetas de TIPO_ACTA que corresponden a representacion proporcional (RP).
# 2015 y 2018 no traen una etiqueta RP identificable en TIPO_ACTA, por eso no aparecen aqui.
ACTAS_RP = {
    2021: {"DIPUTADOS RP"},
    2024: {"4ERP"},
}

# Columnas de votos tal cual aparecen en cada PREP (nombres originales)
COLUMNAS_VOTOS = {
    2015: [
        "PAN", "PRI", "PRD", "PVEM", "PT", "MOVIMIENTO_CIUDADANO", "NUEVA_ALIANZA", "MORENA",
        "PARTIDO_HUMANISTA", "ENCUENTRO_SOCIAL", "PRI_PVEM", "PRD_PT", "CAND_IND_1", "CAND_IND_2",
        "NO_REGISTRADOS", "NULOS",
    ],
    2018: [
        "PAN", "PRI", "PRD", "PVEM", "PT", "MC", "PANAL", "MORENA", "PES",
        "C_PAN_PRD_MC", "C_PAN_PRD", "C_PAN_MC", "C_PRD_MC", "C_PRI_PVEM_PANAL", "C_PRI_PVEM",
        "C_PRI_PANAL", "C_PVEM_PANAL", "C_PT_MORENA_PES", "C_PT_MORENA", "C_PT_PES", "C_MORENA_PES",
        "CAND_IND_01", "CAND_IND_02", "NO_REGISTRADOS", "NULOS",
    ],
    2021: [
        "PAN", "PRI", "PRD", "PVEM", "PT", "MC", "MORENA", "PES", "RSP", "FXM",
        "CAND_IND_1", "CAND_IND_2", "CAND_IND_3",
        "PAN-PRI-PRD", "PAN-PRI", "PAN-PRD", "PRI-PRD", "PVEM-PT-MORENA", "PVEM-PT",
        "PVEM-MORENA", "PT-MORENA", "NO_REGISTRADOS", "NULOS",
    ],
    2024: [
        "PAN", "PRI", "PRD", "PVEM", "PT", "MC", "MORENA", "CI_01", "CI_02",
        "PAN-PRI-PRD", "PAN-PRI", "PAN-PRD", "PRI-PRD", "PVEM_PT_MORENA", "PVEM_PT",
        "PVEM_MORENA", "PT_MORENA", "NO_REGISTRADAS", "NULOS",
    ],
}


def quitar_acentos(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c))


def normalizar_columna(nombre):
    return re.sub(r"\s+", "_", quitar_acentos(nombre).strip().upper())


def normalizar_texto(texto):
    return re.sub(r"\s+", " ", quitar_acentos(texto).strip().upper())


def leer_texto(ruta):
    bruto = ruta.read_bytes()
    try:
        return bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        return bruto.decode("cp1252", errors="replace")


def leer_csv_prep(ruta):
    # Los PREP traen metadatos al inicio (sep=, hora, titulo) y a veces fines de linea CR.
    # Se parte por CR, LF o CRLF y se toma desde la fila de encabezado de casillas.
    lineas = re.split(r"\r\n|\r|\n", leer_texto(ruta))
    encabezado = next(
        (i for i, linea in enumerate(lineas)
         if "SECCION" in linea.upper() and "CASILLA" in linea.upper()),
        None,
    )
    if encabezado is None:
        raise ValueError(f"No se encontro el encabezado de casillas en {ruta.name}")
    separador = "|" if "|" in lineas[encabezado] else ","
    cuerpo = "\n".join(lineas[encabezado:])
    # index_col=False: algunas filas traen un separador final de mas y pandas, sin esto,
    # tomaria la primera columna como indice y correria todas las demas.
    df = pd.read_csv(io.StringIO(cuerpo), sep=separador, dtype=str, index_col=False,
                     keep_default_na=False, low_memory=False)
    df.columns = [normalizar_columna(c) for c in df.columns]
    return df


def cargar_catalogo_colonias():
    texto = leer_texto(CATALOGO_PATH)
    cat = pd.read_csv(io.StringIO(texto), dtype=str, keep_default_na=False)
    cat.columns = [normalizar_columna(c) for c in cat.columns]
    cat = cat.rename(columns={"SECCION_ELECTORAL": "SECCION"})
    cat["ALCALDIA"] = cat["ALCALDIA"].map(normalizar_texto)
    cat["COLONIA"] = cat["COLONIA"].str.strip()
    cat["SECCION"] = pd.to_numeric(cat["SECCION"].str.strip(), errors="coerce")
    cat = cat.dropna(subset=["SECCION"]).astype({"SECCION": int})
    cat = cat[cat["ALCALDIA"].isin(ALCALDIAS_OBJETIVO)].copy()

    alcaldias_por_seccion = cat.groupby("SECCION")["ALCALDIA"].nunique()
    if (alcaldias_por_seccion > 1).any():
        raise ValueError("Hay secciones asignadas a mas de una alcaldia en el catalogo")

    return cat


def cargar_catalogo():
    """Secciones del distrito federal 6 (CDMX) con su alcaldia, segun el catalogo de casillas del INE.
    La colonia viene del listado de colonias; las secciones sin colonia quedan marcadas."""
    ine = pd.read_excel(CATALOGO_INE_PATH)
    ine.columns = [c.strip() for c in ine.columns]
    ine = ine[(ine["ESTADO"].astype(str).str.strip() == "9") & (ine["DISTRITO"].astype(int) == 6)]
    mapa = pd.DataFrame({
        "SECCION": ine["SECCION"].astype(int),
        "ALCALDIA": ine["NOMBRE_MUNICIPIO"].map(normalizar_texto),
    }).drop_duplicates()
    if mapa["SECCION"].duplicated().any():
        raise ValueError("Hay secciones con mas de una alcaldia en el catalogo del INE")

    colonias = cargar_catalogo_colonias()[["SECCION", "COLONIA"]].drop_duplicates("SECCION")
    extra = pd.read_csv(COLONIAS_EXTRA_PATH, encoding="utf-8-sig", dtype={"SECCION": int})
    colonias = pd.concat([colonias, extra[["SECCION", "COLONIA"]]], ignore_index=True).drop_duplicates("SECCION")
    cat = mapa.merge(colonias, on="SECCION", how="left")
    cat["COLONIA"] = cat["COLONIA"].fillna("SIN COLONIA EN CATALOGO")
    sin_colonia = sorted(set(mapa["SECCION"]) - set(colonias["SECCION"]))
    print(f"Catalogo INE: {len(cat)} secciones del distrito 6; sin colonia en el listado: {sin_colonia}")
    return cat


def procesar_anio(anio, ruta, mapa_alcaldia):
    df = leer_csv_prep(ruta)
    col_entidad, valor_entidad = FILTRO_ENTIDAD[anio]
    columnas_votos = COLUMNAS_VOTOS[anio]

    faltantes = [c for c in [col_entidad, "SECCION", "CONTABILIZADA", "LISTA_NOMINAL",
                             TOTAL_COL[anio], *columnas_votos] if c not in df.columns]
    if faltantes:
        raise KeyError(f"{ruta.name}: faltan columnas {faltantes}")

    df = df[[col_entidad, "SECCION", "CONTABILIZADA", "LISTA_NOMINAL", TOTAL_COL[anio],
             *columnas_votos, *(["TIPO_ACTA"] if anio in ACTAS_RP else [])]].copy()
    entidad = df[col_entidad].map(normalizar_texto).str.lstrip("0")
    df = df[entidad == valor_entidad]

    # Actas de representacion proporcional (RP) de casillas especiales: no son parte de la
    # votacion de mayoria relativa que publica el PREP por partido, se excluyen.
    if anio in ACTAS_RP:
        es_rp = df["TIPO_ACTA"].map(normalizar_texto).isin(ACTAS_RP[anio])
        print(f"   {anio}: {int(es_rp.sum())} actas RP excluidas")
        df = df[~es_rp]

    # Solo actas contabilizadas (CONTABILIZADA = 1, segun el README del PREP): es el corte oficial
    contabilizada = df["CONTABILIZADA"].str.strip() == "1"
    print(f"   {anio}: {int((~contabilizada).sum())} actas no contabilizadas excluidas")
    df = df[contabilizada]


    df["SECCION"] = pd.to_numeric(df["SECCION"].str.strip(), errors="coerce")
    df = df.dropna(subset=["SECCION"])
    df["SECCION"] = df["SECCION"].astype(int)

    # Solo secciones del catalogo objetivo; de paso se asigna ALCALDIA desde el catalogo
    df = df.merge(mapa_alcaldia, on="SECCION", how="inner")
    casillas = len(df)

    # Participacion como la publica el PREP: votos totales calculados / lista nominal
    df["LN_PREP"] = pd.to_numeric(df["LISTA_NOMINAL"].str.replace(",", "", regex=False).str.strip(),
                                  errors="coerce").fillna(0)
    df["VOTOS_PREP"] = pd.to_numeric(df[TOTAL_COL[anio]].str.replace(",", "", regex=False).str.strip(),
                                     errors="coerce").fillna(0)
    participacion = df.groupby("SECCION", as_index=False)[["LN_PREP", "VOTOS_PREP"]].sum()
    participacion.insert(0, "ANIO", anio)

    df[columnas_votos] = (
        df[columnas_votos]
        .apply(lambda s: pd.to_numeric(s.str.replace(",", "", regex=False).str.strip(),
                                       errors="coerce"))
        .fillna(0)
    )

    df["ANIO"] = anio
    agrupado = df.groupby(["ANIO", "ALCALDIA", "SECCION"], as_index=False)[columnas_votos].sum()

    largo = agrupado.melt(
        id_vars=["ANIO", "ALCALDIA", "SECCION"],
        value_vars=columnas_votos,
        var_name="PARTIDO_COALICION",
        value_name="VOTOS",
    )
    largo["VOTOS"] = largo["VOTOS"].astype(int)
    return largo, casillas, participacion


def main():
    catalogo = cargar_catalogo()
    mapa_alcaldia = catalogo[["SECCION", "ALCALDIA"]].drop_duplicates()
    secciones_objetivo = set(mapa_alcaldia["SECCION"])
    print(f"Catalogo: {len(secciones_objetivo)} secciones unicas en {ALCALDIAS_OBJETIVO}")

    partes = []
    partes_participacion = []
    resumen_casillas = {}
    for anio, ruta in PREP_PATHS.items():
        largo, casillas, participacion = procesar_anio(anio, ruta, mapa_alcaldia)
        partes.append(largo)
        partes_participacion.append(participacion)
        resumen_casillas[anio] = casillas
        vistas = set(largo["SECCION"])
        no_vistas = sorted(secciones_objetivo - vistas)
        print(f"{anio}: {casillas} casillas en secciones objetivo; "
              f"secciones del catalogo sin casillas en el PREP: {len(no_vistas)}")
        if no_vistas:
            print(f"   {no_vistas}")

    consolidado = pd.concat(partes, ignore_index=True)

    # Cruce con el catalogo: COLONIA/UT por seccion (una fila por seccion para no duplicar votos)
    colonias = (
        catalogo.groupby("SECCION")["COLONIA"]
        .agg(lambda s: " | ".join(sorted(set(s))))
        .rename("COLONIA")
        .reset_index()
    )
    consolidado = consolidado.merge(colonias, on="SECCION", how="left")

    consolidado["VOTOS"] = consolidado["VOTOS"].fillna(0).astype(int)
    consolidado = consolidado[
        ["ANIO", "ALCALDIA", "SECCION", "COLONIA", "PARTIDO_COALICION", "VOTOS"]
    ].sort_values(["ANIO", "ALCALDIA", "SECCION"], kind="stable").reset_index(drop=True)

    consolidado.to_csv(SALIDA, index=False, encoding="utf-8-sig")

    # Participacion oficial por seccion y anio: votos totales / lista nominal de casillas contabilizadas
    participacion = pd.concat(partes_participacion, ignore_index=True)
    participacion = participacion.rename(columns={"LN_PREP": "LISTA_NOMINAL_PREP",
                                                  "VOTOS_PREP": "VOTOS_TOTALES_PREP"})
    participacion["PARTICIPACION_PREP_PCT"] = (
        participacion["VOTOS_TOTALES_PREP"] / participacion["LISTA_NOMINAL_PREP"] * 100
    ).where(participacion["LISTA_NOMINAL_PREP"] > 0).round(2)
    participacion.to_csv(PARTICIPACION_SALIDA, index=False, encoding="utf-8-sig")
    print("\nParticipacion PREP por anio (lista nominal de casillas contabilizadas):")
    resumen = participacion.groupby("ANIO")[["LISTA_NOMINAL_PREP", "VOTOS_TOTALES_PREP"]].sum()
    resumen["PARTICIPACION_PCT"] = (resumen["VOTOS_TOTALES_PREP"] / resumen["LISTA_NOMINAL_PREP"] * 100).round(4)
    print(resumen.to_string())

    print("\n=== Verificacion ===")
    print("Secciones unicas procesadas por ANIO y ALCALDIA:")
    secciones = (
        consolidado.groupby(["ANIO", "ALCALDIA"])["SECCION"].nunique().reset_index()
    )
    print(secciones.to_string(index=False))
    print("\nSuma total de votos por ANIO:")
    print(consolidado.groupby("ANIO")["VOTOS"].sum().to_string())
    print(f"\nFilas en el CSV final: {len(consolidado)}")
    print(f"Archivo guardado: {SALIDA}")


if __name__ == "__main__":
    main()
