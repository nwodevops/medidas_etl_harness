#!/usr/bin/env python3
"""Carga una familia de Google Sheets → STG_MED_* en H2.

Uso:
  python/cargar_sheets.py suscripcion
  python/cargar_sheets.py seguimiento
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from config import load_vars, project_root  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Carga una familia de Sheets a H2")
    parser.add_argument("familia", choices=("suscripcion", "seguimiento"))
    args = parser.parse_args(argv)

    root = project_root()
    variables = load_vars(root)
    cargar = _load("cargar_sheets_io", HERE / "io" / "cargar_sheets.py")
    cargar.cargar_sheets(root, variables, args.familia)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
