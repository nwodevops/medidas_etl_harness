"""SALIDA: DataFrames de logica/ → tablas <base>.DW_MED_* y DW_MED_OD_* (reemplazo total).

La base destino es DB_MYSQL_DW_DATABASE (gappsdb en local y en remote).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from config import require_live_conn
from introspect.h2_ddl import sanitize_ident

_TEXT = 4000
_BATCH = 400
_IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

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
    "ME_LISTA_MA": "DW_MED_OD_LISTA_MA",
    "ME_UBICACION": "DW_MED_OD_UBICACION",
    "ME_ACREDITACION": "DW_MED_OD_ACREDITACION",
    "ME_MODIFICATORIAS": "DW_MED_OD_MODIFICATORIAS",
}


def _ident(name: str) -> str:
    if not _IDENT.match(name):
        raise ValueError(f"identificador no permitido: {name!r}")
    return name


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
    largo = [False] * n_cols
    for rec in rows:
        for i, val in enumerate(rec):
            if val is not None and len(val.encode("utf-8")) > _TEXT:
                largo[i] = True
    return ["LONGTEXT" if flag else "TEXT" for flag in largo]


def conectar(variables: dict[str, str]):
    try:
        import pymysql
    except ImportError as exc:
        raise SystemExit(
            "Falta pymysql. Instala: pip install -r python/requirements.txt"
        ) from exc

    cv = require_live_conn("mysql_dw", variables)
    port = int(cv["port"]) if str(cv["port"]).isdigit() else 3306
    return pymysql.connect(
        host=cv["host"],
        port=port,
        user=cv["username"],
        password=cv["password"],
        database=cv["schema"],
        charset="utf8mb4",
        autocommit=False,
    )


def escribir_mysql(
    frames: dict[str, pd.DataFrame],
    root: Path,
    variables: dict[str, str],
) -> dict[str, int]:
    del root
    faltan = [k for k in TABLAS if k not in frames]
    if faltan:
        raise ValueError(f"Faltan DataFrames para MySQL: {faltan}")

    schema = _ident(require_live_conn("mysql_dw", variables)["schema"])
    conn = conectar(variables)
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
                tabla = _ident(tabla)
                qualified = f"`{schema}`.`{tabla}`"
                cur.execute(f"DROP TABLE IF EXISTS {qualified}")
                body = ",\n".join(f"    `{c}` {tipo}" for c, tipo in zip(cols, tipos))
                cur.execute(
                    f"CREATE TABLE {qualified} (\n{body}\n) "
                    "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
                if rows:
                    marks = ", ".join(["%s"] * len(cols))
                    quoted = ", ".join(f"`{c}`" for c in cols)
                    sql = f"INSERT INTO {qualified} ({quoted}) VALUES ({marks})"
                    for offset in range(0, len(rows), _BATCH):
                        cur.executemany(sql, rows[offset : offset + _BATCH])
                conteos[tabla] = len(rows)
                print(f"MySQL {schema}.{tabla}: {len(rows)} filas")
        finally:
            cur.close()
        conn.commit()
    finally:
        conn.close()
    return conteos
