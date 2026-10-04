"""SALIDA: DataFrames de logica/ → tablas <esquema>.DW_MED_* (reemplazo total).

El esquema destino es DB_ORA_DW_SCHEMA (local: APP, remote: REPOCSEP). Si no
esta definido cae al usuario de conexion en mayusculas.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import require_live_conn
from introspect.h2_ddl import sanitize_ident

_VARCHAR = 4000
_BATCH = 400

TABLAS = {
    "SUSC_INFO_GENERAL": "DW_MED_SUSC_INFO_GENERAL",
    "SUSC_PROCESO_PREVIO": "DW_MED_SUSC_PROCESO_PREVIO",
    "SUSC_ETAPAS_MA": "DW_MED_SUSC_ETAPAS_MA",
    "SUSC_MA_GABINETE": "DW_MED_SUSC_MA_GABINETE",
    "SUSC_MA_CAMPO": "DW_MED_SUSC_MA_CAMPO",
    "SEG_LISTA_MA": "DW_MED_SEG_LISTA_MA",
    "SEG_UBICACION": "DW_MED_SEG_UBICACION",
    "SEG_INFO_ADICIONAL": "DW_MED_SEG_INFO_ADICIONAL",
    "SEG_MEDIDAS": "DW_MED_SEG_MEDIDAS",
    "SEG_ACREDITACION": "DW_MED_SEG_ACREDITACION",
    "SEG_MODIFICATORIAS": "DW_MED_SEG_MODIFICATORIAS",
}


def _columnas(df: pd.DataFrame) -> list[str]:
    used: set[str] = set()
    cols = [sanitize_ident(str(c), used) for c in df.columns]
    if not cols:
        raise ValueError("DataFrame sin columnas")
    return cols


def _filas(df: pd.DataFrame) -> list[tuple]:
    rows: list[tuple] = []
    for rec in df.itertuples(index=False, name=None):
        vals = []
        for cell in rec:
            if cell is None or (isinstance(cell, float) and pd.isna(cell)):
                vals.append(None)
                continue
            if pd.isna(cell):
                vals.append(None)
                continue
            text = str(cell).strip()
            if not text or text.lower() == "nat":
                vals.append(None)
                continue
            vals.append(text)
        rows.append(tuple(vals))
    return rows


def _tipos(rows: list[tuple], n_cols: int) -> list[str]:
    clob = [False] * n_cols
    for rec in rows:
        for i, val in enumerate(rec):
            if val is not None and len(val.encode("utf-8")) > _VARCHAR:
                clob[i] = True
    return ["CLOB" if flag else f"VARCHAR2({_VARCHAR})" for flag in clob]


def _conectar(variables: dict[str, str]):
    try:
        import oracledb
    except ImportError as exc:
        raise SystemExit(
            "Falta oracledb. Instala: pip install -r python/requirements.txt"
        ) from exc

    cv = require_live_conn("oracle_dw", variables)
    port = int(cv["port"]) if str(cv["port"]).isdigit() else 1521
    return oracledb.connect(
        user=cv["username"],
        password=cv["password"],
        host=cv["host"],
        port=port,
        service_name=cv["database"],
    )


def escribir_oracle(
    frames: dict[str, pd.DataFrame],
    root: Path,
    variables: dict[str, str],
) -> dict[str, int]:
    del root
    faltan = [k for k in TABLAS if k not in frames]
    if faltan:
        raise ValueError(f"Faltan DataFrames para Oracle: {faltan}")

    schema = require_live_conn("oracle_dw", variables)["schema"]
    conn = _conectar(variables)
    conteos: dict[str, int] = {}
    try:
        cur = conn.cursor()
        try:
            for clave, tabla in TABLAS.items():
                df = frames[clave]
                if not isinstance(df, pd.DataFrame):
                    raise ValueError(f"{clave} no es un DataFrame")
                cols = _columnas(df)
                rows = _filas(df)
                tipos = _tipos(rows, len(cols))
                qualified = f'{schema}."{tabla}"'
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM ALL_TABLES
                    WHERE OWNER = :owner AND TABLE_NAME = :tname
                    """,
                    {"owner": schema, "tname": tabla},
                )
                if int(cur.fetchone()[0]) > 0:
                    cur.execute(f"DROP TABLE {qualified} PURGE")
                body = ",\n".join(f'    "{c}" {tipo}' for c, tipo in zip(cols, tipos))
                cur.execute(f"CREATE TABLE {qualified} (\n{body}\n)")
                if rows:
                    marks = ", ".join(f":{i + 1}" for i in range(len(cols)))
                    quoted = ", ".join(f'"{c}"' for c in cols)
                    sql = f"INSERT INTO {qualified} ({quoted}) VALUES ({marks})"
                    for offset in range(0, len(rows), _BATCH):
                        cur.executemany(sql, rows[offset : offset + _BATCH])
                conteos[tabla] = len(rows)
                print(f"Oracle {schema}.{tabla}: {len(rows)} filas")
        finally:
            cur.close()
        conn.commit()
    finally:
        conn.close()
    return conteos
