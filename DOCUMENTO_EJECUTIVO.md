# Tablero electoral Distrito 6 (CDMX): documento ejecutivo

Fecha de corte de este documento: 17 de octubre de 2026.

## 1. Resumen ejecutivo

El proyecto consolida resultados electorales del PREP y participación ciudadana para el Distrito Federal 6 de la Ciudad de México (alcaldías La Magdalena Contreras y Álvaro Obregón) y los presenta en un tablero web estático.

Estado al corte:

- **2024 (diputaciones federales):** cuadra con la página oficial del PREP del INE para el distrito completo: 563 casillas contabilizadas, 234,604 votos totales y 327,056 de lista nominal. La participación es 71.7321 %, igual que la publicada (71.7320 %, redondeo distinto).
- **2021:** la base de datos trae 250 secciones en el distrito 6, igual que el mapa KML de 2021 y el catálogo usado originalmente. Pendiente verificar los totales contra la página oficial de 2021.
- **2015 y 2018:** la numeración de distritos cambió. El distrito 6 de 2015 es Gustavo A. Madero, por lo que no se puede identificar el distrito 6 por número. Pendiente.
- **Tablero:** funcional en el entorno de desarrollo local. Pendiente publicarlo y revisarlo en dispositivos reales.

## 2. Arquitectura

El proyecto tiene tres capas:

1. **Procesamiento** (scripts Python en la carpeta de trabajo): lee archivos fuente, aplica reglas de negocio y genera CSV intermedios.
2. **Datos** (`datos_electorales.json`): archivo único que consume el tablero.
3. **Presentación** (`index.html` + `xm.css` en la carpeta `analisiselectoral`): página estática que lee el JSON con JavaScript y muestra resultados, participación, perfil y mapa.

No hay backend ni base de datos. El tablero se puede publicar en GitHub Pages como sitio estático.

### 2.1 Archivos del proyecto

| Archivo | Tipo | Función |
|---|---|---|
| `procesar_prep_puro.py` | Script | Consolida resultados PREP por sección y partido para 2015, 2018, 2021 y 2024. Genera `PREP_PURO_CONSOLIDADO_DISTRITO6.csv` y `PARTICIPACION_PREP_OFICIAL.csv`. |
| `procesar_participacion_historica.py` | Script | Consolida votantes, no votantes y lista nominal por sección, desglosados por sexo y edad, a partir de los archivos del INE. Genera `PARTICIPACION_HISTORICA_DISTRITO6.csv`. |
| `generar_json_web.py` | Script | Une los CSV anteriores y genera `datos_electorales.json`. |
| `index.html` | Página | Tablero: filtros, KPI, gráfica de partidos, lista de secciones, perfil de votantes y mapa. |
| `xm.css` | Hoja de estilos | Tokens y componentes del sistema de diseño (un acento y cinco grises). |
| `datos_electorales.json` | Datos | Lo que lee el tablero: secciones, resultados PREP y participación. |
| `catalogo_ine/20240503_CORTE_CASILLAS_PEF24.xlsx` | Fuente | Catálogo de casillas del INE: entidad, distrito, municipio y sección. |
| `colonias_secciones_faltantes.csv` | Dato derivado | Colonia principal de 7 secciones sin colonia en el listado original. Se obtuvo por cruce geométrico con la BGD del INE. |
| `listado_colonias_secciones_alcaldia.csv` | Fuente (usuario) | Relación sección–colonia original. Está en la carpeta de descargas. |
| `prep_2024_nuevo/DIP_FED_2024.csv` | Fuente | Base de datos del PREP 2024 (descarga oficial del corte 20240603 2005). |

## 3. Flujo de datos

Orden de ejecución (en la carpeta de trabajo):

1. `py -3 procesar_participacion_historica.py`
2. `py -3 procesar_prep_puro.py`
3. `py -3 generar_json_web.py`
4. Copiar `datos_electorales.json` a la carpeta del proyecto web (`analisiselectoral`).

El paso 1 debe ejecutarse antes del 3, porque el JSON une ambos CSV.

## 4. Reglas de negocio

### 4.1 Universo de secciones

- Se usa el catálogo de casillas del INE (`ESTADO = 9` y `DISTRITO = 6`): 256 secciones.
- La alcaldía de cada sección sale de `NOMBRE_MUNICIPIO`.
- La colonia sale del listado original. Si no existe, se usa `colonias_secciones_faltantes.csv`.
- La sección 3574 de la lista original no pertenece al distrito 6 y se excluye.

### 4.2 Resultados PREP

- Solo CDMX (`ID_ESTADO = 9` en 2018 y 2021, `ID_ENTIDAD = 9` en 2024, `ESTADO = DISTRITO FEDERAL` en 2015).
- Solo actas con `CONTABILIZADA = 1`. Según el README del PREP, `0` significa que el acta no fue contabilizada.
- Se excluyen actas de representación proporcional: `4ERP` en 2024 y `DIPUTADOS RP` en 2021.
- Se conservan `4EMR` (casillas especiales de mayoría relativa) porque el INE sí las incluye en los votos del distrito.
- Votos por partido, coalición, candidatura, nulos y no registradas, tal cual vienen en el PREP.

### 4.3 Participación

- Fórmula oficial del INE: votos totales (`TOTAL_VOTOS_CALCULADO`) entre lista nominal de las casillas contabilizadas, por sección y año.
- La lista nominal y los votos salen del PREP, no de los archivos de participación del INE.
- No votantes = lista nominal − votos totales. Esta es una definición operativa, no un dato publicado.

### 4.4 Género y edad

- Vienen de los archivos de votantes, no votantes y lista nominal del INE, por sección.
- Género: hombres y mujeres. Los no binarios no se muestran en el desglose, aunque están en el total.
- Edad: jóvenes 18–29, adultos 30–64 y mayores de 65.
- Estos archivos no son del PREP, por lo que sus cifras no siempre coinciden con las del PREP.

## 5. Casos de uso

| # | Caso de uso | Quién | Cómo lo resuelve el tablero |
|---|---|---|---|
| 1 | Consultar resultados de una elección por año | Equipo de campaña | Selector de año; KPI de participación, lista nominal, no votantes y votos PREP. |
| 2 | Ver qué partido ganó en la alcaldía o la sección | Analista | Gráfica de votos por partido o coalición con la paleta de partidos; filtro por alcaldía. |
| 3 | Buscar una sección o colonia | Coordinador territorial | Buscador por número de sección o nombre de colonia, sin acentos. |
| 4 | Revisar secciones en orden | Coordinador territorial | Tabla de secciones en orden ascendente, con participación, votos y partido más votado. |
| 5 | Conocer el perfil demográfico del electorado | Estratega | Perfil de votantes: género y tres grupos de edad, con tooltips. |
| 6 | Ver la geografía de las secciones | Coordinador territorial | Mapa de Google My Maps por año (en el caso de 2024, enlace público). |
| 7 | Actualizar los datos cuando hay nuevas actas | Operador técnico | Re-ejecutar los tres scripts y copiar el JSON. |

## 6. Cambios realizados

Bitácora de cambios relevantes, en orden cronológico:

1. **Lectura de PREP con delimitador final:** se corrigió que pandas usara la primera columna como índice (`index_col=False`). Afectaba 2015.
2. **Filtro de entidad 2015:** la columna `ID_ESTADO` de 2015 trae el nombre del estado, no la clave. Se usa `ESTADO = DISTRITO FEDERAL`.
3. **Catálogo de secciones:** se pasó de 250 secciones del listado a 256 del catálogo de casillas del INE. Se agregaron 7 secciones de Álvaro Obregón y se quitó la 3574.
4. **Exclusión de RP:** se excluyeron `4ERP` (2024) y `DIPUTADOS RP` (2021).
5. **Actas contabilizadas:** se filtra `CONTABILIZADA = 1`. Con este filtro, el distrito 6 de 2024 cuadra con el INE.
6. **Participación oficial:** pasó de personas que votaron (archivos del INE) a votos totales sobre lista nominal (PREP). Así cuadran las secciones 3430 y 3457 con la página oficial.
7. **Tablero:**
   - Perfil de votantes: barra de género y grupos de edad, con actualización por filtro.
   - Tooltips al pasar el cursor sobre género y grupos de edad.
   - Columna de votos junto a la gráfica de partidos, con tooltip en la paleta de `xm.css`.
   - Lista de secciones ordenada en forma ascendente, con título "Secciones electorales".
   - Barras de desplazamiento con la paleta de `xm.css`.
   - Mapa de Google My Maps por año, con enlace al mapa público.

## 7. Limitaciones y riesgos

- **Secciones por año:** el tablero usa el catálogo de 2024 para todos los años. Como las secciones cambiaron, la asignación de alcaldía para 2015, 2018 y 2021 puede no corresponder a la de su año.
- **2015 y 2018:** el filtro `CONTABILIZADA = 1` se aplicó igual que en 2024, pero no se verificó contra la página oficial de esos años.
- **Colonias de 7 secciones:** la colonia principal se obtuvo por cruce geométrico. Tiene coincidencia entre 18 % y 100 % y no es una relación oficial.
- **Secciones 5621 y 5622:** el catálogo del INE las ubica en Álvaro Obregón. El mapa de 2024 que se usó antes las ubicaba en La Magdalena Contreras, por lo que ese mapa no es confiable para demarcaciones.
- **Mapa de 2021 y 2015 propios:** los KML de 2015, 2018 y 2021 se trazaron a partir de PDF por el usuario. No son cartografía oficial.
- **Perfil de votantes:** viene de archivos del INE, no del PREP, por lo que puede diferir del total de votos.
- **Mapas de Google My Maps:** dependen de un servicio externo. Los mapas de 2015, 2018 y 2021 aún no están configurados en el tablero.
- **Datos de 2024:** la base usada es el corte del 3 de junio de 2024, 20:05 (UTC-6). Si el PREP se actualiza, hay que volver a descargar la base.

## 8. Cambios pendientes

| Prioridad | Cambio | Dependencia |
|---|---|---|
| Alta | Validar 2021 contra la página oficial del PREP 2021 (total de votos, LN y participación del distrito). | Acceso a la página oficial de 2021. |
| Alta | Definir las secciones del distrito 6 para 2015 (distrito 26 y 17 según el PREP) y para 2018. | Lista oficial de secciones por año, por ejemplo el catálogo de casillas o el acuerdo de distritación. |
| Alta | Revisar y publicar el tablero en GitHub Pages, y probarlo en iPhone, iPad y Mac. | Repositorio y cuenta de GitHub. |
| Media | Colonia por año (no solo 2024). | Cartografía de cada año (BGD o KML oficiales) o solicitud a transparencia. |
| Media | Configurar los mapas de 2015, 2018 y 2021 en el tablero. | URLs de Google My Maps. |
| Baja | Mostrar no binarios en el desglose de género, si se considera relevante. | Decisión de producto. |

## 9. Fuentes

- Base de datos PREP 2024 (diputaciones federales), descarga oficial, corte 20240603 2005: `prep2024.ine.mx`.
- Base de datos PREP 2021 (diputaciones) y PREP 2015 (diputados), archivos descargados en la carpeta de descargas.
- Catálogo de casillas PEF 2024 (corte 20240503), INE.
- Base Geográfica Digital (BGD) de la CDMX, INE, 2024 (`bgd_9_Shapefile.zip`).
- Listado de colonias y secciones de la carpeta de descargas (fuente del usuario).
- Condensados de redistritación: `CONDENSADO_REDIS2014.pdf`, `CONDENSADO_2017_DTTO_33_SEPT.pdf` y `CONDENSADO_CDMX_MGE2023-2024.pdf`. Son mapas, no tablas; no se usaron para asignar secciones.
- Mapas KML de diputaciones federales 2015, 2018, 2021 y 2024 (elaborados por el usuario a partir de PDF).
