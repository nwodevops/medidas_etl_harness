"""ENTRADA staging: Google Sheets de una familia → filas en STG_MED_*.

El patrón de columnas es la sede CMIN. Otra sede con pestaña ausente o
fila de códigos distinta aborta la corrida.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from config import load_sources, load_vars
from h2_conn import connect_h2
from introspect.h2_ddl import sanitize_ident

_BATCH = 400
_SEDE_COLS = ("SEDE_CODIGO", "SEDE_NOMBRE")
_REF_SEDE = "CMIN"


def _as_int(source: dict, key: str, default: int) -> int:
    raw = source.get(key, default)
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{source.get('stg_table')}: {key} debe ser entero, recibido {raw!r}"
        ) from exc
    if value < 1:
        raise ValueError(f"{source.get('stg_table')}: {key} debe ser >= 1")
    return value


def _columnas(headers: list, stg: str) -> tuple[list[str], list[int]]:
    used: set[str] = set()
    names: list[str] = []
    indexes: list[int] = []
    for i, header in enumerate(headers):
        if header is None or str(header).strip() == "":
            continue
        names.append(sanitize_ident(str(header), used))
        indexes.append(i)
    if not names:
        raise ValueError(f"{stg}: fila de códigos sin columnas usables")
    return names, indexes


def _filas(grid: list[list], indexes: list[int], start: int, sede_code: str, sede_name: str) -> list[tuple]:
    rows: list[tuple] = []
    for raw in grid[start - 1 :]:
        vals = []
        empty = True
        for i in indexes:
            cell = raw[i] if i < len(raw) else ""
            text = "" if cell is None else str(cell).strip()
            if text:
                empty = False
            vals.append(text or None)
        if not empty:
            vals.append(sede_code)
            vals.append(sede_name)
            rows.append(tuple(vals))
    return rows


def _columnas_h2(cur, stg: str) -> list[str]:
    cur.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE UPPER(TABLE_SCHEMA) = 'PUBLIC' AND UPPER(TABLE_NAME) = ?
        ORDER BY ORDINAL_POSITION
        """,
        [stg.upper()],
    )
    found = [str(row[0]).upper() for row in cur.fetchall()]
    if not found:
        raise ValueError(f"{stg}: no existe en H2. Corre create_stg.py antes.")
    return found


def _api(fn, *args, **kwargs):
    import gspread

    for intento in range(6):
        try:
            return fn(*args, **kwargs)
        except gspread.exceptions.APIError as exc:
            if "429" not in str(exc) or intento == 5:
                raise
            print(f"AVISO: cuota Sheets 429, espera 65s (intento {intento + 1})")
            time.sleep(65)
    raise RuntimeError("cuota Sheets agotada")


def _catalogo(root: Path) -> dict:
    path = root / "input" / "fuentes_medidas.json"
    if not path.is_file():
        raise FileNotFoundError(f"No se encuentra {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    familias = {item["id"]: item for item in data.get("familias") or []}
    if not familias:
        raise ValueError(f"{path.name}: sin familias")
    return familias


def _sedes(familia: dict) -> list[dict]:
    sedes = list(familia.get("sedes") or [])
    codes = [str(s.get("code") or "") for s in sedes]
    if _REF_SEDE not in codes:
        raise ValueError(f"{familia.get('id')}: falta la sede patrón {_REF_SEDE}")
    sedes.sort(key=lambda s: (str(s.get("code")) != _REF_SEDE, str(s.get("code"))))
    return sedes


def cargar_sheets(root: Path, variables: dict[str, str] | None, familia_id: str) -> dict[str, int]:
    variables = variables if variables is not None else load_vars(root)
    familias = _catalogo(root)
    familia = familias.get(familia_id)
    if familia is None:
        raise ValueError(
            f"familia {familia_id!r} no está en fuentes_medidas.json. "
            f"Usa: {', '.join(familias)}"
        )

    sources = [
        s
        for s in load_sources(root, variables)
        if s["type"] == "sheets" and s.get("familia") == familia_id
    ]
    if not sources:
        raise ValueError(f"inputs.yaml no declara fuentes familia={familia_id}")

    try:
        import gspread
    except ImportError as exc:
        raise SystemExit(
            "Falta gspread. Instala: pip install -r python/requirements.txt"
        ) from exc

    secret = root / "client_secret.json"
    if not secret.is_file():
        raise FileNotFoundError(f"No se encuentra {secret}")

    print(f"familia: {familia_id}")
    gc = gspread.service_account(filename=str(secret))
    books: dict[str, object] = {}
    conteos: dict[str, int] = {}
    sedes = _sedes(familia)

    conn = connect_h2(root, variables)
    try:
        cur = conn.cursor()
        try:
            for src in sources:
                stg = src["stg_table"]
                worksheet = str(src.get("worksheet") or "")
                if not worksheet:
                    raise ValueError(f"{stg}: falta worksheet")
                header_row = _as_int(src, "header_row", 1)
                data_start = _as_int(src, "data_start_row", header_row + 1)
                if data_start <= header_row:
                    raise ValueError(
                        f"{stg}: data_start_row ({data_start}) debe ser > header_row ({header_row})"
                    )

                ref_names: list[str] | None = None
                ref_indexes: list[int] | None = None
                todas: list[tuple] = []

                for sede in sedes:
                    code = str(sede.get("code") or "").strip()
                    name = str(sede.get("name") or "").strip()
                    key = str(sede.get("spreadsheet_key") or "").strip()
                    if not code or not key:
                        raise ValueError(f"{familia_id}: sede sin code o spreadsheet_key")
                    if key not in books:
                        book = _api(gc.open_by_key, key)
                        hojas = {ws.title: ws for ws in _api(book.worksheets)}
                        books[key] = hojas
                    hojas = books[key]
                    print(f"{familia_id} {code} {worksheet}")
                    if worksheet not in hojas:
                        raise ValueError(
                            f"{familia_id} {code} '{worksheet}': pestaña ausente. "
                            f"Hojas: {list(hojas)}"
                        )
                    grid = _api(hojas[worksheet].get_all_values)
                    if len(grid) < header_row:
                        raise ValueError(
                            f"{familia_id} {code} '{worksheet}': la hoja no tiene fila {header_row}"
                        )
                    names, indexes = _columnas(grid[header_row - 1], f"{familia_id} {code} {stg}")
                    if ref_names is None:
                        if code != _REF_SEDE:
                            raise ValueError(
                                f"{familia_id}: la primera sede debe ser {_REF_SEDE}, llegó {code}"
                            )
                        ref_names = names
                        ref_indexes = indexes
                    elif names != ref_names:
                        raise ValueError(
                            f"{familia_id} {code} '{worksheet}': fila de códigos {names} "
                            f"distinta de {_REF_SEDE} {ref_names}"
                        )
                    todas.extend(_filas(grid, indexes, data_start, code, name))

                assert ref_names is not None and ref_indexes is not None
                h2_cols = _columnas_h2(cur, stg)
                esperadas = list(ref_names) + list(_SEDE_COLS)
                if esperadas != h2_cols:
                    raise ValueError(
                        f"{stg}: columnas de la hoja {esperadas} no coinciden con H2 {h2_cols}"
                    )

                quoted = ", ".join(f'"{c}"' for c in esperadas)
                marks = ", ".join("?" for _ in esperadas)
                cur.execute(f"DELETE FROM PUBLIC.{stg}")
                sql = f"INSERT INTO PUBLIC.{stg} ({quoted}) VALUES ({marks})"
                for offset in range(0, len(todas), _BATCH):
                    cur.executemany(sql, todas[offset : offset + _BATCH])
                conteos[stg] = len(todas)
                print(f"{stg}: {len(todas)} filas")
        finally:
            cur.close()
        conn.commit()
    finally:
        conn.close()
    return conteos
