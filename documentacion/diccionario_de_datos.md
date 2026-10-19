# Diccionario de datos

Descripción de los archivos generados por el procesamiento.

## data/processed/PREP_PURO_CONSOLIDADO_DISTRITO6.csv

Votación por sección, año y opción política. Una fila por combinación de año, sección y partido o coalición.

| Campo | Tipo | Descripción |
|---|---|---|
| `ANIO` | Entero | Año de la elección (2015, 2018, 2021 o 2024). |
| `ALCALDIA` | Texto | Alcaldía de la sección, en mayúsculas y sin acentos. |
| `SECCION` | Entero | Clave de la sección electoral. |
| `COLONIA` | Texto | Colonia asociada a la sección. Si la sección abarca varias, se separan con ` \| `. |
| `PARTIDO_COALICION` | Texto | Nombre de la columna de votación tal como aparece en el PREP del año. |
| `VOTOS` | Entero | Votos de la opción en la sección, sumando todas las casillas consideradas. |

### Opciones de votación por año

La nomenclatura de partidos y coaliciones cambia entre años porque se conserva la del PREP original.

| Año | Partidos | Coaliciones | Otras opciones |
|---|---|---|---|
| 2015 | PAN, PRI, PRD, PVEM, PT, MOVIMIENTO_CIUDADANO, NUEVA_ALIANZA, MORENA, PARTIDO_HUMANISTA, ENCUENTRO_SOCIAL | PRI_PVEM, PRD_PT | CAND_IND_1, CAND_IND_2, NO_REGISTRADOS, NULOS |
| 2018 | PAN, PRI, PRD, PVEM, PT, MC, PANAL, MORENA, PES | C_PAN_PRD_MC, C_PAN_PRD, C_PAN_MC, C_PRD_MC, C_PRI_PVEM_PANAL, C_PRI_PVEM, C_PRI_PANAL, C_PVEM_PANAL, C_PT_MORENA_PES, C_PT_MORENA, C_PT_PES, C_MORENA_PES | CAND_IND_01, CAND_IND_02, NO_REGISTRADOS, NULOS |
| 2021 | PAN, PRI, PRD, PVEM, PT, MC, MORENA, PES, RSP, FXM | PAN-PRI-PRD, PAN-PRI, PAN-PRD, PRI-PRD, PVEM-PT-MORENA, PVEM-PT, PVEM-MORENA, PT-MORENA | CAND_IND_1, CAND_IND_2, CAND_IND_3, NO_REGISTRADOS, NULOS |
| 2024 | PAN, PRI, PRD, PVEM, PT, MC, MORENA | PAN-PRI-PRD, PAN-PRI, PAN-PRD, PRI-PRD, PVEM_PT_MORENA, PVEM_PT, PVEM_MORENA, PT_MORENA | CI_01, CI_02, NO_REGISTRADAS, NULOS |

Las columnas de coalición registran los votos marcados para más de un partido de la misma coalición; no incluyen los votos de cada partido por separado.

## data/processed/PARTICIPACION_PREP_OFICIAL.csv

Lista nominal, votos totales y participación por sección, calculados con el criterio del PREP. Una fila por año y sección.

| Campo | Tipo | Descripción |
|---|---|---|
| `ANIO` | Entero | Año de la elección. |
| `SECCION` | Entero | Clave de la sección electoral. |
| `LISTA_NOMINAL_PREP` | Entero | Lista nominal de las casillas con actas contabilizadas. |
| `VOTOS_TOTALES_PREP` | Entero | Votos totales de las actas contabilizadas, incluidos nulos y candidaturas no registradas. |
| `PARTICIPACION_PREP_PCT` | Decimal | `VOTOS_TOTALES_PREP × 100 ÷ LISTA_NOMINAL_PREP`, con dos decimales. Vacío si la lista nominal es cero. |

## data/processed/PARTICIPACION_HISTORICA_DISTRITO6.csv

Participación por sección con desglose por sexo y grupo de edad, a partir de las estadísticas de participación ciudadana. Una fila por año y sección.

| Campo | Tipo | Descripción |
|---|---|---|
| `ANIO` | Entero | Año de la elección. |
| `SECCION` | Entero | Clave de la sección electoral. |
| `ALCALDIA` | Texto | Alcaldía de la sección. |
| `COLONIA` | Texto | Colonia asociada a la sección. |
| `Votantes_Totales` | Entero | Personas que votaron. |
| `No_Votantes_Totales` | Entero | Personas de la lista nominal que no votaron. |
| `Lista_Nominal` | Entero | Lista nominal de la sección. |
| `Participacion_Pct` | Decimal | `Votantes_Totales × 100 ÷ Lista_Nominal`, con dos decimales. |
| `Votantes_Jovenes_18_29` | Entero | Votantes de 18 a 29 años. |
| `No_Votantes_Jovenes_18_29` | Entero | No votantes de 18 a 29 años. |
| `Participacion_Jovenes_Pct` | Decimal | Participación de 18 a 29 años, con dos decimales. |
| `Votantes_Mujeres` | Entero | Mujeres que votaron. |
| `Votantes_Hombres` | Entero | Hombres que votaron. |
| `Votantes_Adultos_30_64` | Entero | Votantes de 30 a 64 años. |
| `Votantes_Mayores_65` | Entero | Votantes de 65 años o más. |
| `No_Votantes_Mujeres` | Entero | Mujeres que no votaron. |
| `No_Votantes_Hombres` | Entero | Hombres que no votaron. |
| `Lista_Nominal_Mujeres` | Entero | Mujeres en la lista nominal. |
| `Lista_Nominal_Hombres` | Entero | Hombres en la lista nominal. |

## docs/datos_electorales.json

Archivo que consume el tablero. Se genera con `scripts/generar_json_web.py` a partir de los tres archivos anteriores.

```json
{
  "secciones": [
    { "seccion": 3457, "alcaldia": "ALVARO OBREGON", "colonia": "AXOTLA" }
  ],
  "resultados_prep": {
    "2024": {
      "3457": [ { "partido": "PAN", "votos": 527 } ]
    }
  },
  "participacion": {
    "2024": {
      "3457": {
        "lista_nominal": 1179,
        "votantes": 993,
        "no_votantes": 186,
        "pct_part": 84.22,
        "genero": {
          "hombres": 423, "mujeres": 540, "pct_mujeres": 56.07,
          "no_votantes_hombres": 121, "no_votantes_mujeres": 95
        },
        "grupos_edad": { "jovenes_18_29": 165, "adultos_30_64": 540, "mayores_65": 258 }
      }
    }
  }
}
```

| Clave | Fuente | Descripción |
|---|---|---|
| `secciones` | Catálogos | Secciones del universo con su alcaldía y colonia. |
| `resultados_prep` | PREP | Votación por año, sección y opción política. |
| `participacion.*.lista_nominal`, `votantes`, `pct_part` | PREP | Lista nominal, votos totales y participación con el criterio del PREP. |
| `participacion.*.no_votantes` | PREP | Lista nominal menos votos totales. |
| `participacion.*.genero`, `grupos_edad` | IECM | Perfil de la ciudadanía votante por sexo y grupo de edad. |
