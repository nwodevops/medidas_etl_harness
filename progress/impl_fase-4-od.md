# fase-4-od

Familia `od` en `input/fuentes_medidas.json`: 31 oficinas, `ref_code` `AMAZONAS`. Cuatro pestañas reales del libro (`1) Lista MA`, `2) Involuacrados - Ubicación`, `3) Acreditación`, `4)Modificatorias`). `inputs.yaml` declara `STG_ME_*` sobre el libro de Amazonas.

`cargar_sheets.py` toma el patrón de `ref_code` de cada familia (`CMIN` en suscripción y seguimiento). Paso `od` en `init.sh`, `scripts/step_cargar_od.bat`, `init.bat`, `wf_main.hwf` y `wf_main_windows.hwf`.

Cotabambas tiene `4)Modificatorias` con la fila de códigos de Acreditación y cero filas. Esa pestaña se omite con aviso. Si otra OD trae códigos distintos y sí tiene filas, la corrida falla.

`./init.sh` terminó en `HARNESS OK` (esquema `APP`). Conteos H2 = Oracle:

- `DW_ME_LISTA_MA` 44951
- `DW_ME_UBICACION` 287
- `DW_ME_ACREDITACION` 871
- `DW_ME_MODIFICATORIAS` 372

CLOB nuevo: `DW_ME_ACREDITACION.DETALLE_ACREDIT`. Las 11 `DW_MED_*` se volvieron a escribir con los mismos conteos de antes.

Las llamadas a Sheets tienen espera máxima de 120 s y reintento si la conexión se corta. Windows no se ejecutó aquí: `init.bat remote`.
