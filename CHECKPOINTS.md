# CHECKPOINTS — medidas

Verificación: [`./init.sh`](init.sh) termina en **`HARNESS OK`**.

## Global

- [ ] `./init.sh` termina con **`HARNESS OK`**.
- [ ] Bitácora en `logs/init_YYYYMMDD.log`.
- [ ] Sin passwords reales en `project-config.json` versionado / `environments/`.
- [ ] Log sin literales `${VAR}`.
- [ ] Un solo `.py` en `logica/` (`medidas.py`).
- [ ] Máximo **una** feature `in_progress`.
- [ ] Base destino MySQL vía `DB_MYSQL_DW_DATABASE` (`gappsdb` en local y en remote).

## Fase 1 — Entorno

- [ ] `switch-env.sh local` sobrepone `DB_ORA_DW_*` desde `docs/credenciales/local.txt`.
- [ ] `DB_ORA_DW_SCHEMA` = `APP` en local y `REPOCSEP` en remote.
- [ ] H2 levanta en puerto 9092.

## Fase 2 — Fuentes

- [ ] `input/fuentes_medidas.json` con 2 familias, 10 sedes y 20 libros.
- [ ] `inputs.yaml` con 11 fuentes `type: sheets`.
- [ ] `cargar_sheets.py suscripcion` y `cargar_sheets.py seguimiento` en ese orden.
- [ ] Si una sede no trae la pestaña o la fila de códigos de `CMIN`, la corrida falla nombrando familia, sede y pestaña.

## Fase 3 — Oracle

- [ ] 11 tablas `<esquema>.DW_MED_*` con filas > 0.
- [ ] `python/verificar.py`: conteo H2 = conteo Oracle en los 11 pares.
- [ ] Espejo Windows: `init.bat`, `scripts/step_*.bat`, `workflows/wf_main_windows.hwf`.

## Fase 4 — OD

- [ ] Familia `od` en `input/fuentes_medidas.json`: 31 oficinas, `ref_code` `AMAZONAS`.
- [ ] 4 fuentes `STG_MED_OD_*` en `inputs.yaml` y 4 tablas `<esquema>.DW_MED_OD_*` con filas > 0.
- [ ] `cargar_sheets.py od` después de seguimiento. Si una OD no trae la pestaña, o trae otra fila de códigos con datos, la corrida falla nombrando familia, OD y pestaña. Una pestaña con códigos distintos y cero filas se omite con aviso.
- [ ] `python/verificar.py`: conteo H2 = conteo Oracle en los 15 pares.
- [ ] Espejo Windows: `scripts/step_cargar_od.bat` llamado desde `init.bat` y `wf_main_windows.hwf`.
