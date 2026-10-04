# fase-2-fuentes

Catálogo `input/fuentes_medidas.json`: 2 familias, 10 sedes, 20 libros, 11 pestañas. `inputs.yaml` declara las 11 `STG_MED_*` con la fila de códigos y `sede_columns`.

`python/cargar_sheets.py suscripcion` y luego `seguimiento`. Cada sede se compara con `CMIN` (pestaña y fila de códigos). Cuota 429 de Sheets espera 65 s y reintenta.

Conteos H2 de la corrida verde:

- STG_MED_SUSC_INFO_GENERAL 809
- STG_MED_SUSC_PROCESO_PREVIO 615
- STG_MED_SUSC_ETAPAS_MA 2360
- STG_MED_SUSC_MA_GABINETE 441
- STG_MED_SUSC_MA_CAMPO 185
- STG_MED_SEG_LISTA_MA 4166
- STG_MED_SEG_UBICACION 2022
- STG_MED_SEG_INFO_ADICIONAL 13298
- STG_MED_SEG_MEDIDAS 4247
- STG_MED_SEG_ACREDITACION 3806
- STG_MED_SEG_MODIFICATORIAS 2624

Windows: `scripts/step_cargar_suscripcion.bat` y `scripts/step_cargar_seguimiento.bat`.
