"""Participacion ciudadana por seccion electoral (2015, 2018, 2021 y 2024) para el
distrito federal 6 de la Ciudad de Mexico, desglosada por sexo y grupo de edad.

Entradas:  data/raw/participacion/ (votantes, no votantes y lista nominal por seccion)
           data/raw/catalogos/
Salida:    data/processed/PARTICIPACION_HISTORICA_DISTRITO6.csv
"""

import io
import re
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CATALOGOS = RAIZ / "data" / "raw" / "catalogos"
PART_DIR = RAIZ / "data" / "raw" / "participacion"
PROCESADOS = RAIZ / "data" / "processed"

CATALOGO_PATH = CATALOGOS / "listado_colonias_secciones_alcaldia.csv"
CATALOGO_INE_PATH = CATALOGOS / "20240503_CORTE_CASILLAS_PEF24.xlsx"
COLONIAS_EXTRA_PATH = CATALOGOS / "colonias_secciones_faltantes.csv"  # secciones sin colonia en el listado
SALIDA = PROCESADOS / "PARTICIPACION_HISTORICA_DISTRITO6.csv"

ALCALDIAS_OBJETIVO = ["LA MAGDALENA CONTRERAS", "ALVARO OBREGON"]
ID_CDMX = 9

# Grupos de edad: jovenes (18 a 29), adultos (30 a 64) y mayores (65 o mas)
JOVENES = {"1819", "2024", "2529"}
ADULTOS = {"3034", "3539", "4044", "4549", "5054", "5559", "6064"}
MAYORES = "65MAS"

ARCHIVOS = {
    2015: {
        "votantes": PART_DIR / "votantes_participacion2015_sec.csv",
        "no_votantes": PART_DIR / "no_votantes_participacion2015_sec.csv",
        "lista_nominal": PART_DIR / "ln_20150415_ajustada_sec.csv",
    },
    2018: {
        "votantes": PART_DIR / "part2018peVotoSec.xlsx",
        "no_votantes": PART_DIR / "part2018peNoVotoSec.xlsx",
        "lista_nominal": PART_DIR / "part2018peListaNominalSec.xlsx",
    },
    2021: {
        "votantes": PART_DIR / "part2021peVotoSec.xlsx",
        "no_votantes": PART_DIR / "part2021peNoVotoSec.xlsx",
        "lista_nominal": PART_DIR / "part2021peListaNominalSec.xlsx",
    },
    2024: {
        "votantes": PART_DIR / "VotantesSEC.xlsx",
        "no_votantes": PART_DIR / "NoVotantesSEC.xlsx",
        "lista_nominal": PART_DIR / "LnSEC.xlsx",
    },
}


def quitar_acentos(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c))


def norm(texto):
    return re.sub(r"\s+", " ", quitar_acentos(texto).strip().upper())


def leer_texto(ruta):
    bruto = ruta.read_bytes()
    try:
        return bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        return bruto.decode("cp1252", errors="replace")


def leer_tabla(ruta):
    if ruta.suffix.lower() == ".csv":
        lineas = re.split(r"\r\n|\r|\n", leer_texto(ruta))
        df = pd.read_csv(io.StringIO("\n".join(lineas)), sep=",", dtype=str,
                         index_col=False, keep_default_na=False)
    else:
        # En los xlsx de 2024 hay filas de titulo antes del encabezado: se busca la fila
        # cuya celda empieza con SEC (Seccion Electoral / SEC).
        bruto = pd.read_excel(ruta, header=None)
        fila = next(
            i for i, valores in enumerate(bruto.itertuples(index=False))
            if any(isinstance(v, str) and norm(v).startswith("SEC") for v in valores)
        )
        df = pd.read_excel(ruta, header=fila)
    df.columns = [norm(c) for c in df.columns]
    return df


def parse_columna(nombre):
    """Devuelve (sexo, grupo_edad) para columnas de conteo; None si no lo es.

    Acepta el formato codificado (H1819, M65MAS) y el formato largo de 2024
    ('Votantes Hombres de 18 - 19 anos', 'No Votantes No Binarios 65 anos y mas').
    """
    n = norm(nombre)
    m = re.match(r"^([HM])(\d{4}|65MAS)$", n)
    if m:
        return m.group(1), m.group(2)
    if "HOMBRE" in n or "MUJER" in n or "BINARIO" in n:
        sexo = "H" if "HOMBRE" in n else "M" if "MUJER" in n else "NB"
        if re.search(r"\b65\b", n):
            return sexo, "65MAS"
        m = re.search(r"(\d{2})\s*-\s*(\d{2})", n)
        if m:
            return sexo, m.group(1) + m.group(2)
    return None


def cargar_catalogo_colonias():
    cat = pd.read_csv(io.StringIO(leer_texto(CATALOGO_PATH)), dtype=str, keep_default_na=False)
    cat.columns = [norm(c).replace(" ", "_") for c in cat.columns]
    cat = cat.rename(columns={"SECCION_ELECTORAL": "SECCION"})
    cat["ALCALDIA"] = cat["ALCALDIA"].map(norm)
    cat["COLONIA"] = cat["COLONIA"].str.strip()
    cat["SECCION"] = pd.to_numeric(cat["SECCION"].str.strip(), errors="coerce")
    cat = cat.dropna(subset=["SECCION"]).astype({"SECCION": int})
    cat = cat[cat["ALCALDIA"].isin(ALCALDIAS_OBJETIVO)].copy()
    if (cat.groupby("SECCION")["ALCALDIA"].nunique() > 1).any():
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
        "ALCALDIA": ine["NOMBRE_MUNICIPIO"].map(norm),
    }).drop_duplicates()
    if mapa["SECCION"].duplicated().any():
        raise ValueError("Hay secciones con mas de una alcaldia en el catalogo del INE")

    colonias = cargar_catalogo_colonias()[["SECCION", "COLONIA"]].drop_duplicates("SECCION")
    extra = pd.read_csv(COLONIAS_EXTRA_PATH, encoding="utf-8-sig", dtype={"SECCION": int})
    colonias = pd.concat([colonias, extra[["SECCION", "COLONIA"]]], ignore_index=True).drop_duplicates("SECCION")
    cat = mapa.merge(colonias, on="SECCION", how="left")
    cat["COLONIA"] = cat["COLONIA"].fillna("SIN COLONIA EN CATALOGO")
    return cat


def resumen_archivo(ruta, prefijo):
    """Suma por seccion: TOTAL, HOMBRES, MUJERES, NO_BINARIOS, JOVENES y, si existe,
    el total reportado por el propio archivo (para validar)."""
    df = leer_tabla(ruta)

    col_sec = next(c for c in df.columns if c.startswith("SEC"))
    col_del = next((c for c in df.columns if re.match(r"^(DEL$|NOMBRE_DEM|DEMARCACION)", c)), None)
    if "ENT" in df.columns:
        df = df[pd.to_numeric(df["ENT"], errors="coerce") == ID_CDMX]

    df = df.assign(SECCION=pd.to_numeric(df[col_sec].astype(str).str.strip(), errors="coerce"))
    df = df.dropna(subset=["SECCION"])
    df["SECCION"] = df["SECCION"].astype(int)

    conteo = {c: parse_columna(c) for c in df.columns if parse_columna(c)}
    for c in conteo:
        df[c] = pd.to_numeric(
            df[c].astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce"
        ).fillna(0)

    cols_h = [c for c, v in conteo.items() if v[0] == "H"]
    cols_m = [c for c, v in conteo.items() if v[0] == "M"]
    cols_nb = [c for c, v in conteo.items() if v[0] == "NB"]
    cols_j = [c for c, v in conteo.items() if v[1] in JOVENES]
    cols_a = [c for c, v in conteo.items() if v[1] in ADULTOS]
    cols_y = [c for c, v in conteo.items() if v[1] == MAYORES]

    out = pd.DataFrame({"SECCION": df["SECCION"].to_numpy()})
    out["TOTAL"] = df[list(conteo)].sum(axis=1).to_numpy()
    out["HOMBRES"] = df[cols_h].sum(axis=1).to_numpy()
    out["MUJERES"] = df[cols_m].sum(axis=1).to_numpy()
    out["NO_BINARIOS"] = df[cols_nb].sum(axis=1).to_numpy() if cols_nb else 0
    out["JOVENES"] = df[cols_j].sum(axis=1).to_numpy()
    out["ADULTOS"] = df[cols_a].sum(axis=1).to_numpy()
    out["MAYORES"] = df[cols_y].sum(axis=1).to_numpy()
    out["DEL"] = df[col_del].map(norm).to_numpy() if col_del else ""

    reportado = next((c for c in ("TOTAL", "TOTAL_VOTANTES", "LN_AJUSTADA") if c in df.columns), None)
    if reportado:
        out["TOTAL_REPORTADO"] = pd.to_numeric(
            df[reportado].astype(str).str.replace(",", "", regex=False), errors="coerce"
        ).fillna(0).to_numpy()

    duplicadas = out["SECCION"].duplicated().sum()
    if duplicadas:
        print(f"  aviso: {duplicadas} filas repetidas por seccion en {ruta.name}; se suman")

    agg = {c: "sum" for c in out.columns if c not in ("SECCION", "DEL")}
    agg["DEL"] = "first"
    out = out.groupby("SECCION", as_index=False).agg(agg)
    return out.rename(columns=lambda c: c if c == "SECCION" else f"{prefijo}_{c}")


def procesar_anio(anio, mapa_alcaldia, colonias):
    archivos = ARCHIVOS[anio]
    v = resumen_archivo(archivos["votantes"], "V")
    nv = resumen_archivo(archivos["no_votantes"], "NV")
    ln = resumen_archivo(archivos["lista_nominal"], "LN")

    df = ln.merge(v, on="SECCION", how="inner").merge(nv, on="SECCION", how="inner")
    df = df[df["SECCION"].isin(mapa_alcaldia["SECCION"])]
    print(f"{anio}: {len(df)} secciones objetivo presentes en los 3 archivos "
          f"(de {len(mapa_alcaldia)} en el catalogo)")

    df = df.merge(mapa_alcaldia, on="SECCION", how="left").merge(colonias, on="SECCION", how="left")

    # Validaciones contra los totales que traen los propios archivos
    for prefijo in ("V", "LN"):
        col = f"{prefijo}_TOTAL_REPORTADO"
        if col in df.columns:
            dif = (df[f"{prefijo}_TOTAL"] - df[col]).abs()
            print(f"   {prefijo}: secciones donde la suma no coincide con el total reportado: "
                  f"{int((dif > 0).sum())}")

    cambio_del = (df["LN_DEL"] != df["ALCALDIA"]) & (df["LN_DEL"] != "")
    if cambio_del.any():
        print(f"   aviso: {int(cambio_del.sum())} secciones con demarcacion distinta a la del catalogo")

    # Los tres grupos de edad deben sumar el total de votantes (todos los sexos)
    suma_edades = df["V_JOVENES"] + df["V_ADULTOS"] + df["V_MAYORES"]
    print(f"   V: secciones donde jovenes+adultos+mayores != votantes: "
          f"{int((suma_edades != df['V_TOTAL']).sum())}")

    df["ANIO"] = anio
    return pd.DataFrame({
        "ANIO": df["ANIO"],
        "SECCION": df["SECCION"],
        "ALCALDIA": df["ALCALDIA"],
        "COLONIA": df["COLONIA"],
        "Votantes_Totales": df["V_TOTAL"],
        "No_Votantes_Totales": df["NV_TOTAL"],
        "Lista_Nominal": df["LN_TOTAL"],
        "Participacion_Pct": (df["V_TOTAL"] / df["LN_TOTAL"] * 100).round(2),
        "Votantes_Jovenes_18_29": df["V_JOVENES"],
        "No_Votantes_Jovenes_18_29": df["NV_JOVENES"],
        "Participacion_Jovenes_Pct": (
            df["V_JOVENES"] / (df["V_JOVENES"] + df["NV_JOVENES"]) * 100
        ).round(2),
        "Votantes_Mujeres": df["V_MUJERES"],
        "Votantes_Hombres": df["V_HOMBRES"],
        "Votantes_Adultos_30_64": df["V_ADULTOS"],
        "Votantes_Mayores_65": df["V_MAYORES"],
        "No_Votantes_Mujeres": df["NV_MUJERES"],
        "No_Votantes_Hombres": df["NV_HOMBRES"],
        "Lista_Nominal_Mujeres": df["LN_MUJERES"],
        "Lista_Nominal_Hombres": df["LN_HOMBRES"],
    })


def main():
    entradas = [CATALOGO_PATH, CATALOGO_INE_PATH, COLONIAS_EXTRA_PATH,
                *(ruta for archivos in ARCHIVOS.values() for ruta in archivos.values())]
    faltan = [str(p.relative_to(RAIZ)) for p in entradas if not p.exists()]
    if faltan:
        raise SystemExit("Faltan archivos de entrada (ver data/raw/README.md):\n  " + "\n  ".join(faltan))

    PROCESADOS.mkdir(parents=True, exist_ok=True)
    catalogo = cargar_catalogo()
    mapa_alcaldia = catalogo[["SECCION", "ALCALDIA"]].drop_duplicates()
    colonias = (
        catalogo.groupby("SECCION")["COLONIA"]
        .agg(lambda s: " | ".join(sorted(set(s))))
        .reset_index()
    )
    print(f"Catalogo: {len(mapa_alcaldia)} secciones en {ALCALDIAS_OBJETIVO}")

    partes = [procesar_anio(anio, mapa_alcaldia, colonias) for anio in ARCHIVOS]
    final = (
        pd.concat(partes, ignore_index=True)
        .sort_values(["ANIO", "ALCALDIA", "SECCION"], kind="stable")
        .reset_index(drop=True)
    )
    final.to_csv(SALIDA, index=False, encoding="utf-8-sig")

    print("\n=== Participacion promedio por alcaldia ===")
    promedio = final.groupby(["ALCALDIA", "ANIO"])["Participacion_Pct"].mean().unstack("ANIO")
    print("Promedio simple de % por seccion:")
    print(promedio.round(2).to_string())

    agregada = (
        final.groupby(["ALCALDIA", "ANIO"])[["Votantes_Totales", "Lista_Nominal"]].sum()
    )
    agregada = (agregada["Votantes_Totales"] / agregada["Lista_Nominal"] * 100).unstack("ANIO")
    print("\nPonderada (votantes totales / lista nominal):")
    print(agregada.round(2).to_string())

    if 2015 in promedio.columns and 2024 in promedio.columns:
        cambio = (promedio[2024] - promedio[2015]).round(2).rename("Cambio_2015_2024_pp")
        print("\nCambio 2015 -> 2024 (puntos porcentuales, promedio simple):")
        print(cambio.to_string())

    print(f"\nFilas en el CSV final: {len(final)}")
    print(f"Archivo guardado: {SALIDA}")


if __name__ == "__main__":
    main()
