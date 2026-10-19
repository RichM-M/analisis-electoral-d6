# Datos de entrada

## catalogos/ (incluidos en el repositorio)

| Archivo | Descripción |
|---|---|
| `20240503_CORTE_CASILLAS_PEF24.xlsx` | Catálogo de casillas del INE, Proceso Electoral Federal 2023-2024, corte del 3 de mayo de 2024. Define las secciones del distrito federal 6 y su alcaldía. |
| `listado_colonias_secciones_alcaldia.csv` | Relación colonia–sección de elaboración propia. |
| `colonias_secciones_faltantes.csv` | Colonia asignada por cruce geográfico a siete secciones que no figuran en la relación anterior. Ver `documentacion/metodologia.md`, sección 7. |

## prep/ (no incluidos; se descargan)

Bases de datos del PREP de diputaciones federales del INE. Cada archivo se descarga desde la sección *Base de datos* del sitio de publicación del PREP de cada año y se guarda con el nombre indicado.

| Archivo esperado | Contenido | Corte |
|---|---|---|
| `DIP_FED_2015.csv` | PREP 2015, diputaciones federales | 8 de junio de 2015, 20:10 (UTC-5) |
| `DIP_FED_2018.csv` | PREP 2018, diputaciones federales | 2 de julio de 2018, 21:00 (UTC-5) |
| `DIP_FED_2021.csv` | PREP 2021, diputaciones federales | 7 de junio de 2021, 20:00 (UTC-5) |
| `DIP_FED_2024.csv` | PREP 2024, diputaciones federales (`prep2024.ine.mx`) | 3 de junio de 2024, 20:05 (UTC-6) |

## participacion/ (no incluidos; se descargan)

Estadísticas de participación ciudadana por sección electoral del Instituto Electoral de la Ciudad de México (IECM): ciudadanía votante, no votante y lista nominal por sexo y grupo de edad.

| Año | Votantes | No votantes | Lista nominal |
|---|---|---|---|
| 2015 | `votantes_participacion2015_sec.csv` | `no_votantes_participacion2015_sec.csv` | `ln_20150415_ajustada_sec.csv` |
| 2018 | `part2018peVotoSec.xlsx` | `part2018peNoVotoSec.xlsx` | `part2018peListaNominalSec.xlsx` |
| 2021 | `part2021peVotoSec.xlsx` | `part2021peNoVotoSec.xlsx` | `part2021peListaNominalSec.xlsx` |
| 2024 | `VotantesSEC.xlsx` | `NoVotantesSEC.xlsx` | `LnSEC.xlsx` |

Si falta algún archivo, el script que lo necesita indica cuál es al iniciar y se detiene.
