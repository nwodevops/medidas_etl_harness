# fase-5-mysql

El destino de las 15 tablas pasó de Oracle a MySQL `gappsdb`. `switch-env` lee el bloque `#Mysql` de `docs/credenciales/<env>.txt` hacia `DB_MYSQL_DW_*` y deja el bloque de arriba en `DB_ORA_DW_*`. `python/io/escribir_mysql.py` reemplaza cada tabla (`TEXT`, o `LONGTEXT` si un valor pasa de 4000 bytes).

`./init.sh` del 2026-10-07 terminó en `HARNESS OK`. `VERIF OK 15 pares, base gappsdb`.

- `DW_MED_SUSC_INFO_GENERAL` 814
- `DW_MED_SUSC_PROCESO_PREVIO` 619
- `DW_MED_SUSC_ETAPAS_MA` 2387
- `DW_MED_SUSC_MA_GABINETE` 445
- `DW_MED_SUSC_MA_CAMPO` 186
- `DW_MED_SEG_LISTA_MA` 4175
- `DW_MED_SEG_UBICACION` 2026
- `DW_MED_SEG_INFO_ADICIONAL` 13298
- `DW_MED_SEG_MEDIDAS` 4255
- `DW_MED_SEG_ACREDITACION` 3814
- `DW_MED_SEG_MODIFICATORIAS` 2624
- `DW_MED_OD_LISTA_MA` 44951
- `DW_MED_OD_UBICACION` 289
- `DW_MED_OD_ACREDITACION` 876
- `DW_MED_OD_MODIFICATORIAS` 372

`LONGTEXT`: `DW_MED_SEG_MEDIDAS.DESCRIP_MA`, `DW_MED_SEG_MEDIDAS.OBS_1`, `DW_MED_SEG_ACREDITACION.DETALLE_ACREDIT`, `DW_MED_OD_ACREDITACION.DETALLE_ACREDIT`.

Las tablas Oracle `APP` no se tocaron. Windows no se ejecutó aquí: `init.bat remote` contra `10.1.1.217:3306/gappsdb`.
