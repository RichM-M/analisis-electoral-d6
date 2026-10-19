# Tablero Electoral · Distrito Federal 6, Ciudad de México

Análisis de resultados electorales y participación ciudadana a nivel de sección electoral para el distrito federal 6 de la Ciudad de México, que comprende secciones de las alcaldías **La Magdalena Contreras** y **Álvaro Obregón**. Abarca las elecciones de diputaciones federales de **2015, 2018, 2021 y 2024**.

**Tablero en línea:** https://richm-m.github.io/analisis-electoral-d6/

---

## Descripción

El proyecto integra las bases de datos públicas del Programa de Resultados Electorales Preliminares (PREP) del Instituto Nacional Electoral (INE) y las estadísticas de participación ciudadana por sección electoral. Los datos se depuran y consolidan con reglas documentadas, se genera un archivo único de datos y se presentan en un tablero web estático.

El procesamiento es reproducible: a partir de las fuentes originales, un solo comando regenera todos los resultados.

## Funcionalidades del tablero

- Selección del año electoral y de la alcaldía, y búsqueda por número de sección o nombre de colonia.
- Indicadores principales: participación ciudadana, lista nominal, ciudadanía que no votó y votos totales.
- Listado de secciones electorales con su participación, votación total y fuerza política con mayor votación.
- Votación por partido político y coalición.
- Perfil de la ciudadanía votante por sexo y grupo de edad.
- Mapa territorial de las secciones para cada año.
- Diseño adaptable a teléfono, tableta y escritorio.

## Cobertura

| Elemento | Detalle |
|---|---|
| Elección | Diputaciones federales de mayoría relativa |
| Años | 2015, 2018, 2021 y 2024 |
| Ámbito | Distrito federal 6, Ciudad de México |
| Secciones | 256 (149 de La Magdalena Contreras y 107 de Álvaro Obregón) |
| Unidad de análisis | Sección electoral |

Corte de las bases del PREP utilizadas:

| Año | Corte |
|---|---|
| 2015 | 8 de junio de 2015, 20:10 (UTC-5) |
| 2018 | 2 de julio de 2018, 21:00 (UTC-5) |
| 2021 | 7 de junio de 2021, 20:00 (UTC-5) |
| 2024 | 3 de junio de 2024, 20:05 (UTC-6) |

## Metodología

En síntesis:

- **Universo:** secciones del distrito federal 6 según el catálogo de casillas del INE para el Proceso Electoral Federal 2023-2024.
- **Actas:** se consideran únicamente las actas contabilizadas. Se excluyen las actas de representación proporcional de casillas especiales y se incluyen las de mayoría relativa.
- **Votación:** los votos de partidos, coaliciones, candidaturas independientes, candidaturas no registradas y votos nulos se conservan tal como los publica el PREP.
- **Participación ciudadana:** votos totales de las actas contabilizadas entre la lista nominal de las casillas con actas contabilizadas, multiplicado por 100. Es el mismo criterio que utiliza el PREP.

La descripción completa está en [documentacion/metodologia.md](documentacion/metodologia.md) y la definición de cada campo en [documentacion/diccionario_de_datos.md](documentacion/diccionario_de_datos.md).

## Validación

Los totales del distrito para 2024 coinciden con los publicados por el PREP del INE:

| Indicador (2024) | Este proyecto | PREP (INE) |
|---|---|---|
| Actas contabilizadas | 563 | 563 |
| Votos totales | 234,604 | 234,604 |
| Lista nominal de casillas con actas contabilizadas | 327,056 | 327,056 |
| Participación ciudadana | 71.7321 % | 71.7320 % |

La diferencia en la participación se debe solo a la forma de presentar el cuarto decimal. También se verificaron, sección por sección, los resultados de las secciones 3430 y 3457.

## Participación por año

| Año | Lista nominal | Votos totales | Participación |
|---|---|---|---|
| 2015 | 270,721 | 125,734 | 46.44 % |
| 2018 | 275,138 | 197,263 | 71.70 % |
| 2021 | 328,908 | 187,062 | 56.87 % |
| 2024 | 327,056 | 234,604 | 71.73 % |

Las cifras de 2015, 2018 y 2021 se calculan sobre el universo de secciones vigente en 2024, por lo que no corresponden necesariamente a la integración del distrito en esos años. Ver la sección de limitaciones.

## Estructura del repositorio

```
.
├── docs/                      Tablero web, publicado con GitHub Pages
│   ├── index.html
│   ├── xm.css
│   └── datos_electorales.json
├── scripts/                   Procesamiento de datos (Python)
│   ├── ejecutar_pipeline.py
│   ├── procesar_participacion_historica.py
│   ├── procesar_prep_puro.py
│   └── generar_json_web.py
├── data/
│   ├── raw/
│   │   ├── catalogos/         Catálogos de secciones y colonias (incluidos)
│   │   ├── prep/              Bases del PREP (se descargan, no se incluyen)
│   │   └── participacion/     Estadísticas de participación (se descargan, no se incluyen)
│   └── processed/             Resultados consolidados
├── documentacion/             Metodología y diccionario de datos
├── requirements.txt
└── README.md
```

## Reproducir el procesamiento

1. Instalar Python 3.10 o superior y las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Descargar las fuentes originales en `data/raw/prep/` y `data/raw/participacion/`, con los nombres indicados en [data/raw/README.md](data/raw/README.md).

3. Ejecutar el procesamiento completo:

   ```bash
   python scripts/ejecutar_pipeline.py
   ```

   El resultado se escribe en `data/processed/` y en `docs/datos_electorales.json`.

4. Para revisar el tablero en local, servir la carpeta `docs/` y abrir `http://localhost:8000`:

   ```bash
   python -m http.server 8000 --directory docs
   ```

   El tablero debe abrirse desde un servidor; si se abre el archivo directamente, el navegador bloquea la lectura de los datos.

## Fuentes de datos

| Fuente | Institución | Uso |
|---|---|---|
| Base de datos del PREP, diputaciones federales 2015, 2018, 2021 y 2024 | INE | Votación por partido y coalición, lista nominal y votos totales por casilla |
| Catálogo de casillas, Proceso Electoral Federal 2023-2024 (corte del 3 de mayo de 2024) | INE | Secciones del distrito federal 6 y alcaldía de cada sección |
| Base Geográfica Digital de la Ciudad de México | INE | Asignación de colonia en secciones sin registro previo |
| Estadísticas de participación ciudadana por sección electoral | IECM | Ciudadanía votante y no votante por sexo y grupo de edad |
| Relación colonia–sección | Elaboración propia | Colonia asociada a cada sección |

## Limitaciones

- El universo de secciones corresponde a 2024. Las secciones y los distritos cambiaron entre elecciones, por lo que las comparaciones históricas por sección son aproximadas.
- La validación contra los totales publicados por el PREP se realizó para 2024. Los años 2015, 2018 y 2021 no se han contrastado con los totales oficiales del distrito.
- El perfil por sexo y edad proviene de una fuente distinta al PREP, por lo que sus totales pueden no coincidir con la votación del PREP.
- En siete secciones la colonia se asignó por cruce geográfico y corresponde a la colonia con mayor coincidencia territorial.

El detalle se encuentra en [documentacion/metodologia.md](documentacion/metodologia.md).

## Aviso

Los resultados del PREP son preliminares y no tienen efectos jurídicos; los resultados oficiales son los de los cómputos distritales. Este es un proyecto independiente y no está afiliado al Instituto Nacional Electoral ni al Instituto Electoral de la Ciudad de México.

## Autor

Desarrollado por [RichM-M](https://github.com/RichM-M).
