# fase-3-oracle

`logica/medidas.py` es el único `.py` de `logica/`. `python/io/escribir_oracle.py` reemplaza `APP.DW_MED_*`. Columna con texto de más de 4000 bytes queda `CLOB`; el resto `VARCHAR2(4000)`.

`python/verificar.py` comparó los 11 pares. `VERIF OK 11 pares, esquema APP`.

Espejo Windows escrito, no ejecutado aquí: `init.bat`, `scripts/step_*.bat`, `workflows/wf_main_windows.hwf`. El agente Windows debe correr `init.bat remote`.
