# Scripts del análisis de encuestas Alianza 4U

Generan los tres entregables de `resultados/` a partir de `Resultados_encuestas_Alianza_4U.zip`.

1. Descomprimir el zip y ejecutar los scripts desde la carpeta donde quedan los cuatro `.xlsx`.
2. Dependencias: `pandas openpyxl xlsxwriter python-docx matplotlib scipy statsmodels`. Los efectos ajustados (`extend.effects`) se guardan en `eff_todos.pkl` y `eff_rechazados.pkl` antes de generar los informes.
3. Ejecutar:
   - `python verify.py` (genera la verificación contra la plataforma; ejecutar primero)
   - `python build_excel.py` → `Estadisticas_Alianza_4U.xlsx`
   - `python report_detallado.py` → `Informe_detallado_Alianza_4U.docx`
   - `python report_ejecutivo.py` → `Informe_ejecutivo_Alianza_4U.docx`

Las rutas de salida (`OUT` en cada script y `OUTD` en `charts.py`) están fijadas al entorno donde se generaron; ajústelas si ejecuta en otro equipo.
