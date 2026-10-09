#!/usr/bin/env bash
# Copia environments/<env>.json -> project-config.json (estructura Hop).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ENV="${1:-local}"
SRC="$ROOT/environments/${ENV}.json"
DST="$ROOT/project-config.json"
if [[ ! -f "$SRC" ]]; then
  echo "No existe: $SRC" >&2
  exit 1
fi
CRED="$ROOT/docs/credenciales/${ENV}.txt"
python3 - "$SRC" "$DST" "$CRED" <<'PY'
import json, sys
from pathlib import Path

src, dst, cred = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(src, encoding="utf-8"))
vars_ = data.get("variables") or data.get("config", {}).get("variables") or []

def _parse_block(text: str) -> dict:
    wanted = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if key in ("Host", "Port", "Service", "Database", "User", "Password"):
            wanted[key] = val
    return wanted


def _apply(variables, mapping: dict) -> None:
    for item in variables:
        name = item.get("name")
        if name in mapping:
            item["value"] = mapping[name]


def overlay_dw(variables, cred_path: str) -> None:
    path = Path(cred_path)
    if not path.is_file():
        return
    import re

    raw = path.read_text(encoding="utf-8")
    parts = re.split(r"(?im)^#\s*mysql\b.*$", raw, maxsplit=1)
    ora = _parse_block(parts[0])
    missing = [k for k in ("Host", "Port", "Service", "User", "Password") if not ora.get(k)]
    if missing:
        raise SystemExit(f"Faltan {', '.join(missing)} en el bloque Oracle de {cred_path}")
    host, port, service = ora["Host"], ora["Port"], ora["Service"]
    _apply(variables, {
        "DB_ORA_DW_HOST": host,
        "DB_ORA_DW_PORT": port,
        "DB_ORA_DW_DATABASE": service,
        "DB_ORA_DW_USERNAME": ora["User"],
        "DB_ORA_DW_PASSWORD": ora["Password"],
        "DB_ORA_DW_URL": f"jdbc:oracle:thin:@//{host}:{port}/{service}",
    })
    print(f"DW Oracle: {host}:{port}/{service} user={ora['User']}")
    if len(parts) < 2:
        raise SystemExit(f"Falta el bloque #Mysql en {cred_path}")
    my = _parse_block(parts[1])
    missing = [k for k in ("Host", "Port", "Database", "User", "Password") if not my.get(k)]
    if missing:
        raise SystemExit(f"Faltan {', '.join(missing)} en el bloque Mysql de {cred_path}")
    _apply(variables, {
        "DB_MYSQL_DW_HOST": my["Host"],
        "DB_MYSQL_DW_PORT": my["Port"],
        "DB_MYSQL_DW_DATABASE": my["Database"],
        "DB_MYSQL_DW_USERNAME": my["User"],
        "DB_MYSQL_DW_PASSWORD": my["Password"],
    })
    print(f"DW MySQL: {my['Host']}:{my['Port']}/{my['Database']} user={my['User']}")

overlay_dw(vars_, cred)
out = {
    "metadataBaseFolder": "${PROJECT_HOME}/metadata",
    "unitTestsBasePath": "${PROJECT_HOME}",
    "dataSetsCsvFolder": "${PROJECT_HOME}/datasets",
    "enforcingExecutionInHome": True,
    "parentProjectName": "default",
    "config": {"variables": vars_},
}
json.dump(out, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"OK: {src} -> {dst}")
PY
