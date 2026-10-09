# AGENTS.md — mapa para agentes (medidas, Hop + H2 + Python)

ETL **Apache Hop + H2 in-memory + Python**. Arquitectura: [`docs/arquitectura.md`](docs/arquitectura.md).

**Verificación:** `./init.sh` (Linux) o `init.bat remote` (Windows) debe terminar en **`HARNESS OK`**. Criterios: [`CHECKPOINTS.md`](CHECKPOINTS.md).

## Harness

| Archivo | Propósito |
|---|---|
| [`feature_list.json`](feature_list.json) | Alcance; **una** `in_progress` a la vez |
| [`progress/current.md`](progress/current.md) | Plan de sesión activa |
| [`progress/history.md`](progress/history.md) | Bitácora append-only |
| [`docs/harness/workflow.md`](docs/harness/workflow.md) | Roles líder / implementador / revisor |
| [`docs/harness/platform.md`](docs/harness/platform.md) | Hop, H2, variables |

## Skills

- [`.agents/skills/hop-python-etl/SKILL.md`](.agents/skills/hop-python-etl/SKILL.md) — capas Hop / H2 / Python
- [`.agents/skills/linux-windows-parity/SKILL.md`](.agents/skills/linux-windows-parity/SKILL.md) — el cambio de Linux se espeja en `init.bat` y `wf_main_windows.hwf`
- [`.agents/skills/etl-run-logs/SKILL.md`](.agents/skills/etl-run-logs/SKILL.md) — cada corrida deja bitácora en `logs/`
- [`.agents/skills/release-etl/SKILL.md`](.agents/skills/release-etl/SKILL.md) — corta la rama `release` solo con el ETL

## Inicio rápido

### Linux (desarrollo, entorno `local`)

```bash
./switch-env.sh local
./init.sh
~/apps/hop/hop-gui.sh   # → wf_main.hwf
```

### Windows (este equipo, entorno `remote`)

```bat
powershell -ExecutionPolicy Bypass -File switch-env.ps1 remote
init.bat remote
REM Hop GUI → workflows\wf_main_windows.hwf
```

## Entornos

| | Oracle | Esquema `DW_MED_*` |
|---|---|---|
| `local` | `localhost:1524/BD_CURSOR` | `APP` |
| `remote` | `10.6.0.15:1532/dvoefacore` | `REPOCSEP` |

Base destino vía `DB_MYSQL_DW_DATABASE` (`gappsdb`). Credenciales solo en `docs/credenciales/*.txt` (gitignored), sobrepuestas por `switch-env.sh` / `switch-env.ps1`.

## Reglas críticas

1. **Un solo `.py`** en `logica/` (`medidas.py`).
2. **Sin secretos** en git (`project-config.json` es generado).
3. **Sin `${VAR}` literal** en logs Hop = variable mal definida.
4. `logica/` no abre conexiones. I/O en `python/io/`.
5. **No solapar corridas**: `mem:csep`:9092 es compartido con los repos hermanos y todos hacen `DROP ALL OBJECTS`.
6. **Corrida en `logs/`**: `logs/init_YYYYMMDD.log` y `logs/wf_main_YYYYMMDD.log`. stdout o un temporal que se borra no cuentan. Skill `etl-run-logs`.

## Corrida

51 libros en `input/fuentes_medidas.json` (20 de sedes y 31 de OD). Tres pasos: `cargar_sheets.py suscripcion`, `seguimiento` y `od`. Destino: `<DB_MYSQL_DW_DATABASE>.DW_MED_*` y `DW_MED_OD_*` en MySQL.
