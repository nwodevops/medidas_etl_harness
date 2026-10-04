# Contrato logica/ — medidas

## Flujo

```
python/main.py
  → io/leer_h2.py          (H2 STG_MED_* → DataFrames)
  → logica/medidas.py      (un solo archivo)
  → io/escribir_oracle.py  (<esquema>.DW_MED_*)
  → io/escribir_excel.py   (conteos en output/resultado.xlsx)
```

La carga de filas no pasa por `main.py`. La hace `python/cargar_sheets.py suscripcion` y luego `python/cargar_sheets.py seguimiento`.

## Entrada

DataFrames con nombres = claves de `LECTURAS` en `python/io/leer_h2.py`.

## Salida obligatoria

| Nombre | Descripción |
|---|---|
| `RESULTADO` | Conteos por tabla `DW_MED_*` |
| las 11 claves de `LECTURAS` | DataFrames que `main.py` escribe en Oracle |

## Reglas

- Un solo `.py` en `logica/`.
- Sin conexiones ni drivers en `logica/` (I/O en `python/io/`).
- `pandas` inyectado como `pd`.
- Esquema Oracle: `DB_ORA_DW_SCHEMA`. Nunca un literal `APP` en el SQL.
