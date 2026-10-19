# Metodología

Este documento describe las fuentes, las reglas de procesamiento y las validaciones utilizadas para construir los datos del tablero.

## 1. Objetivo

Consolidar, a nivel de sección electoral, la votación y la participación ciudadana del distrito federal 6 de la Ciudad de México en las elecciones de diputaciones federales de 2015, 2018, 2021 y 2024, con criterios consistentes con los publicados por el Programa de Resultados Electorales Preliminares (PREP) del Instituto Nacional Electoral (INE).

## 2. Universo de análisis

El universo está formado por las secciones electorales del distrito federal 6 según el catálogo de casillas del INE para el Proceso Electoral Federal 2023-2024, con corte al 3 de mayo de 2024.

| Alcaldía | Secciones |
|---|---|
| La Magdalena Contreras | 149 |
| Álvaro Obregón | 107 |
| **Total** | **256** |

La alcaldía de cada sección se toma del mismo catálogo. El mismo universo se aplica a los cuatro años analizados.

## 3. Fuentes y cortes

| Fuente | Institución | Corte o versión |
|---|---|---|
| Base de datos del PREP, diputaciones federales 2015 | INE | 8 de junio de 2015, 20:10 (UTC-5) |
| Base de datos del PREP, diputaciones federales 2018 | INE | 2 de julio de 2018, 21:00 (UTC-5) |
| Base de datos del PREP, diputaciones federales 2021 | INE | 7 de junio de 2021, 20:00 (UTC-5) |
| Base de datos del PREP, diputaciones federales 2024 | INE | 3 de junio de 2024, 20:05 (UTC-6) |
| Catálogo de casillas PEF 2023-2024 | INE | 3 de mayo de 2024 |
| Base Geográfica Digital de la Ciudad de México | INE | Último corte disponible al momento de la consulta |
| Estadísticas de participación ciudadana por sección | IECM | Por proceso electoral |
| Relación colonia–sección | Elaboración propia | Versión incluida en el repositorio |

## 4. Procesamiento del PREP

El script `scripts/procesar_prep_puro.py` aplica, en este orden, las siguientes reglas.

### 4.1 Entidad

Se conservan únicamente las actas de la Ciudad de México. El campo que identifica la entidad varía por año:

| Año | Campo | Valor |
|---|---|---|
| 2015 | `ESTADO` | `DISTRITO FEDERAL` |
| 2018 | `ID_ESTADO` | `9` |
| 2021 | `ID_ESTADO` | `9` |
| 2024 | `ID_ENTIDAD` | `9` |

### 4.2 Actas de representación proporcional

Las casillas especiales generan dos actas: una de mayoría relativa (MR) y otra de representación proporcional (RP). La votación que publica el PREP por distrito corresponde a mayoría relativa, por lo que se excluyen las actas RP:

| Año | Valor de `TIPO_ACTA` excluido |
|---|---|
| 2021 | `Diputados RP` |
| 2024 | `4ERP` |

Las bases de 2015 y 2018 no identifican las actas RP en el campo `TIPO_ACTA`. Las actas de casillas especiales de mayoría relativa (por ejemplo, `4EMR` en 2024) sí se incluyen, ya que el PREP las suma a la votación del distrito.

### 4.3 Actas contabilizadas

Se consideran solo las actas con `CONTABILIZADA = 1`. De acuerdo con la documentación del PREP, el valor `0` indica que el acta no fue contabilizada.

### 4.4 Votación

Los votos se conservan con los nombres de columna originales de cada año: partidos, coaliciones, candidaturas independientes, candidaturas no registradas y votos nulos. No se agrupan partidos en bloques ni se redistribuyen los votos de coalición. La votación de cada sección es la suma de sus casillas.

### 4.5 Lista nominal y votos totales

Para cada sección se suman la lista nominal (`LISTA_NOMINAL`) y los votos totales calculados de las actas que cumplen las reglas anteriores. El campo de votos totales es `TOTAL_VOTOS` en 2015, `TOTAL_VOTOS_CALCULADO` en 2018 y 2024, y `TOTAL_VOTOS_CALCULADOS` en 2021. Las casillas especiales no tienen lista nominal.

## 5. Participación ciudadana

La participación se calcula con el mismo criterio que publica el PREP:

```
Participación (%) = votos totales de las actas contabilizadas × 100
                    ÷ lista nominal de las casillas con actas contabilizadas
```

Los votos totales incluyen los votos nulos y los de candidaturas no registradas, así como los de casillas especiales de mayoría relativa.

La ciudadanía que no votó se calcula como la lista nominal menos los votos totales. Es un indicador de referencia del tablero, no una cifra publicada por el PREP.

## 6. Perfil de la ciudadanía votante

El perfil por sexo y grupo de edad proviene de las estadísticas de participación ciudadana por sección del Instituto Electoral de la Ciudad de México (IECM), procesadas por `scripts/procesar_participacion_historica.py`.

- **Sexo:** mujeres y hombres. Las personas no binarias forman parte del total, pero no se muestran como categoría separada.
- **Grupos de edad:** de 18 a 29 años, de 30 a 64 años y de 65 años o más.

Durante el procesamiento se verifica que la suma de los grupos de edad sea igual al total de votantes de cada sección y que las sumas coincidan con los totales reportados por cada archivo fuente.

Como se trata de una fuente distinta al PREP, sus totales pueden diferir de la votación del PREP.

## 7. Asignación de colonias

La colonia de cada sección proviene de la relación colonia–sección incluida en el repositorio. Siete secciones del distrito no figuraban en esa relación; para ellas, la colonia se asignó por cruce geográfico entre el polígono de la sección y los polígonos de colonias de la Base Geográfica Digital del INE. Se registra la colonia con mayor coincidencia territorial:

| Sección | Alcaldía | Colonia asignada | Coincidencia territorial |
|---|---|---|---|
| 3533 | Álvaro Obregón | La Peñita | 34 % |
| 3535 | Álvaro Obregón | Lomas de Guadalupe | 37 % |
| 3539 | Álvaro Obregón | Olivar de los Padres | 18 % |
| 3540 | Álvaro Obregón | La Joyita | 33 % |
| 3541 | Álvaro Obregón | Tetelpan | 51 % |
| 5621 | Álvaro Obregón | La Angostura | 80 % |
| 5622 | Álvaro Obregón | La Angostura | 100 % |

El método se validó con secciones de colonia conocida (2972, 3430 y 3457), en las que el cruce geográfico asignó la misma colonia que la relación original. Las asignaciones con coincidencia baja indican secciones que abarcan varias colonias.

## 8. Validación

### 8.1 Totales del distrito, 2024

| Indicador | Este proyecto | PREP (INE) |
|---|---|---|
| Actas contabilizadas | 563 | 563 |
| Votos totales | 234,604 | 234,604 |
| Lista nominal de casillas con actas contabilizadas | 327,056 | 327,056 |
| Participación ciudadana | 71.7321 % | 71.7320 % |

### 8.2 Secciones, 2024

| Sección | Indicador | Este proyecto | PREP (INE) |
|---|---|---|---|
| 3430 | Votos del PAN | 491 | 491 |
| 3430 | Votos del PRI | 62 | 62 |
| 3457 | Votos del PAN | 527 | 527 |
| 3457 | Votos de MORENA | 194 | 194 |
| 3457 | Votos totales | 993 | 993 |

### 8.3 Controles internos

- La suma de los votos de cada sección coincide con el total calculado por el PREP para las mismas actas.
- Los totales de votantes y de lista nominal por sección coinciden con los totales reportados en las estadísticas de participación.
- El procesamiento completo produce resultados idénticos en ejecuciones sucesivas.

## 9. Limitaciones

1. **Universo fijo.** Las secciones y los distritos se modificaron entre 2015 y 2024. Al aplicar el universo de 2024 a todos los años, algunas secciones no tienen datos en años anteriores y los totales históricos no corresponden necesariamente a la integración del distrito en cada elección.
2. **Validación parcial.** Los totales de 2015, 2018 y 2021 no se han contrastado con los totales publicados por el PREP para el distrito en esos años.
3. **Actas RP en 2015 y 2018.** Las bases de esos años no identifican las actas de representación proporcional, por lo que no se pudieron excluir.
4. **Fuentes distintas.** El perfil por sexo y edad proviene del IECM y no del PREP.
5. **Colonias aproximadas.** Las siete colonias asignadas por cruce geográfico son aproximaciones y no constituyen una relación oficial.
6. **Resultados preliminares.** El PREP no tiene efectos jurídicos; los resultados oficiales son los de los cómputos distritales.

## 10. Glosario

| Término | Definición |
|---|---|
| PREP | Programa de Resultados Electorales Preliminares del INE. |
| Sección electoral | Unidad territorial básica de la geografía electoral. |
| Casilla | Lugar donde vota la ciudadanía de una sección. Puede ser básica, contigua, extraordinaria o especial. |
| Casilla especial | Casilla donde vota ciudadanía en tránsito fuera de su sección; no tiene lista nominal. |
| Lista nominal | Relación de ciudadanas y ciudadanos con credencial vigente que pueden votar en una casilla. |
| Acta contabilizada | Acta del PREP cuyos datos se suman a los resultados por cumplir los criterios del programa. |
| Mayoría relativa (MR) | Principio por el que se elige a la diputación del distrito. |
| Representación proporcional (RP) | Principio por el que se asignan diputaciones según la votación por circunscripción. |
