# Tablero electoral Distrito 6 (CDMX)

Consolida resultados del PREP y participacion ciudadana (2015, 2018, 2021 y 2024) para las secciones del distrito federal 6 y las presenta en un tablero web estatico.

## Flujo
1. python procesar_participacion_historica.py
2. python procesar_prep_puro.py
3. python generar_json_web.py
4. Ya esta en docs/; GitHub Pages publica esa carpeta. Para probar en local, abrir docs/index.html con un servidor con un servidor local.

Las rutas de los archivos fuente apuntan a la carpeta de descargas del usuario. Ver DOCUMENTO_EJECUTIVO.md para reglas de negocio, limitaciones y pendientes.
