# fase-1-entorno

`switch-env.sh` y `switch-env.ps1` sobreponen `DB_ORA_DW_*` desde `docs/credenciales/<env>.txt`. `DB_ORA_DW_SCHEMA` es `APP` en local y `REPOCSEP` en remote. `python/config.py` usa ese esquema y, si falta, el usuario en mayúsculas.

`init.sh` e `init.bat` agregan la corrida a `logs/init_YYYYMMDD.log`.

Evidencia: `./switch-env.sh local` imprimió `DW: localhost:1524/BD_CURSOR user=app`. `./init.sh` terminó en `HARNESS OK` (ver `logs/init_20261004.log`).

Windows: correr `init.bat remote` y confirmar el mismo `HARNESS OK` contra `REPOCSEP`.
