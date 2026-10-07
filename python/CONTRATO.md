# Contrato logica/ — medidas

## Flujo

```
python/main.py
  → io/leer_h2.py          (H2 STG_MED_* y STG_MED_OD_* → DataFrames)
  → logica/medidas.py      (un solo archivo)
  → io/escribir_mysql.py   (<base>.DW_MED_* y DW_MED_OD_*)
  → io/escribir_excel.py   (conteos en output/resultado.xlsx)
```

La carga de filas no pasa por `main.py`. La hace `python/cargar_sheets.py suscripcion`, luego `seguimiento` y luego `od`.

## Entrada

DataFrames con nombres = claves de `LECTURAS` en `python/io/leer_h2.py`.

## Salida obligatoria

| Nombre | Descripción |
|---|---|
| `RESULTADO` | Conteos por tabla `DW_MED_*` y `DW_MED_OD_*` |
| las 15 claves de `LECTURAS` | DataFrames que `main.py` escribe en Oracle |

## Reglas

- Un solo `.py` en `logica/`.
- Sin conexiones ni drivers en `logica/` (I/O en `python/io/`).
- `pandas` inyectado como `pd`.
- Base MySQL: `DB_MYSQL_DW_DATABASE`. Nunca un literal `gappsdb` en el SQL.
